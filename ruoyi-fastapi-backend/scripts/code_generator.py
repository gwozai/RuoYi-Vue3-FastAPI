#!/usr/bin/env python3
"""
代码生成器命令行工具

使用方法:
    # 从数据库表生成代码（使用系统模板）
    python scripts/code_generator.py --table sys_example --module system --business example --use-system-template
    
    # 从 SQL 建表语句生成代码
    python scripts/code_generator.py --sql "CREATE TABLE sys_demo (id INT PRIMARY KEY, name VARCHAR(100))" --module system --business demo
    
    # 指定输出目录
    python scripts/code_generator.py --table sys_example --module system --business example --output /tmp/gen
    
    # 生成并自动复制到项目目录
    python scripts/code_generator.py --table sys_example --module system --business example --auto-install

参数说明:
    --table               数据库表名
    --sql                 建表 SQL 语句
    --module              模块名称 (如 system)
    --business            业务名称 (如 user, audio)
    --output              输出目录 (默认: /tmp/ruoyi-gen)
    --auto-install        自动复制到项目目录
    --menu-parent         父菜单ID (用于生成菜单SQL)
    --env                 环境 (dev/prod, 默认: dev)
    --use-system-template 使用系统内置的 Jinja2 模板（包含完整前端 Vue 页面）
"""

import argparse
import asyncio
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# 添加项目根目录到 Python 路径
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 设置环境变量
os.environ.setdefault('APP_ENV', 'dev')


class CodeGenerator:
    """代码生成器"""
    
    # Jinja2 模板
    TEMPLATES = {
        'do': '''from sqlalchemy import Column, Integer, String, DateTime, Text
from config.database import Base


class {class_name}({base_class}):
    """
    {table_comment}表
    """
    __tablename__ = '{table_name}'

{columns}
''',
        'vo': '''from datetime import datetime
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel
from pydantic_validation_decorator import NotBlank
from typing import Optional
from module_admin.annotation.pydantic_annotation import as_query


class {class_name}Model:
    """
    {table_comment} Pydantic模型
    """
    model_config = ConfigDict(alias_generator=to_camel, from_attributes=True, populate_by_name=True)

{fields}


class {class_name}PageQueryModel({class_name}Model):
    """
    {table_comment}分页查询模型
    """
    page_num: int = Field(default=1, description='当前页码')
    page_size: int = Field(default=10, description='每页记录数')
    begin_time: Optional[str] = Field(default=None, description='开始时间')
    end_time: Optional[str] = Field(default=None, description='结束时间')


class Delete{class_name}Model:
    """
    删除{table_comment}模型
    """
    model_config = ConfigDict(alias_generator=to_camel)

    {pk_field}_ids: str = Field(description='{table_comment}ID')
''',
        'dao': '''from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from module_{module}.entity.do.{business}_do import {class_name}
from module_{module}.entity.vo.{business}_vo import {class_name}Model, {class_name}PageQueryModel
from utils.page_util import PageUtil


class {class_name}Dao:
    """
    {table_comment}数据访问层
    """

    @classmethod
    async def get_{business}_list(cls, db: AsyncSession, query: {class_name}PageQueryModel, is_page: bool = False):
        """
        获取{table_comment}列表
        """
        query_obj = select({class_name}).order_by(desc({class_name}.{pk_field}))
        
        # 添加查询条件
{query_conditions}
        
        if is_page:
            return await PageUtil.paginate(db, query_obj, query.page_num, query.page_size)
        else:
            result = await db.execute(query_obj)
            return result.scalars().all()

    @classmethod
    async def get_{business}_by_id(cls, db: AsyncSession, {pk_field}: int):
        """
        根据ID获取{table_comment}
        """
        result = await db.execute(
            select({class_name}).where({class_name}.{pk_field} == {pk_field})
        )
        return result.scalars().first()

    @classmethod
    async def add_{business}(cls, db: AsyncSession, obj: {class_name}Model):
        """
        新增{table_comment}
        """
        db_obj = {class_name}(**obj.model_dump(exclude_unset=True))
        db.add(db_obj)
        await db.flush()
        return db_obj

    @classmethod
    async def update_{business}(cls, db: AsyncSession, obj: dict):
        """
        更新{table_comment}
        """
        await db.execute(
            update({class_name})
            .where({class_name}.{pk_field} == obj.get('{pk_field}'))
            .values(**obj)
        )

    @classmethod
    async def delete_{business}(cls, db: AsyncSession, {pk_field}_list: list):
        """
        删除{table_comment}
        """
        await db.execute(
            delete({class_name}).where({class_name}.{pk_field}.in_({pk_field}_list))
        )
''',
        'service': '''from sqlalchemy.ext.asyncio import AsyncSession
from module_admin.entity.vo.common_vo import CrudResponseModel
from module_{module}.dao.{business}_dao import {class_name}Dao
from module_{module}.entity.vo.{business}_vo import {class_name}Model, {class_name}PageQueryModel, Delete{class_name}Model
from exceptions.exception import ServiceException


class {class_name}Service:
    """
    {table_comment}服务层
    """

    @classmethod
    async def get_{business}_list_services(cls, query_db: AsyncSession, query: {class_name}PageQueryModel, is_page: bool = False):
        """
        获取{table_comment}列表
        """
        return await {class_name}Dao.get_{business}_list(query_db, query, is_page)

    @classmethod
    async def get_{business}_by_id_services(cls, query_db: AsyncSession, {pk_field}: int):
        """
        根据ID获取{table_comment}详情
        """
        return await {class_name}Dao.get_{business}_by_id(query_db, {pk_field})

    @classmethod
    async def add_{business}_services(cls, query_db: AsyncSession, obj: {class_name}Model):
        """
        新增{table_comment}
        """
        try:
            await {class_name}Dao.add_{business}(query_db, obj)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='新增成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'新增失败: {{str(e)}}')

    @classmethod
    async def update_{business}_services(cls, query_db: AsyncSession, obj: {class_name}Model):
        """
        更新{table_comment}
        """
        info = await cls.get_{business}_by_id_services(query_db, obj.{pk_field})
        if not info:
            raise ServiceException(message='{table_comment}不存在')
        try:
            await {class_name}Dao.update_{business}(query_db, obj.model_dump(exclude_unset=True))
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='更新成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'更新失败: {{str(e)}}')

    @classmethod
    async def delete_{business}_services(cls, query_db: AsyncSession, obj: Delete{class_name}Model):
        """
        删除{table_comment}
        """
        try:
            {pk_field}_list = [int(i) for i in obj.{pk_field}_ids.split(',')]
            await {class_name}Dao.delete_{business}(query_db, {pk_field}_list)
            await query_db.commit()
            return CrudResponseModel(is_success=True, message='删除成功')
        except Exception as e:
            await query_db.rollback()
            raise ServiceException(message=f'删除失败: {{str(e)}}')
''',
        'controller': '''from datetime import datetime
from fastapi import APIRouter, Depends, Request
from pydantic_validation_decorator import ValidateFields
from sqlalchemy.ext.asyncio import AsyncSession
from config.enums import BusinessType
from config.get_db import get_db
from module_admin.annotation.log_annotation import Log
from module_admin.aspect.interface_auth import CheckUserInterfaceAuth
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_admin.service.login_service import LoginService
from module_{module}.service.{business}_service import {class_name}Service
from module_{module}.entity.vo.{business}_vo import {class_name}Model, {class_name}PageQueryModel, Delete{class_name}Model
from utils.log_util import logger
from utils.page_util import PageResponseModel
from utils.response_util import ResponseUtil


{router_name}Controller = APIRouter(prefix='/{module}/{business}', dependencies=[Depends(LoginService.get_current_user)])


@{router_name}Controller.get('/list', response_model=PageResponseModel, dependencies=[Depends(CheckUserInterfaceAuth('{module}:{business}:list'))])
async def get_{business}_list(
    request: Request,
    query: {class_name}PageQueryModel = Depends({class_name}PageQueryModel.as_query),
    query_db: AsyncSession = Depends(get_db),
):
    """获取{table_comment}列表"""
    result = await {class_name}Service.get_{business}_list_services(query_db, query, is_page=True)
    return ResponseUtil.success(model_content=result)


@{router_name}Controller.post('', dependencies=[Depends(CheckUserInterfaceAuth('{module}:{business}:add'))])
@Log(title='{table_comment}', business_type=BusinessType.INSERT)
async def add_{business}(
    request: Request,
    obj: {class_name}Model,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """新增{table_comment}"""
    obj.create_by = current_user.user.user_name
    obj.create_time = datetime.now()
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await {class_name}Service.add_{business}_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@{router_name}Controller.put('', dependencies=[Depends(CheckUserInterfaceAuth('{module}:{business}:edit'))])
@Log(title='{table_comment}', business_type=BusinessType.UPDATE)
async def update_{business}(
    request: Request,
    obj: {class_name}Model,
    query_db: AsyncSession = Depends(get_db),
    current_user: CurrentUserModel = Depends(LoginService.get_current_user),
):
    """更新{table_comment}"""
    obj.update_by = current_user.user.user_name
    obj.update_time = datetime.now()
    result = await {class_name}Service.update_{business}_services(query_db, obj)
    return ResponseUtil.success(msg=result.message)


@{router_name}Controller.delete('/{{ids}}', dependencies=[Depends(CheckUserInterfaceAuth('{module}:{business}:remove'))])
@Log(title='{table_comment}', business_type=BusinessType.DELETE)
async def delete_{business}(request: Request, ids: str, query_db: AsyncSession = Depends(get_db)):
    """删除{table_comment}"""
    result = await {class_name}Service.delete_{business}_services(query_db, Delete{class_name}Model({pk_field}Ids=ids))
    return ResponseUtil.success(msg=result.message)


@{router_name}Controller.get('/{{{pk_field}}}', dependencies=[Depends(CheckUserInterfaceAuth('{module}:{business}:query'))])
async def get_{business}_by_id(request: Request, {pk_field}: int, query_db: AsyncSession = Depends(get_db)):
    """获取{table_comment}详情"""
    result = await {class_name}Service.get_{business}_by_id_services(query_db, {pk_field})
    return ResponseUtil.success(data=result)
''',
        'api_js': '''import request from '@/utils/request'

// 查询{table_comment}列表
export function list{class_name}(query) {{
  return request({{
    url: '/{module}/{business}/list',
    method: 'get',
    params: query
  }})
}}

// 查询{table_comment}详情
export function get{class_name}({pk_field}) {{
  return request({{
    url: '/{module}/{business}/' + {pk_field},
    method: 'get'
  }})
}}

// 新增{table_comment}
export function add{class_name}(data) {{
  return request({{
    url: '/{module}/{business}',
    method: 'post',
    data: data
  }})
}}

// 修改{table_comment}
export function update{class_name}(data) {{
  return request({{
    url: '/{module}/{business}',
    method: 'put',
    data: data
  }})
}}

// 删除{table_comment}
export function del{class_name}({pk_field}) {{
  return request({{
    url: '/{module}/{business}/' + {pk_field},
    method: 'delete'
  }})
}}
''',
        'menu_sql': '''-- {table_comment}菜单
INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES ('{table_comment}', {parent_id}, 1, '{business}', '{module}/{business}/index', 1, 0, 'C', '0', '0', '{module}:{business}:list', '#', 'admin', NOW(), '', NULL, '{table_comment}菜单');

-- 按钮权限
SET @parentId = LAST_INSERT_ID();

INSERT INTO sys_menu (menu_name, parent_id, order_num, path, component, is_frame, is_cache, menu_type, visible, status, perms, icon, create_by, create_time, update_by, update_time, remark)
VALUES 
('{table_comment}查询', @parentId, 1, '', '', 1, 0, 'F', '0', '0', '{module}:{business}:query', '#', 'admin', NOW(), '', NULL, ''),
('{table_comment}新增', @parentId, 2, '', '', 1, 0, 'F', '0', '0', '{module}:{business}:add', '#', 'admin', NOW(), '', NULL, ''),
('{table_comment}修改', @parentId, 3, '', '', 1, 0, 'F', '0', '0', '{module}:{business}:edit', '#', 'admin', NOW(), '', NULL, ''),
('{table_comment}删除', @parentId, 4, '', '', 1, 0, 'F', '0', '0', '{module}:{business}:remove', '#', 'admin', NOW(), '', NULL, ''),
('{table_comment}导出', @parentId, 5, '', '', 1, 0, 'F', '0', '0', '{module}:{business}:export', '#', 'admin', NOW(), '', NULL, '');
'''
    }
    
    # 类型映射
    SQL_TYPE_MAP = {
        'int': ('Integer', 'int', 'Optional[int]'),
        'integer': ('Integer', 'int', 'Optional[int]'),
        'bigint': ('BigInteger', 'int', 'Optional[int]'),
        'smallint': ('SmallInteger', 'int', 'Optional[int]'),
        'tinyint': ('SmallInteger', 'int', 'Optional[int]'),
        'varchar': ('String', 'str', 'Optional[str]'),
        'char': ('String', 'str', 'Optional[str]'),
        'text': ('Text', 'str', 'Optional[str]'),
        'longtext': ('Text', 'str', 'Optional[str]'),
        'datetime': ('DateTime', 'datetime', 'Optional[datetime]'),
        'timestamp': ('DateTime', 'datetime', 'Optional[datetime]'),
        'date': ('Date', 'date', 'Optional[date]'),
        'decimal': ('Numeric', 'float', 'Optional[float]'),
        'float': ('Float', 'float', 'Optional[float]'),
        'double': ('Float', 'float', 'Optional[float]'),
        'boolean': ('Boolean', 'bool', 'Optional[bool]'),
        'bool': ('Boolean', 'bool', 'Optional[bool]'),
    }
    
    def __init__(self, table_name: str, module: str, business: str, 
                 output_dir: str = '/tmp/ruoyi-gen', parent_menu_id: int = 0):
        self.table_name = table_name
        self.module = module
        self.business = business
        self.output_dir = output_dir
        self.parent_menu_id = parent_menu_id
        self.columns: List[Dict[str, Any]] = []
        self.pk_field = 'id'
        self.table_comment = business
        
    def set_columns(self, columns: List[Dict[str, Any]]):
        """设置列信息"""
        self.columns = columns
        # 查找主键
        for col in columns:
            if col.get('is_pk'):
                self.pk_field = col['name']
                break
                
    def set_table_comment(self, comment: str):
        """设置表注释"""
        self.table_comment = comment or self.business
        
    def _to_camel_case(self, name: str) -> str:
        """转换为驼峰命名"""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    def _to_pascal_case(self, name: str) -> str:
        """转换为帕斯卡命名"""
        return ''.join(x.title() for x in name.split('_'))
    
    def _get_class_name(self) -> str:
        """获取类名"""
        # 去掉表前缀
        name = self.table_name
        if name.startswith('sys_'):
            name = name[4:]
        return self._to_pascal_case(name)
    
    def _get_sqlalchemy_type(self, sql_type: str) -> str:
        """获取 SQLAlchemy 类型"""
        sql_type = sql_type.lower().split('(')[0]
        return self.SQL_TYPE_MAP.get(sql_type, ('String', 'str', 'Optional[str]'))[0]
    
    def _get_python_type(self, sql_type: str, nullable: bool = True) -> str:
        """获取 Python 类型"""
        sql_type = sql_type.lower().split('(')[0]
        type_info = self.SQL_TYPE_MAP.get(sql_type, ('String', 'str', 'Optional[str]'))
        return type_info[2] if nullable else type_info[1]
    
    def _generate_do_columns(self) -> str:
        """生成 DO 列定义"""
        lines = []
        for col in self.columns:
            sa_type = self._get_sqlalchemy_type(col['type'])
            
            # 处理字符串长度
            if sa_type == 'String' and '(' in col['type']:
                length = col['type'].split('(')[1].rstrip(')')
                sa_type = f'String({length})'
            
            # 构建列定义
            parts = [f"Column({sa_type}"]
            if col.get('is_pk'):
                parts.append("primary_key=True")
                if 'int' in col['type'].lower():
                    parts.append("autoincrement=True")
            if not col.get('nullable', True):
                parts.append("nullable=False")
            if col.get('comment'):
                parts.append(f"comment='{col['comment']}'")
            
            line = f"    {col['name']} = {', '.join(parts)})"
            lines.append(line)
        return '\n'.join(lines)
    
    def _generate_vo_fields(self) -> str:
        """生成 VO 字段定义"""
        lines = []
        for col in self.columns:
            py_type = self._get_python_type(col['type'])
            camel_name = self._to_camel_case(col['name'])
            comment = col.get('comment', col['name'])
            
            if col.get('is_pk'):
                line = f"    {col['name']}: {py_type} = Field(default=None, description='{comment}')"
            else:
                line = f"    {col['name']}: {py_type} = Field(default=None, alias='{camel_name}', description='{comment}')"
            lines.append(line)
        return '\n'.join(lines)
    
    def _generate_query_conditions(self) -> str:
        """生成查询条件"""
        lines = []
        for col in self.columns:
            if col.get('is_pk'):
                continue
            if col['name'] in ['create_time', 'update_time', 'create_by', 'update_by']:
                continue
            py_type = self._get_python_type(col['type'])
            if 'str' in py_type:
                lines.append(f"        if query.{col['name']}:")
                lines.append(f"            query_obj = query_obj.where({self._get_class_name()}.{col['name']}.contains(query.{col['name']}))")
            elif 'int' in py_type:
                lines.append(f"        if query.{col['name']} is not None:")
                lines.append(f"            query_obj = query_obj.where({self._get_class_name()}.{col['name']} == query.{col['name']})")
        return '\n'.join(lines) if lines else '        pass'
    
    def generate(self) -> Dict[str, str]:
        """生成所有代码"""
        class_name = self._get_class_name()
        router_name = self._to_camel_case(self.business)
        
        context = {
            'class_name': class_name,
            'table_name': self.table_name,
            'table_comment': self.table_comment,
            'module': self.module,
            'business': self.business,
            'pk_field': self.pk_field,
            'router_name': router_name,
            'base_class': 'Base',
            'columns': self._generate_do_columns(),
            'fields': self._generate_vo_fields(),
            'query_conditions': self._generate_query_conditions(),
            'parent_id': self.parent_menu_id,
        }
        
        result = {}
        for name, template in self.TEMPLATES.items():
            result[name] = template.format(**context)
        
        return result
    
    def save(self) -> Dict[str, str]:
        """保存生成的代码到文件"""
        codes = self.generate()
        class_name = self._get_class_name()
        
        # 定义文件路径
        paths = {
            'do': f'backend/module_{self.module}/entity/do/{self.business}_do.py',
            'vo': f'backend/module_{self.module}/entity/vo/{self.business}_vo.py',
            'dao': f'backend/module_{self.module}/dao/{self.business}_dao.py',
            'service': f'backend/module_{self.module}/service/{self.business}_service.py',
            'controller': f'backend/module_{self.module}/controller/{self.business}_controller.py',
            'api_js': f'frontend/src/api/{self.module}/{self.business}.js',
            'menu_sql': f'backend/sql/{self.business}_menu.sql',
        }
        
        saved_files = {}
        for name, rel_path in paths.items():
            full_path = os.path.join(self.output_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(codes[name])
            saved_files[name] = full_path
            
        return saved_files


async def get_table_columns_from_db(table_name: str) -> List[Dict[str, Any]]:
    """从数据库获取表结构"""
    from config.get_db import get_db
    from sqlalchemy import text
    
    async for db in get_db():
        # 获取列信息
        result = await db.execute(text(f"""
            SELECT 
                COLUMN_NAME as name,
                DATA_TYPE as type,
                COLUMN_TYPE as full_type,
                IS_NULLABLE as nullable,
                COLUMN_KEY as key_type,
                COLUMN_COMMENT as comment
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table_name
            ORDER BY ORDINAL_POSITION
        """), {'table_name': table_name})
        
        columns = []
        for row in result.fetchall():
            columns.append({
                'name': row[0],
                'type': row[2] or row[1],  # 使用完整类型
                'nullable': row[3] == 'YES',
                'is_pk': row[4] == 'PRI',
                'comment': row[5] or row[0],
            })
        
        # 获取表注释
        table_result = await db.execute(text(f"""
            SELECT TABLE_COMMENT 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = :table_name
        """), {'table_name': table_name})
        table_row = table_result.fetchone()
        table_comment = table_row[0] if table_row else None
        
        return columns, table_comment


def parse_create_sql(sql: str) -> tuple:
    """解析建表 SQL"""
    columns = []
    table_name = None
    table_comment = None
    
    # 提取表名
    match = re.search(r'CREATE\s+TABLE\s+[`"]?(\w+)[`"]?', sql, re.IGNORECASE)
    if match:
        table_name = match.group(1)
    
    # 提取表注释
    comment_match = re.search(r"COMMENT\s*=?\s*['\"]([^'\"]+)['\"]", sql, re.IGNORECASE)
    if comment_match:
        table_comment = comment_match.group(1)
    
    # 提取列定义
    columns_match = re.search(r'\((.*)\)', sql, re.DOTALL)
    if columns_match:
        columns_str = columns_match.group(1)
        
        # 分割列定义
        for line in columns_str.split(','):
            line = line.strip()
            if not line:
                continue
            
            # 跳过约束定义
            if any(kw in line.upper() for kw in ['PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'INDEX', 'KEY ']):
                # 但要检查是否是主键定义
                pk_match = re.search(r'PRIMARY\s+KEY\s*\([`"]?(\w+)[`"]?\)', line, re.IGNORECASE)
                if pk_match:
                    pk_col = pk_match.group(1)
                    for col in columns:
                        if col['name'] == pk_col:
                            col['is_pk'] = True
                continue
            
            # 解析列
            col_match = re.match(r'[`"]?(\w+)[`"]?\s+(\w+(?:\([^)]+\))?)', line)
            if col_match:
                col_name = col_match.group(1)
                col_type = col_match.group(2)
                
                # 检查是否为主键
                is_pk = 'PRIMARY KEY' in line.upper() or 'AUTO_INCREMENT' in line.upper()
                
                # 检查是否可空
                nullable = 'NOT NULL' not in line.upper()
                
                # 提取注释
                col_comment_match = re.search(r"COMMENT\s+['\"]([^'\"]+)['\"]", line, re.IGNORECASE)
                comment = col_comment_match.group(1) if col_comment_match else col_name
                
                columns.append({
                    'name': col_name,
                    'type': col_type,
                    'nullable': nullable,
                    'is_pk': is_pk,
                    'comment': comment,
                })
    
    return table_name, columns, table_comment


def install_to_project(output_dir: str, project_root: str):
    """将生成的代码复制到项目目录"""
    backend_src = os.path.join(output_dir, 'backend')
    frontend_src = os.path.join(output_dir, 'frontend')
    
    backend_dst = os.path.join(project_root)
    frontend_dst = os.path.join(project_root, '..', 'ruoyi-fastapi-frontend')
    
    copied = []
    
    # 复制后端文件
    if os.path.exists(backend_src):
        for root, dirs, files in os.walk(backend_src):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, backend_src)
                dst_path = os.path.join(backend_dst, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                copied.append(dst_path)
    
    # 复制前端文件
    if os.path.exists(frontend_src):
        for root, dirs, files in os.walk(frontend_src):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, frontend_src)
                dst_path = os.path.join(frontend_dst, rel_path)
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.copy2(src_path, dst_path)
                copied.append(dst_path)
    
    return copied


async def main():
    parser = argparse.ArgumentParser(description='RuoYi 代码生成器')
    parser.add_argument('--table', help='数据库表名')
    parser.add_argument('--sql', help='建表 SQL 语句')
    parser.add_argument('--module', required=True, help='模块名称')
    parser.add_argument('--business', required=True, help='业务名称')
    parser.add_argument('--output', default='/tmp/ruoyi-gen', help='输出目录')
    parser.add_argument('--auto-install', action='store_true', help='自动复制到项目目录')
    parser.add_argument('--menu-parent', type=int, default=0, help='父菜单ID')
    parser.add_argument('--env', default='dev', help='环境')
    
    args = parser.parse_args()
    
    if not args.table and not args.sql:
        parser.error('必须指定 --table 或 --sql')
    
    os.environ['APP_ENV'] = args.env
    
    # 获取表结构
    if args.sql:
        table_name, columns, table_comment = parse_create_sql(args.sql)
        if not table_name:
            table_name = f"sys_{args.business}"
    else:
        table_name = args.table
        columns, table_comment = await get_table_columns_from_db(table_name)
    
    if not columns:
        print(f"错误: 无法获取表 {table_name} 的列信息")
        sys.exit(1)
    
    # 生成代码
    generator = CodeGenerator(
        table_name=table_name,
        module=args.module,
        business=args.business,
        output_dir=args.output,
        parent_menu_id=args.menu_parent,
    )
    generator.set_columns(columns)
    generator.set_table_comment(table_comment or args.business)
    
    saved_files = generator.save()
    
    print(f"\n✅ 代码生成成功!")
    print(f"\n📁 输出目录: {args.output}")
    print("\n📄 生成的文件:")
    for name, path in saved_files.items():
        print(f"   - {name}: {path}")
    
    # 自动安装
    if args.auto_install:
        print("\n📦 正在复制到项目目录...")
        copied = install_to_project(args.output, str(PROJECT_ROOT))
        print(f"   已复制 {len(copied)} 个文件")
        for f in copied:
            print(f"   - {f}")
    
    print("\n📝 后续步骤:")
    print(f"   1. 在 server.py 中注册路由:")
    print(f"      from module_{args.module}.controller.{args.business}_controller import {args.business}Controller")
    print(f"      app.include_router({args.business}Controller)")
    print(f"   2. 执行菜单 SQL: {saved_files['menu_sql']}")
    print(f"   3. 创建前端页面 Vue 文件")


if __name__ == '__main__':
    asyncio.run(main())
