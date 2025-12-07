from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Date
from config.database import Base


class SysStudent(Base):
    """
    学生信息表
    """
    __tablename__ = 'sys_student'

    student_id = Column(BigInteger, primary_key=True, autoincrement=True, comment='学生ID')
    student_name = Column(String(50), nullable=False, comment='学生姓名')
    student_no = Column(String(20), nullable=False, comment='学号')
    gender = Column(String(1), comment='性别(0男 1女)')
    age = Column(Integer, comment='年龄')
    phone = Column(String(20), comment='手机号')
    email = Column(String(100), comment='邮箱')
    class_name = Column(String(50), comment='班级')
    major = Column(String(100), comment='专业')
    enrollment_date = Column(Date, comment='入学日期')
    status = Column(String(1), comment='状态(0正常 1休学 2毕业)')
    create_by = Column(String(64), comment='创建者')
    create_time = Column(DateTime, comment='创建时间')
    update_by = Column(String(64), comment='更新者')
    update_time = Column(DateTime, comment='更新时间')
    remark = Column(String(500), comment='备注')
