# 开发脚本 API 文档

本文档介绍 RuoYi-Vue3-FastAPI 系统提供的 Python 脚本 API，包括**代码生成**和**菜单管理**两大模块，支持命令行和 Python 代码两种调用方式。

---

## 目录

- [快速开始](#快速开始)
- [代码生成 API](#代码生成-api)
  - [generate_crud - 生成 CRUD 代码](#generate_crud---生成-crud-代码)
  - [quick_generate - 快速生成](#quick_generate---快速生成)
  - [命令行使用](#代码生成命令行)
- [菜单管理 API](#菜单管理-api)
  - [add_directory - 添加目录](#add_directory---添加目录)
  - [add_menu - 添加页面菜单](#add_menu---添加页面菜单)
  - [add_button - 添加按钮权限](#add_button---添加按钮权限)
  - [add_crud_buttons - 添加 CRUD 按钮组](#add_crud_buttons---添加-crud-按钮组)
  - [create_module - 创建完整模块](#create_module---创建完整模块)
  - [list_menus - 列出菜单](#list_menus---列出菜单)
  - [delete_menu - 删除菜单](#delete_menu---删除菜单)
  - [move_menu - 移动菜单](#move_menu---移动菜单)
  - [命令行使用](#菜单管理命令行)
- [完整示例](#完整示例)
- [常用图标](#常用图标)

---

## 快速开始

### 环境准备

```python
import sys
sys.path.insert(0, 'ruoyi-fastapi-backend')
```

### 一键创建完整模块

```python
from scripts.gen_api import generate_crud
from scripts.menu_manager import create_module

# 1. 生成代码
generate_crud(
    sql='''
    CREATE TABLE sys_article (
        article_id INT PRIMARY KEY AUTO_INCREMENT COMMENT '文章ID',
        title VARCHAR(200) NOT NULL COMMENT '标题',
        content TEXT COMMENT '内容',
        status CHAR(1) DEFAULT '0' COMMENT '状态',
        create_by VARCHAR(64) COMMENT '创建者',
        create_time DATETIME COMMENT '创建时间',
        update_by VARCHAR(64) COMMENT '更新者',
        update_time DATETIME COMMENT '更新时间',
        remark VARCHAR(500) COMMENT '备注'
    ) COMMENT='文章管理';
    ''',
    module='system',
    business='article',
    auto_install=True
)

# 2. 创建菜单
create_module(
    module_name="内容管理",
    module_path="content",
    business_name="文章管理",
    business_path="article",
    component="content/article/index",
    icon="documentation"
)
```

---

## 代码生成 API

文件位置：`ruoyi-fastapi-backend/scripts/gen_api.py`

### generate_crud - 生成 CRUD 代码

根据表结构生成完整的前后端 CRUD 代码。

```python
from scripts.gen_api import generate_crud

result = generate_crud(
    table='sys_product',           # 表名（与 sql 二选一）
    sql='CREATE TABLE ...',        # 建表 SQL（与 table 二选一）
    module='system',               # 模块名称
    business='product',            # 业务名称（可选，默认从表名推断）
    columns=[...],                 # 列定义（可选，从 sql 自动解析）
    table_comment='产品信息',       # 表注释（可选）
    output_dir='/tmp/ruoyi-gen',   # 输出目录
    parent_menu_id=0,              # 父菜单ID
    auto_install=False,            # 是否自动复制到项目
)
```

#### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `table` | str | 二选一 | - | 表名 |
| `sql` | str | 二选一 | - | 建表 SQL 语句 |
| `module` | str | 否 | 'admin' | 模块名称 |
| `business` | str | 否 | 从表名推断 | 业务名称 |
| `columns` | list | 否 | 从 sql 解析 | 列定义列表 |
| `table_comment` | str | 否 | business | 表注释 |
| `output_dir` | str | 否 | '/tmp/ruoyi-gen' | 输出目录 |
| `parent_menu_id` | int | 否 | 0 | 父菜单ID |
| `auto_install` | bool | 否 | False | 自动复制到项目 |

#### 返回值

```python
{
    'do': '/tmp/ruoyi-gen/backend/module_system/entity/do/product_do.py',
    'vo': '/tmp/ruoyi-gen/backend/module_system/entity/vo/product_vo.py',
    'dao': '/tmp/ruoyi-gen/backend/module_system/dao/product_dao.py',
    'service': '/tmp/ruoyi-gen/backend/module_system/service/product_service.py',
    'controller': '/tmp/ruoyi-gen/backend/module_system/controller/product_controller.py',
    'api_js': '/tmp/ruoyi-gen/frontend/src/api/system/product.js',
    'menu_sql': '/tmp/ruoyi-gen/backend/sql/product_menu.sql',
}
```

#### 使用示例

**方式 1：从 SQL 生成**

```python
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

**方式 2：从已有表生成**

```python
generate_crud(
    table='sys_user',
    module='system',
    business='user'
)
```

**方式 3：手动指定列**

```python
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

---

### quick_generate - 快速生成

更简洁的生成接口，自动添加通用字段。

```python
from scripts.gen_api import quick_generate

quick_generate(
    name='order',                  # 业务名称
    fields={                       # 字段定义
        'order_no': 'varchar(50) 订单号',
        'amount': 'decimal(10,2) 金额',
        'status': 'char(1) 状态',
    },
    module='system',               # 模块名称
    pk='order_id',                 # 主键名（可选）
)
```

#### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | str | 是 | - | 业务名称 |
| `fields` | dict | 是 | - | 字段定义 `{字段名: '类型 注释'}` |
| `module` | str | 否 | 'admin' | 模块名称 |
| `pk` | str | 否 | `{name}_id` | 主键字段名 |

#### 自动添加的字段

- `{name}_id` - 主键
- `create_by` - 创建者
- `create_time` - 创建时间
- `update_by` - 更新者
- `update_time` - 更新时间
- `remark` - 备注

---

### 代码生成命令行

```bash
cd ruoyi-fastapi-backend

# 从数据库表生成
python scripts/code_generator.py \
    --table sys_product \
    --module system \
    --business product

# 从 SQL 生成
python scripts/code_generator.py \
    --sql "CREATE TABLE sys_demo (id INT PRIMARY KEY, name VARCHAR(100))" \
    --module system \
    --business demo

# 指定输出目录
python scripts/code_generator.py \
    --table sys_product \
    --module system \
    --business product \
    --output /tmp/gen

# 生成并自动安装
python scripts/code_generator.py \
    --table sys_product \
    --module system \
    --business product \
    --auto-install
```

#### 命令行参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `--table` | 二选一 | 数据库表名 |
| `--sql` | 二选一 | 建表 SQL 语句 |
| `--module` | 是 | 模块名称 |
| `--business` | 是 | 业务名称 |
| `--output` | 否 | 输出目录（默认 /tmp/ruoyi-gen） |
| `--auto-install` | 否 | 自动复制到项目目录 |
| `--menu-parent` | 否 | 父菜单 ID |
| `--env` | 否 | 环境（dev/prod） |

---

## 菜单管理 API

文件位置：`ruoyi-fastapi-backend/scripts/menu_manager.py`

### add_directory - 添加目录

添加一级目录菜单（侧边栏目录）。

```python
from scripts.menu_manager import add_directory

menu_id = add_directory(
    name='语音服务',        # 目录名称
    path='voice',          # 路由路径
    icon='message',        # 图标
    order=0,               # 排序
    parent=None,           # 父菜单名称（可选）
)
```

#### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | str | 是 | - | 目录名称 |
| `path` | str | 是 | - | 路由路径 |
| `icon` | str | 否 | '#' | 图标名称 |
| `order` | int | 否 | 0 | 排序号 |
| `parent` | str | 否 | None | 父菜单名称 |

#### 返回值

`int` - 创建的菜单 ID

---

### add_menu - 添加页面菜单

添加页面菜单（可点击跳转的菜单项）。

```python
from scripts.menu_manager import add_menu

menu_id = add_menu(
    name='音频生成',                    # 菜单名称
    path='audio',                      # 路由路径
    component='voice/audio/index',     # 组件路径
    perms='voice:audio:list',          # 权限标识
    parent='语音服务',                  # 父菜单名称
    icon='#',                          # 图标
    order=1,                           # 排序
)
```

#### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | str | 是 | - | 菜单名称 |
| `path` | str | 是 | - | 路由路径 |
| `component` | str | 是 | - | 组件路径（如 `system/user/index`） |
| `perms` | str | 是 | - | 权限标识（如 `system:user:list`） |
| `parent` | str | 否 | None | 父菜单名称 |
| `icon` | str | 否 | '#' | 图标名称 |
| `order` | int | 否 | 1 | 排序号 |

---

### add_button - 添加按钮权限

添加按钮级别的权限控制。

```python
from scripts.menu_manager import add_button

menu_id = add_button(
    name='新增',                    # 按钮名称
    perms='voice:audio:add',       # 权限标识
    parent='音频生成',              # 父菜单名称
    order=1,                       # 排序
)
```

#### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | str | 是 | - | 按钮名称（如 新增、修改、删除） |
| `perms` | str | 是 | - | 权限标识（如 `system:user:add`） |
| `parent` | str | 是 | - | 父菜单名称 |
| `order` | int | 否 | 1 | 排序号 |

---

### add_crud_buttons - 添加 CRUD 按钮组

一次性添加标准的 5 个 CRUD 按钮权限。

```python
from scripts.menu_manager import add_crud_buttons

button_ids = add_crud_buttons(
    parent='音频生成',     # 父菜单名称
    module='voice',       # 模块名
    business='audio',     # 业务名
)
```

#### 自动创建的按钮

| 按钮名称 | 权限标识 | 排序 |
|----------|----------|------|
| 查询 | `{module}:{business}:query` | 1 |
| 新增 | `{module}:{business}:add` | 2 |
| 修改 | `{module}:{business}:edit` | 3 |
| 删除 | `{module}:{business}:remove` | 4 |
| 导出 | `{module}:{business}:export` | 5 |

#### 返回值

`List[int]` - 创建的按钮 ID 列表

---

### create_module - 创建完整模块

一次性创建完整的模块菜单结构（目录 + 页面 + CRUD 按钮）。

```python
from scripts.menu_manager import create_module

result = create_module(
    module_name='语音服务',              # 模块名称（目录）
    module_path='voice',                # 模块路径
    business_name='音频生成',            # 业务名称（页面）
    business_path='audio',              # 业务路径
    component='voice/audio/index',      # 组件路径
    icon='message',                     # 图标
)
```

#### 参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `module_name` | str | 是 | - | 模块名称（显示在侧边栏） |
| `module_path` | str | 是 | - | 模块路径 |
| `business_name` | str | 是 | - | 业务名称（页面标题） |
| `business_path` | str | 是 | - | 业务路径 |
| `component` | str | 是 | - | Vue 组件路径 |
| `icon` | str | 否 | '#' | 图标名称 |

#### 返回值

```python
{
    'directory_id': 100,      # 目录菜单 ID
    'page_id': 101,           # 页面菜单 ID
    'button_ids': [102, 103, 104, 105, 106]  # 按钮 ID 列表
}
```

#### 创建的菜单结构

```
📁 语音服务 (目录)
└── 📄 音频生成 (页面)
    ├── 🔘 查询
    ├── 🔘 新增
    ├── 🔘 修改
    ├── 🔘 删除
    └── 🔘 导出
```

---

### list_menus - 列出菜单

获取菜单列表。

```python
from scripts.menu_manager import list_menus

# 列出所有菜单
menus = list_menus()

# 列出指定父菜单下的菜单
menus = list_menus(parent='语音服务')
```

#### 返回值

```python
[
    {
        'menu_id': 1,
        'menu_name': '系统管理',
        'parent_id': 0,
        'order_num': 1,
        'path': 'system',
        'component': '',
        'menu_type': 'M',      # M=目录, C=菜单, F=按钮
        'perms': '',
        'icon': 'system',
        'status': '0',
    },
    ...
]
```

---

### delete_menu - 删除菜单

删除指定菜单。

```python
from scripts.menu_manager import delete_menu

success = delete_menu(name='测试菜单')
```

> ⚠️ 如果菜单下有子菜单，需要先删除子菜单或使用命令行的 `--recursive` 参数。

---

### move_menu - 移动菜单

将菜单移动到新的父菜单下。

```python
from scripts.menu_manager import move_menu

success = move_menu(
    name='音频生成',       # 要移动的菜单
    parent='语音服务',     # 新的父菜单
)
```

---

### 菜单管理命令行

```bash
cd ruoyi-fastapi-backend

# 添加目录菜单
python scripts/menu_manager.py add-dir \
    --name "语音服务" \
    --path voice \
    --icon message \
    --order 0

# 添加页面菜单
python scripts/menu_manager.py add-menu \
    --name "音频生成" \
    --parent "语音服务" \
    --path audio \
    --component "voice/audio/index" \
    --perms "voice:audio:list"

# 添加按钮权限
python scripts/menu_manager.py add-button \
    --name "新增" \
    --parent "音频生成" \
    --perms "voice:audio:add"

# 添加 CRUD 按钮组
python scripts/menu_manager.py add-crud \
    --parent "音频生成" \
    --module voice \
    --business audio

# 创建完整模块
python scripts/menu_manager.py create-module \
    --module-name "语音服务" \
    --module-path voice \
    --business-name "音频生成" \
    --business-path audio \
    --component "voice/audio/index" \
    --icon message

# 列出菜单
python scripts/menu_manager.py list
python scripts/menu_manager.py list --tree
python scripts/menu_manager.py list --parent "语音服务"

# 删除菜单
python scripts/menu_manager.py delete --name "测试菜单"
python scripts/menu_manager.py delete --name "测试菜单" --recursive

# 移动菜单
python scripts/menu_manager.py move --name "音频生成" --parent "语音服务"
```

---

## 完整示例

### 示例 1：创建产品管理模块

```python
import sys
sys.path.insert(0, 'ruoyi-fastapi-backend')

from scripts.gen_api import generate_crud
from scripts.menu_manager import create_module

# 1. 生成代码
generate_crud(
    sql='''
    CREATE TABLE sys_product (
        product_id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '产品ID',
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
    auto_install=True
)

# 2. 创建菜单
create_module(
    module_name="商品管理",
    module_path="goods",
    business_name="产品信息",
    business_path="product",
    component="goods/product/index",
    icon="shopping"
)

# 3. 后续步骤提示
print("""
后续步骤:
1. 在 server.py 中注册路由
2. 重启后端服务
3. 刷新前端页面
""")
```

### 示例 2：快速添加子模块

```python
from scripts.menu_manager import add_menu, add_crud_buttons

# 在已有目录下添加新页面
add_menu(
    name='TTS配置',
    path='ttsConfig',
    component='voice/ttsConfig/index',
    perms='voice:ttsConfig:list',
    parent='语音服务',
    order=2
)

# 添加 CRUD 按钮
add_crud_buttons('TTS配置', 'voice', 'ttsConfig')
```

### 示例 3：使用系统模板生成完整代码

```bash
# 使用 gen_full.py 调用系统内置模板（包含完整 Vue 页面）
python scripts/gen_full.py --table sys_student --auto-install
```

---

## 常用图标

菜单管理支持以下常用图标：

| 图标名 | 用途 | 图标名 | 用途 |
|--------|------|--------|------|
| `system` | 系统管理 | `monitor` | 系统监控 |
| `tool` | 系统工具 | `guide` | 引导 |
| `user` | 用户 | `peoples` | 用户组 |
| `tree` | 树形 | `tree-table` | 树表 |
| `message` | 消息 | `log` | 日志 |
| `dict` | 字典 | `edit` | 编辑 |
| `list` | 列表 | `chart` | 图表 |
| `form` | 表单 | `table` | 表格 |
| `code` | 代码 | `build` | 构建 |
| `server` | 服务器 | `job` | 任务 |
| `online` | 在线 | `redis` | Redis |
| `download` | 下载 | `upload` | 上传 |
| `star` | 收藏 | `link` | 链接 |
| `documentation` | 文档 | `example` | 示例 |

---

## 脚本文件说明

| 文件 | 说明 |
|------|------|
| `scripts/gen_api.py` | 代码生成 Python API（推荐使用） |
| `scripts/code_generator.py` | 代码生成器核心实现 + 命令行 |
| `scripts/gen_full.py` | 使用系统 Jinja2 模板的完整生成器 |
| `scripts/menu_manager.py` | 菜单管理 Python API + 命令行 |

---

## 注意事项

1. **数据库连接**：菜单管理 API 需要数据库连接，确保 `APP_ENV` 环境变量正确设置
2. **路径调整**：生成的代码使用 `module_{module}` 路径，可能需要调整为 `module_admin`
3. **重启服务**：添加菜单后需要重新登录以刷新权限
4. **幂等性**：API 会检查是否已存在同名菜单，避免重复创建
