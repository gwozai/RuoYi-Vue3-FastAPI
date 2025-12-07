from decimal import Decimal
from sqlalchemy import CHAR, Text, DateTime, Column, Integer, String, BigInteger, DECIMAL
from config.database import Base


class SysAudio(Base):
    """
    音频生成记录表
    """

    __tablename__ = 'sys_audio'
    __table_args__ = {'comment': '音频生成记录表'}

    audio_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='音频ID')
    audio_name = Column(String(200), nullable=False, comment='音频名称')
    input_text = Column(Text, nullable=False, comment='输入文本')
    voice = Column(String(100), nullable=True, default='zh-CN-XiaoxiaoNeural', comment='语音模型')
    model = Column(String(50), nullable=True, default='tts-1', comment='TTS模型')
    speed = Column(DECIMAL(3, 2), nullable=True, default=1.0, comment='语速')
    response_format = Column(String(20), nullable=True, default='mp3', comment='音频格式')
    file_path = Column(String(500), nullable=True, comment='文件存储路径')
    file_size = Column(BigInteger, nullable=True, default=0, comment='文件大小(字节)')
    duration = Column(Integer, nullable=True, default=0, comment='音频时长(秒)')
    status = Column(CHAR(1), nullable=True, default='0', comment='状态（0生成中 1成功 2失败）')
    error_msg = Column(String(500), nullable=True, comment='错误信息')
    create_by = Column(String(64), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_by = Column(String(64), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')
