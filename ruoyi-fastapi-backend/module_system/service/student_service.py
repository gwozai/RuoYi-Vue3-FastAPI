from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_system.dao.student_dao import StudentDao
from module_system.entity.vo.student_vo import StudentModel, StudentPageQueryModel, DeleteStudentModel
from exceptions.exception import ServiceException


class StudentService:
    """
    学生信息服务层
    """

    @classmethod
    async def get_student_list_services(cls, query_db: AsyncSession, query: StudentPageQueryModel, is_page: bool = False):
        """
        获取学生信息列表
        """
        return await StudentDao.get_student_list(query_db, query, is_page)

    @classmethod
    async def get_student_by_id_services(cls, query_db: AsyncSession, student_id: int):
        """
        根据ID获取学生信息详情
        """
        return await StudentDao.get_student_by_id(query_db, student_id)

    @classmethod
    async def add_student_services(cls, query_db: AsyncSession, obj: StudentModel):
        """
        新增学生ID
        """
        try:
            await StudentDao.add_student(query_db, obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'新增失败: {str(e)}')

    @classmethod
    async def update_student_services(cls, query_db: AsyncSession, obj: StudentModel):
        """
        更新学生信息
        """
        info = await cls.get_student_by_id_services(query_db, obj.student_id)
        if not info:
            raise ServiceException(message='学生信息不存在')
        try:
            await StudentDao.update_student(query_db, obj.model_dump(exclude_unset=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新失败: {str(e)}')

    @classmethod
    async def delete_student_services(cls, query_db: AsyncSession, obj: DeleteStudentModel):
        """
        删除学生信息
        """
        try:
            id_list = [int(i) for i in obj.student_ids.split(',')]
            await StudentDao.delete_student(query_db, id_list)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'删除失败: {str(e)}')
