from sqlalchemy import BigInteger, Column, Integer, String, DateTime, Text
from config.database import Base


class NotifyLog(Base):
    """
    通知发送记录表
    """
    __tablename__ = 'notify_log'
    __table_args__ = {'comment': '通知发送记录表'}

    log_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='日志ID')
    user_id = Column(BigInteger, comment='用户ID')
    key_id = Column(BigInteger, comment='API密钥ID')
    channel_id = Column(BigInteger, comment='渠道ID')
    platform_id = Column(BigInteger, comment='平台ID')
    title = Column(String(200), comment='消息标题')
    content = Column(Text, comment='消息内容')
    msg_type = Column(String(20), comment='消息类型')
    request_data = Column(Text, comment='请求数据')
    response_data = Column(Text, comment='响应数据')
    status = Column(String(1), comment='状态(0成功 1失败)')
    error_msg = Column(String(500), comment='错误信息')
    ip_address = Column(String(50), comment='IP地址')
    send_time = Column(DateTime, comment='发送时间')
    cost_time = Column(Integer, comment='耗时(毫秒)')
    create_time = Column(DateTime, comment='创建时间')
