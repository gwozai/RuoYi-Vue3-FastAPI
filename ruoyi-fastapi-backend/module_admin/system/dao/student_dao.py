from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.system.entity.do.student_do import SysStudent
from module_admin.system.entity.vo.student_vo import StudentModel, StudentPageQueryModel
from utils.page_util import PageUtil


class StudentDao:
    """
    【请填写功能名称】模块数据库操作层
    """

    @classmethod
    async def get_student_detail_by_id(cls, db: AsyncSession, student_id: int):
        """
        根据学生ID获取【请填写功能名称】详细信息

        :param db: orm对象
        :param student_id: 学生ID
        :return: 【请填写功能名称】信息对象
        """
        student_info = (
            (
                await db.execute(
                    select(SysStudent)
                    .where(
                        SysStudent.student_id == student_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return student_info

    @classmethod
    async def get_student_detail_by_info(cls, db: AsyncSession, student: StudentModel):
        """
        根据【请填写功能名称】参数获取【请填写功能名称】信息

        :param db: orm对象
        :param student: 【请填写功能名称】参数对象
        :return: 【请填写功能名称】信息对象
        """
        student_info = (
            (
                await db.execute(
                    select(SysStudent).where(
                    )
                )
            )
            .scalars()
            .first()
        )

        return student_info

    @classmethod
    async def get_student_list(cls, db: AsyncSession, query_object: StudentPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取【请填写功能名称】列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 【请填写功能名称】列表信息对象
        """
        query = (
            select(SysStudent)
            .where(
                SysStudent.student_name.like(f'%{query_object.student_name}%') if query_object.student_name else True,
                SysStudent.student_no == query_object.student_no if query_object.student_no else True,
                SysStudent.gender == query_object.gender if query_object.gender else True,
                SysStudent.age == query_object.age if query_object.age else True,
                SysStudent.phone == query_object.phone if query_object.phone else True,
                SysStudent.email == query_object.email if query_object.email else True,
                SysStudent.class_name.like(f'%{query_object.class_name}%') if query_object.class_name else True,
                SysStudent.major == query_object.major if query_object.major else True,
                SysStudent.enrollment_date == query_object.enrollment_date if query_object.enrollment_date else True,
                SysStudent.status == query_object.status if query_object.status else True,
            )
            .order_by(SysStudent.student_id)
            .distinct()
        )
        student_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return student_list

    @classmethod
    async def add_student_dao(cls, db: AsyncSession, student: StudentModel):
        """
        新增【请填写功能名称】数据库操作

        :param db: orm对象
        :param student: 【请填写功能名称】对象
        :return:
        """
        db_student = SysStudent(**student.model_dump(exclude={}))
        db.add(db_student)
        await db.flush()

        return db_student

    @classmethod
    async def edit_student_dao(cls, db: AsyncSession, student: dict):
        """
        编辑【请填写功能名称】数据库操作

        :param db: orm对象
        :param student: 需要更新的【请填写功能名称】字典
        :return:
        """
        await db.execute(update(SysStudent), [student])

    @classmethod
    async def delete_student_dao(cls, db: AsyncSession, student: StudentModel):
        """
        删除【请填写功能名称】数据库操作

        :param db: orm对象
        :param student: 【请填写功能名称】对象
        :return:
        """
        await db.execute(delete(SysStudent).where(SysStudent.student_id.in_([student.student_id])))

