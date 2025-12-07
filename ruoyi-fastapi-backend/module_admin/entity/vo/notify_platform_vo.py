from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class NotifyPlatformModel(BaseModel):
    """
    通知平台 Pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    platform_id: Optional[int] = Field(default=None, alias='platformId', description='平台ID')
    platform_name: Optional[str] = Field(default=None, alias='platformName', description='平台名称')
    platform_code: Optional[str] = Field(default=None, alias='platformCode', description='平台编码')
    platform_icon: Optional[str] = Field(default=None, alias='platformIcon', description='平台图标')
    webhook_template: Optional[str] = Field(default=None, alias='webhookTemplate', description='Webhook模板')
    request_method: Optional[str] = Field(default=None, alias='requestMethod', description='请求方式')
    content_type: Optional[str] = Field(default=None, alias='contentType', description='内容类型')
    body_template: Optional[str] = Field(default=None, alias='bodyTemplate', description='请求体模板')
    status: Optional[str] = Field(default=None, alias='status', description='状态(0正常 1停用)')
    order_num: Optional[int] = Field(default=None, alias='orderNum', description='排序')
    create_by: Optional[str] = Field(default=None, alias='createBy', description='创建者')
    create_time: Optional[datetime] = Field(default=None, alias='createTime', description='创建时间')
    update_by: Optional[str] = Field(default=None, alias='updateBy', description='更新者')
    update_time: Optional[datetime] = Field(default=None, alias='updateTime', description='更新时间')
    remark: Optional[str] = Field(default=None, alias='remark', description='备注')


@as_query
class NotifyPlatformPageQueryModel(NotifyPlatformModel):
    """
    通知平台分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class DeleteNotifyPlatformModel(BaseModel):
    """
    删除通知平台模型
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    platform_ids: str = Field(alias='platformIds', description='平台ID')
