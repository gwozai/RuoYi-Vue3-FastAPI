from sqlalchemy import CHAR, Date, Text, DateTime, Column, Integer, String, BigInteger, DECIMAL
from config.database import Base


class SysBook(Base):
    """
    图书信息表
    """

    __tablename__ = 'sys_book'
    __table_args__ = {'comment': '图书信息表'}

    book_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='图书ID')
    book_name = Column(String(100), nullable=False, comment='图书名称')
    author = Column(String(50), nullable=True, comment='作者')
    isbn = Column(String(20), nullable=True, comment='ISBN编号')
    publisher = Column(String(100), nullable=True, comment='出版社')
    publish_date = Column(Date, nullable=True, comment='出版日期')
    price = Column(DECIMAL, nullable=True, comment='价格')
    category = Column(String(50), nullable=True, comment='分类')
    stock = Column(Integer, nullable=True, comment='库存数量')
    description = Column(Text, nullable=True, comment='图书简介')
    cover_image = Column(String(255), nullable=True, comment='封面图片')
    status = Column(CHAR(1), nullable=True, comment='状态（0正常 1停用）')
    create_by = Column(String(64), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_by = Column(String(64), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')



