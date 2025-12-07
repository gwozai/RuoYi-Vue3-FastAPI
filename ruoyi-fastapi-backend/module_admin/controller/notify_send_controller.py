"""
通知发送API控制器

公开API，通过API密钥认证，不需要登录

使用方式:
    GET  /notify/send/{api_key}?title=标题&content=内容
    POST /notify/send/{api_key}
    GET  /notify/send/{api_key}/{content}  # 快捷方式
"""

from fastapi import APIRouter, Depends, Request, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel, Field

from config.get_db import get_db
from module_admin.service.notify_send_service import NotifySendService
from utils.response_util import ResponseUtil
from utils.log_util import logger


# 公开API，不需要登录验证
notifySendController = APIRouter(prefix='/notify/send', tags=['通知发送'])


class SendNotifyRequest(BaseModel):
    """发送通知请求"""
    title: Optional[str] = Field(default='', description='消息标题')
    content: str = Field(default='', description='消息内容')
    msg_type: Optional[str] = Field(default='text', description='消息类型(text/markdown)')
    channel_id: Optional[int] = Field(default=None, description='指定渠道ID')


def get_client_ip(request: Request) -> str:
    """获取客户端IP"""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.client.host if request.client else ''


@notifySendController.get('/{api_key}')
async def send_notify_get(
    request: Request,
    api_key: str,
    title: Optional[str] = Query(default='', description='消息标题'),
    content: Optional[str] = Query(default='', alias='text', description='消息内容'),
    desp: Optional[str] = Query(default='', description='消息内容(兼容Server酱)'),
    msg_type: Optional[str] = Query(default='text', description='消息类型'),
    channel_id: Optional[int] = Query(default=None, description='指定渠道ID'),
    query_db: AsyncSession = Depends(get_db),
):
    """
    GET方式发送通知
    
    兼容Server酱的参数格式:
    - title: 消息标题
    - desp: 消息内容
    
    也支持:
    - content/text: 消息内容
    """
    # 兼容Server酱的desp参数
    message_content = content or desp
    
    if not message_content and not title:
        return ResponseUtil.error(msg='消息内容不能为空')
    
    try:
        ip_address = get_client_ip(request)
        result = await NotifySendService.send_by_api_key(
            db=query_db,
            api_key=api_key,
            title=title,
            content=message_content,
            msg_type=msg_type,
            channel_id=channel_id,
            ip_address=ip_address,
        )
        
        if result['success']:
            return ResponseUtil.success(
                data=result,
                msg=f"发送成功 ({result['success_count']}/{result['total']})"
            )
        else:
            return ResponseUtil.error(
                msg=f"发送失败",
                data=result
            )
    except Exception as e:
        logger.error(f"发送通知失败: {e}")
        return ResponseUtil.error(msg=str(e))


@notifySendController.post('/{api_key}')
async def send_notify_post(
    request: Request,
    api_key: str,
    body: SendNotifyRequest = Body(default=None),
    title: Optional[str] = Query(default=None, description='消息标题'),
    content: Optional[str] = Query(default=None, description='消息内容'),
    query_db: AsyncSession = Depends(get_db),
):
    """
    POST方式发送通知
    
    支持JSON Body或Query参数
    """
    # 优先使用Body参数，其次Query参数
    msg_title = (body.title if body else None) or title or ''
    msg_content = (body.content if body else None) or content or ''
    msg_type = (body.msg_type if body else None) or 'text'
    channel_id = (body.channel_id if body else None)
    
    if not msg_content and not msg_title:
        return ResponseUtil.error(msg='消息内容不能为空')
    
    try:
        ip_address = get_client_ip(request)
        result = await NotifySendService.send_by_api_key(
            db=query_db,
            api_key=api_key,
            title=msg_title,
            content=msg_content,
            msg_type=msg_type,
            channel_id=channel_id,
            ip_address=ip_address,
        )
        
        if result['success']:
            return ResponseUtil.success(
                data=result,
                msg=f"发送成功 ({result['success_count']}/{result['total']})"
            )
        else:
            return ResponseUtil.error(
                msg=f"发送失败",
                data=result
            )
    except Exception as e:
        logger.error(f"发送通知失败: {e}")
        return ResponseUtil.error(msg=str(e))


@notifySendController.get('/{api_key}/{content}')
async def send_notify_simple(
    request: Request,
    api_key: str,
    content: str,
    query_db: AsyncSession = Depends(get_db),
):
    """
    快捷发送通知
    
    URL路径直接包含内容: /notify/send/{api_key}/你好世界
    """
    try:
        ip_address = get_client_ip(request)
        result = await NotifySendService.send_by_api_key(
            db=query_db,
            api_key=api_key,
            title='',
            content=content,
            msg_type='text',
            ip_address=ip_address,
        )
        
        if result['success']:
            return ResponseUtil.success(
                data=result,
                msg=f"发送成功 ({result['success_count']}/{result['total']})"
            )
        else:
            return ResponseUtil.error(
                msg=f"发送失败",
                data=result
            )
    except Exception as e:
        logger.error(f"发送通知失败: {e}")
        return ResponseUtil.error(msg=str(e))
