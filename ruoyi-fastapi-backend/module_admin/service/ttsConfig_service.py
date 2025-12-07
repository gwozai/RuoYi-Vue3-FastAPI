from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.dao.ttsConfig_dao import TtsconfigDao
from module_admin.entity.vo.ttsConfig_vo import DeleteTtsconfigModel, TtsconfigModel, TtsconfigPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class TtsconfigService:
    """
    TTS API配置模块服务层
    """

    @classmethod
    async def get_ttsConfig_list_services(
        cls, query_db: AsyncSession, query_object: TtsconfigPageQueryModel, is_page: bool = False
    ):
        """
        获取TTS API配置列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: TTS API配置列表信息对象
        """
        ttsConfig_list_result = await TtsconfigDao.get_ttsConfig_list(query_db, query_object, is_page)

        return ttsConfig_list_result


    @classmethod
    async def add_ttsConfig_services(cls, query_db: AsyncSession, page_object: TtsconfigModel):
        """
        新增TTS API配置信息service

        :param query_db: orm对象
        :param page_object: 新增TTS API配置对象
        :return: 新增TTS API配置校验结果
        """
        try:
            await TtsconfigDao.add_ttsConfig_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_ttsConfig_services(cls, query_db: AsyncSession, page_object: TtsconfigModel):
        """
        编辑TTS API配置信息service

        :param query_db: orm对象
        :param page_object: 编辑TTS API配置对象
        :return: 编辑TTS API配置校验结果
        """
        edit_ttsConfig = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time', })
        ttsConfig_info = await cls.ttsConfig_detail_services(query_db, page_object.config_id)
        if ttsConfig_info.config_id:
            try:
                await TtsconfigDao.edit_ttsConfig_dao(query_db, edit_ttsConfig)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='TTS API配置不存在')

    @classmethod
    async def delete_ttsConfig_services(cls, query_db: AsyncSession, page_object: DeleteTtsconfigModel):
        """
        删除TTS API配置信息service

        :param query_db: orm对象
        :param page_object: 删除TTS API配置对象
        :return: 删除TTS API配置校验结果
        """
        if page_object.config_ids:
            config_id_list = page_object.config_ids.split(',')
            try:
                for config_id in config_id_list:
                    await TtsconfigDao.delete_ttsConfig_dao(query_db, TtsconfigModel(configId=config_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入配置ID为空')

    @classmethod
    async def ttsConfig_detail_services(cls, query_db: AsyncSession, config_id: int):
        """
        获取TTS API配置详细信息service

        :param query_db: orm对象
        :param config_id: 配置ID
        :return: 配置ID对应的信息
        """
        ttsConfig = await TtsconfigDao.get_ttsConfig_detail_by_id(query_db, config_id=config_id)
        if ttsConfig:
            result = TtsconfigModel(**CamelCaseUtil.transform_result(ttsConfig))
        else:
            result = TtsconfigModel(**dict())

        return result

    @staticmethod
    async def export_ttsConfig_list_services(ttsConfig_list: List):
        """
        导出TTS API配置信息service

        :param ttsConfig_list: TTS API配置信息列表
        :return: TTS API配置信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'configId': '配置ID',
            'userId': '用户ID',
            'configName': '配置名称',
            'apiUrl': 'API地址',
            'apiKey': 'API密钥',
            'apiModel': 'API模型',
            'isDefault': '是否默认',
            'status': '状态',
            'createBy': '创建者',
            'createTime': '创建时间',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'remark': '备注',
        }
        binary_data = ExcelUtil.export_list2excel(ttsConfig_list, mapping_dict)

        return binary_data
