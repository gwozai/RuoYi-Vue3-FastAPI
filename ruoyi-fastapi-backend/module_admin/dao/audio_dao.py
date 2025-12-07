from sqlalchemy import delete, select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.audio_do import SysAudio
from module_admin.entity.vo.audio_vo import AudioModel, AudioPageQueryModel
from utils.page_util import PageUtil


class AudioDao:
    """
    音频生成模块数据库操作层
    """

    @classmethod
    async def get_audio_detail_by_id(cls, db: AsyncSession, audio_id: int):
        """
        根据音频ID获取音频详细信息

        :param db: orm对象
        :param audio_id: 音频ID
        :return: 音频信息对象
        """
        audio_info = (
            (
                await db.execute(
                    select(SysAudio)
                    .where(SysAudio.audio_id == audio_id)
                )
            )
            .scalars()
            .first()
        )

        return audio_info

    @classmethod
    async def get_audio_list(cls, db: AsyncSession, query_object: AudioPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取音频列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 音频列表信息对象
        """
        conditions = []
        if query_object.audio_name:
            conditions.append(SysAudio.audio_name.like(f'%{query_object.audio_name}%'))
        if query_object.voice:
            conditions.append(SysAudio.voice == query_object.voice)
        if query_object.status:
            conditions.append(SysAudio.status == query_object.status)
        if query_object.begin_time and query_object.end_time:
            conditions.append(SysAudio.create_time.between(query_object.begin_time, query_object.end_time))

        query = (
            select(SysAudio)
            .where(and_(*conditions) if conditions else True)
            .order_by(SysAudio.audio_id.desc())
            .distinct()
        )
        audio_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return audio_list

    @classmethod
    async def add_audio_dao(cls, db: AsyncSession, audio: AudioModel):
        """
        新增音频数据库操作

        :param db: orm对象
        :param audio: 音频对象
        :return:
        """
        db_audio = SysAudio(**audio.model_dump(exclude_unset=True))
        db.add(db_audio)
        await db.flush()

        return db_audio

    @classmethod
    async def edit_audio_dao(cls, db: AsyncSession, audio: dict):
        """
        编辑音频数据库操作

        :param db: orm对象
        :param audio: 需要更新的音频字典
        :return:
        """
        await db.execute(update(SysAudio), [audio])

    @classmethod
    async def delete_audio_dao(cls, db: AsyncSession, audio: AudioModel):
        """
        删除音频数据库操作

        :param db: orm对象
        :param audio: 音频对象
        :return:
        """
        await db.execute(delete(SysAudio).where(SysAudio.audio_id.in_([audio.audio_id])))

    @classmethod
    async def update_audio_status(cls, db: AsyncSession, audio_id: int, status: str, 
                                   file_path: str = None, file_size: int = None, 
                                   duration: int = None, error_msg: str = None):
        """
        更新音频生成状态

        :param db: orm对象
        :param audio_id: 音频ID
        :param status: 状态
        :param file_path: 文件路径
        :param file_size: 文件大小
        :param duration: 音频时长
        :param error_msg: 错误信息
        :return:
        """
        update_data = {'audio_id': audio_id, 'status': status}
        if file_path:
            update_data['file_path'] = file_path
        if file_size:
            update_data['file_size'] = file_size
        if duration:
            update_data['duration'] = duration
        if error_msg:
            update_data['error_msg'] = error_msg

        await db.execute(update(SysAudio), [update_data])
