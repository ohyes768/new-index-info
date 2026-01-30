# 新股发行信息获取系统

自动获取沪深两市和港股的新股发行信息，支持命令行工具和 FastAPI RESTful API 两种使用方式。

## 功能特性

- ✅ 支持 A股和港股新股信息获取
- ✅ 完整的股票信息（申购代码、申购日期、发行价格、行业、公司简介等）
- ✅ 详细的市场分类（上海-主板、上海-科创板、深圳-主板、深圳-创业板、北交所）
- ✅ 以 Markdown 格式输出，便于阅读和二次处理
- ✅ 完善的日志记录
- ✅ **FastAPI RESTful API** - 通过 HTTP API 调用
- ✅ **Docker Compose 一键部署** - 微服务架构，易于扩展

## 技术栈

### 命令行工具
- **Python 3.10+**
- **akshare**: 免费财经数据接口（A股）
- **pandas**: 数据处理
- **requests**: HTTP 请求（港股）
- **beautifulsoup4**: HTML 解析（港股）

### FastAPI 服务
- **FastAPI**: 现代化的 Web 框架
- **Docker & Docker Compose**: 容器化部署
- **httpx**: 异步 HTTP 客户端

## 使用方式

本项目支持两种使用方式：

### 方式一：命令行工具（原有方式）

适合个人使用或简单场景。

### 方式二：FastAPI RESTful API（推荐）

适合集成到自动化工具（如 n8n）或需要长期运行的服务。

---

## 方式一：命令行工具

### 快速开始

### 1. 安装依赖

**方式一：使用 uv（推荐）**
```bash
# 创建虚拟环境
uv venv

# 安装依赖
uv pip install akshare pandas
```

**方式二：使用 pip**
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境并安装依赖
# Windows
.venv\Scripts\activate
pip install akshare pandas

# Linux/Mac
source .venv/bin/activate
pip install akshare pandas
```

### 2. 运行

**方式一：使用启动脚本（推荐）**
```bash
# Windows - 双击运行或在命令行执行
run.bat

# 或使用 scripts 目录下的脚本
scripts\run.bat

# Linux/Mac
bash scripts/run.sh
```

**方式二：直接运行 Python**
```bash
# Windows
cd deploy
..\.venv\Scripts\python.exe main_simple.py

# Linux/Mac
cd deploy
../.venv/bin/python main_simple.py
```

### 3. 输出示例

运行后会在控制台输出 Markdown 格式的新股信息：

```markdown
# 新股发行信息

**生成时间**: 2026-01-02 10:00:00
**新股数量**: 3 只

---

## 2026-01-05

### XYZ科技（301001）

| 项目 | 信息 |
|------|------|
| **申购代码** | 301001 |
| **申购日期** | 2026-01-05 |
| **发行价格** | 15.80元 |
| **发行数量** | 5000万股 |
| **申购上限** | 15万股 |
| **中签率** | 0.03% |
| **上市日期** | 2026-01-10 |
| **上市地点** | 深圳-创业板 |
| **所属行业** | 软件/互联网 |

**公司简介**:
XXX公司是一家...
```

## 集成到 n8n

在 n8n 中使用 "Execute Command" 节点：

**Windows:**
```
cd /d F:\github\person_project\new-index-info\deploy && ..\.venv\Scripts\python.exe main_simple.py
```

**Linux/Mac:**
```
cd /path/to/new-index-info/deploy && ../.venv/bin/python main_simple.py
```

然后读取标准输出作为后续节点的输入，添加钉钉节点推送 Markdown 内容。

---

## 方式二：FastAPI RESTful API

### 架构设计

采用 **独立后端服务** 架构：

```
n8n / 客户端
    ↓
├── A-Stock Service (8001) - A股新股服务
└── HK-Stock Service (8002) - 港股新股服务
```

### 快速开始

#### 1. 前置要求

安装 Docker 和 Docker Compose：
```bash
# 验证安装
docker --version
docker-compose --version
```

#### 2. 构建镜像

```bash
bash scripts/build.sh
```

#### 3. 启动服务

```bash
bash scripts/start.sh
```

#### 4. 测试 API

```bash
# A股服务健康检查
curl http://localhost:8001/health

# 获取 A股新股信息
curl http://localhost:8001/api/stocks

# 港股服务健康检查
curl http://localhost:8002/health

# 获取港股新股信息
curl http://localhost:8002/api/stocks
```

### API 端点

#### A股服务（端口 8001）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | A股服务健康检查 |
| `/api/stocks` | GET | 获取 A股新股信息 |

#### 港股服务（端口 8002）

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 港股服务健康检查 |
| `/api/stocks` | GET | 获取港股新股信息 |

#### 响应格式

**成功响应**：
```json
{
  "success": true,
  "market": "A股",
  "data": "# A股新股发行信息\n...",
  "subscribable_count": 2,
  "future_count": 5
}
```

**错误响应**：
```json
{
  "error": "服务暂时不可用"
}
```

### 配置说明

编辑 `docker/.env` 文件自定义配置：

```bash
# 日志级别
LOG_LEVEL=INFO

# A股服务配置
FETCH_TIMEOUT=10
MAX_RETRIES=3

# 港股服务配置
MIN_INTERVAL=5
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose -f docker/docker-compose.yml logs -f

# 查看 A股服务日志
docker-compose -f docker/docker-compose.yml logs -f a_stock_service

# 查看港股服务日志
docker-compose -f docker/docker-compose.yml logs -f hk_stock_service
```

### 停止服务

```bash
bash scripts/stop.sh
```

### 集成到 n8n 2.x

在 n8n 中使用 **HTTP Request** 节点：

1. **节点配置**：
   - Method: `GET`
   - URL: `http://your-server:8001/api/stocks`（A股）或 `http://your-server:8002/api/stocks`（港股）
   - Authentication: `None`

2. **响应处理**：
   - 使用 JSON 数据的 `data` 字段（Markdown 格式）
   - 使用 `subscribable_count` 和 `future_count` 进行条件判断

3. **示例 Workflow**：
   ```
   HTTP Request → IF (subscribable_count > 0) → 钉钉/企业微信推送
   ```

### 项目结构（FastAPI 版本）

```
new-index-info/
├── backend/                          # FastAPI 后端服务
│   ├── a_stock_service/              # A股服务
│   │   ├── main.py
│   │   ├── models/                   # 数据模型
│   │   ├── services/                 # 业务逻辑
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── hk_stock_service/             # 港股服务
│       ├── main.py
│       ├── models/
│       ├── services/
│       ├── Dockerfile
│       └── requirements.txt
├── docker/                           # Docker 配置
│   ├── docker-compose.yml            # 服务编排
│   └── .env.example                  # 环境变量模板
├── scripts/                          # 启动脚本
│   ├── build.sh
│   ├── start.sh
│   └── stop.sh
└── deploy/                           # 保留命令行工具
    ├── Amarket/
    └── Hmarket/
```

---

## 项目结构（命令行版本）

```
new-index-info/
├── deploy/                       # 主程序目录
│   ├── models.py                 # 数据模型
│   ├── services.py               # 所有服务模块
│   ├── main_simple.py            # 主入口
│   └── DEPLOY_README.md          # 部署说明
├── scripts/                      # 启动脚本
│   ├── run.bat                   # Windows 启动脚本
│   └── run.sh                    # Linux/Mac 启动脚本
├── logs/                         # 日志文件（自动创建）
├── docs/                         # 文档
│   └── 需求文档.md
├── discuss/                      # 讨论文档
│   └── 设计文档.md
├── README.md                     # 项目说明
└── DEPLOY_README.md              # 部署说明（根目录副本）
```

## 日志

日志文件位于 `logs/` 目录，按日期分割：

```
logs/new-index-info-2026-01-02.log
```

## 常见问题

### 1. 获取不到数据

- 检查网络连接
- 检查 akshare API 是否变化

### 2. 输出格式不正确

- 检查 Markdown 格式化逻辑
- 确保特殊字符已转义

### 3. n8n 无法读取输出

- 检查标准输出是否正确
- 确保 print() 语句在最后执行

## 代码架构

### 文件说明

**deploy/models.py** (约 100 行)
- 定义 NewStockInfo 数据类
- 包含所有新股信息字段

**deploy/services.py** (约 500 行)
- DataFetcher: 数据获取服务
- DataProcessor: 数据处理服务
- MarkdownFormatter: 格式化服务
- 日志配置函数

**deploy/main_simple.py** (约 70 行)
- 主流程编排
- 异常处理

### 代码规范

- 使用强类型数据结构（dataclass）
- 详细的日志记录
- 清晰的模块划分
- 单个文件不超过 500 行

## 部署到服务器

项目设计简洁，只需复制 3 个文件即可在服务器上运行：

### 快速部署

**1. 复制文件到服务器**
```bash
scp deploy/*.py user@server:/path/to/project/
scp deploy/requirements.txt user@server:/path/to/project/
```

**2. 安装依赖**
```bash
ssh user@server
cd /path/to/project
pip install -r requirements.txt
```

**3. 运行**
```bash
python main_simple.py
```

详细说明请参考 [DEPLOY_README.md](DEPLOY_README.md)

### 定时任务

**Linux Crontab:**
```bash
# 每天早上9点执行
0 9 * * * cd /path/to/project && python main_simple.py
```

**Windows 计划任务:**
```bash
# 创建任务计划程序，定时运行
python C:\path\to\project\main_simple.py
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
