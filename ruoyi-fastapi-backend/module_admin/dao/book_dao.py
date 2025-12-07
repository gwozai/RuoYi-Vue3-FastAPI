from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.do.book_do import SysBook
from module_admin.entity.vo.book_vo import BookModel, BookPageQueryModel
from utils.page_util import PageUtil


class BookDao:
    """
    图书信息模块数据库操作层
    """

    @classmethod
    async def get_book_detail_by_id(cls, db: AsyncSession, book_id: int):
        """
        根据图书ID获取图书信息详细信息

        :param db: orm对象
        :param book_id: 图书ID
        :return: 图书信息信息对象
        """
        book_info = (
            (
                await db.execute(
                    select(SysBook)
                    .where(
                        SysBook.book_id == book_id
                    )
                )
            )
            .scalars()
            .first()
        )

        return book_info

    @classmethod
    async def get_book_detail_by_info(cls, db: AsyncSession, book: BookModel):
        """
        根据图书信息参数获取图书信息信息

        :param db: orm对象
        :param book: 图书信息参数对象
        :return: 图书信息信息对象
        """
        book_info = (
            (
                await db.execute(
                    select(SysBook).where(
                    )
                )
            )
            .scalars()
            .first()
        )

        return book_info

    @classmethod
    async def get_book_list(cls, db: AsyncSession, query_object: BookPageQueryModel, is_page: bool = False):
        """
        根据查询参数获取图书信息列表信息

        :param db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 图书信息列表信息对象
        """
        query = (
            select(SysBook)
            .where(
                SysBook.book_name.like(f'%{query_object.book_name}%') if query_object.book_name else True,
                SysBook.author == query_object.author if query_object.author else True,
                SysBook.isbn == query_object.isbn if query_object.isbn else True,
                SysBook.publisher == query_object.publisher if query_object.publisher else True,
                SysBook.publish_date == query_object.publish_date if query_object.publish_date else True,
                SysBook.price == query_object.price if query_object.price else True,
                SysBook.category == query_object.category if query_object.category else True,
                SysBook.stock == query_object.stock if query_object.stock else True,
                SysBook.description == query_object.description if query_object.description else True,
                SysBook.cover_image == query_object.cover_image if query_object.cover_image else True,
                SysBook.status == query_object.status if query_object.status else True,
            )
            .order_by(SysBook.book_id)
            .distinct()
        )
        book_list = await PageUtil.paginate(db, query, query_object.page_num, query_object.page_size, is_page)

        return book_list

    @classmethod
    async def add_book_dao(cls, db: AsyncSession, book: BookModel):
        """
        新增图书信息数据库操作

        :param db: orm对象
        :param book: 图书信息对象
        :return:
        """
        db_book = SysBook(**book.model_dump(exclude={}))
        db.add(db_book)
        await db.flush()

        return db_book

    @classmethod
    async def edit_book_dao(cls, db: AsyncSession, book: dict):
        """
        编辑图书信息数据库操作

        :param db: orm对象
        :param book: 需要更新的图书信息字典
        :return:
        """
        await db.execute(update(SysBook), [book])

    @classmethod
    async def delete_book_dao(cls, db: AsyncSession, book: BookModel):
        """
        删除图书信息数据库操作

        :param db: orm对象
        :param book: 图书信息对象
        :return:
        """
        await db.execute(delete(SysBook).where(SysBook.book_id.in_([book.book_id])))

