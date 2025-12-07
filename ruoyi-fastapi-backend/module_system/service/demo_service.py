from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_system.dao.demo_dao import DemoDao
from module_system.entity.vo.demo_vo import DemoModel, DemoPageQueryModel, DeleteDemoModel
from exceptions.exception import ServiceException


class DemoService:
    """
    演示ID服务层
    """

    @classmethod
    async def get_demo_list_services(cls, query_db: AsyncSession, query: DemoPageQueryModel, is_page: bool = False):
        """
        获取演示ID列表
        """
        return await DemoDao.get_demo_list(query_db, query, is_page)

    @classmethod
    async def get_demo_by_id_services(cls, query_db: AsyncSession, id: int):
        """
        根据ID获取演示ID详情
        """
        return await DemoDao.get_demo_by_id(query_db, id)

    @classmethod
    async def add_demo_services(cls, query_db: AsyncSession, obj: DemoModel):
        """
        新增演示ID
        """
        try:
            await DemoDao.add_demo(query_db, obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'新增失败: {str(e)}')

    @classmethod
    async def update_demo_services(cls, query_db: AsyncSession, obj: DemoModel):
        """
        更新演示ID
        """
        info = await cls.get_demo_by_id_services(query_db, obj.id)
        if not info:
            raise ServiceException(message='演示ID不存在')
        try:
            await DemoDao.update_demo(query_db, obj.model_dump(exclude_unset=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新失败: {str(e)}')

    @classmethod
    async def delete_demo_services(cls, query_db: AsyncSession, obj: DeleteDemoModel):
        """
        删除演示ID
        """
        try:
            id_list = [int(i) for i in obj.id_ids.split(',')]
            await DemoDao.delete_demo(query_db, id_list)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'删除失败: {str(e)}')
