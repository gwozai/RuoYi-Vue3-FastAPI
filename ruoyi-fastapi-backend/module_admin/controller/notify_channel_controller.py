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
from module_admin.service.notify_channel_service import NotifyChannelService
from module_admin.service.notify_send_service import NotifySendService
from module_admin.entity.vo.notify_channel_vo import NotifyChannelModel, NotifyChannelPageQueryModel, DeleteNotifyChannelModel
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


notifyChannelController = APIRouter(prefix='/notify/channel', dependencies=[Depends(LoginService.get_current_user)])


@notifyChannelController.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('notify:channel:list'))])
async def get_notify_channel_list(
    request: Request,
    query: NotifyChannelPageQueryModel = Depends(NotifyChannelPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """获取渠道ID列表"""
    result = await NotifyChannelService.get_notify_channel_list_services(query_db, query, is_page=True)
    return ResponseUtil.success(model_content=result)


@notifyChannelController.post('', dependencies=[Depends(CheckUserInterfaceAuth('notify:channel:add'))])
@Log(title='渠道ID', business_type=BusinessType.INSERT)
async def add_notify_channel(
    request: Request,
    obj: NotifyChannelModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增渠道ID"""
    obj.create_by = current_user.user.user_name
    obj.create_time = datetime.now()
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyChannelService.add_notify_channel_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@notifyChannelController.put('', dependencies=[Depends(CheckUserInterfaceAuth('notify:channel:edit'))])
@Log(title='渠道ID', business_type=BusinessType.UPDATE)
async def update_notify_channel(
    request: Request,
    obj: NotifyChannelModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新渠道ID"""
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyChannelService.update_notify_channel_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@notifyChannelController.delete('/{channel_ids}', dependencies=[Depends(CheckUserInterfaceAuth('notify:channel:remove'))])
@Log(title='通知渠道', business_type=BusinessType.DELETE)
async def delete_notify_channel(request: Request, channel_ids: str, query_db: AsyncSession = Depends(get_db)):
    """删除通知渠道"""
    result = await NotifyChannelService.delete_notify_channel_services(query_db, DeleteNotifyChannelModel(channel_ids=channel_ids))
    return ResponseUtil.success(msg=result.message)


@notifyChannelController.get('/{channel_id}', dependencies=[Depends(CheckUserInterfaceAuth('notify:channel:query'))])
async def get_notify_channel_by_id(request: Request, channel_id: int, query_db: AsyncSession = Depends(get_db)):
    """获取渠道详情"""
    result = await NotifyChannelService.get_notify_channel_by_id_services(query_db, channel_id)
    return ResponseUtil.success(data=result)


@notifyChannelController.post('/test/{channel_id}', dependencies=[Depends(CheckUserInterfaceAuth('notify:channel:test'))])
async def test_notify_channel(
    request: Request,
    channel_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """测试渠道连通性"""
    result = await NotifySendService.test_channel(query_db, channel_id, current_user.user.user_id)
    if result['success']:
        return ResponseUtil.success(msg=result['message'])
    else:
        return ResponseUtil.error(msg=result['message'])
