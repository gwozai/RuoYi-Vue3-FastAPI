from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.notify_platform_do import NotifyPlatform
from module_admin.entity.vo.notify_platform_vo import NotifyPlatformModel, NotifyPlatformPageQueryModel
from utils.page_util import PageUtil


class NotifyPlatformDao:
    """
    平台ID数据访问层
    """

    @classmethod
    async def get_notify_platform_list(cls, db: AsyncSession, query: NotifyPlatformPageQueryModel, is_page: bool = False):
        """
        获取平台ID列表
        """
        query_obj = select(NotifyPlatform).order_by(desc(NotifyPlatform.platform_id))
        
        # 添加查询条件
        if query.platform_name:
            query_obj = query_obj.where(NotifyPlatform.platform_name.contains(query.platform_name))
        if query.platform_code:
            query_obj = query_obj.where(NotifyPlatform.platform_code.contains(query.platform_code))
        if query.platform_icon:
            query_obj = query_obj.where(NotifyPlatform.platform_icon.contains(query.platform_icon))
        if query.webhook_template:
            query_obj = query_obj.where(NotifyPlatform.webhook_template.contains(query.webhook_template))
        if query.request_method:
            query_obj = query_obj.where(NotifyPlatform.request_method.contains(query.request_method))
        if query.content_type:
            query_obj = query_obj.where(NotifyPlatform.content_type.contains(query.content_type))
        if query.body_template:
            query_obj = query_obj.where(NotifyPlatform.body_template.contains(query.body_template))
        if query.status:
            query_obj = query_obj.where(NotifyPlatform.status.contains(query.status))
        if query.order_num is not None:
            query_obj = query_obj.where(NotifyPlatform.order_num == query.order_num)
        if query.remark:
            query_obj = query_obj.where(NotifyPlatform.remark.contains(query.remark))
        
        if is_page:
            return await PageUtil.paginate(db, query_obj, query.page_num, query.page_size, is_page=True)
        else:
            result = await db.execute(query_obj)
            return result.scalars().all()

    @classmethod
    async def get_notify_platform_by_id(cls, db: AsyncSession, id: int):
        """
        根据ID获取平台ID
        """
        result = await db.execute(
            select(NotifyPlatform).where(NotifyPlatform.platform_id == id)
        )
        return result.scalars().first()

    @classmethod
    async def add_notify_platform(cls, db: AsyncSession, obj: NotifyPlatformModel):
        """
        新增平台ID
        """
        db_obj = NotifyPlatform(**obj.model_dump(exclude_unset=True))
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def update_notify_platform(cls, db: AsyncSession, obj: dict):
        """
        更新平台ID
        """
        await db.execute(
            update(NotifyPlatform)
            .where(NotifyPlatform.platform_id == obj.get('platform_id'))
            .values(**obj)
        )

    @classmethod
    async def delete_notify_platform(cls, db: AsyncSession, id_list: list):
        """
        删除平台ID
        """
        await db.execute(
            delete(NotifyPlatform).where(NotifyPlatform.platform_id.in_(id_list))
        )
