from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.dao.notify_channel_dao import NotifyChannelDao
from module_admin.entity.vo.notify_channel_vo import NotifyChannelModel, NotifyChannelPageQueryModel, DeleteNotifyChannelModel
from exceptions.exception import ServiceException


class NotifyChannelService:
    """
    渠道ID服务层
    """

    @classmethod
    async def get_notify_channel_list_services(cls, query_db: AsyncSession, query: NotifyChannelPageQueryModel, is_page: bool = False):
        """
        获取渠道ID列表
        """
        return await NotifyChannelDao.get_notify_channel_list(query_db, query, is_page)

    @classmethod
    async def get_notify_channel_by_id_services(cls, query_db: AsyncSession, id: int):
        """
        根据ID获取渠道ID详情
        """
        return await NotifyChannelDao.get_notify_channel_by_id(query_db, id)

    @classmethod
    async def add_notify_channel_services(cls, query_db: AsyncSession, obj: NotifyChannelModel):
        """
        新增渠道ID
        """
        try:
            await NotifyChannelDao.add_notify_channel(query_db, obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'新增失败: {str(e)}')

    @classmethod
    async def update_notify_channel_services(cls, query_db: AsyncSession, obj: NotifyChannelModel):
        """
        更新渠道ID
        """
        info = await cls.get_notify_channel_by_id_services(query_db, obj.channel_id)
        if not info:
            raise ServiceException(message='渠道ID不存在')
        try:
            await NotifyChannelDao.update_notify_channel(query_db, obj.model_dump(exclude_unset=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新失败: {str(e)}')

    @classmethod
    async def delete_notify_channel_services(cls, query_db: AsyncSession, obj: DeleteNotifyChannelModel):
        """
        删除渠道ID
        """
        try:
            id_list = [int(i) for i in obj.channel_ids.split(',')]
            await NotifyChannelDao.delete_notify_channel(query_db, id_list)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'删除失败: {str(e)}')
