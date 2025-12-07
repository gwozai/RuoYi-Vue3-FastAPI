#!/usr/bin/env python3
"""
完整代码生成器 - 使用系统内置模板

此工具使用若依系统内置的 Jinja2 模板生成完整的前后端代码，包括：
- 后端: DO、VO、DAO、Service、Controller
- 前端: Vue 页面、API JS
- SQL: 菜单 SQL

使用方法:
    # 从数据库表生成（需要先在数据库中创建表）
    python scripts/gen_full.py --table sys_student
    
    # 从 SQL 创建表并生成代码
    python scripts/gen_full.py --sql "CREATE TABLE sys_demo (...)"
    
    # 指定输出目录
    python scripts/gen_full.py --table sys_student --output /tmp/gen
    
    # 生成并自动安装到项目
    python scripts/gen_full.py --table sys_student --auto-install
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('APP_ENV', 'dev')


async def generate_from_table(table_name: str, output_dir: str = '/tmp/ruoyi-gen', auto_install: bool = False):
    """
    从数据库表生成代码
    
    Args:
        table_name: 表名
        output_dir: 输出目录
        auto_install: 是否自动安装到项目
    """
    from config.get_db import get_db
    from module_generator.service.gen_service import GenTableService
    from module_admin.entity.vo.user_vo import CurrentUserModel, UserInfoModel
    
    # 创建模拟用户
    mock_user = CurrentUserModel(
        permissions=['*:*:*'],
        roles=['admin'],
        user=UserInfoModel(user_id=1, user_name='admin', nick_name='管理员'),
    )
    
    async for db in get_db():
        try:
            # 1. 检查表是否已导入
            from module_generator.dao.gen_dao import GenTableDao
            existing = await GenTableDao.get_gen_table_by_name(db, table_name)
            
            if not existing:
                # 2. 导入表结构
                print(f"📥 正在导入表 {table_name}...")
                gen_table_list = await GenTableService.get_gen_db_table_list_by_name_services(db, [table_name])
                if not gen_table_list:
                    print(f"❌ 表 {table_name} 不存在于数据库中")
                    return
                await GenTableService.import_gen_table_services(db, gen_table_list, mock_user)
                print(f"✅ 表 {table_name} 导入成功")
            else:
                print(f"📋 表 {table_name} 已存在于代码生成器中")
            
            # 3. 获取表信息并设置默认配置
            from utils.common_util import CamelCaseUtil
            from module_generator.entity.vo.gen_vo import GenTableModel
            import json
            
            gen_table_data = await GenTableDao.get_gen_table_by_name(db, table_name)
            gen_table = GenTableModel(**CamelCaseUtil.transform_result(gen_table_data))
            
            # 检查是否已配置
            if not gen_table.options:
                print(f"⚙️  正在配置生成选项...")
                # 设置默认配置
                default_options = {
                    'parentMenuId': '0',
                    'treeName': '',
                    'treeParentCode': '',
                    'treeCode': ''
                }
                
                # 使用 SQL 更新
                from sqlalchemy import update
                from module_generator.entity.do.gen_do import GenTable
                await db.execute(
                    update(GenTable)
                    .where(GenTable.table_id == gen_table.table_id)
                    .values(
                        options=json.dumps(default_options),
                        tpl_category='crud',
                        tpl_web_type='element-plus',
                        gen_type='0',
                        gen_path='/',
                    )
                )
                await db.commit()
                
                # 重新获取更新后的数据
                gen_table_data = await GenTableDao.get_gen_table_by_name(db, table_name)
                gen_table = GenTableModel(**CamelCaseUtil.transform_result(gen_table_data))
                print(f"✅ 配置完成")
            
            # 4. 生成代码
            print(f"\n🔨 正在生成代码...")
            zip_data = await GenTableService.batch_gen_code_services(db, [table_name])
            
            # 5. 保存到输出目录
            import zipfile
            import io
            
            os.makedirs(output_dir, exist_ok=True)
            zip_path = os.path.join(output_dir, f'{table_name}_code.zip')
            
            with open(zip_path, 'wb') as f:
                f.write(zip_data)
            
            # 6. 解压
            with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_file:
                zip_file.extractall(output_dir)
            
            print(f"\n✅ 代码生成成功!")
            print(f"\n📁 输出目录: {output_dir}")
            print("\n📄 生成的文件:")
            
            with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_file:
                for name in zip_file.namelist():
                    print(f"   - {name}")
            
            # 7. 自动安装
            if auto_install:
                print(f"\n📦 正在安装到项目目录...")
                install_generated_code(output_dir, str(PROJECT_ROOT))
            
            # 8. 打印后续步骤
            print(f"\n" + "="*60)
            print("📝 后续步骤:")
            print("="*60)
            print(f"""
1. 在 server.py 中注册路由:
   
   from module_admin.controller.{gen_table.business_name}_controller import {gen_table.business_name}Controller
   app.include_router({gen_table.business_name}Controller)

2. 执行菜单 SQL:
   
   执行文件: {output_dir}/backend/sql/{gen_table.business_name}_menu.sql

3. 前端页面已生成:
   
   路径: {output_dir}/frontend/views/{gen_table.module_name}/{gen_table.business_name}/index.vue
   API:  {output_dir}/frontend/api/{gen_table.module_name}/{gen_table.business_name}.js
""")
            
        except Exception as e:
            print(f"❌ 生成失败: {e}")
            import traceback
            traceback.print_exc()
            raise


async def generate_from_sql(sql: str, output_dir: str = '/tmp/ruoyi-gen', auto_install: bool = False):
    """
    从 SQL 创建表并生成代码
    
    Args:
        sql: 建表 SQL
        output_dir: 输出目录
        auto_install: 是否自动安装
    """
    from config.get_db import get_db
    from module_generator.service.gen_service import GenTableService
    from module_admin.entity.vo.user_vo import CurrentUserModel, UserInfoModel
    
    # 创建模拟用户
    mock_user = CurrentUserModel(
        permissions=['*:*:*'],
        roles=['admin'],
        user=UserInfoModel(user_id=1, user_name='admin', nick_name='管理员'),
    )
    
    async for db in get_db():
        try:
            # 1. 创建表
            print(f"📥 正在创建表...")
            result = await GenTableService.create_table_services(db, sql, mock_user)
            print(f"✅ {result.message}")
            
            # 2. 从 SQL 中提取表名
            import re
            match = re.search(r'CREATE\s+TABLE\s+[`"]?(\w+)[`"]?', sql, re.IGNORECASE)
            if match:
                table_name = match.group(1)
                # 3. 生成代码
                await generate_from_table(table_name, output_dir, auto_install)
            else:
                print("❌ 无法从 SQL 中提取表名")
                
        except Exception as e:
            print(f"❌ 创建表失败: {e}")
            raise


def install_generated_code(output_dir: str, project_root: str):
    """将生成的代码安装到项目目录"""
    import shutil
    
    backend_src = os.path.join(output_dir, 'backend')
    frontend_src = os.path.join(output_dir, 'frontend')
    
    backend_dst = project_root
    frontend_dst = os.path.join(project_root, '..', 'ruoyi-fastapi-frontend', 'src')
    
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
                print(f"   ✅ {rel_path}")
    
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
                print(f"   ✅ {rel_path}")
    
    print(f"\n   共复制 {len(copied)} 个文件")
    return copied


async def main():
    parser = argparse.ArgumentParser(description='若依完整代码生成器（使用系统模板）')
    parser.add_argument('--table', help='数据库表名')
    parser.add_argument('--sql', help='建表 SQL 语句')
    parser.add_argument('--output', default='/tmp/ruoyi-gen', help='输出目录')
    parser.add_argument('--auto-install', action='store_true', help='自动安装到项目目录')
    
    args = parser.parse_args()
    
    if not args.table and not args.sql:
        parser.error('必须指定 --table 或 --sql')
    
    if args.sql:
        await generate_from_sql(args.sql, args.output, args.auto_install)
    else:
        await generate_from_table(args.table, args.output, args.auto_install)


if __name__ == '__main__':
    asyncio.run(main())
