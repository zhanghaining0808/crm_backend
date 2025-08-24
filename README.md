# CRM Backend 项目

这是一个基于FastAPI的CRM（客户关系管理）后端系统，使用Python venv作为虚拟环境管理工具。

## 项目特性

- 🚀 基于FastAPI框架，高性能异步API
- 🔐 JWT身份认证和授权
- 🗄️ SQLModel ORM，支持多种数据库
- 📧 邮件任务管理
- 👥 用户和客户管理
- 🔧 完整的日志系统
- 🌐 CORS支持，前端友好

## 技术栈

- **Python**: 3.11+
- **Web框架**: FastAPI
- **ORM**: SQLModel
- **数据库**: PostgreSQL (psycopg2)
- **认证**: JWT (python-jose)
- **包管理**: pip + venv
- **日志**: loguru
- **服务器**: uvicorn

## 环境要求

- Python 3.11 或更高版本
- PostgreSQL 数据库

## 快速开始

### 1. 克隆项目

```bash
git clone <your-repository-url>
cd CRM_backend
```

### 2. 创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 3. 环境配置

复制.env.template 创建 `.env` 文件并配置对应环境变量

### 4. 启动项目

```bash
# 确保虚拟环境已激活
python main.py
```

### 5. 访问API

- API文档: http://localhost:8000/docs
- 交互式API文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/api/health

## 项目结构

```
CRM_backend/
├── crm_backend/           # 主要代码目录
│   ├── controls/         # 控制器层
│   ├── models/           # 数据模型
│   ├── db/              # 数据库相关
│   ├── utils/           # 工具函数
│   └── middleware/      # 中间件
├── logs/                # 日志文件
├── main.py             # 应用入口
├── requirements.txt     # 项目依赖
└── README.md          # 项目说明
```
