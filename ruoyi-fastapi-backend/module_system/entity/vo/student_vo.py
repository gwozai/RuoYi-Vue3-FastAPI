from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class StudentModel(BaseModel):
    """
    学生信息 Pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

    student_id: Optional[int] = Field(default=None, alias='studentId', description='学生ID')
    student_name: Optional[str] = Field(default=None, alias='studentName', description='学生姓名')
    student_no: Optional[str] = Field(default=None, alias='studentNo', description='学号')
    gender: Optional[str] = Field(default=None, alias='gender', description='性别(0男 1女)')
    age: Optional[int] = Field(default=None, alias='age', description='年龄')
    phone: Optional[str] = Field(default=None, alias='phone', description='手机号')
    email: Optional[str] = Field(default=None, alias='email', description='邮箱')
    class_name: Optional[str] = Field(default=None, alias='className', description='班级')
    major: Optional[str] = Field(default=None, alias='major', description='专业')
    enrollment_date: Optional[date] = Field(default=None, alias='enrollmentDate', description='入学日期')
    status: Optional[str] = Field(default=None, alias='status', description='状态(0正常 1休学 2毕业)')
    create_by: Optional[str] = Field(default=None, alias='createBy', description='创建者')
    create_time: Optional[datetime] = Field(default=None, alias='createTime', description='创建时间')
    update_by: Optional[str] = Field(default=None, alias='updateBy', description='更新者')
    update_time: Optional[datetime] = Field(default=None, alias='updateTime', description='更新时间')
    remark: Optional[str] = Field(default=None, alias='remark', description='备注')


@as_query
class StudentPageQueryModel(StudentModel):
    """
    学生信息分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class DeleteStudentModel(BaseModel):
    """
    删除学生信息模型
    """
    model_config = ConfigDict(alias_generator=to_camel)

    student_ids: str = Field(alias='studentIds', description='学生ID')
