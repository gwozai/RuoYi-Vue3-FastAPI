from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.system.dao.student_dao import StudentDao
from module_admin.system.entity.vo.student_vo import DeleteStudentModel, StudentModel, StudentPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class StudentService:
    """
    【请填写功能名称】模块服务层
    """

    @classmethod
    async def get_student_list_services(
        cls, query_db: AsyncSession, query_object: StudentPageQueryModel, is_page: bool = False
    ):
        """
        获取【请填写功能名称】列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 【请填写功能名称】列表信息对象
        """
        student_list_result = await StudentDao.get_student_list(query_db, query_object, is_page)

        return student_list_result


    @classmethod
    async def add_student_services(cls, query_db: AsyncSession, page_object: StudentModel):
        """
        新增【请填写功能名称】信息service

        :param query_db: orm对象
        :param page_object: 新增【请填写功能名称】对象
        :return: 新增【请填写功能名称】校验结果
        """
        try:
            await StudentDao.add_student_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_student_services(cls, query_db: AsyncSession, page_object: StudentModel):
        """
        编辑【请填写功能名称】信息service

        :param query_db: orm对象
        :param page_object: 编辑【请填写功能名称】对象
        :return: 编辑【请填写功能名称】校验结果
        """
        edit_student = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time', })
        student_info = await cls.student_detail_services(query_db, page_object.student_id)
        if student_info.student_id:
            try:
                await StudentDao.edit_student_dao(query_db, edit_student)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='【请填写功能名称】不存在')

    @classmethod
    async def delete_student_services(cls, query_db: AsyncSession, page_object: DeleteStudentModel):
        """
        删除【请填写功能名称】信息service

        :param query_db: orm对象
        :param page_object: 删除【请填写功能名称】对象
        :return: 删除【请填写功能名称】校验结果
        """
        if page_object.student_ids:
            student_id_list = page_object.student_ids.split(',')
            try:
                for student_id in student_id_list:
                    await StudentDao.delete_student_dao(query_db, StudentModel(studentId=student_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入学生ID为空')

    @classmethod
    async def student_detail_services(cls, query_db: AsyncSession, student_id: int):
        """
        获取【请填写功能名称】详细信息service

        :param query_db: orm对象
        :param student_id: 学生ID
        :return: 学生ID对应的信息
        """
        student = await StudentDao.get_student_detail_by_id(query_db, student_id=student_id)
        if student:
            result = StudentModel(**CamelCaseUtil.transform_result(student))
        else:
            result = StudentModel(**dict())

        return result

    @staticmethod
    async def export_student_list_services(student_list: List):
        """
        导出【请填写功能名称】信息service

        :param student_list: 【请填写功能名称】信息列表
        :return: 【请填写功能名称】信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'studentId': '学生ID',
            'studentName': '学生姓名',
            'studentNo': '学号',
            'gender': '性别(0男 1女)',
            'age': '年龄',
            'phone': '手机号',
            'email': '邮箱',
            'className': '班级',
            'major': '专业',
            'enrollmentDate': '入学日期',
            'status': '状态(0正常 1休学 2毕业)',
            'createBy': '创建者',
            'createTime': '创建时间',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'remark': '备注',
        }
        binary_data = ExcelUtil.export_list2excel(student_list, mapping_dict)

        return binary_data
