from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.notify_channel_do import NotifyChannel
from module_admin.entity.vo.notify_channel_vo import NotifyChannelModel, NotifyChannelPageQueryModel
from utils.page_util import PageUtil


class NotifyChannelDao:
    """
    渠道ID数据访问层
    """

    @classmethod
    async def get_notify_channel_list(cls, db: AsyncSession, query: NotifyChannelPageQueryModel, is_page: bool = False):
        """
        获取渠道ID列表
        """
        query_obj = select(NotifyChannel).order_by(desc(NotifyChannel.channel_id))
        
        # 添加查询条件
        if query.user_id is not None:
            query_obj = query_obj.where(NotifyChannel.user_id == query.user_id)
        if query.platform_id is not None:
            query_obj = query_obj.where(NotifyChannel.platform_id == query.platform_id)
        if query.channel_name:
            query_obj = query_obj.where(NotifyChannel.channel_name.contains(query.channel_name))
        if query.webhook_url:
            query_obj = query_obj.where(NotifyChannel.webhook_url.contains(query.webhook_url))
        if query.is_default:
            query_obj = query_obj.where(NotifyChannel.is_default.contains(query.is_default))
        if query.status:
            query_obj = query_obj.where(NotifyChannel.status.contains(query.status))
        if query.use_count is not None:
            query_obj = query_obj.where(NotifyChannel.use_count == query.use_count)
        if query.remark:
            query_obj = query_obj.where(NotifyChannel.remark.contains(query.remark))
        
        if is_page:
            return await PageUtil.paginate(db, query_obj, query.page_num, query.page_size, is_page=True)
        else:
            result = await db.execute(query_obj)
            return result.scalars().all()

    @classmethod
    async def get_notify_channel_by_id(cls, db: AsyncSession, id: int):
        """
        根据ID获取渠道ID
        """
        result = await db.execute(
            select(NotifyChannel).where(NotifyChannel.channel_id == id)
        )
        return result.scalars().first()

    @classmethod
    async def add_notify_channel(cls, db: AsyncSession, obj: NotifyChannelModel):
        """
        新增渠道ID
        """
        db_obj = NotifyChannel(**obj.model_dump(exclude_unset=True))
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def update_notify_channel(cls, db: AsyncSession, obj: dict):
        """
        更新渠道ID
        """
        await db.execute(
            update(NotifyChannel)
            .where(NotifyChannel.channel_id == obj.get('channel_id'))
            .values(**obj)
        )

    @classmethod
    async def delete_notify_channel(cls, db: AsyncSession, id_list: list):
        """
        删除渠道ID
        """
        await db.execute(
            delete(NotifyChannel).where(NotifyChannel.channel_id.in_(id_list))
        )
