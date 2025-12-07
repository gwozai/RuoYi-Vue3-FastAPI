# 若依代码生成器使用指南

本文档介绍如何使用若依代码生成器快速创建 CRUD 模块。

---

## 快速开始 (命令行/脚本方式) 🚀

### 方式一: Python API 调用 (推荐给 AI 使用)

```python
# 在项目根目录下执行
import sys
sys.path.insert(0, 'ruoyi-fastapi-backend')
from scripts.gen_api import generate_crud, quick_generate

# 从 SQL 生成完整 CRUD 代码
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

# 快速生成 - 更简洁的方式
quick_generate('order', {
    'order_no': 'varchar(50) 订单号',
    'amount': 'decimal(10,2) 金额',
    'status': 'char(1) 状态',
}, module='system')
```

### 方式二: 命令行调用

```bash
cd ruoyi-fastapi-backend

# 从数据库表生成
python scripts/code_generator.py --table sys_example --module system --business example

# 从 SQL 生成
python scripts/code_generator.py --sql "CREATE TABLE sys_demo (id INT PRIMARY KEY, name VARCHAR(100))" --module system --business demo

# 生成并自动复制到项目
python scripts/code_generator.py --table sys_example --module system --business example --auto-install
```

### 生成的文件列表

| 文件 | 路径 | 说明 |
|------|------|------|
| DO | `module_{module}/entity/do/{business}_do.py` | 数据库模型 |
| VO | `module_{module}/entity/vo/{business}_vo.py` | Pydantic 模型 |
| DAO | `module_{module}/dao/{business}_dao.py` | 数据访问层 |
| Service | `module_{module}/service/{business}_service.py` | 业务逻辑层 |
| Controller | `module_{module}/controller/{business}_controller.py` | 路由控制器 |
| API JS | `src/api/{module}/{business}.js` | 前端 API |
| Menu SQL | `sql/{business}_menu.sql` | 菜单 SQL |

### 生成后的步骤

1. **注册路由** - 在 `server.py` 中添加:
   ```python
   from module_{module}.controller.{business}_controller import {business}Controller
   app.include_router({business}Controller)
   ```

2. **执行菜单 SQL** - 在数据库中执行生成的 `sql/{business}_menu.sql`

3. **创建前端页面** - 在 `src/views/{module}/{business}/index.vue` 创建 Vue 页面

---

## 页面方式 (通过系统界面操作)

以图书管理模块为例。

## 目录

1. [创建数据库表](#1-创建数据库表)
2. [导入表到代码生成器](#2-导入表到代码生成器)
3. [配置生成选项](#3-配置生成选项)
4. [生成代码](#4-生成代码)
5. [集成到项目](#5-集成到项目)
6. [添加菜单权限](#6-添加菜单权限)
7. [重启服务验证](#7-重启服务验证)

---

## 1. 创建数据库表

首先在 MySQL 中创建业务表。表名建议使用 `sys_` 前缀以保持一致性。

```sql
CREATE TABLE IF NOT EXISTS sys_book (
  book_id         BIGINT          NOT NULL AUTO_INCREMENT    COMMENT '图书ID',
  book_name       VARCHAR(100)    NOT NULL                   COMMENT '图书名称',
  author          VARCHAR(50)     DEFAULT ''                 COMMENT '作者',
  isbn            VARCHAR(20)     DEFAULT ''                 COMMENT 'ISBN编号',
  publisher       VARCHAR(100)    DEFAULT ''                 COMMENT '出版社',
  publish_date    DATE            DEFAULT NULL               COMMENT '出版日期',
  price           DECIMAL(10,2)   DEFAULT 0                  COMMENT '价格',
  category        VARCHAR(50)     DEFAULT ''                 COMMENT '分类',
  stock           INT             DEFAULT 0                  COMMENT '库存数量',
  description     TEXT            DEFAULT NULL               COMMENT '图书简介',
  cover_image     VARCHAR(255)    DEFAULT ''                 COMMENT '封面图片',
  status          CHAR(1)         DEFAULT '0'                COMMENT '状态（0正常 1停用）',
  create_by       VARCHAR(64)     DEFAULT ''                 COMMENT '创建者',
  create_time     DATETIME                                   COMMENT '创建时间',
  update_by       VARCHAR(64)     DEFAULT ''                 COMMENT '更新者',
  update_time     DATETIME                                   COMMENT '更新时间',
  remark          VARCHAR(500)    DEFAULT NULL               COMMENT '备注',
  PRIMARY KEY (book_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 COMMENT = '图书信息表';
```

**表设计规范：**
- 主键使用 `BIGINT` 类型，自增
- 必须包含 `create_by`, `create_time`, `update_by`, `update_time` 字段
- 状态字段使用 `CHAR(1)`，0 表示正常，1 表示停用
- 字段注释会自动生成为表单标签

---

## 2. 导入表到代码生成器

1. 登录系统，进入 **系统工具 > 代码生成**
2. 点击 **导入** 按钮
3. 在弹出的对话框中勾选刚创建的表（如 `sys_book`）
4. 点击 **确定** 完成导入

---

## 3. 配置生成选项

导入成功后，点击表对应的 **编辑** 按钮进行配置：

### 3.1 基本信息

默认自动生成，一般无需修改。

### 3.2 字段信息

配置每个字段的属性：
- **插入**：新增时是否包含该字段
- **编辑**：修改时是否包含该字段
- **列表**：列表页是否显示该字段
- **查询**：是否作为查询条件
- **查询方式**：`=`（精确匹配）或 `LIKE`（模糊匹配）
- **必填**：表单验证是否必填
- **显示类型**：文本框、文本域、下拉框、日期控件等

### 3.3 生成信息

| 配置项 | 说明 | 示例值 |
|--------|------|--------|
| 生成模板 | 单表或树表 | 单表（增删改查） |
| 前端类型 | 前端框架 | Vue3 Element Plus 模版 |
| 生成包路径 | 后端包路径 | module_admin.system |
| 生成模块名 | 模块名称 | system |
| 生成业务名 | 业务名称（小写） | book |
| 生成功能名 | 功能描述（中文） | 图书信息 |
| 上级菜单 | 菜单归属 | 系统管理 |

点击 **提交** 保存配置。

---

## 4. 生成代码

1. 返回代码生成列表
2. 勾选要生成的表
3. 点击 **生成** 按钮
4. 下载 `vfadmin.zip` 压缩包

解压后的目录结构：
```
vfadmin/
├── backend/
│   ├── module_admin/system/
│   │   ├── controller/book_controller.py  # API控制器
│   │   ├── dao/book_dao.py                # 数据访问层
│   │   ├── entity/
│   │   │   ├── do/book_do.py              # 数据库模型
│   │   │   └── vo/book_vo.py              # Pydantic模型
│   │   └── service/book_service.py        # 业务服务层
│   └── sql/book_menu.sql                  # 菜单SQL
└── frontend/
    ├── api/system/book.js                 # API接口
    └── views/system/book/index.vue        # 页面组件
```

---

## 5. 集成到项目

### 5.1 后端文件

由于项目结构是扁平的，需要调整 import 路径后复制文件：

```bash
# 复制实体文件（无需修改）
cp backend/module_admin/system/entity/do/book_do.py \
   ruoyi-fastapi-backend/module_admin/entity/do/

cp backend/module_admin/system/entity/vo/book_vo.py \
   ruoyi-fastapi-backend/module_admin/entity/vo/

# 复制并修改 DAO（调整 import 路径）
sed 's/module_admin.system.entity/module_admin.entity/g' \
    backend/module_admin/system/dao/book_dao.py > \
    ruoyi-fastapi-backend/module_admin/dao/book_dao.py

# 复制并修改 Service
sed -e 's/module_admin.system.dao/module_admin.dao/g' \
    -e 's/module_admin.system.entity/module_admin.entity/g' \
    backend/module_admin/system/service/book_service.py > \
    ruoyi-fastapi-backend/module_admin/service/book_service.py

# 复制并修改 Controller
sed -e 's/module_admin.system.service/module_admin.service/g' \
    -e 's/module_admin.system.entity/module_admin.entity/g' \
    backend/module_admin/system/controller/book_controller.py > \
    ruoyi-fastapi-backend/module_admin/controller/book_controller.py
```

### 5.2 注册路由

编辑 `ruoyi-fastapi-backend/server.py`：

```python
# 添加 import
from module_admin.controller.book_controller import bookController

# 在 controller_list 中添加
controller_list = [
    # ... 其他控制器
    {'router': bookController, 'tags': ['系统管理-图书管理']},
]
```

### 5.3 前端文件

```bash
# 复制 API 文件
cp frontend/api/system/book.js \
   ruoyi-fastapi-frontend/src/api/system/

# 创建目录并复制页面组件
mkdir -p ruoyi-fastapi-frontend/src/views/system/book
cp frontend/views/system/book/index.vue \
   ruoyi-fastapi-frontend/src/views/system/book/
```

---

## 6. 添加菜单权限

执行生成的菜单 SQL：

```bash
docker exec -i ruoyi-mysql mysql -uroot -pmysqlroot \
    --default-character-set=utf8mb4 ruoyi-fastapi < backend/sql/book_menu.sql
```

或者手动在 **系统管理 > 菜单管理** 中添加：

| 菜单名称 | 菜单类型 | 路由地址 | 组件路径 | 权限标识 |
|----------|----------|----------|----------|----------|
| 图书信息 | 菜单 | book | system/book/index | system:book:list |
| 图书信息查询 | 按钮 | - | - | system:book:query |
| 图书信息新增 | 按钮 | - | - | system:book:add |
| 图书信息修改 | 按钮 | - | - | system:book:edit |
| 图书信息删除 | 按钮 | - | - | system:book:remove |
| 图书信息导出 | 按钮 | - | - | system:book:export |

---

## 7. 重启服务验证

```bash
# 重启后端服务
cd ruoyi-fastapi-backend
pkill -f "python app.py"
python app.py --env=dev

# 前端热更新会自动生效，无需重启
```

刷新页面，在 **系统管理** 菜单下即可看到 **图书信息** 菜单。

---

## 常见问题

### Q1: 生成的代码 import 路径不对？

生成器默认使用 `module_admin.system.xxx` 路径，但项目实际结构是扁平的 `module_admin.xxx`。需要手动替换：

```bash
sed -i 's/module_admin.system./module_admin./g' your_file.py
```

### Q2: 菜单不显示？

1. 确认菜单 SQL 已执行
2. 刷新字典缓存：**系统管理 > 字典管理 > 刷新缓存**
3. 重新登录以刷新权限

### Q3: 接口 404？

1. 确认 Controller 已在 `server.py` 中注册
2. 确认后端服务已重启
3. 检查路由前缀是否正确（如 `/system/book`）

### Q4: 前端页面空白？

1. 检查浏览器控制台是否有错误
2. 确认 Vue 组件文件路径正确
3. 确认 API 文件已正确放置

---

## 附录：生成的文件说明

| 文件 | 说明 |
|------|------|
| `book_do.py` | SQLAlchemy ORM 模型，对应数据库表结构 |
| `book_vo.py` | Pydantic 模型，用于请求/响应数据验证 |
| `book_dao.py` | 数据访问对象，封装数据库 CRUD 操作 |
| `book_service.py` | 业务服务层，处理业务逻辑 |
| `book_controller.py` | FastAPI 路由控制器，定义 API 接口 |
| `book.js` | 前端 API 封装，调用后端接口 |
| `index.vue` | Vue 页面组件，包含列表、表单、搜索等功能 |
| `book_menu.sql` | 菜单和权限 SQL 脚本 |
