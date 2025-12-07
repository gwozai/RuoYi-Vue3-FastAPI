from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class NotifyChannelModel(BaseModel):
    """
    通知渠道 Pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    channel_id: Optional[int] = Field(default=None, alias='channelId', description='渠道ID')
    user_id: Optional[int] = Field(default=None, alias='userId', description='用户ID')
    platform_id: Optional[int] = Field(default=None, alias='platformId', description='平台ID')
    channel_name: Optional[str] = Field(default=None, alias='channelName', description='渠道名称')
    webhook_key: Optional[str] = Field(default=None, alias='webhookKey', description='Webhook密钥')
    webhook_url: Optional[str] = Field(default=None, alias='webhookUrl', description='完整Webhook地址')
    is_default: Optional[str] = Field(default=None, alias='isDefault', description='是否默认(0否 1是)')
    status: Optional[str] = Field(default=None, alias='status', description='状态(0正常 1停用)')
    last_used_time: Optional[datetime] = Field(default=None, alias='lastUsedTime', description='最后使用时间')
    use_count: Optional[int] = Field(default=None, alias='useCount', description='使用次数')
    create_by: Optional[str] = Field(default=None, alias='createBy', description='创建者')
    create_time: Optional[datetime] = Field(default=None, alias='createTime', description='创建时间')
    update_by: Optional[str] = Field(default=None, alias='updateBy', description='更新者')
    update_time: Optional[datetime] = Field(default=None, alias='updateTime', description='更新时间')
    remark: Optional[str] = Field(default=None, alias='remark', description='备注')


@as_query
class NotifyChannelPageQueryModel(NotifyChannelModel):
    """
    通知渠道分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class DeleteNotifyChannelModel(BaseModel):
    """
    删除通知渠道模型
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    channel_ids: str = Field(alias='channelIds', description='渠道ID')
