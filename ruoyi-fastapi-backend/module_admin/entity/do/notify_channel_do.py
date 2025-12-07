from sqlalchemy import BigInteger, Column, Integer, String, DateTime, Text
from config.database import Base


class NotifyChannel(Base):
    """
    通知渠道表
    """
    __tablename__ = 'notify_channel'
    __table_args__ = {'comment': '通知渠道表'}

    channel_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='渠道ID')
    user_id = Column(BigInteger, nullable=False, comment='用户ID')
    platform_id = Column(BigInteger, nullable=False, comment='平台ID')
    channel_name = Column(String(100), nullable=False, comment='渠道名称')
    webhook_key = Column(String(255), nullable=False, comment='Webhook密钥')
    webhook_url = Column(String(500), comment='完整Webhook地址')
    is_default = Column(String(1), comment='是否默认(0否 1是)')
    status = Column(String(1), comment='状态(0正常 1停用)')
    last_used_time = Column(DateTime, comment='最后使用时间')
    use_count = Column(Integer, comment='使用次数')
    create_by = Column(String(64), comment='创建者')
    create_time = Column(DateTime, comment='创建时间')
    update_by = Column(String(64), comment='更新者')
    update_time = Column(DateTime, comment='更新时间')
    remark = Column(String(500), comment='备注')
