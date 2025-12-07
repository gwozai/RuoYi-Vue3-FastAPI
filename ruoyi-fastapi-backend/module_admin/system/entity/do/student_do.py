from sqlalchemy import Column, DateTime, BigInteger, String, Date, Integer
from config.database import Base


class SysStudent(Base):
    """
    【请填写功能名称】表
    """

    __tablename__ = 'sys_student'
    __table_args__ = {'comment': ''}

    student_id = Column(BigInteger, primary_key=True, autoincrement=True, nullable=False, comment='学生ID')
    student_name = Column(String(50), nullable=False, comment='学生姓名')
    student_no = Column(String(20), nullable=False, comment='学号')
    gender = Column(String(1), nullable=True, comment='性别(0男 1女)')
    age = Column(Integer, nullable=True, comment='年龄')
    phone = Column(String(20), nullable=True, comment='手机号')
    email = Column(String(100), nullable=True, comment='邮箱')
    class_name = Column(String(50), nullable=True, comment='班级')
    major = Column(String(100), nullable=True, comment='专业')
    enrollment_date = Column(Date, nullable=True, comment='入学日期')
    status = Column(String(1), nullable=True, comment='状态(0正常 1休学 2毕业)')
    create_by = Column(String(64), nullable=True, comment='创建者')
    create_time = Column(DateTime, nullable=True, comment='创建时间')
    update_by = Column(String(64), nullable=True, comment='更新者')
    update_time = Column(DateTime, nullable=True, comment='更新时间')
    remark = Column(String(500), nullable=True, comment='备注')



