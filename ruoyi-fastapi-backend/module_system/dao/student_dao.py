from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_system.entity.do.student_do import SysStudent
from module_system.entity.vo.student_vo import StudentModel, StudentPageQueryModel
from utils.page_util import PageUtil


class StudentDao:
    """
    学生信息数据访问层
    """

    @classmethod
    async def get_student_list(cls, db: AsyncSession, query: StudentPageQueryModel, is_page: bool = False):
        """
        获取学生信息列表
        """
        query_obj = select(SysStudent).order_by(desc(SysStudent.student_id))
        
        # 添加查询条件
        if query.student_name:
            query_obj = query_obj.where(SysStudent.student_name.contains(query.student_name))
        if query.student_no:
            query_obj = query_obj.where(SysStudent.student_no.contains(query.student_no))
        if query.status:
            query_obj = query_obj.where(SysStudent.status == query.status)
        
        if is_page:
            return await PageUtil.paginate(db, query_obj, query.page_num, query.page_size)
        else:
            result = await db.execute(query_obj)
            return result.scalars().all()

    @classmethod
    async def get_student_by_id(cls, db: AsyncSession, student_id: int):
        """
        根据ID获取学生信息
        """
        result = await db.execute(
            select(SysStudent).where(SysStudent.student_id == student_id)
        )
        return result.scalars().first()

    @classmethod
    async def add_student(cls, db: AsyncSession, obj: StudentModel):
        """
        新增学生信息
        """
        db_obj = SysStudent(**obj.model_dump(exclude_unset=True))
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def update_student(cls, db: AsyncSession, obj: dict):
        """
        更新学生信息
        """
        await db.execute(
            update(SysStudent)
            .where(SysStudent.student_id == obj.get('student_id'))
            .values(**obj)
        )

    @classmethod
    async def delete_student(cls, db: AsyncSession, student_id_list: list):
        """
        删除学生信息
        """
        await db.execute(
            delete(SysStudent).where(SysStudent.student_id.in_(student_id_list))
        )
