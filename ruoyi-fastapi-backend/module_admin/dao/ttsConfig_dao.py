from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.ttsConfig_do import SysTtsConfig
from module_admin.entity.vo.ttsConfig_vo import TtsconfigModel, TtsconfigPageQueryModel
from utils.page_util import PageUtil


class TtsconfigDao:
    """
    TTS API配置模块数据库操作层
    """

    @classmethod
    async def get_ttsConfig_detail_by_id(cls, db: AsyncSession, config_id: int):
        """
        根据配置ID获取TTS API配置详细信息

        :param db: orm对象
        :param config_id: 配置ID
        :return: TTS API配置信息对象
        """
        ttsConfig_info = (
            (
                await db.execute(
                    select(SysTtsConfig)
                    .where(
                        SysTtsConfig.config_id == config_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return ttsConfig_info

    @classmethod
    async def get_ttsConfig_detail_by_info(cls, db: AsyncSession, ttsConfig: TtsconfigModel):
        """
        根据TTS API配置参数获取TTS API配置信息

        :param db: orm对象
        :param ttsConfig: TTS API配置参数对象
        :return: TTS API配置信息对象
        """
        ttsConfig_info = (
            (
                await db.execute(
                    select(SysTtsConfig).where(
                    )
                )
            )
            .scalars()
            .first()
        )

        return ttsConfig_info

    @classmethod
    async def get_ttsConfig_list(cls, db: AsyncSession, query_object: TtsconfigPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取TTS API配置列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: TTS API配置列表信息对象
        """
        query = (
            select(SysTtsConfig)
            .where(
                SysTtsConfig.user_id == query_object.user_id if query_object.user_id else True,
                SysTtsConfig.config_name.like(f'%{query_object.config_name}%') if query_object.config_name else True,
                SysTtsConfig.api_url == query_object.api_url if query_object.api_url else True,
                SysTtsConfig.api_key == query_object.api_key if query_object.api_key else True,
                SysTtsConfig.api_model == query_object.api_model if query_object.api_model else True,
                SysTtsConfig.is_default == query_object.is_default if query_object.is_default else True,
                SysTtsConfig.status == query_object.status if query_object.status else True,
            )
            .order_by(SysTtsConfig.config_id)
            .distinct()
        )
        ttsConfig_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return ttsConfig_list

    @classmethod
    async def add_ttsConfig_dao(cls, db: AsyncSession, ttsConfig: TtsconfigModel):
        """
        新增TTS API配置数据库操作

        :param db: orm对象
        :param ttsConfig: TTS API配置对象
        :return:
        """
        db_ttsConfig = SysTtsConfig(**ttsConfig.model_dump(exclude={}))
        db.add(db_ttsConfig)
        await db.flush()

        return db_ttsConfig

    @classmethod
    async def edit_ttsConfig_dao(cls, db: AsyncSession, ttsConfig: dict):
        """
        编辑TTS API配置数据库操作

        :param db: orm对象
        :param ttsConfig: 需要更新的TTS API配置字典
        :return:
        """
        await db.execute(update(SysTtsConfig), [ttsConfig])

    @classmethod
    async def delete_ttsConfig_dao(cls, db: AsyncSession, ttsConfig: TtsconfigModel):
        """
        删除TTS API配置数据库操作

        :param db: orm对象
        :param ttsConfig: TTS API配置对象
        :return:
        """
        await db.execute(delete(SysTtsConfig).where(SysTtsConfig.config_id.in_([ttsConfig.config_id])))

