from decimal import Decimal
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query




class BookModel(BaseModel):
    """
    图书信息表对应pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True)

    book_id: Optional[int] = Field(default=None, description='图书ID')
    book_name: Optional[str] = Field(default=None, description='图书名称')
    author: Optional[str] = Field(default=None, description='作者')
    isbn: Optional[str] = Field(default=None, description='ISBN编号')
    publisher: Optional[str] = Field(default=None, description='出版社')
    publish_date: Optional[date] = Field(default=None, description='出版日期')
    price: Optional[Decimal] = Field(default=None, description='价格')
    category: Optional[str] = Field(default=None, description='分类')
    stock: Optional[int] = Field(default=None, description='库存数量')
    description: Optional[str] = Field(default=None, description='图书简介')
    cover_image: Optional[str] = Field(default=None, description='封面图片')
    status: Optional[str] = Field(default=None, description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(default=None, description='创建者')
    create_time: Optional[datetime] = Field(default=None, description='创建时间')
    update_by: Optional[str] = Field(default=None, description='更新者')
    update_time: Optional[datetime] = Field(default=None, description='更新时间')
    remark: Optional[str] = Field(default=None, description='备注')

    @NotBlank(field_name='book_name', message='图书名称不能为空')
    def get_book_name(self):
        return self.book_name


    def validate_fields(self):
        self.get_book_name()




class BookQueryModel(BookModel):
    """
    图书信息不分页查询模型
    """
    pass


@as_query
class BookPageQueryModel(BookQueryModel):
    """
    图书信息分页查询模型
    """

    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')


class DeleteBookModel(BaseModel):
    """
    删除图书信息模型
    """

    model_config = ConfigDict(alias_generator=to_camel)

    book_ids: str = Field(description='需要删除的图书ID')
