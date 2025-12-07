from datetime import datetime
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse
from pathlib import Path
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.env import UploadConfig
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_admin.service.audio_service import AudioService
from module_admin.entity.vo.audio_vo import (
    DeleteAudioModel, AudioModel, AudioPageQueryModel, AudioGenerateModel
)
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


audioController = APIRouter(prefix='/system/audio', dependencies=[Depends(LoginService.get_current_user)])


@audioController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('system:audio:list'))]
)
async def get_system_audio_list(
    request: Request,
    audio_page_query: AudioPageQueryModel = Depends(AudioPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """获取音频列表"""
    audio_page_query_result = await AudioService.get_audio_list_services(query_db, audio_page_query, is_page=True)
    logger.info('获取音频列表成功')

    return ResponseUtil.success(model_content=audio_page_query_result)


@audioController.post('/generate', dependencies=[Depends(CheckUserInterfaceAuth('system:audio:add'))])
@Log(title='音频生成', business_type=BusinessType.INSERT)
async def generate_audio(
    request: Request,
    generate_audio: AudioGenerateModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """生成音频"""
    generate_result = await AudioService.generate_audio_services(
        query_db, generate_audio, current_user.user.user_id, current_user.user.user_name
    )
    logger.info(generate_result.message)

    return ResponseUtil.success(msg=generate_result.message, data=generate_result.result)


@audioController.post('', dependencies=[Depends(CheckUserInterfaceAuth('system:audio:add'))])
@ValidateFields(validate_model='add_audio')
@Log(title='音频记录', business_type=BusinessType.INSERT)
async def add_system_audio(
    request: Request,
    add_audio: AudioModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增音频记录"""
    add_audio.create_by = current_user.user.user_name
    add_audio.create_time = datetime.now()
    add_audio.update_by = current_user.user.user_name
    add_audio.update_time = datetime.now()
    add_audio_result = await AudioService.add_audio_services(query_db, add_audio)
    logger.info(add_audio_result.message)

    return ResponseUtil.success(msg=add_audio_result.message)


@audioController.put('', dependencies=[Depends(CheckUserInterfaceAuth('system:audio:edit'))])
@ValidateFields(validate_model='edit_audio')
@Log(title='音频记录', business_type=BusinessType.UPDATE)
async def edit_system_audio(
    request: Request,
    edit_audio: AudioModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """编辑音频记录"""
    edit_audio.update_by = current_user.user.user_name
    edit_audio.update_time = datetime.now()
    edit_audio_result = await AudioService.edit_audio_services(query_db, edit_audio)
    logger.info(edit_audio_result.message)

    return ResponseUtil.success(msg=edit_audio_result.message)


@audioController.delete('/{audio_ids}', dependencies=[Depends(CheckUserInterfaceAuth('system:audio:remove'))])
@Log(title='音频记录', business_type=BusinessType.DELETE)
async def delete_system_audio(request: Request, audio_ids: str, query_db: AsyncSession = Depends(get_db)):
    """删除音频记录"""
    delete_audio = DeleteAudioModel(audioIds=audio_ids)
    delete_audio_result = await AudioService.delete_audio_services(query_db, delete_audio)
    logger.info(delete_audio_result.message)

    return ResponseUtil.success(msg=delete_audio_result.message)


@audioController.get(
    '/{audio_id}', response_model=AudioModel, dependencies=[Depends(CheckUserInterfaceAuth('system:audio:query'))]
)
async def query_detail_system_audio(request: Request, audio_id: int, query_db: AsyncSession = Depends(get_db)):
    """获取音频详情"""
    audio_detail_result = await AudioService.audio_detail_services(query_db, audio_id)
    logger.info(f'获取audio_id为{audio_id}的信息成功')

    return ResponseUtil.success(data=audio_detail_result)


@audioController.get('/voices/list')
async def get_available_voices(request: Request):
    """获取可用的语音模型列表"""
    voices = AudioService.get_available_voices()
    return ResponseUtil.success(data=voices)


@audioController.get('/ttsConfigs/list')
async def get_user_tts_configs(
    request: Request,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """获取当前用户的 TTS 配置列表"""
    tts_configs = await AudioService.get_user_tts_configs(query_db, current_user.user.user_id)
    return ResponseUtil.success(data=tts_configs)


@audioController.get('/download/{audio_id}', dependencies=[Depends(CheckUserInterfaceAuth('system:audio:query'))])
async def download_audio(request: Request, audio_id: int, query_db: AsyncSession = Depends(get_db)):
    """下载音频文件"""
    audio_detail = await AudioService.audio_detail_services(query_db, audio_id)
    if not audio_detail.file_path:
        return ResponseUtil.failure(msg='音频文件不存在')
    
    # 构建完整文件路径 - 将 /profile/audio/xxx.mp3 转换为实际路径
    file_full_path = Path(UploadConfig.UPLOAD_PATH) / audio_detail.file_path.replace(UploadConfig.UPLOAD_PREFIX, '').lstrip('/')
    
    if not file_full_path.exists():
        return ResponseUtil.failure(msg='音频文件不存在')
    
    return FileResponse(
        path=str(file_full_path),
        filename=f"{audio_detail.audio_name}.{audio_detail.response_format}",
        media_type=f"audio/{audio_detail.response_format}"
    )
