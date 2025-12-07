from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from config.constant import CommonConstant
from exceptions.exception import ServiceException
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_admin.dao.book_dao import BookDao
from module_admin.entity.vo.book_vo import DeleteBookModel, BookModel, BookPageQueryModel
from utils.common_util import CamelCaseUtil
from utils.excel_util import ExcelUtil


class BookService:
    """
    图书信息模块服务层
    """

    @classmethod
    async def get_book_list_services(
        cls, query_db: AsyncSession, query_object: BookPageQueryModel, is_page: bool = False
    ):
        """
        获取图书信息列表信息service

        :param query_db: orm对象
        :param query_object: 查询参数对象
        :param is_page: 是否开启分页
        :return: 图书信息列表信息对象
        """
        book_list_result = await BookDao.get_book_list(query_db, query_object, is_page)

        return book_list_result


    @classmethod
    async def add_book_services(cls, query_db: AsyncSession, page_object: BookModel):
        """
        新增图书信息信息service

        :param query_db: orm对象
        :param page_object: 新增图书信息对象
        :return: 新增图书信息校验结果
        """
        try:
            await BookDao.add_book_dao(query_db, page_object)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise e

    @classmethod
    async def edit_book_services(cls, query_db: AsyncSession, page_object: BookModel):
        """
        编辑图书信息信息service

        :param query_db: orm对象
        :param page_object: 编辑图书信息对象
        :return: 编辑图书信息校验结果
        """
        edit_book = page_object.model_dump(exclude_unset=True, exclude={'create_by', 'create_time', })
        book_info = await cls.book_detail_services(query_db, page_object.book_id)
        if book_info.book_id:
            try:
                await BookDao.edit_book_dao(query_db, edit_book)
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='更新成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='图书信息不存在')

    @classmethod
    async def delete_book_services(cls, query_db: AsyncSession, page_object: DeleteBookModel):
        """
        删除图书信息信息service

        :param query_db: orm对象
        :param page_object: 删除图书信息对象
        :return: 删除图书信息校验结果
        """
        if page_object.book_ids:
            book_id_list = page_object.book_ids.split(',')
            try:
                for book_id in book_id_list:
                    await BookDao.delete_book_dao(query_db, BookModel(bookId=book_id))
                await query_db.commit()
                return CrudResponseModel(is_success=True, message='删除成功')
            except Exception as e:
                await query_db.rollback()
                raise e
        else:
            raise ServiceException(message='传入图书ID为空')

    @classmethod
    async def book_detail_services(cls, query_db: AsyncSession, book_id: int):
        """
        获取图书信息详细信息service

        :param query_db: orm对象
        :param book_id: 图书ID
        :return: 图书ID对应的信息
        """
        book = await BookDao.get_book_detail_by_id(query_db, book_id=book_id)
        if book:
            result = BookModel(**CamelCaseUtil.transform_result(book))
        else:
            result = BookModel(**dict())

        return result

    @staticmethod
    async def export_book_list_services(book_list: List):
        """
        导出图书信息信息service

        :param book_list: 图书信息信息列表
        :return: 图书信息信息对应excel的二进制数据
        """
        # 创建一个映射字典，将英文键映射到中文键
        mapping_dict = {
            'bookId': '图书ID',
            'bookName': '图书名称',
            'author': '作者',
            'isbn': 'ISBN编号',
            'publisher': '出版社',
            'publishDate': '出版日期',
            'price': '价格',
            'category': '分类',
            'stock': '库存数量',
            'description': '图书简介',
            'coverImage': '封面图片',
            'status': '状态',
            'createBy': '创建者',
            'createTime': '创建时间',
            'updateBy': '更新者',
            'updateTime': '更新时间',
            'remark': '备注',
        }
        binary_data = ExcelUtil.export_list2excel(book_list, mapping_dict)

        return binary_data
