import os
import uuid
import httpx
from datetime import datetime
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.env import UploadConfig
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.dao.audio_dao import AudioDao
from module_admin.dao.ttsConfig_dao import TtsconfigDao
from module_admin.entity.vo.audio_vo import (
    DeleteAudioModel, AudioModel, AudioPageQueryModel, 
    AudioGenerateModel, AVAILABLE_VOICES
)
from module_admin.entity.vo.ttsConfig_vo import TtsconfigPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.log_util import logger


# 默认 TTS API 配置（当用户没有配置时使用）
DEFAULT_TTS_API_URL = "http://117.72.56.34:5050/v1/audio/speech"
DEFAULT_TTS_API_KEY = "your_api_key_here"


class AudioService:
    """
    音频生成模块服务层
    """

    @classmethod
    async def get_audio_list_services(
        cls, query_db: AsyncSession, query_object: AudioPageQueryModel, is_page: bool = False
    ):
        """
        获取音频列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 音频列表信息对象
        """
        audio_list_result = await AudioDao.get_audio_list(query_db, query_object, is_page)

        return audio_list_result

    @classmethod
    async def generate_audio_services(cls, query_db: AsyncSession, generate_object: AudioGenerateModel, user_id: int, user_name: str):
        """
        生成音频service

        :param query_db: orm对象
        :param generate_object: 生成音频参数对象
        :param user_id: 当前用户ID
        :param user_name: 当前用户名
        :return: 生成结果
        """
        try:
            logger.info(f"接收到的生成参数: {generate_object.model_dump()}")
            
            # 获取用户的 TTS 配置（如果指定了 config_id 则使用指定配置，否则使用默认配置）
            tts_config = await cls._get_user_tts_config(query_db, user_id, generate_object.config_id)
            
            # 生成音频名称
            audio_name = generate_object.audio_name or f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # 创建音频记录
            audio_model = AudioModel(
                audio_name=audio_name,
                input_text=generate_object.input_text,
                voice=generate_object.voice,
                model=generate_object.model,
                speed=generate_object.speed,
                response_format=generate_object.response_format,
                status='0',  # 生成中
                create_by=user_name,
                create_time=datetime.now(),
                update_by=user_name,
                update_time=datetime.now(),
                remark=generate_object.remark
            )
            
            db_audio = await AudioDao.add_audio_dao(query_db, audio_model)
            audio_id = db_audio.audio_id
            
            # 调用 TTS API 生成音频
            try:
                audio_data = await cls._call_tts_api(generate_object, tts_config)
                
                # 保存音频文件
                file_name = f"{uuid.uuid4().hex}.{generate_object.response_format}"
                upload_path = Path(UploadConfig.UPLOAD_PATH) / "audio"
                upload_path.mkdir(parents=True, exist_ok=True)
                file_path = upload_path / file_name
                
                with open(file_path, 'wb') as f:
                    f.write(audio_data)
                
                file_size = len(audio_data)
                relative_path = f"{UploadConfig.UPLOAD_PREFIX}/audio/{file_name}"
                
                # 更新状态为成功
                await AudioDao.update_audio_status(
                    query_db, 
                    audio_id, 
                    status='1',
                    file_path=relative_path,
                    file_size=file_size
                )
                await query_db.commit()
                
                return CrudResponseModel(
                    is_success=True, 
                    message='音频生成成功',
                    result={'audio_id': audio_id, 'file_path': relative_path}
                )
                
            except Exception as e:
                # 更新状态为失败
                await AudioDao.update_audio_status(
                    query_db,
                    audio_id,
                    status='2',
                    error_msg=str(e)[:500]
                )
                await query_db.commit()
                logger.error(f"TTS API调用失败: {e}")
                raise ServiceException(message=f'音频生成失败: {str(e)}')
                
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def _get_user_tts_config(cls, query_db: AsyncSession, user_id: int, config_id: int = None) -> dict:
        """
        获取用户的 TTS 配置

        :param query_db: orm对象
        :param user_id: 用户ID
        :param config_id: 指定的配置ID（可选）
        :return: TTS 配置字典
        """
        try:
            from sqlalchemy import select, and_
            from module_admin.entity.do.ttsConfig_do import SysTtsConfig
            
            # 如果指定了 config_id，直接查询该配置
            if config_id:
                query = select(SysTtsConfig).where(
                    and_(
                        SysTtsConfig.config_id == config_id,
                        SysTtsConfig.user_id == user_id,  # 确保是用户自己的配置
                        SysTtsConfig.status == '0'
                    )
                )
                result = await query_db.execute(query)
                config = result.scalars().first()
                
                if config:
                    logger.info(f"使用指定的TTS配置: {config.config_name} (ID: {config.config_id})")
                    return {
                        'config_id': config.config_id,
                        'config_name': config.config_name,
                        'api_url': config.api_url,
                        'api_key': config.api_key,
                        'api_model': config.api_model
                    }
                else:
                    logger.warning(f"指定的TTS配置不存在或无权限: config_id={config_id}")
            
            # 查询用户的默认 TTS 配置
            query = select(SysTtsConfig).where(
                and_(
                    SysTtsConfig.user_id == user_id,
                    SysTtsConfig.is_default == '1',
                    SysTtsConfig.status == '0'
                )
            )
            result = await query_db.execute(query)
            config = result.scalars().first()
            
            if config:
                logger.info(f"使用默认TTS配置: {config.config_name} (ID: {config.config_id})")
                return {
                    'config_id': config.config_id,
                    'config_name': config.config_name,
                    'api_url': config.api_url,
                    'api_key': config.api_key,
                    'api_model': config.api_model
                }
            
            # 如果用户没有默认配置，查询用户的任意可用配置
            query = select(SysTtsConfig).where(
                and_(
                    SysTtsConfig.user_id == user_id,
                    SysTtsConfig.status == '0'
                )
            ).limit(1)
            result = await query_db.execute(query)
            config = result.scalars().first()
            
            if config:
                logger.info(f"使用用户首个可用TTS配置: {config.config_name} (ID: {config.config_id})")
                return {
                    'config_id': config.config_id,
                    'config_name': config.config_name,
                    'api_url': config.api_url,
                    'api_key': config.api_key,
                    'api_model': config.api_model
                }
            
        except Exception as e:
            logger.warning(f"获取用户TTS配置失败: {e}")
        
        # 返回系统默认配置
        logger.info("使用系统默认TTS配置")
        return {
            'config_id': None,
            'config_name': '系统默认',
            'api_url': DEFAULT_TTS_API_URL,
            'api_key': DEFAULT_TTS_API_KEY,
            'api_model': 'tts-1'
        }

    @classmethod
    async def get_user_tts_configs(cls, query_db: AsyncSession, user_id: int) -> List[dict]:
        """
        获取用户的所有 TTS 配置列表

        :param query_db: orm对象
        :param user_id: 用户ID
        :return: TTS 配置列表
        """
        try:
            from sqlalchemy import select, and_
            from module_admin.entity.do.ttsConfig_do import SysTtsConfig
            
            query = select(SysTtsConfig).where(
                and_(
                    SysTtsConfig.user_id == user_id,
                    SysTtsConfig.status == '0'
                )
            ).order_by(SysTtsConfig.is_default.desc(), SysTtsConfig.config_id.asc())
            
            result = await query_db.execute(query)
            configs = result.scalars().all()
            
            config_list = []
            for config in configs:
                config_list.append({
                    'configId': config.config_id,
                    'configName': config.config_name,
                    'apiUrl': config.api_url,
                    'apiModel': config.api_model,
                    'isDefault': config.is_default
                })
            
            return config_list
            
        except Exception as e:
            logger.warning(f"获取用户TTS配置列表失败: {e}")
            return []

    @classmethod
    async def _call_tts_api(cls, generate_object: AudioGenerateModel, tts_config: dict) -> bytes:
        """
        调用 TTS API

        :param generate_object: 生成参数
        :param tts_config: TTS 配置
        :return: 音频二进制数据
        """
        api_url = tts_config.get('api_url', DEFAULT_TTS_API_URL)
        api_key = tts_config.get('api_key', DEFAULT_TTS_API_KEY)
        api_model = tts_config.get('api_model', 'tts-1')
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": generate_object.model or api_model,
            "input": generate_object.input_text,
            "voice": generate_object.voice or "zh-CN-XiaoxiaoNeural",
            "response_format": generate_object.response_format or "mp3",
            "speed": generate_object.speed or 1.0
        }
        
        logger.info(f"调用TTS API: {api_url}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(api_url, headers=headers, json=payload)
            
            if response.status_code != 200:
                raise Exception(f"TTS API返回错误: {response.status_code} - {response.text}")
            
            return response.content

    @classmethod
    async def add_audio_services(cls, query_db: AsyncSession, page_object: AudioModel):
        """
        新增音频信息service

        :param query_db: orm对象
        :param page_object: 新增音频对象
        :return: 新增音频校验结果
        """
        try:
            await AudioDao.add_audio_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_audio_services(cls, query_db: AsyncSession, page_object: AudioModel):
        """
        编辑音频信息service

        :param query_db: orm对象
        :param page_object: 编辑音频对象
        :return: 编辑音频校验结果
        """
        edit_audio = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time'})
        audio_info = await cls.audio_detail_services(query_db, page_object.audio_id)
        if audio_info.audio_id:
            try:
                await AudioDao.edit_audio_dao(query_db, edit_audio)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='音频记录不存在')

    @classmethod
    async def delete_audio_services(cls, query_db: AsyncSession, page_object: DeleteAudioModel):
        """
        删除音频信息service

        :param query_db: orm对象
        :param page_object: 删除音频对象
        :return: 删除音频校验结果
        """
        if page_object.audio_ids:
            audio_id_list = page_object.audio_ids.split(',')
            try:
                for audio_id in audio_id_list:
                    # 获取音频信息，删除文件
                    audio_info = await cls.audio_detail_services(query_db, int(audio_id))
                    if audio_info.file_path:
                        # 将 /profile/audio/xxx.mp3 转换为实际路径
                        file_full_path = Path(UploadConfig.UPLOAD_PATH) / audio_info.file_path.replace(UploadConfig.UPLOAD_PREFIX, '').lstrip('/')
                        if file_full_path.exists():
                            file_full_path.unlink()
                    
                    await AudioDao.delete_audio_dao(query_db, AudioModel(audioId=audio_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入音频ID为空')

    @classmethod
    async def audio_detail_services(cls, query_db: AsyncSession, audio_id: int):
        """
        获取音频详细信息service

        :param query_db: orm对象
        :param audio_id: 音频ID
        :return: 音频ID对应的信息
        """
        audio = await AudioDao.get_audio_detail_by_id(query_db, audio_id=audio_id)
        if audio:
            result = AudioModel(**CamelCaseUtil.transform_result(audio))
        else:
            result = AudioModel(**dict())

        return result

    @staticmethod
    def get_available_voices():
        """
        获取可用的语音模型列表
        """
        return AVAILABLE_VOICES
