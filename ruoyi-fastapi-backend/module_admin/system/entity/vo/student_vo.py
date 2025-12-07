from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query




class StudentModel(BaseModel):
    """
    【请填写功能名称】表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    student_id: Optional[int] = Field(default=None, description='学生ID')
    student_name: Optional[str] = Field(default=None, description='学生姓名')
    student_no: Optional[str] = Field(default=None, description='学号')
    gender: Optional[str] = Field(default=None, description='性别(0男 1女)')
    age: Optional[int] = Field(default=None, description='年龄')
    phone: Optional[str] = Field(default=None, description='手机号')
    email: Optional[str] = Field(default=None, description='邮箱')
    class_name: Optional[str] = Field(default=None, description='班级')
    major: Optional[str] = Field(default=None, description='专业')
    enrollment_date: Optional[date] = Field(default=None, description='入学日期')
    status: Optional[str] = Field(default=None, description='状态(0正常 1休学 2毕业)')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='student_name', message='学生姓名不能为空')
    def get_student_name(self):
        return self.student_name

    @NotBlank(field_name='student_no', message='学号不能为空')
    def get_student_no(self):
        return self.student_no


    def validate_fields(self):
        self.get_student_name()
        self.get_student_no()




class StudentQueryModel(StudentModel):
    """
    【请填写功能名称】不分页查询模型
    """
    pass


@as_query
class StudentPageQueryModel(StudentQueryModel):
    """
    【请填写功能名称】分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteStudentModel(BaseModel):
    """
    删除【请填写功能名称】模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    student_ids: str = Field(description='需要删除的学生ID')
