from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.notify_key_do import NotifyKey
from module_admin.entity.vo.notify_key_vo import NotifyKeyModel, NotifyKeyPageQueryModel
from utils.page_util import PageUtil


class NotifyKeyDao:
    """
    密钥ID数据访问层
    """

    @classmethod
    async def get_notify_key_list(cls, db: AsyncSession, query: NotifyKeyPageQueryModel, is_page: bool = False):
        """
        获取密钥ID列表
        """
        query_obj = select(NotifyKey).order_by(desc(NotifyKey.key_id))
        
        # 添加查询条件
        if query.user_id is not None:
            query_obj = query_obj.where(NotifyKey.user_id == query.user_id)
        if query.key_name:
            query_obj = query_obj.where(NotifyKey.key_name.contains(query.key_name))
        if query.channel_ids:
            query_obj = query_obj.where(NotifyKey.channel_ids.contains(query.channel_ids))
        if query.daily_limit is not None:
            query_obj = query_obj.where(NotifyKey.daily_limit == query.daily_limit)
        if query.daily_used is not None:
            query_obj = query_obj.where(NotifyKey.daily_used == query.daily_used)
        if query.total_count is not None:
            query_obj = query_obj.where(NotifyKey.total_count == query.total_count)
        if query.status:
            query_obj = query_obj.where(NotifyKey.status.contains(query.status))
        if query.remark:
            query_obj = query_obj.where(NotifyKey.remark.contains(query.remark))
        
        if is_page:
            return await PageUtil.paginate(db, query_obj, query.page_num, query.page_size, is_page=True)
        else:
            result = await db.execute(query_obj)
            return result.scalars().all()

    @classmethod
    async def get_notify_key_by_id(cls, db: AsyncSession, id: int):
        """
        根据ID获取密钥ID
        """
        result = await db.execute(
            select(NotifyKey).where(NotifyKey.key_id == id)
        )
        return result.scalars().first()

    @classmethod
    async def add_notify_key(cls, db: AsyncSession, obj: NotifyKeyModel):
        """
        新增密钥ID
        """
        db_obj = NotifyKey(**obj.model_dump(exclude_unset=True, exclude_none=True, exclude={'key_id'}))
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def update_notify_key(cls, db: AsyncSession, obj: dict):
        """
        更新密钥ID
        """
        await db.execute(
            update(NotifyKey)
            .where(NotifyKey.key_id == obj.get('key_id'))
            .values(**obj)
        )

    @classmethod
    async def delete_notify_key(cls, db: AsyncSession, id_list: list):
        """
        删除密钥ID
        """
        await db.execute(
            delete(NotifyKey).where(NotifyKey.key_id.in_(id_list))
        )
