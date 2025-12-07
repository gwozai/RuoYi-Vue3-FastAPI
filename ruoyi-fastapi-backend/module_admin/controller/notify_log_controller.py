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
from module_admin.service.notify_log_service import NotifyLogService
from module_admin.entity.vo.notify_log_vo import NotifyLogModel, NotifyLogPageQueryModel, DeleteNotifyLogModel
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


notifyLogController = APIRouter(prefix='/notify/log', dependencies=[Depends(LoginService.get_current_user)])


@notifyLogController.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('notify:log:list'))])
async def get_notify_log_list(
    request: Request,
    query: NotifyLogPageQueryModel = Depends(NotifyLogPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """获取日志ID列表"""
    result = await NotifyLogService.get_notify_log_list_services(query_db, query, is_page=True)
    return ResponseUtil.success(model_content=result)


@notifyLogController.post('', dependencies=[Depends(CheckUserInterfaceAuth('notify:log:add'))])
@Log(title='日志ID', business_type=BusinessType.INSERT)
async def add_notify_log(
    request: Request,
    obj: NotifyLogModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增日志ID"""
    obj.create_by = current_user.user.user_name
    obj.create_time = datetime.now()
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyLogService.add_notify_log_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@notifyLogController.put('', dependencies=[Depends(CheckUserInterfaceAuth('notify:log:edit'))])
@Log(title='日志ID', business_type=BusinessType.UPDATE)
async def update_notify_log(
    request: Request,
    obj: NotifyLogModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新日志ID"""
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyLogService.update_notify_log_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@notifyLogController.delete('/{log_ids}', dependencies=[Depends(CheckUserInterfaceAuth('notify:log:remove'))])
@Log(title='发送记录', business_type=BusinessType.DELETE)
async def delete_notify_log(request: Request, log_ids: str, query_db: AsyncSession = Depends(get_db)):
    """删除发送记录"""
    result = await NotifyLogService.delete_notify_log_services(query_db, DeleteNotifyLogModel(log_ids=log_ids))
    return ResponseUtil.success(msg=result.message)


@notifyLogController.get('/{log_id}', dependencies=[Depends(CheckUserInterfaceAuth('notify:log:query'))])
async def get_notify_log_by_id(request: Request, log_id: int, query_db: AsyncSession = Depends(get_db)):
    """获取发送记录详情"""
    result = await NotifyLogService.get_notify_log_by_id_services(query_db, log_id)
    return ResponseUtil.success(data=result)
