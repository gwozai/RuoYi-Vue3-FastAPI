"""
通知发送服务 - 核心发送逻辑

支持通过API密钥发送通知到飞书、企业微信、钉钉等平台
类似Server酱的功能

使用方式:
    GET/POST /notify/send/{api_key}?title=标题&content=内容
    GET/POST /notify/send/{api_key}/{content}
"""

import asyncio
import hashlib
import json
import secrets
import time
from datetime import datetime, date
from typing import Optional, List, Dict, Any

import httpx
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from module_admin.entity.do.notify_platform_do import NotifyPlatform
from module_admin.entity.do.notify_channel_do import NotifyChannel
from module_admin.entity.do.notify_key_do import NotifyKey
from module_admin.entity.do.notify_log_do import NotifyLog
from exceptions.exception import ServiceException


class NotifySendService:
    """通知发送服务"""

    @classmethod
    def generate_api_key(cls) -> str:
        """生成API密钥 (类似Server酱的SCKEY)"""
        # 生成32字节的随机密钥，转为64字符的十六进制字符串
        return secrets.token_hex(32)

    @classmethod
    async def send_by_api_key(
        cls,
        db: AsyncSession,
        api_key: str,
        title: str = '',
        content: str = '',
        msg_type: str = 'text',
        channel_id: int = None,
        ip_address: str = '',
    ) -> Dict[str, Any]:
        """
        通过API密钥发送通知
        
        Args:
            db: 数据库会话
            api_key: API密钥
            title: 消息标题
            content: 消息内容
            msg_type: 消息类型 (text/markdown)
            channel_id: 指定渠道ID (可选，不指定则发送到所有绑定渠道)
            ip_address: 调用者IP
            
        Returns:
            发送结果
        """
        start_time = time.time()
        
        # 1. 验证API密钥
        key_info = await cls._validate_api_key(db, api_key)
        if not key_info:
            raise ServiceException(message='API密钥无效或已过期')
        
        # 2. 检查每日限额
        today = date.today()
        if key_info.last_reset_date != today:
            # 重置每日计数
            await db.execute(
                update(NotifyKey)
                .where(NotifyKey.key_id == key_info.key_id)
                .values(daily_used=0, last_reset_date=today)
            )
            key_info.daily_used = 0
        
        if key_info.daily_used >= key_info.daily_limit:
            raise ServiceException(message=f'已达每日限额({key_info.daily_limit}次)')
        
        # 3. 获取要发送的渠道
        channels = await cls._get_channels(db, key_info, channel_id)
        if not channels:
            raise ServiceException(message='没有可用的通知渠道')
        
        # 4. 发送通知
        results = []
        success_count = 0
        
        for channel in channels:
            result = await cls._send_to_channel(
                db=db,
                channel=channel,
                key_info=key_info,
                title=title,
                content=content,
                msg_type=msg_type,
                ip_address=ip_address,
                start_time=start_time,
            )
            results.append(result)
            if result['success']:
                success_count += 1
        
        # 5. 更新API密钥使用统计
        await db.execute(
            update(NotifyKey)
            .where(NotifyKey.key_id == key_info.key_id)
            .values(
                daily_used=NotifyKey.daily_used + 1,
                total_count=NotifyKey.total_count + 1,
                last_used_time=datetime.now(),
            )
        )
        await db.commit()
        
        return {
            'success': success_count > 0,
            'total': len(channels),
            'success_count': success_count,
            'fail_count': len(channels) - success_count,
            'results': results,
        }

    @classmethod
    async def _validate_api_key(cls, db: AsyncSession, api_key: str) -> Optional[NotifyKey]:
        """验证API密钥"""
        result = await db.execute(
            select(NotifyKey).where(
                and_(
                    NotifyKey.api_key == api_key,
                    NotifyKey.status == '0',
                )
            )
        )
        key_info = result.scalars().first()
        
        if not key_info:
            return None
        
        # 检查是否过期
        if key_info.expire_time and key_info.expire_time < datetime.now():
            return None
        
        return key_info

    @classmethod
    async def _get_channels(
        cls,
        db: AsyncSession,
        key_info: NotifyKey,
        channel_id: int = None,
    ) -> List[NotifyChannel]:
        """获取要发送的渠道列表"""
        
        if channel_id:
            # 指定了渠道ID
            result = await db.execute(
                select(NotifyChannel).where(
                    and_(
                        NotifyChannel.channel_id == channel_id,
                        NotifyChannel.user_id == key_info.user_id,
                        NotifyChannel.status == '0',
                    )
                )
            )
            channel = result.scalars().first()
            return [channel] if channel else []
        
        # 获取绑定的渠道
        if key_info.channel_ids:
            channel_id_list = [int(x) for x in key_info.channel_ids.split(',') if x.strip()]
            if channel_id_list:
                result = await db.execute(
                    select(NotifyChannel).where(
                        and_(
                            NotifyChannel.channel_id.in_(channel_id_list),
                            NotifyChannel.status == '0',
                        )
                    )
                )
                return list(result.scalars().all())
        
        # 没有绑定渠道，使用用户的默认渠道
        result = await db.execute(
            select(NotifyChannel).where(
                and_(
                    NotifyChannel.user_id == key_info.user_id,
                    NotifyChannel.is_default == '1',
                    NotifyChannel.status == '0',
                )
            )
        )
        channels = list(result.scalars().all())
        
        # 如果没有默认渠道，使用用户的所有渠道
        if not channels:
            result = await db.execute(
                select(NotifyChannel).where(
                    and_(
                        NotifyChannel.user_id == key_info.user_id,
                        NotifyChannel.status == '0',
                    )
                )
            )
            channels = list(result.scalars().all())
        
        return channels

    @classmethod
    async def _send_to_channel(
        cls,
        db: AsyncSession,
        channel: NotifyChannel,
        key_info: NotifyKey,
        title: str,
        content: str,
        msg_type: str,
        ip_address: str,
        start_time: float,
    ) -> Dict[str, Any]:
        """发送消息到指定渠道"""
        
        # 获取平台信息
        result = await db.execute(
            select(NotifyPlatform).where(NotifyPlatform.platform_id == channel.platform_id)
        )
        platform = result.scalars().first()
        
        if not platform:
            return {
                'success': False,
                'channel_id': channel.channel_id,
                'channel_name': channel.channel_name,
                'error': '平台不存在',
            }
        
        # 构建Webhook URL
        webhook_url = platform.webhook_template.replace('{key}', channel.webhook_key)
        if channel.webhook_url:
            webhook_url = channel.webhook_url
        
        # 构建请求体
        full_content = f"{title}\n{content}" if title else content
        # 转义JSON特殊字符
        escaped_content = full_content.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        escaped_title = title.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') if title else ''
        body_template = platform.body_template or '{"msg_type":"text","content":{"text":"{content}"}}'
        request_body = body_template.replace('{content}', escaped_content).replace('{title}', escaped_title)
        
        # 发送请求
        response_data = ''
        error_msg = ''
        status = '0'
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=platform.request_method or 'POST',
                    url=webhook_url,
                    headers={'Content-Type': platform.content_type or 'application/json'},
                    content=request_body,
                )
                response_data = response.text
                
                # 检查响应
                if response.status_code != 200:
                    status = '1'
                    error_msg = f'HTTP {response.status_code}'
                else:
                    # 尝试解析响应判断是否成功
                    try:
                        resp_json = response.json()
                        # 飞书
                        if 'code' in resp_json and resp_json['code'] != 0:
                            status = '1'
                            error_msg = resp_json.get('msg', str(resp_json))
                        # 企业微信
                        elif 'errcode' in resp_json and resp_json['errcode'] != 0:
                            status = '1'
                            error_msg = resp_json.get('errmsg', str(resp_json))
                    except:
                        pass
                        
        except Exception as e:
            status = '1'
            error_msg = str(e)
            response_data = str(e)
        
        # 计算耗时
        cost_time = int((time.time() - start_time) * 1000)
        
        # 记录日志
        log = NotifyLog(
            user_id=key_info.user_id,
            key_id=key_info.key_id,
            channel_id=channel.channel_id,
            platform_id=channel.platform_id,
            title=title[:200] if title else '',
            content=content[:5000] if content else '',
            msg_type=msg_type,
            request_data=request_body[:5000],
            response_data=response_data[:5000] if response_data else '',
            status=status,
            error_msg=error_msg[:500] if error_msg else '',
            ip_address=ip_address,
            send_time=datetime.now(),
            cost_time=cost_time,
            create_time=datetime.now(),
        )
        db.add(log)
        
        # 更新渠道使用统计
        await db.execute(
            update(NotifyChannel)
            .where(NotifyChannel.channel_id == channel.channel_id)
            .values(
                use_count=NotifyChannel.use_count + 1,
                last_used_time=datetime.now(),
            )
        )
        
        return {
            'success': status == '0',
            'channel_id': channel.channel_id,
            'channel_name': channel.channel_name,
            'platform': platform.platform_name,
            'error': error_msg if status == '1' else None,
            'cost_time': cost_time,
        }

    @classmethod
    async def test_channel(
        cls,
        db: AsyncSession,
        channel_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """测试渠道连通性"""
        
        # 获取渠道
        result = await db.execute(
            select(NotifyChannel).where(
                and_(
                    NotifyChannel.channel_id == channel_id,
                    NotifyChannel.user_id == user_id,
                )
            )
        )
        channel = result.scalars().first()
        
        if not channel:
            raise ServiceException(message='渠道不存在')
        
        # 获取平台
        result = await db.execute(
            select(NotifyPlatform).where(NotifyPlatform.platform_id == channel.platform_id)
        )
        platform = result.scalars().first()
        
        if not platform:
            raise ServiceException(message='平台不存在')
        
        # 构建测试消息
        webhook_url = platform.webhook_template.replace('{key}', channel.webhook_key)
        if channel.webhook_url:
            webhook_url = channel.webhook_url
        
        test_content = f"🔔 测试通知\\n\\n渠道: {channel.channel_name}\\n平台: {platform.platform_name}\\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        # 转义JSON特殊字符
        escaped_content = test_content.replace('\\', '\\\\').replace('"', '\\"')
        body_template = platform.body_template or '{"msg_type":"text","content":{"text":"{content}"}}'
        request_body = body_template.replace('{content}', escaped_content).replace('{title}', '测试通知')
        
        # 发送测试请求
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=platform.request_method or 'POST',
                    url=webhook_url,
                    headers={'Content-Type': platform.content_type or 'application/json'},
                    content=request_body,
                )
                
                if response.status_code == 200:
                    try:
                        resp_json = response.json()
                        if resp_json.get('code', 0) == 0 and resp_json.get('errcode', 0) == 0:
                            return {'success': True, 'message': '测试成功'}
                        else:
                            return {'success': False, 'message': resp_json.get('msg') or resp_json.get('errmsg') or str(resp_json)}
                    except:
                        return {'success': True, 'message': '测试成功'}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}: {response.text}'}
                    
        except Exception as e:
            return {'success': False, 'message': str(e)}
