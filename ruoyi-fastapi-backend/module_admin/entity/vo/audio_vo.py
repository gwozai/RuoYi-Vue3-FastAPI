from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional, List
from module_admin.annotation.pydantic_annotation import as_query


class AudioModel(BaseModel):
    """
    音频生成记录表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    audio_id: Optional[int] = Field(default=None, description='音频ID')
    audio_name: Optional[str] = Field(default=None, description='音频名称')
    input_text: Optional[str] = Field(default=None, description='输入文本')
    voice: Optional[str] = Field(default='zh-CN-XiaoxiaoNeural', description='语音模型')
    model: Optional[str] = Field(default='tts-1', description='TTS模型')
    speed: Optional[Decimal] = Field(default=Decimal('1.0'), description='语速')
    response_format: Optional[str] = Field(default='mp3', description='音频格式')
    file_path: Optional[str] = Field(default=None, description='文件存储路径')
    file_size: Optional[int] = Field(default=0, description='文件大小(字节)')
    duration: Optional[int] = Field(default=0, description='音频时长(秒)')
    status: Optional[str] = Field(default='0', description='状态（0生成中 1成功 2失败）')
    error_msg: Optional[str] = Field(default=None, description='错误信息')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='input_text', message='输入文本不能为空')
    def get_input_text(self):
        return self.input_text

    def validate_fields(self):
        self.get_input_text()


class AudioGenerateModel(BaseModel):
    """
    音频生成请求模型
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    config_id: Optional[int] = Field(default=None, alias='configId', description='TTS配置ID，不传则使用默认配置')
    input_text: str = Field(..., alias='inputText', description='输入文本')
    audio_name: Optional[str] = Field(default=None, alias='audioName', description='音频名称')
    voice: Optional[str] = Field(default='zh-CN-XiaoxiaoNeural', description='语音模型')
    model: Optional[str] = Field(default='tts-1', description='TTS模型')
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=4.0, description='语速(0.25-4.0)')
    response_format: Optional[str] = Field(default='mp3', alias='responseFormat', description='音频格式')
    remark: Optional[str] = Field(default=None, description='备注')


class AudioQueryModel(BaseModel):
    """
    音频不分页查询模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    audio_name: Optional[str] = Field(default=None, description='音频名称')
    voice: Optional[str] = Field(default=None, description='语音模型')
    status: Optional[str] = Field(default=None, description='状态')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


@as_query
class AudioPageQueryModel(AudioQueryModel):
    """
    音频分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteAudioModel(BaseModel):
    """
    删除音频模型
    """
    model_config = ConfigDict(alias_generator=to_camel)

    audio_ids: str = Field(description='需要删除的音频ID')


# 可用的语音模型列表
AVAILABLE_VOICES = [
    {"value": "zh-CN-XiaoxiaoNeural", "label": "晓晓 (女声-中文)"},
    {"value": "zh-CN-YunxiNeural", "label": "云希 (男声-中文)"},
    {"value": "zh-CN-YunjianNeural", "label": "云健 (男声-中文)"},
    {"value": "zh-CN-XiaoyiNeural", "label": "晓伊 (女声-中文)"},
    {"value": "zh-TW-HsiaoChenNeural", "label": "曉臻 (女声-台湾)"},
    {"value": "ja-JP-NanamiNeural", "label": "七海 (女声-日语)"},
    {"value": "en-US-JennyNeural", "label": "Jenny (女声-英语)"},
    {"value": "en-US-GuyNeural", "label": "Guy (男声-英语)"},
]
