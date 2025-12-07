from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.dao.notify_key_dao import NotifyKeyDao
from module_admin.entity.vo.notify_key_vo import NotifyKeyModel, NotifyKeyPageQueryModel, DeleteNotifyKeyModel
from exceptions.exception import ServiceException


class NotifyKeyService:
    """
    密钥ID服务层
    """

    @classmethod
    async def get_notify_key_list_services(cls, query_db: AsyncSession, query: NotifyKeyPageQueryModel, is_page: bool = False):
        """
        获取密钥ID列表
        """
        return await NotifyKeyDao.get_notify_key_list(query_db, query, is_page)

    @classmethod
    async def get_notify_key_by_id_services(cls, query_db: AsyncSession, id: int):
        """
        根据ID获取密钥ID详情
        """
        return await NotifyKeyDao.get_notify_key_by_id(query_db, id)

    @classmethod
    async def add_notify_key_services(cls, query_db: AsyncSession, obj: NotifyKeyModel):
        """
        新增密钥ID
        """
        try:
            await NotifyKeyDao.add_notify_key(query_db, obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'新增失败: {str(e)}')

    @classmethod
    async def update_notify_key_services(cls, query_db: AsyncSession, obj: NotifyKeyModel):
        """
        更新密钥ID
        """
        info = await cls.get_notify_key_by_id_services(query_db, obj.key_id)
        if not info:
            raise ServiceException(message='密钥ID不存在')
        try:
            await NotifyKeyDao.update_notify_key(query_db, obj.model_dump(exclude_unset=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新失败: {str(e)}')

    @classmethod
    async def delete_notify_key_services(cls, query_db: AsyncSession, obj: DeleteNotifyKeyModel):
        """
        删除密钥ID
        """
        try:
            id_list = [int(i) for i in obj.key_ids.split(',')]
            await NotifyKeyDao.delete_notify_key(query_db, id_list)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'删除失败: {str(e)}')
