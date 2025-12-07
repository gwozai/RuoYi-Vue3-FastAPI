from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class NotifyKeyModel(BaseModel):
    """
    通知API密钥 Pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    key_id: Optional[int] = Field(default=None, alias='keyId', description='密钥ID')
    user_id: Optional[int] = Field(default=None, alias='userId', description='用户ID')
    key_name: Optional[str] = Field(default=None, alias='keyName', description='密钥名称')
    api_key: Optional[str] = Field(default=None, alias='apiKey', description='API密钥')
    channel_ids: Optional[str] = Field(default=None, alias='channelIds', description='绑定渠道ID(逗号分隔)')
    daily_limit: Optional[int] = Field(default=None, alias='dailyLimit', description='每日限额')
    daily_used: Optional[int] = Field(default=None, alias='dailyUsed', description='今日已用')
    total_count: Optional[int] = Field(default=None, alias='totalCount', description='总调用次数')
    last_used_time: Optional[datetime] = Field(default=None, alias='lastUsedTime', description='最后使用时间')
    last_reset_date: Optional[date] = Field(default=None, alias='lastResetDate', description='最后重置日期')
    status: Optional[str] = Field(default=None, alias='status', description='状态(0正常 1停用)')
    expire_time: Optional[datetime] = Field(default=None, alias='expireTime', description='过期时间')
    create_by: Optional[str] = Field(default=None, alias='createBy', description='创建者')
    create_time: Optional[datetime] = Field(default=None, alias='createTime', description='创建时间')
    update_by: Optional[str] = Field(default=None, alias='updateBy', description='更新者')
    update_time: Optional[datetime] = Field(default=None, alias='updateTime', description='更新时间')
    remark: Optional[str] = Field(default=None, alias='remark', description='备注')


@as_query
class NotifyKeyPageQueryModel(NotifyKeyModel):
    """
    通知API密钥分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class DeleteNotifyKeyModel(BaseModel):
    """
    删除通知API密钥模型
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    key_ids: str = Field(alias='keyIds', description='密钥ID')
