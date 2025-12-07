from sqlalchemy import Column, Integer, String, DateTime, Text
from config.database import Base


class Demo(Base):
    """
    演示ID表
    """
    __tablename__ = 'sys_demo'

    demo_name = Column(String(100), comment='名称')
    status = Column(String(1), comment='状态')
