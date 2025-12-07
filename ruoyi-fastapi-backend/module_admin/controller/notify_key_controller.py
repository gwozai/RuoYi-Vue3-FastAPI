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
from module_admin.service.notify_key_service import NotifyKeyService
from module_admin.service.notify_send_service import NotifySendService
from module_admin.entity.vo.notify_key_vo import NotifyKeyModel, NotifyKeyPageQueryModel, DeleteNotifyKeyModel
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


notifyKeyController = APIRouter(prefix='/notify/key', dependencies=[Depends(LoginService.get_current_user)])


@notifyKeyController.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('notify:key:list'))])
async def get_notify_key_list(
    request: Request,
    query: NotifyKeyPageQueryModel = Depends(NotifyKeyPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """获取密钥ID列表"""
    result = await NotifyKeyService.get_notify_key_list_services(query_db, query, is_page=True)
    return ResponseUtil.success(model_content=result)


@notifyKeyController.post('', dependencies=[Depends(CheckUserInterfaceAuth('notify:key:add'))])
@Log(title='密钥ID', business_type=BusinessType.INSERT)
async def add_notify_key(
    request: Request,
    obj: NotifyKeyModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增密钥ID"""
    obj.create_by = current_user.user.user_name
    obj.create_time = datetime.now()
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyKeyService.add_notify_key_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@notifyKeyController.put('', dependencies=[Depends(CheckUserInterfaceAuth('notify:key:edit'))])
@Log(title='密钥ID', business_type=BusinessType.UPDATE)
async def update_notify_key(
    request: Request,
    obj: NotifyKeyModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新密钥ID"""
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyKeyService.update_notify_key_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@notifyKeyController.delete('/{key_ids}', dependencies=[Depends(CheckUserInterfaceAuth('notify:key:remove'))])
@Log(title='API密钥', business_type=BusinessType.DELETE)
async def delete_notify_key(request: Request, key_ids: str, query_db: AsyncSession = Depends(get_db)):
    """删除API密钥"""
    result = await NotifyKeyService.delete_notify_key_services(query_db, DeleteNotifyKeyModel(key_ids=key_ids))
    return ResponseUtil.success(msg=result.message)


@notifyKeyController.get('/{key_id}', dependencies=[Depends(CheckUserInterfaceAuth('notify:key:query'))])
async def get_notify_key_by_id(request: Request, key_id: int, query_db: AsyncSession = Depends(get_db)):
    """获取API密钥详情"""
    result = await NotifyKeyService.get_notify_key_by_id_services(query_db, key_id)
    return ResponseUtil.success(data=result)


@notifyKeyController.post('/generate', dependencies=[Depends(CheckUserInterfaceAuth('notify:key:add'))])
@Log(title='API密钥', business_type=BusinessType.INSERT)
async def generate_api_key(
    request: Request,
    obj: NotifyKeyModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """生成新的API密钥"""
    obj.key_id = None  # 确保不传入key_id，让数据库自动生成
    obj.user_id = current_user.user.user_id
    obj.api_key = NotifySendService.generate_api_key()
    obj.create_by = current_user.user.user_name
    obj.create_time = datetime.now()
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await NotifyKeyService.add_notify_key_services(query_db, obj)
    return ResponseUtil.success(msg=result.message, data={'api_key': obj.api_key})


@notifyKeyController.post('/reset/{key_id}', dependencies=[Depends(CheckUserInterfaceAuth('notify:key:reset'))])
@Log(title='API密钥', business_type=BusinessType.UPDATE)
async def reset_api_key(
    request: Request,
    key_id: int,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """重置API密钥"""
    from sqlalchemy import update
    from module_admin.entity.do.notify_key_do import NotifyKey
    
    new_api_key = NotifySendService.generate_api_key()
    await query_db.execute(
        update(NotifyKey)
        .where(NotifyKey.key_id == key_id)
        .values(
            api_key=new_api_key,
            update_by=current_user.user.user_name,
            update_time=datetime.now(),
        )
    )
    await query_db.commit()
    return ResponseUtil.success(msg='密钥重置成功', data={'api_key': new_api_key})
