# 新股发行信息获取系统

自动获取未来10天内沪深两市的新股发行信息，并以 Markdown 格式输出到控制台。

## 功能特性

- ✅ 自动获取未来10天的新股发行信息
- ✅ 完整的股票信息（申购代码、申购日期、发行价格、行业、公司简介等）
- ✅ 详细的市场分类（上海-主板、上海-科创板、深圳-主板、深圳-创业板、北交所）
- ✅ 以 Markdown 格式输出，便于阅读和二次处理
- ✅ 完善的日志记录
- ✅ 简洁的代码架构（仅 3 个 Python 文件）

## 技术栈

- **Python 3.10+**
- **akshare**: 免费财经数据接口
- **pandas**: 数据处理
- **uv**: 现代化的包管理工具（可选）

## 快速开始

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

## 项目结构

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
