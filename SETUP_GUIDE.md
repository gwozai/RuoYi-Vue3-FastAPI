# RuoYi-Vue3-FastAPI 本地开发环境搭建教程

## 环境要求

- **Node.js**: >= 18
- **Python**: >= 3.9
- **Docker**: 用于运行 MySQL 和 Redis
- **Conda**: 用于管理 Python 环境

## 一、启动 MySQL 和 Redis 容器

使用 Docker 启动 MySQL 8.0 和 Redis，使用 30000+ 端口避免与本地服务冲突：

```bash
# 启动 MySQL 容器
docker run -d --name ruoyi-mysql \
  -p 30306:3306 \
  -e MYSQL_ROOT_PASSWORD=mysqlroot \
  -e MYSQL_DATABASE=ruoyi-fastapi \
  mysql:8.0

# 启动 Redis 容器
docker run -d --name ruoyi-redis \
  -p 30379:6379 \
  redis:alpine
```

## 二、创建 Conda 环境并安装依赖

```bash
# 创建 Python 3.11 环境
conda create -n ruoyi-fastapi python=3.11 -y

# 激活环境
conda activate ruoyi-fastapi

# 进入后端目录
cd ruoyi-fastapi-backend

# 安装依赖（使用国内镜像加速）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 三、配置后端环境

编辑 `ruoyi-fastapi-backend/.env.dev` 文件，修改数据库和 Redis 端口：

```ini
# 数据库端口
DB_PORT = 30306

# Redis端口
REDIS_PORT = 30379
```

## 四、导入数据库

等待 MySQL 容器完全启动后（约 15 秒），导入 SQL 文件：

```bash
cd ruoyi-fastapi-backend

# 导入数据库（必须指定 utf8mb4 字符集，否则中文会乱码）
docker exec -i ruoyi-mysql mysql -uroot -pmysqlroot --default-character-set=utf8mb4 ruoyi-fastapi < sql/ruoyi-fastapi.sql
```

> **注意**: 
> - 必须添加 `--default-character-set=utf8mb4` 参数，否则中文菜单会显示乱码
> - 如果遇到 `Data too long for column 'notice_title'` 错误，需要修改 `sql/ruoyi-fastapi.sql` 文件中 `notice_title` 字段长度从 `varchar(50)` 改为 `varchar(255)`

## 五、启动后端服务

```bash
# 确保在 ruoyi-fastapi 环境中
conda activate ruoyi-fastapi

cd ruoyi-fastapi-backend
python app.py --env=dev
```

后端服务将在 `http://localhost:9099/dev-api` 启动。

## 六、安装前端依赖并启动

```bash
cd ruoyi-fastapi-frontend

# 安装依赖（使用国内镜像）
npm install --registry=https://registry.npmmirror.com

# 启动开发服务器
npm run dev
```

前端服务将在 `http://localhost:80` 启动。

## 七、访问系统

- **访问地址**: http://localhost:80
- **默认账号**: admin
- **默认密码**: admin123

## 服务端口汇总

| 服务 | 地址 | 端口 |
|------|------|------|
| 前端 | http://localhost:80 | 80 |
| 后端 API | http://localhost:9099/dev-api | 9099 |
| MySQL | 127.0.0.1:30306 | 30306 |
| Redis | 127.0.0.1:30379 | 30379 |

## 常用命令

### 停止/启动 Docker 容器

```bash
# 停止容器
docker stop ruoyi-mysql ruoyi-redis

# 启动容器
docker start ruoyi-mysql ruoyi-redis

# 删除容器（需要先停止）
docker rm ruoyi-mysql ruoyi-redis
```

### 查看容器日志

```bash
docker logs ruoyi-mysql
docker logs ruoyi-redis
```

### 连接 MySQL

```bash
docker exec -it ruoyi-mysql mysql -uroot -pmysqlroot ruoyi-fastapi
```

## 故障排查

1. **后端连接数据库失败**: 确认 MySQL 容器已启动，端口配置正确
2. **前端接口 404**: 确认后端服务已启动，检查 `.env.development` 中的代理配置
3. **Redis 连接失败**: 确认 Redis 容器已启动，端口配置正确
4. **菜单或页面显示中文乱码**: 
   - 重新导入 SQL 时确保使用 `--default-character-set=utf8mb4` 参数
   - 登录系统后，进入 **系统管理 > 字典管理**，点击 **刷新缓存** 按钮
