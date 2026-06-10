
# 数据统计报表系统

一个用于事业单位日常数据统计和报表生成的Web应用系统。

## 功能特性

- **数据管理**: 支持数据的录入、编辑、删除、查询和导入导出
- **报表生成**: 自动统计汇总数据，生成可视化报表
- **图表展示**: 支持柱状图、饼图等多种图表展示
- **用户管理**: 管理员可以管理系统用户
- **数据安全**: 用户认证和权限控制

## 技术栈

### 前端
- Vue.js 3 + Vue Router
- Element Plus UI组件库
- ECharts 图表库
- Axios HTTP客户端

### 后端
- FastAPI (Python)
- SQLAlchemy ORM
- SQLite 数据库
- JWT 认证

### 部署
- Docker + Docker Compose
- Nginx 反向代理

## 项目结构

```
├── backend/                    # 后端代码
│   ├── app/                   # 应用代码
│   │   ├── main.py            # 入口文件
│   │   ├── database.py        # 数据库配置
│   │   ├── models.py          # 数据模型
│   │   ├── schemas.py         # 数据结构定义
│   │   ├── routers/           # API路由
│   │   └── utils/             # 工具函数
│   ├── requirements.txt       # 依赖列表
│   └── Dockerfile             # 后端Dockerfile
├── frontend/                  # 前端代码
│   ├── src/
│   │   ├── views/             # 页面视图
│   │   ├── router/            # 路由配置
│   │   ├── utils/             # 工具函数
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   ├── index.html             # HTML模板
│   ├── package.json           # 依赖配置
│   ├── vite.config.js         # Vite配置
│   ├── nginx.conf             # Nginx配置
│   └── Dockerfile             # 前端Dockerfile
├── docker-compose.yml         # Docker Compose配置
└── README.md                  # 项目说明
```

## 快速开始

### 环境要求

- Docker >= 20.10
- Docker Compose >= 1.29

### 部署步骤

1. 克隆项目到服务器
2. 进入项目目录
3. 运行以下命令启动服务：

```bash
docker-compose up -d --build
```

4. 服务启动后，访问 http://服务器IP 即可使用

### 首次使用

1. 打开浏览器访问系统
2. 点击"立即注册"创建账户
3. 使用注册的账户登录系统
4. 开始录入数据并生成报表

## 使用说明

### 数据管理

1. 进入"数据管理"页面
2. 点击"新增记录"录入数据
3. 支持按分类、日期筛选数据
4. 支持导入Excel/CSV文件批量导入数据
5. 支持导出数据为Excel文件

### 报表中心

1. 进入"报表中心"页面
2. 选择筛选条件（分类、日期范围）
3. 点击"生成报表"查看统计结果
4. 点击"导出Excel"下载报表文件

### 用户管理（管理员）

1. 管理员用户登录后，点击"用户管理"
2. 可以查看、添加、编辑、删除用户
3. 可以设置用户角色（管理员/普通用户）

## API 接口

### 认证接口
- POST /api/auth/login - 用户登录
- POST /api/auth/register - 用户注册
- GET /api/auth/me - 获取当前用户

### 数据接口
- GET /api/data - 查询数据列表
- POST /api/data - 创建数据
- PUT /api/data/{id} - 更新数据
- DELETE /api/data/{id} - 删除数据
- POST /api/data/import - 批量导入数据
- GET /api/data/export - 导出数据

### 报表接口
- POST /api/reports/generate - 生成报表数据
- POST /api/reports/export - 导出报表

### 用户接口（管理员）
- GET /api/users - 获取用户列表
- POST /api/users - 创建用户
- PUT /api/users/{id} - 更新用户
- DELETE /api/users/{id} - 删除用户

## 开发模式

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发

```bash
cd frontend
npm install
npm run dev
```

## 注意事项

1. 首次部署时，数据库会自动创建
2. 建议定期备份数据库文件 (backend/sql_app.db)
3. 生产环境请修改 backend/app/utils/security.py 中的 SECRET_KEY
4. 建议配置HTTPS证书

## License

MIT License
