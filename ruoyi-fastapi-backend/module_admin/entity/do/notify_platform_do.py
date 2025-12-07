from sqlalchemy import BigInteger, Column, Integer, String, DateTime, Text
from config.database import Base


class NotifyPlatform(Base):
    """
    通知平台表
    """
    __tablename__ = 'notify_platform'
    __table_args__ = {'comment': '通知平台表'}

    platform_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='平台ID')
    platform_name = Column(String(50), nullable=False, comment='平台名称')
    platform_code = Column(String(50), nullable=False, comment='平台编码')
    platform_icon = Column(String(255), comment='平台图标')
    webhook_template = Column(String(500), nullable=False, comment='Webhook模板')
    request_method = Column(String(10), comment='请求方式')
    content_type = Column(String(50), comment='内容类型')
    body_template = Column(Text, comment='请求体模板')
    status = Column(String(1), comment='状态(0正常 1停用)')
    order_num = Column(Integer, comment='排序')
    create_by = Column(String(64), comment='创建者')
    create_time = Column(DateTime, comment='创建时间')
    update_by = Column(String(64), comment='更新者')
    update_time = Column(DateTime, comment='更新时间')
    remark = Column(String(500), comment='备注')
