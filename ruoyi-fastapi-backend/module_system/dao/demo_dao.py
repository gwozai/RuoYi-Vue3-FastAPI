from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_system.entity.do.demo_do import Demo
from module_system.entity.vo.demo_vo import DemoModel, DemoPageQueryModel
from utils.page_util import PageUtil


class DemoDao:
    """
    演示ID数据访问层
    """

    @classmethod
    async def get_demo_list(cls, db: AsyncSession, query: DemoPageQueryModel, is_page: bool = False):
        """
        获取演示ID列表
        """
        query_obj = select(Demo).order_by(desc(Demo.id))
        
        # 添加查询条件
        if query.demo_name:
            query_obj = query_obj.where(Demo.demo_name.contains(query.demo_name))
        if query.status:
            query_obj = query_obj.where(Demo.status.contains(query.status))
        
        if is_page:
            return await PageUtil.paginate(db, query_obj, query.page_num, query.page_size)
        else:
            result = await db.execute(query_obj)
            return result.scalars().all()

    @classmethod
    async def get_demo_by_id(cls, db: AsyncSession, id: int):
        """
        根据ID获取演示ID
        """
        result = await db.execute(
            select(Demo).where(Demo.id == id)
        )
        return result.scalars().first()

    @classmethod
    async def add_demo(cls, db: AsyncSession, obj: DemoModel):
        """
        新增演示ID
        """
        db_obj = Demo(**obj.model_dump(exclude_unset=True))
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def update_demo(cls, db: AsyncSession, obj: dict):
        """
        更新演示ID
        """
        await db.execute(
            update(Demo)
            .where(Demo.id == obj.get('id'))
            .values(**obj)
        )

    @classmethod
    async def delete_demo(cls, db: AsyncSession, id_list: list):
        """
        删除演示ID
        """
        await db.execute(
            delete(Demo).where(Demo.id.in_(id_list))
        )
