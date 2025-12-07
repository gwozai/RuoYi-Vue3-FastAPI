from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.dao.notify_log_dao import NotifyLogDao
from module_admin.entity.vo.notify_log_vo import NotifyLogModel, NotifyLogPageQueryModel, DeleteNotifyLogModel
from exceptions.exception import ServiceException


class NotifyLogService:
    """
    日志ID服务层
    """

    @classmethod
    async def get_notify_log_list_services(cls, query_db: AsyncSession, query: NotifyLogPageQueryModel, is_page: bool = False):
        """
        获取日志ID列表
        """
        return await NotifyLogDao.get_notify_log_list(query_db, query, is_page)

    @classmethod
    async def get_notify_log_by_id_services(cls, query_db: AsyncSession, id: int):
        """
        根据ID获取日志ID详情
        """
        return await NotifyLogDao.get_notify_log_by_id(query_db, id)

    @classmethod
    async def add_notify_log_services(cls, query_db: AsyncSession, obj: NotifyLogModel):
        """
        新增日志ID
        """
        try:
            await NotifyLogDao.add_notify_log(query_db, obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'新增失败: {str(e)}')

    @classmethod
    async def update_notify_log_services(cls, query_db: AsyncSession, obj: NotifyLogModel):
        """
        更新日志ID
        """
        info = await cls.get_notify_log_by_id_services(query_db, obj.log_id)
        if not info:
            raise ServiceException(message='日志ID不存在')
        try:
            await NotifyLogDao.update_notify_log(query_db, obj.model_dump(exclude_unset=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新失败: {str(e)}')

    @classmethod
    async def delete_notify_log_services(cls, query_db: AsyncSession, obj: DeleteNotifyLogModel):
        """
        删除日志ID
        """
        try:
            id_list = [int(i) for i in obj.log_ids.split(',')]
            await NotifyLogDao.delete_notify_log(query_db, id_list)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'删除失败: {str(e)}')
