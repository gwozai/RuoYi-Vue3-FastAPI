from datetime import datetime
from fastapi import APIRouter, Depends, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_admin.service.notify_platform_service import NotifyPlatformService
from module_admin.entity.vo.notify_platform_vo import NotifyPlatformModel, NotifyPlatformPageQueryModel, DeleteNotifyPlatformModel
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


notifyPlatformController = APIRouter(prefix='/notify/platform', dependencies=[Depends(LoginService.get_current_user)])


@notifyPlatformController.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('notify:platform:list'))])
async def get_notify_platform_list(
    request: Request,
    query: NotifyPlatformPageQueryModel = Depends(NotifyPlatformPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """获取平台ID列表"""
    result = await NotifyPlatformService.get_notify_platform_list_services(query_db, query, is_page=True)
    return ResponseUtil.success(model_content=result)


@notifyPlatformController.post('', dependencies=[Depends(CheckUserInterfaceAuth('notify:platform:add'))])
@Log(title='平台ID', business_type=BusinessType.INSERT)
async def add_notify_platform(
    request: Request,
    obj: NotifyPlatformModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增平台ID"""
    obj.create_by = current_user.user.user_name
    obj.create_time = datetime.now()
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyPlatformService.add_notify_platform_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@notifyPlatformController.put('', dependencies=[Depends(CheckUserInterfaceAuth('notify:platform:edit'))])
@Log(title='平台ID', business_type=BusinessType.UPDATE)
async def update_notify_platform(
    request: Request,
    obj: NotifyPlatformModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新平台ID"""
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyPlatformService.update_notify_platform_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@notifyPlatformController.delete('/{platform_ids}', dependencies=[Depends(CheckUserInterfaceAuth('notify:platform:remove'))])
@Log(title='通知平台', business_type=BusinessType.DELETE)
async def delete_notify_platform(request: Request, platform_ids: str, query_db: AsyncSession = Depends(get_db)):
    """删除通知平台"""
    result = await NotifyPlatformService.delete_notify_platform_services(query_db, DeleteNotifyPlatformModel(platform_ids=platform_ids))
    return ResponseUtil.success(msg=result.message)


@notifyPlatformController.get('/{platform_id}', dependencies=[Depends(CheckUserInterfaceAuth('notify:platform:query'))])
async def get_notify_platform_by_id(request: Request, platform_id: int, query_db: AsyncSession = Depends(get_db)):
    """获取通知平台详情"""
    result = await NotifyPlatformService.get_notify_platform_by_id_services(query_db, platform_id)
    return ResponseUtil.success(data=result)
