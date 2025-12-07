# API 代码生成使用教程

本项目提供了一套完整的代码生成工具，可以从数据库表或 SQL 语句快速生成前后端 CRUD 代码。

---

## 功能特性

- **一键生成**：从 SQL 或表名自动生成完整的前后端代码
- **多种模板**：支持 DO、VO、DAO、Service、Controller、Vue 页面
- **菜单管理**：自动生成菜单 SQL 或直接写入数据库
- **灵活配置**：支持自定义模块、业务名、输出目录等

---

## 快速开始

### 方式一：Python API 调用

```python
from scripts.gen_api import generate_crud

# 从 SQL 生成代码
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
```

### 方式二：命令行调用

```bash
cd ruoyi-fastapi-backend

# 从 SQL 生成
python scripts/code_generator.py \
    --sql "CREATE TABLE sys_demo (demo_id INT PRIMARY KEY AUTO_INCREMENT, demo_name VARCHAR(100))" \
    --module system \
    --business demo

# 从数据库表生成
python scripts/code_generator.py \
    --table sys_user \
    --module system \
    --business user \
    --use-system-template
```

---

## API 函数详解

### generate_crud - 生成 CRUD 代码

```python
from scripts.gen_api import generate_crud

generate_crud(
    table='sys_product',           # 表名（可选，如果有 sql 则自动解析）
    sql='CREATE TABLE ...',        # 建表 SQL（可选）
    module='system',               # 模块名称
    business='product',            # 业务名称
    columns=[...],                 # 列定义（可选，如果有 sql 则自动解析）
    table_comment='产品信息',       # 表注释
    output_dir='/tmp/ruoyi-gen',   # 输出目录
    parent_menu_id=0,              # 父菜单ID
    auto_install=False,            # 是否自动复制到项目目录
)
```

**参数说明**：

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| table | str | 否 | 表名，如果提供 sql 则可选 |
| sql | str | 否 | 建表 SQL 语句 |
| module | str | 是 | 模块名称（如 system, admin） |
| business | str | 否 | 业务名称，默认从表名推断 |
| columns | list | 否 | 列定义列表 |
| table_comment | str | 否 | 表注释 |
| output_dir | str | 否 | 输出目录，默认 /tmp/ruoyi-gen |
| parent_menu_id | int | 否 | 父菜单ID |
| auto_install | bool | 否 | 是否自动复制到项目目录 |

### quick_generate - 快速生成

更简洁的接口，自动添加通用字段：

```python
from scripts.gen_api import quick_generate

quick_generate(
    name='product',
    fields={
        'name': 'varchar(100) 产品名称',
        'price': 'decimal(10,2) 价格',
        'status': 'char(1) 状态',
    },
    module='system'
)
```

自动添加的字段：
- `{name}_id` - 主键
- `create_by` - 创建者
- `create_time` - 创建时间
- `update_by` - 更新者
- `update_time` - 更新时间
- `remark` - 备注

---

## 菜单管理 API

### 创建完整模块菜单

```python
from scripts.menu_manager import create_module

create_module(
    module_name="产品管理",      # 目录名称
    module_path="product",       # 目录路径
    business_name="产品列表",    # 页面名称
    business_path="list",        # 页面路径
    component="product/list/index",  # Vue 组件路径
    icon="shopping"              # 图标
)
```

这会自动创建：
- 📁 目录菜单（产品管理）
- 📄 页面菜单（产品列表）
- 🔘 CRUD 按钮（查询、新增、修改、删除、导出）

### 单独添加菜单

```python
from scripts.menu_manager import add_directory, add_menu, add_button

# 添加目录
add_directory(name="产品管理", path="product", icon="shopping")

# 添加页面
add_menu(
    name="产品列表",
    path="list",
    component="product/list/index",
    perms="product:list:list",
    parent="产品管理"
)

# 添加按钮
add_button(name="新增", perms="product:list:add", parent="产品列表")
```

### 列出菜单

```python
from scripts.menu_manager import list_menus

# 列出所有菜单
menus = list_menus()

# 列出指定父菜单下的菜单
menus = list_menus(parent="系统管理")
```

### 删除菜单

```python
from scripts.menu_manager import delete_menu

delete_menu(name="测试菜单")
```

---

## 命令行工具

### 代码生成器

```bash
cd ruoyi-fastapi-backend

# 查看帮助
python scripts/code_generator.py --help

# 从 SQL 生成
python scripts/code_generator.py \
    --sql "CREATE TABLE sys_demo (id INT PRIMARY KEY, name VARCHAR(100))" \
    --module system \
    --business demo

# 从数据库表生成（使用系统模板）
python scripts/code_generator.py \
    --table sys_user \
    --module system \
    --business user \
    --use-system-template

# 指定输出目录
python scripts/code_generator.py \
    --table sys_example \
    --module system \
    --business example \
    --output /tmp/gen

# 生成并自动复制到项目
python scripts/code_generator.py \
    --table sys_example \
    --module system \
    --business example \
    --auto-install
```

### 菜单管理器

```bash
cd ruoyi-fastapi-backend

# 查看帮助
python scripts/menu_manager.py --help

# 添加目录
python scripts/menu_manager.py add-dir \
    --name "产品管理" \
    --path product \
    --icon shopping

# 添加页面菜单
python scripts/menu_manager.py add-menu \
    --name "产品列表" \
    --path list \
    --component "product/list/index" \
    --perms "product:list:list" \
    --parent "产品管理"

# 添加按钮
python scripts/menu_manager.py add-button \
    --name "新增" \
    --perms "product:list:add" \
    --parent "产品列表"

# 添加 CRUD 按钮
python scripts/menu_manager.py add-crud \
    --parent "产品列表" \
    --module product \
    --business list

# 创建完整模块
python scripts/menu_manager.py create-module \
    --module-name "产品管理" \
    --module-path product \
    --business-name "产品列表" \
    --business-path list \
    --component "product/list/index" \
    --icon shopping

# 列出菜单（树形）
python scripts/menu_manager.py list --tree

# 删除菜单
python scripts/menu_manager.py delete --name "测试菜单"

# 递归删除（包含子菜单）
python scripts/menu_manager.py delete --name "测试目录" --recursive

# 移动菜单
python scripts/menu_manager.py move --name "产品列表" --parent "系统管理"
```

---

## 生成的文件结构

执行代码生成后，会在输出目录生成以下文件：

```
/tmp/ruoyi-gen/
├── backend/
│   ├── entity/
│   │   ├── do/
│   │   │   └── product_do.py      # 数据库实体
│   │   └── vo/
│   │       └── product_vo.py      # Pydantic 模型
│   ├── dao/
│   │   └── product_dao.py         # 数据访问层
│   ├── service/
│   │   └── product_service.py     # 业务逻辑层
│   └── controller/
│       └── product_controller.py  # 控制器
├── frontend/
│   ├── api/
│   │   └── product.js             # 前端 API
│   └── views/
│       └── product/
│           └── index.vue          # Vue 页面
└── sql/
    └── menu.sql                   # 菜单 SQL
```

---

## 完整示例

### 示例1：创建产品管理模块

```python
# 1. 生成代码
from scripts.gen_api import generate_crud

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

# 2. 创建菜单
from scripts.menu_manager import create_module

create_module(
    module_name="产品管理",
    module_path="product",
    business_name="产品列表",
    business_path="list",
    component="system/product/index",
    icon="shopping"
)
```

### 示例2：快速生成订单模块

```python
from scripts.gen_api import quick_generate
from scripts.menu_manager import create_module

# 生成代码
quick_generate('order', {
    'order_no': 'varchar(50) 订单号',
    'user_id': 'int 用户ID',
    'amount': 'decimal(10,2) 订单金额',
    'status': 'char(1) 状态',
    'pay_time': 'datetime 支付时间',
})

# 创建菜单
create_module(
    module_name="订单管理",
    module_path="order",
    business_name="订单列表",
    business_path="list",
    component="admin/order/index",
    icon="shopping"
)
```

---

## 后续步骤

代码生成后，需要完成以下步骤：

### 1. 注册路由

在 `server.py` 中添加：

```python
from module_system.controller.product_controller import productController

app.include_router(productController)
```

### 2. 复制前端文件

将生成的前端文件复制到对应目录：

```bash
# API 文件
cp /tmp/ruoyi-gen/frontend/api/product.js \
   ruoyi-fastapi-frontend/src/api/system/

# Vue 页面
cp -r /tmp/ruoyi-gen/frontend/views/product \
   ruoyi-fastapi-frontend/src/views/system/
```

### 3. 执行数据库脚本

如果需要创建表：

```sql
-- 执行建表 SQL
CREATE TABLE sys_product (...);
```

### 4. 刷新菜单缓存

登录系统后，刷新页面或重新登录以加载新菜单。

---

## 常用图标

菜单管理支持以下常用图标：

| 图标名 | 说明 | 图标名 | 说明 |
|--------|------|--------|------|
| system | 系统 | monitor | 监控 |
| tool | 工具 | guide | 指南 |
| user | 用户 | peoples | 人员 |
| tree | 树形 | menu | 菜单 |
| message | 消息 | log | 日志 |
| dict | 字典 | edit | 编辑 |
| list | 列表 | chart | 图表 |
| form | 表单 | table | 表格 |
| code | 代码 | build | 构建 |
| server | 服务器 | job | 任务 |
| online | 在线 | redis | Redis |
| download | 下载 | upload | 上传 |
| star | 星标 | link | 链接 |
| shopping | 购物 | documentation | 文档 |

---

## 常见问题

### Q: 生成的代码报错 "模块未找到"

**A**: 确保在 `server.py` 中正确注册了路由，并且模块路径正确。

### Q: 菜单不显示

**A**: 检查以下几点：
1. 菜单是否正确插入数据库
2. 用户是否有该菜单的权限
3. 尝试重新登录刷新权限缓存

### Q: 如何自定义模板

**A**: 修改 `scripts/code_generator.py` 中的 `TEMPLATES` 字典，或使用 `--use-system-template` 参数使用系统内置模板。

### Q: 如何生成关联查询

**A**: 目前生成器只支持单表 CRUD，关联查询需要手动修改 DAO 和 Service 层代码。
