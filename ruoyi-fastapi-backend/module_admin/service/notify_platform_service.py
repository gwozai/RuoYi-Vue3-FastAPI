from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.dao.notify_platform_dao import NotifyPlatformDao
from module_admin.entity.vo.notify_platform_vo import NotifyPlatformModel, NotifyPlatformPageQueryModel, DeleteNotifyPlatformModel
from exceptions.exception import ServiceException


class NotifyPlatformService:
    """
    平台ID服务层
    """

    @classmethod
    async def get_notify_platform_list_services(cls, query_db: AsyncSession, query: NotifyPlatformPageQueryModel, is_page: bool = False):
        """
        获取平台ID列表
        """
        return await NotifyPlatformDao.get_notify_platform_list(query_db, query, is_page)

    @classmethod
    async def get_notify_platform_by_id_services(cls, query_db: AsyncSession, id: int):
        """
        根据ID获取平台ID详情
        """
        return await NotifyPlatformDao.get_notify_platform_by_id(query_db, id)

    @classmethod
    async def add_notify_platform_services(cls, query_db: AsyncSession, obj: NotifyPlatformModel):
        """
        新增平台ID
        """
        try:
            await NotifyPlatformDao.add_notify_platform(query_db, obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'新增失败: {str(e)}')

    @classmethod
    async def update_notify_platform_services(cls, query_db: AsyncSession, obj: NotifyPlatformModel):
        """
        更新通知平台
        """
        info = await cls.get_notify_platform_by_id_services(query_db, obj.platform_id)
        if not info:
            raise ServiceException(message='平台ID不存在')
        try:
            await NotifyPlatformDao.update_notify_platform(query_db, obj.model_dump(exclude_unset=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新失败: {str(e)}')

    @classmethod
    async def delete_notify_platform_services(cls, query_db: AsyncSession, obj: DeleteNotifyPlatformModel):
        """
        删除平台ID
        """
        try:
            id_list = [int(i) for i in obj.platform_ids.split(',')]
            await NotifyPlatformDao.delete_notify_platform(query_db, id_list)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'删除失败: {str(e)}')
