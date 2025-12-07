from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query




class TtsconfigModel(BaseModel):
    """
    TTS API配置表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    config_id: Optional[int] = Field(default=None, description='配置ID')
    user_id: Optional[int] = Field(default=None, description='用户ID')
    config_name: Optional[str] = Field(default=None, description='配置名称')
    api_url: Optional[str] = Field(default=None, description='API地址')
    api_key: Optional[str] = Field(default=None, description='API密钥')
    api_model: Optional[str] = Field(default=None, description='API模型')
    is_default: Optional[str] = Field(default=None, description='是否默认（0否 1是）')
    status: Optional[str] = Field(default=None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='user_id', message='用户ID不能为空')
    def get_user_id(self):
        return self.user_id

    @NotBlank(field_name='config_name', message='配置名称不能为空')
    def get_config_name(self):
        return self.config_name

    @NotBlank(field_name='api_url', message='API地址不能为空')
    def get_api_url(self):
        return self.api_url


    def validate_fields(self):
        self.get_user_id()
        self.get_config_name()
        self.get_api_url()




class TtsconfigQueryModel(TtsconfigModel):
    """
    TTS API配置不分页查询模型
    """
    pass


@as_query
class TtsconfigPageQueryModel(TtsconfigQueryModel):
    """
    TTS API配置分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteTtsconfigModel(BaseModel):
    """
    删除TTS API配置模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    config_ids: str = Field(description='需要删除的配置ID')
