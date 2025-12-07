from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.notify_log_do import NotifyLog
from module_admin.entity.vo.notify_log_vo import NotifyLogModel, NotifyLogPageQueryModel
from utils.page_util import PageUtil


class NotifyLogDao:
    """
    日志ID数据访问层
    """

    @classmethod
    async def get_notify_log_list(cls, db: AsyncSession, query: NotifyLogPageQueryModel, is_page: bool = False):
        """
        获取日志ID列表
        """
        query_obj = select(NotifyLog).order_by(desc(NotifyLog.log_id))
        
        # 添加查询条件
        if query.user_id is not None:
            query_obj = query_obj.where(NotifyLog.user_id == query.user_id)
        if query.key_id is not None:
            query_obj = query_obj.where(NotifyLog.key_id == query.key_id)
        if query.channel_id is not None:
            query_obj = query_obj.where(NotifyLog.channel_id == query.channel_id)
        if query.platform_id is not None:
            query_obj = query_obj.where(NotifyLog.platform_id == query.platform_id)
        if query.title:
            query_obj = query_obj.where(NotifyLog.title.contains(query.title))
        if query.content:
            query_obj = query_obj.where(NotifyLog.content.contains(query.content))
        if query.msg_type:
            query_obj = query_obj.where(NotifyLog.msg_type.contains(query.msg_type))
        if query.request_data:
            query_obj = query_obj.where(NotifyLog.request_data.contains(query.request_data))
        if query.response_data:
            query_obj = query_obj.where(NotifyLog.response_data.contains(query.response_data))
        if query.status:
            query_obj = query_obj.where(NotifyLog.status == query.status)
        if query.error_msg:
            query_obj = query_obj.where(NotifyLog.error_msg.contains(query.error_msg))
        if query.ip_address:
            query_obj = query_obj.where(NotifyLog.ip_address.contains(query.ip_address))
        if query.cost_time is not None:
            query_obj = query_obj.where(NotifyLog.cost_time == query.cost_time)
        
        if is_page:
            return await PageUtil.paginate(db, query_obj, query.page_num, query.page_size, is_page=True)
        else:
            result = await db.execute(query_obj)
            return result.scalars().all()

    @classmethod
    async def get_notify_log_by_id(cls, db: AsyncSession, id: int):
        """
        根据ID获取日志ID
        """
        result = await db.execute(
            select(NotifyLog).where(NotifyLog.log_id == id)
        )
        return result.scalars().first()

    @classmethod
    async def add_notify_log(cls, db: AsyncSession, obj: NotifyLogModel):
        """
        新增日志ID
        """
        db_obj = NotifyLog(**obj.model_dump(exclude_unset=True))
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def update_notify_log(cls, db: AsyncSession, obj: dict):
        """
        更新日志ID
        """
        await db.execute(
            update(NotifyLog)
            .where(NotifyLog.log_id == obj.get('log_id'))
            .values(**obj)
        )

    @classmethod
    async def delete_notify_log(cls, db: AsyncSession, id_list: list):
        """
        删除日志ID
        """
        await db.execute(
            delete(NotifyLog).where(NotifyLog.log_id.in_(id_list))
        )
