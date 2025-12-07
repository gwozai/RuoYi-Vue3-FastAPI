from datetime import datetime
from fastapi import APIRouter, Depends, Form, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_admin.service.book_service import BookService
from module_admin.entity.vo.book_vo import DeleteBookModel, BookModel, BookPageQueryModel
from utils.common_util import bytes2file_response
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


bookController = APIRouter(prefix='/system/book', dependencies=[Depends(LoginService.get_current_user)])


@bookController.get(
    '/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('system:book:list'))]
)
async def get_system_book_list(
    request: Request,
book_page_query: BookPageQueryModel = Depends(BookPageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取分页数据
    book_page_query_result = await BookService.get_book_list_services(query_db, book_page_query, is_page=True)
    logger.info('获取成功')

    return ResponseUtil.success(model_content=book_page_query_result)


@bookController.post('', dependencies=[Depends(CheckUserInterfaceAuth('system:book:add'))])
@ValidateFields(validate_model='add_book')
@Log(title='图书信息', business_type=BusinessType.INSERT)
async def add_system_book(
    request: Request,
    add_book: BookModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    add_book.create_by = current_user.user.user_name
    add_book.create_time = datetime.now()
    add_book.update_by = current_user.user.user_name
    add_book.update_time = datetime.now()
    add_book_result = await BookService.add_book_services(query_db, add_book)
    logger.info(add_book_result.message)

    return ResponseUtil.success(msg=add_book_result.message)


@bookController.put('', dependencies=[Depends(CheckUserInterfaceAuth('system:book:edit'))])
@ValidateFields(validate_model='edit_book')
@Log(title='图书信息', business_type=BusinessType.UPDATE)
async def edit_system_book(
    request: Request,
    edit_book: BookModel,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    edit_book.update_by = current_user.user.user_name
    edit_book.update_time = datetime.now()
    edit_book_result = await BookService.edit_book_services(query_db, edit_book)
    logger.info(edit_book_result.message)

    return ResponseUtil.success(msg=edit_book_result.message)


@bookController.delete('/{book_ids}', dependencies=[Depends(CheckUserInterfaceAuth('system:book:remove'))])
@Log(title='图书信息', business_type=BusinessType.DELETE)
async def delete_system_book(request: Request, book_ids: str, query_db: AsyncSession = Depends(get_db)):
    delete_book = DeleteBookModel(bookIds=book_ids)
    delete_book_result = await BookService.delete_book_services(query_db, delete_book)
    logger.info(delete_book_result.message)

    return ResponseUtil.success(msg=delete_book_result.message)


@bookController.get(
    '/{book_id}', response_model=BookModel, dependencies=[Depends(CheckUserInterfaceAuth('system:book:query'))]
)
async def query_detail_system_book(request: Request, book_id: int, query_db: AsyncSession = Depends(get_db)):
    book_detail_result = await BookService.book_detail_services(query_db, book_id)
    logger.info(f'获取book_id为{book_id}的信息成功')

    return ResponseUtil.success(data=book_detail_result)


@bookController.post('/export', dependencies=[Depends(CheckUserInterfaceAuth('system:book:export'))])
@Log(title='图书信息', business_type=BusinessType.EXPORT)
async def export_system_book_list(
    request: Request,
    book_page_query: BookPageQueryModel = Form(),
    query_db: AsyncSession = Depends(get_db),
):
    # 获取全量数据
    book_query_result = await BookService.get_book_list_services(query_db, book_page_query, is_page=False)
    book_export_result = await BookService.export_book_list_services(book_query_result)
    logger.info('导出成功')

    return ResponseUtil.streaming(data=bytes2file_response(book_export_result))
