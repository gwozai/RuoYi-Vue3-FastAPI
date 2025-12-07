from sqlalchemy import BigInteger, Column, Date, Integer, String, DateTime, Text
from config.database import Base


class NotifyKey(Base):
    """
    通知API密钥表
    """
    __tablename__ = 'notify_key'
    __table_args__ = {'comment': '通知API密钥表'}

    key_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='密钥ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    key_name = Column(String(100), nullable=False, comment='密钥名称')
    api_key = Column(String(64), nullable=False, unique=True, comment='API密钥')
    channel_ids = Column(String(500), comment='绑定渠道ID(逗号分隔)')
    daily_limit = Column(Integer, default=100, comment='每日限额')
    daily_used = Column(Integer, default=0, comment='今日已用')
    total_count = Column(Integer, default=0, comment='总调用次数')
    last_used_time = Column(DateTime, comment='最后使用时间')
    last_reset_date = Column(Date, comment='最后重置日期')
    status = Column(String(1), comment='状态(0正常 1停用)')
    expire_time = Column(DateTime, comment='过期时间')
    create_by = Column(String(64), comment='创建者')
    create_time = Column(DateTime, comment='创建时间')
    update_by = Column(String(64), comment='更新者')
    update_time = Column(DateTime, comment='更新时间')
    remark = Column(String(500), comment='备注')
