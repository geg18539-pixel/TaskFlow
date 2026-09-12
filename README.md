# TaskFlow 任务管理系统

一个前后端分离的任务管理系统,覆盖从数据库建模、JWT 鉴权、分页筛选,到容器化编排与 CI/CD 的完整工程链路。

技术栈为 **Vue 3 + FastAPI + MySQL**,支持 Docker Compose 一键部署,并提供 Kubernetes 编排清单与 GitHub Actions 自动化流水线。

---

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [API 接口文档](#api-接口文档)
- [数据模型](#数据模型)
- [项目结构](#项目结构)
- [工程化实践](#工程化实践)
- [环境变量](#环境变量)
- [已知取舍与后续规划](#已知取舍与后续规划)

---

## 功能特性

**用户与鉴权**

- 用户注册与登录,密码使用 bcrypt 加盐哈希存储,数据库中不保存明文
- 基于 JWT 的无状态鉴权,Token 默认 24 小时过期
- 提供 `OAuth2PasswordBearer` 集成的 Swagger UI 授权入口,可直接在 `/docs` 调试

**任务管理**

- 任务的增、删、改、查,支持标题模糊搜索与状态筛选
- 数据隔离:每个用户只能访问和操作自己的任务,越权访问统一返回 404
- 服务端分页,前端表格配合页码与每页条数切换
- 任务字段包含优先级(low / medium / high)、截止日期、标签(逗号分隔多值)

**交互与展示**

- 数据概览页使用 ECharts 呈现任务状态分布(饼图)与近 7 天新建趋势(折线图)
- 深色模式切换,基于 Element Plus 的 CSS 变量实现,偏好持久化到 localStorage
- 响应式布局,窄屏下侧边栏收起为浮层,由顶栏汉堡按钮控制
- 全局请求拦截器统一处理 Token 注入、错误提示与登录态失效跳转

---

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端框架 | Vue 3(组合式 API)、Vite 8、TypeScript |
| UI 与状态 | Element Plus、Pinia、Vue Router、ECharts |
| 网络层 | Axios(封装拦截器) |
| 后端框架 | Python 3.10、FastAPI、Uvicorn |
| 数据层 | SQLAlchemy 2.0(现代 `Mapped` 语法)、PyMySQL |
| 校验与配置 | Pydantic v2、pydantic-settings |
| 鉴权 | passlib[bcrypt]、python-jose[cryptography] |
| 数据库 | MySQL 8.0 |
| 部署 | Docker(多阶段构建)、Docker Compose、Nginx、Kubernetes |
| CI/CD | GitHub Actions |

---

## 系统架构

```mermaid
flowchart LR
    U["用户浏览器"] -->|"HTTP :80"| FE["frontend 容器<br/>Nginx + Vue3 静态资源"]
    FE -->|"/api/* 反向代理"| BE["backend 容器<br/>FastAPI :8000"]
    BE -->|"SQLAlchemy 2.0 + PyMySQL"| DB[("db 容器<br/>MySQL 8.0 :3306")]
    DB -.->|"命名卷持久化"| VOL[("mysql_data")]
```

请求链路:浏览器访问前端 Nginx 容器,静态资源由 Nginx 直接返回;前端发出的 `/api/*` 请求被 Nginx 反向代理到后端容器;后端通过 SQLAlchemy 访问 MySQL。三个服务由 Docker Compose 编排在同一网络内,通过**服务名**互相通信(`backend`、`db`),无需关心容器 IP。

---

## 快速开始

### 方式一:Docker Compose(推荐)

前置要求:已安装 Docker 与 Docker Compose。

```bash
git clone <你的仓库地址>
cd TaskFlow
docker compose up --build
```

启动完成后访问:

| 服务 | 地址 |
| --- | --- |
| 前端页面 | http://localhost |
| 后端 API 文档 | http://localhost:8000/docs |
| MySQL | localhost:3306 |

首次使用请先注册账号:打开前端页面在登录页注册,或在 `/docs` 中调用 `POST /api/register`。

停止服务:

```bash
docker compose down          # 停止并移除容器,保留数据
docker compose down -v       # 同时删除数据卷,清空数据库
```

### 方式二:本地开发

后端:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

后端启动时会自动建表(通过 FastAPI lifespan 调用 `Base.metadata.create_all`),无需手动初始化。

前端:

```bash
cd frontend
pnpm install
pnpm dev
```

Vite 开发服务器已配置 `/api` 代理指向 `http://127.0.0.1:8000`,前端代码统一使用相对路径请求,不产生跨域问题。

---

## API 接口文档

所有接口以 `/api` 为前缀。除注册与登录外,均需在请求头携带 Token:

```
Authorization: Bearer <access_token>
```

### 用户

| 方法 | 路径 | 说明 | 是否需要鉴权 |
| --- | --- | --- | --- |
| POST | `/api/register` | 注册新用户 | 否 |
| POST | `/api/login` | 登录并获取 Token | 否 |
| GET | `/api/users/me` | 获取当前登录用户信息 | 是 |

### 任务

| 方法 | 路径 | 说明 | 是否需要鉴权 |
| --- | --- | --- | --- |
| GET | `/api/tasks` | 分页查询当前用户的任务 | 是 |
| POST | `/api/tasks` | 创建任务 | 是 |
| PUT | `/api/tasks/{id}` | 更新任务 | 是 |
| DELETE | `/api/tasks/{id}` | 删除任务 | 是 |

### 请求与响应示例

**注册**

```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'
```

**登录** —— 注意此接口接收的是**表单数据**(`application/x-www-form-urlencoded`),而非 JSON,以兼容 OAuth2 标准:

```bash
curl -X POST http://localhost:8000/api/login \
  -d "username=alice&password=secret123"
```

响应:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**查询任务(分页 + 筛选)**

`GET /api/tasks` 支持的查询参数:

| 参数 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `skip` | int | 0 | 跳过条数,用于分页 |
| `limit` | int | 20 | 单页条数,上限 100 |
| `search` | string | 无 | 按标题模糊匹配 |
| `status` | string | 无 | 按状态筛选:todo / doing / done |

```bash
curl "http://localhost:8000/api/tasks?skip=0&limit=10&status=doing&search=文档" \
  -H "Authorization: Bearer <access_token>"
```

响应为分页对象:

```json
{
  "data": [
    {
      "id": 1,
      "title": "编写接口文档",
      "description": "整理 API 说明",
      "status": "doing",
      "priority": "high",
      "due_date": "2026-09-30",
      "tags": "后端,文档",
      "owner_id": 1,
      "created_at": "2026-09-12T10:30:00",
      "updated_at": "2026-09-12T11:00:00"
    }
  ],
  "total": 42
}
```

**创建任务**

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{"title": "编写接口文档", "status": "todo", "priority": "high", "due_date": "2026-09-30", "tags": "后端,文档"}'
```

字段说明:`description`、`due_date`、`tags` 可为空;`status` 默认 `todo`,`priority` 默认 `medium`。创建时 `owner_id` 由服务端从当前登录用户注入,**不接受客户端传入**。

---

## 数据模型

**User**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int | 主键,自增 |
| username | varchar(50) | 唯一,建索引 |
| hashed_password | varchar(255) | bcrypt 哈希值 |
| role | varchar(20) | 默认 `user` |
| created_at | datetime | 数据库默认当前时间 |

**Task**

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | int | 主键,自增 |
| title | varchar(200) | 必填 |
| description | text | 可选 |
| status | enum | `todo` / `doing` / `done`,默认 `todo` |
| priority | enum | `low` / `medium` / `high`,默认 `medium` |
| due_date | date | 可选 |
| tags | varchar(255) | 逗号分隔的字符串,可选 |
| owner_id | int | 外键 → `users.id` |
| created_at | datetime | 数据库默认当前时间 |
| updated_at | datetime | 更新时自动刷新 |

User 与 Task 为一对多关系,配置了级联删除:通过 ORM 删除用户时,其名下任务一并删除。

---

## 项目结构

```
TaskFlow/
├── backend/                     # 后端服务
│   ├── main.py                  # 应用入口、路由定义、启动时自动建表
│   ├── database.py              # 配置读取(settings)、engine、SessionLocal、Base、get_db
│   ├── models.py                # SQLAlchemy 2.0 模型(User、Task)与枚举
│   ├── schemas.py               # Pydantic v2 请求/响应模型
│   ├── auth.py                  # 密码哈希、JWT 签发与校验、get_current_user 依赖
│   ├── init_db.py               # 手动建表脚本(本地开发备用)
│   ├── tests/test_smoke.py      # 冒烟测试(密码哈希、Token、枚举)
│   ├── pytest.ini               # pytest 配置(含 pythonpath)
│   ├── requirements.txt         # 锁定版本的依赖清单
│   ├── Dockerfile               # 基于 python:3.10-slim
│   └── .dockerignore
│
├── frontend/                    # 前端应用
│   ├── src/
│   │   ├── api/request.ts       # Axios 实例与全局拦截器
│   │   ├── layouts/MainLayout.vue   # 后台整体布局(侧边栏 + 顶栏 + 内容区)
│   │   ├── router/index.ts      # 路由表与登录守卫
│   │   ├── stores/user.ts       # Pinia 用户状态(登录、刷新恢复、登出)
│   │   ├── views/
│   │   │   ├── LoginView.vue        # 登录页
│   │   │   ├── TaskView.vue         # 任务列表(搜索、筛选、分页、增删改)
│   │   │   ├── DashboardView.vue    # 数据概览(ECharts 饼图 + 折线图)
│   │   │   └── ProfileView.vue      # 个人中心
│   │   ├── App.vue              # 根组件
│   │   ├── main.ts              # 应用入口(挂载 Pinia、Router、Element Plus)
│   │   └── style.css            # 全局样式
│   ├── vite.config.ts           # 别名 @ → src、开发代理 /api → 后端
│   ├── tsconfig.json            # TypeScript 配置(含路径别名)
│   ├── nginx.conf               # 生产环境 Nginx 配置(SPA 回落 + API 反向代理)
│   ├── Dockerfile               # 多阶段构建(node 构建 → nginx 运行)
│   └── .dockerignore
│
├── .github/workflows/docker-build.yml   # CI:前端构建 + 后端测试 + 镜像构建
├── docker-compose.yml           # 三服务编排(db / backend / frontend)
├── k8s-deployment.yaml          # Kubernetes 编排清单
├── .gitignore
└── README.md
```

---

## 工程化实践

### 容器化:多阶段构建与层缓存

后端 Dockerfile 先复制 `requirements.txt` 安装依赖,**再**复制源码。这样只改业务代码时能命中 Docker 层缓存,跳过耗时的 `pip install`。

前端采用**多阶段构建**:第一阶段用 `node:20-alpine` 构建静态产物,第二阶段只把 `dist/` 复制进 `nginx:alpine`。Vite、`node_modules` 和源码都不会进入运行镜像,最终镜像从数百 MB 降到几十 MB。

依赖安装配置了国内镜像源加速,并通过 `.dockerignore` 排除虚拟环境、`node_modules`、`.env` 等——既缩小构建上下文,也避免密钥被打进镜像。

### Docker Compose 编排

三个服务通过 Compose 定义的服务名互相寻址,`DATABASE_URL` 中的主机名从 `localhost` 改为服务名 `db`——容器里的 `localhost` 指向容器自身,这是容器化后最常见的踩坑点。

MySQL 配置了基于 `mysqladmin ping` 的健康检查,后端通过 `depends_on: condition: service_healthy` 等待数据库真正就绪后再启动,避免"后端先起来、建表失败"的竞态。数据通过命名卷 `mysql_data` 持久化。

### CI/CD:GitHub Actions

推送到 `main` 分支时自动触发流水线,结构为**两个并行任务 + 一个依赖任务**:

1. `build-frontend` —— 安装 pnpm 依赖并执行 `vite build`
2. `test-backend` —— 安装 Python 依赖并运行 pytest 冒烟测试
3. `docker-build` —— **前两者都通过后**才构建前后端两个镜像(`needs` 依赖)

这套结构的意义在于质量门禁:测试不通过就不会产出镜像。同时使用了构建缓存(`type=gha`)和并发控制(`cancel-in-progress`),减少重复构建与额度浪费。

> 说明:出于学习演示目的,当前流水线只做镜像构建、不推送到仓库。如需推送,补充 `docker/login-action` 并把 `push` 置为 `true` 即可,凭据通过仓库 Secrets 注入。

### Kubernetes 编排

`k8s-deployment.yaml` 为本项目编写了完整的 K8s 清单,涵盖:

- 三组 `Deployment` + `Service`(MySQL 与后端用 ClusterIP,前端用 NodePort)
- MySQL 通过 `PersistentVolumeClaim` 申请持久卷,并采用 `Recreate` 更新策略,避免滚动更新时两个 Pod 争抢同一个 RWO 卷
- 全部容器配置 `readinessProbe` / `livenessProbe` 与资源 `requests` / `limits`
- 敏感配置(数据库密码、JWT 密钥)通过 `Secret` 注入,非敏感配置走环境变量

**Service 通过 label 选择器动态匹配 Pod,而非绑定固定 IP**,这正是 Pod 重建后服务仍可用的原因。文件顶部以注释形式记录了 Pod、Deployment、Service 三者的关系。

### 前后端协作中的几个关键处理

**鉴权链路闭环**。前端 Axios 请求拦截器自动注入 `Authorization` 头;响应拦截器在收到 401 时清除本地 Token 并跳转登录页。后端 JWT 过期由 `get_current_user` 依赖统一拦截。两侧配合形成完整的登录态失效处理。

**登录接口的表单编码**。FastAPI 的 `OAuth2PasswordRequestForm` 要求 `application/x-www-form-urlencoded`,因此前端登录请求使用 `URLSearchParams` 而非 JSON 对象——这类细节不一致会直接导致 422 校验失败。

**全局提示去重**。错误提示统一由响应拦截器负责,组件内不再重复调用 `ElMessage`,避免同一次失败弹出两个提示。对需要自定义文案的场景(如登录失败),通过自定义的 `silent` 标志关闭全局提示。

**权限隔离在服务端**。更新和删除接口先按主键取出记录,再比对 `owner_id`,不匹配时统一返回 404 而非 403,避免泄露"该资源存在但不属于你"的信息。列表查询则直接在 SQL 条件里按 `owner_id` 过滤。

**分页的页码换算**。前端使用"第几页 + 每页条数",后端使用 `skip` / `limit`,换算为 `skip = (page - 1) * pageSize`。筛选条件变化时重置回第一页,删除当前页最后一条时自动回退一页。

---

## 环境变量

后端配置通过 `backend/.env` 读取(pydantic-settings),关键变量如下:

| 变量 | 说明 | 示例 |
| --- | --- | --- |
| `DATABASE_URL` | 数据库连接串 | `mysql+pymysql://root:root1234@localhost:3306/taskflow` |
| `SECRET_KEY` | JWT 签名密钥,生产环境须使用强随机值 | `openssl rand -hex 32` 生成 |
| `ALGORITHM` | JWT 签名算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 有效期(分钟) | `1440`(24 小时) |

`.env` 已加入 `.gitignore`,不应提交到仓库。在 Docker Compose 与 Kubernetes 环境中,这些值改由编排文件的环境变量或 Secret 注入——**同一份代码不因部署环境而修改**。

---

## 已知取舍与后续规划

当前实现偏向完整展示技术链路,以下是有意识省略或简化的部分:

**数据库迁移**。目前依赖启动时的 `create_all` 自动建表,它只会创建不存在的表,不会修改已有表结构。一旦表中有真实数据,应引入 Alembic 做版本化迁移;届时多副本部署需要把迁移拆到独立的 initContainer 或 Job,避免并发执行。

**搜索性能**。`search` 使用 `LIKE '%关键词%'`,前后通配符无法命中索引,数据量大时会退化为全表扫描。可通过为 `owner_id`、`status`、`created_at` 建立复合索引缓解,更大规模则应引入专门的搜索方案。

**统计接口**。数据概览页目前由前端拉取任务列表后自行聚合,任务量较大时不够经济。规划新增 `GET /api/tasks/stats` 聚合接口,由数据库直接返回分组统计结果。

**前端测试**。后端已有 pytest 冒烟测试,前端尚无单元测试与端到端测试,可考虑引入 Vitest 与 Playwright。

**生产级部署**。K8s 清单为基础版本,生产环境还需补充 Ingress(替代 NodePort 对外暴露)、HorizontalPodAutoscaler、NetworkPolicy,并把 MySQL 换成 StatefulSet + Operator,Secret 改为 Sealed Secrets 等外部密钥管理方案。

**令牌机制**。当前仅有 Access Token,没有 Refresh Token。增强方向是引入双 Token 机制,配合前端的静默续期,减少用户被强制登出的情况。
