from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class NotifyLogModel(BaseModel):
    """
    通知发送记录 Pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    log_id: Optional[int] = Field(default=None, alias='logId', description='日志ID')
    user_id: Optional[int] = Field(default=None, alias='userId', description='用户ID')
    key_id: Optional[int] = Field(default=None, alias='keyId', description='API密钥ID')
    channel_id: Optional[int] = Field(default=None, alias='channelId', description='渠道ID')
    platform_id: Optional[int] = Field(default=None, alias='platformId', description='平台ID')
    title: Optional[str] = Field(default=None, alias='title', description='消息标题')
    content: Optional[str] = Field(default=None, alias='content', description='消息内容')
    msg_type: Optional[str] = Field(default=None, alias='msgType', description='消息类型')
    request_data: Optional[str] = Field(default=None, alias='requestData', description='请求数据')
    response_data: Optional[str] = Field(default=None, alias='responseData', description='响应数据')
    status: Optional[str] = Field(default=None, alias='status', description='状态(0成功 1失败)')
    error_msg: Optional[str] = Field(default=None, alias='errorMsg', description='错误信息')
    ip_address: Optional[str] = Field(default=None, alias='ipAddress', description='IP地址')
    send_time: Optional[datetime] = Field(default=None, alias='sendTime', description='发送时间')
    cost_time: Optional[int] = Field(default=None, alias='costTime', description='耗时(毫秒)')
    create_time: Optional[datetime] = Field(default=None, alias='createTime', description='创建时间')


@as_query
class NotifyLogPageQueryModel(NotifyLogModel):
    """
    通知发送记录分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class DeleteNotifyLogModel(BaseModel):
    """
    删除通知发送记录模型
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    log_ids: str = Field(alias='logIds', description='日志ID')
