"""
代码生成 API - 简化调用接口

使用示例:

```python
from scripts.gen_api import generate_crud

# 方式1: 从 SQL 生成
generate_crud(
    sql='''
    CREATE TABLE sys_product (
        product_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '产品ID',
        product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
        price DECIMAL(10,2) COMMENT '价格',
        status CHAR(1) DEFAULT '0' COMMENT '状态',
        create_by VARCHAR(64) COMMENT '创建者',
        create_time DATETIME COMMENT '创建时间',
        update_by VARCHAR(64) COMMENT '更新者',
        update_time DATETIME COMMENT '更新时间',
        remark VARCHAR(500) COMMENT '备注'
    ) COMMENT='产品信息表';
    ''',
    module='system',
    business='product'
)

# 方式2: 从已有表生成
generate_crud(
    table='sys_user',
    module='system', 
    business='user'
)

# 方式3: 手动指定列
generate_crud(
    table='sys_demo',
    module='system',
    business='demo',
    columns=[
        {'name': 'demo_id', 'type': 'int', 'is_pk': True, 'comment': '演示ID'},
        {'name': 'demo_name', 'type': 'varchar(100)', 'comment': '演示名称'},
        {'name': 'status', 'type': 'char(1)', 'comment': '状态'},
    ],
    table_comment='演示表'
)
```
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# 添加项目路径
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.code_generator import CodeGenerator, parse_create_sql


def generate_crud(
    table: str = None,
    sql: str = None,
    module: str = 'admin',
    business: str = None,
    columns: List[Dict[str, Any]] = None,
    table_comment: str = None,
    output_dir: str = '/tmp/ruoyi-gen',
    parent_menu_id: int = 0,
    auto_install: bool = False,
) -> Dict[str, str]:
    """
    生成 CRUD 代码
    
    Args:
        table: 表名 (如果有 sql 参数则可选)
        sql: 建表 SQL 语句
        module: 模块名称 (如 system, admin)
        business: 业务名称 (如 user, product)
        columns: 列定义列表 (可选，如果提供 sql 则自动解析)
        table_comment: 表注释
        output_dir: 输出目录
        parent_menu_id: 父菜单ID
        auto_install: 是否自动复制到项目目录
        
    Returns:
        生成的文件路径字典
    """
    # 从 SQL 解析
    if sql:
        parsed_table, parsed_columns, parsed_comment = parse_create_sql(sql)
        table = table or parsed_table
        columns = columns or parsed_columns
        table_comment = table_comment or parsed_comment
    
    if not table:
        raise ValueError("必须提供 table 或 sql 参数")
    
    if not business:
        # 从表名推断业务名
        business = table.replace('sys_', '').replace('t_', '')
    
    if not columns:
        raise ValueError("必须提供 columns 或 sql 参数")
    
    # 创建生成器
    generator = CodeGenerator(
        table_name=table,
        module=module,
        business=business,
        output_dir=output_dir,
        parent_menu_id=parent_menu_id,
    )
    generator.set_columns(columns)
    generator.set_table_comment(table_comment or business)
    
    # 生成并保存
    saved_files = generator.save()
    
    # 打印结果
    print(f"\n✅ 代码生成成功!")
    print(f"\n📁 输出目录: {output_dir}")
    print("\n📄 生成的文件:")
    for name, path in saved_files.items():
        print(f"   - {name}: {path}")
    
    # 自动安装
    if auto_install:
        from scripts.code_generator import install_to_project
        print("\n📦 正在复制到项目目录...")
        copied = install_to_project(output_dir, str(PROJECT_ROOT))
        print(f"   已复制 {len(copied)} 个文件")
    
    # 打印后续步骤
    print("\n" + "="*60)
    print("📝 后续步骤:")
    print("="*60)
    print(f"""
1. 在 server.py 中注册路由:
   
   from module_{module}.controller.{business}_controller import {business}Controller
   app.include_router({business}Controller)

2. 执行菜单 SQL (可选):
   
   执行文件: {saved_files['menu_sql']}

3. 创建前端 Vue 页面:
   
   路径: ruoyi-fastapi-frontend/src/views/{module}/{business}/index.vue
   
4. 在前端路由中添加菜单 (或通过系统菜单管理添加)
""")
    
    return saved_files


def quick_generate(
    name: str,
    fields: Dict[str, str],
    module: str = 'admin',
    pk: str = None,
) -> Dict[str, str]:
    """
    快速生成 - 更简洁的接口
    
    Args:
        name: 业务名称 (如 product, order)
        fields: 字段字典 {字段名: 字段类型/注释}
        module: 模块名称
        pk: 主键字段名 (默认为 {name}_id)
        
    Returns:
        生成的文件路径字典
        
    Example:
        quick_generate('product', {
            'name': 'varchar(100) 产品名称',
            'price': 'decimal(10,2) 价格',
            'status': 'char(1) 状态',
        })
    """
    pk = pk or f"{name}_id"
    
    columns = [
        {'name': pk, 'type': 'int', 'is_pk': True, 'comment': f'{name}ID'}
    ]
    
    for field_name, field_def in fields.items():
        parts = field_def.split(' ', 1)
        field_type = parts[0]
        comment = parts[1] if len(parts) > 1 else field_name
        columns.append({
            'name': field_name,
            'type': field_type,
            'comment': comment,
        })
    
    # 添加通用字段
    columns.extend([
        {'name': 'create_by', 'type': 'varchar(64)', 'comment': '创建者'},
        {'name': 'create_time', 'type': 'datetime', 'comment': '创建时间'},
        {'name': 'update_by', 'type': 'varchar(64)', 'comment': '更新者'},
        {'name': 'update_time', 'type': 'datetime', 'comment': '更新时间'},
        {'name': 'remark', 'type': 'varchar(500)', 'comment': '备注'},
    ])
    
    return generate_crud(
        table=f"sys_{name}",
        module=module,
        business=name,
        columns=columns,
        table_comment=name,
    )


# 便捷别名
gen = generate_crud
quick = quick_generate


if __name__ == '__main__':
    # 示例: 生成产品管理模块
    generate_crud(
        sql='''
        CREATE TABLE sys_product (
            product_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '产品ID',
            product_name VARCHAR(100) NOT NULL COMMENT '产品名称',
            category VARCHAR(50) COMMENT '分类',
            price DECIMAL(10,2) COMMENT '价格',
            stock INT DEFAULT 0 COMMENT '库存',
            status CHAR(1) DEFAULT '0' COMMENT '状态(0正常 1停用)',
            create_by VARCHAR(64) COMMENT '创建者',
            create_time DATETIME COMMENT '创建时间',
            update_by VARCHAR(64) COMMENT '更新者',
            update_time DATETIME COMMENT '更新时间',
            remark VARCHAR(500) COMMENT '备注'
        ) COMMENT='产品信息表';
        ''',
        module='system',
        business='product',
    )
