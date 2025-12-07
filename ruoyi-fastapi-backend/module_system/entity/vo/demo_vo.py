from datetime import datetime
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class DemoModel:
    """
    演示ID Pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    demo_name: Optional[str] = Field(default=None, alias='demoName', description='名称')
    status: Optional[str] = Field(default=None, alias='status', description='状态')


class DemoPageQueryModel(DemoModel):
    """
    演示ID分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class DeleteDemoModel:
    """
    删除演示ID模型
    """
    model_config = ConfigDict(alias_generator=to_camel)

    id_ids: str = Field(description='演示IDID')
