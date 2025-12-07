from sqlalchemy import DateTime, Column, CHAR, BigInteger, String
from config.database import Base


class SysTtsConfig(Base):
    """
    TTS API配置表
    """

    __tablename__ = 'sys_tts_config'
    __table_args__ = {'comment': 'TTS API配置表'}

    config_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='配置ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    config_name = Column(String(100), nullable=False, comment='配置名称')
    api_url = Column(String(500), nullable=False, comment='API地址')
    api_key = Column(String(500), nullable=True, comment='API密钥')
    api_model = Column(String(100), nullable=True, comment='API模型')
    is_default = Column(CHAR(1), nullable=True, comment='是否默认（0否 1是）')
    status = Column(CHAR(1), nullable=True, comment='状态（0正常 1停用）')
    create_by = Column(String(64), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_by = Column(String(64), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')



