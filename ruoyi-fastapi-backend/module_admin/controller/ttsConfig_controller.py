from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_admin.service.ttsConfig_service import TtsconfigService
from module_admin.entity.vo.ttsConfig_vo import DeleteTtsconfigModel, TtsconfigModel, TtsconfigPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


ttsConfigController = APIRouter(prefix='/system/ttsConfig', dependencies=[Depends(LoginService.get_current_user)])


@ttsConfigController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('system:ttsConfig:list'))]
)
async def get_system_ttsConfig_list(
    request: Request,
    ttsConfig_page_query: TtsconfigPageQueryModel = Depends(TtsconfigPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 管理员可以查看所有配置，普通用户只能查看自己的配置
    if not current_user.user.admin:
        ttsConfig_page_query.user_id = current_user.user.user_id
    ttsConfig_page_query_result = await TtsconfigService.get_ttsConfig_list_services(query_db, ttsConfig_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=ttsConfig_page_query_result)


@ttsConfigController.post('', dependencies=[Depends(CheckUserInterfaceAuth('system:ttsConfig:add'))])
@ValidateFields(validate_model='add_ttsConfig')
@Log(title='TTS API配置', business_type=BusinessType.INSERT)
async def add_system_ttsConfig(
    request: Request,
    add_ttsConfig: TtsconfigModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    # 管理员可以为任意用户添加配置，普通用户只能为自己添加
    if not current_user.user.admin or add_ttsConfig.user_id is None:
        add_ttsConfig.user_id = current_user.user.user_id
    add_ttsConfig.create_by = current_user.user.user_name
    add_ttsConfig.create_time = datetime.now()
    add_ttsConfig.update_by = current_user.user.user_name
    add_ttsConfig.update_time = datetime.now()
    add_ttsConfig_result = await TtsconfigService.add_ttsConfig_services(query_db, add_ttsConfig)
    logger.info(add_ttsConfig_result.message)

    return ResponseUtil.success(msg=add_ttsConfig_result.message)


@ttsConfigController.put('', dependencies=[Depends(CheckUserInterfaceAuth('system:ttsConfig:edit'))])
@ValidateFields(validate_model='edit_ttsConfig')
@Log(title='TTS API配置', business_type=BusinessType.UPDATE)
async def edit_system_ttsConfig(
    request: Request,
    edit_ttsConfig: TtsconfigModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_ttsConfig.update_by = current_user.user.user_name
    edit_ttsConfig.update_time = datetime.now()
    edit_ttsConfig_result = await TtsconfigService.edit_ttsConfig_services(query_db, edit_ttsConfig)
    logger.info(edit_ttsConfig_result.message)

    return ResponseUtil.success(msg=edit_ttsConfig_result.message)


@ttsConfigController.delete('/{config_ids}', dependencies=[Depends(CheckUserInterfaceAuth('system:ttsConfig:remove'))])
@Log(title='TTS API配置', business_type=BusinessType.DELETE)
async def delete_system_ttsConfig(request: Request, config_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_ttsConfig = DeleteTtsconfigModel(configIds=config_ids)
    delete_ttsConfig_result = await TtsconfigService.delete_ttsConfig_services(query_db, delete_ttsConfig)
    logger.info(delete_ttsConfig_result.message)

    return ResponseUtil.success(msg=delete_ttsConfig_result.message)


@ttsConfigController.get(
    '/{config_id}', response_model=TtsconfigModel, dependencies=[Depends(CheckUserInterfaceAuth('system:ttsConfig:query'))]
)
async def query_detail_system_ttsConfig(request: Request, config_id: int, query_db: AsyncSession = Depends(get_db)):
    ttsConfig_detail_result = await TtsconfigService.ttsConfig_detail_services(query_db, config_id)
    logger.info(f'获取config_id为{config_id}的信息成功')

    return ResponseUtil.success(data=ttsConfig_detail_result)


@ttsConfigController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('system:ttsConfig:export'))])
@Log(title='TTS API配置', business_type=BusinessType.EXPORT)
async def export_system_ttsConfig_list(
    request: Request,
    ttsConfig_page_query: TtsconfigPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    ttsConfig_query_result = await TtsconfigService.get_ttsConfig_list_services(query_db, ttsConfig_page_query, is_page=False)
    ttsConfig_export_result = await TtsconfigService.export_ttsConfig_list_services(ttsConfig_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(ttsConfig_export_result))
