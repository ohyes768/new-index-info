# 新股发行信息获取系统 - API 接口文档

**版本**: v2.0.0
**最后更新**: 2026-01-29
**API 类型**: RESTful API
**基础 URL**: `http://localhost:8010`

---

## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-01-29 | v2.0.0 | 新增 FastAPI RESTful API 接口 |

---

## 目录

- [API 概述](#api-概述)
- [Gateway 接口](#gateway-接口)
- [后端服务接口](#后端服务接口)
- [响应格式](#响应格式)
- [错误处理](#错误处理)
- [部署说明](#部署说明)
- [使用示例](#使用示例)

---

## API 概述

### 架构说明

新股信息 API 采用 **Gateway + 后端服务** 微服务架构：

```
客户端 → Gateway (8000) → 后端服务
                        ├─ A股服务 (8001)
                        └─ 港股服务 (8002)
```

### 访问方式

**推荐方式**：通过 Gateway 访问（统一入口）
- 基础 URL：`http://localhost:8010`
- 优点：统一接口、简化配置、便于扩展

**直接方式**：直接访问后端服务（内部网络）
- A股服务：`http://localhost:8001`
- 港股服务：`http://localhost:8002`
- 注意：仅用于内部网络或开发调试

### 技术栈

- **框架**：FastAPI 0.104.1+
- **服务器**：Uvicorn (ASGI)
- **HTTP 客户端**：httpx（异步）
- **部署方式**：Docker Compose

---

## Gateway 接口

### 1. 健康检查

检查 Gateway 服务是否正常运行。

**请求**：
```
GET /health
```

**响应示例**：
```json
{
  "status": "ok",
  "service": "gateway",
  "timestamp": "2026-01-29T10:30:45.123456"
}
```

**字段说明**：
| 字段 | 类型 | 说明 |
|------|------|------|
| status | string | 服务状态，固定为 "ok" |
| service | string | 服务名称，固定为 "gateway" |
| timestamp | string | ISO 8601 格式的时间戳 |

**状态码**：
- `200 OK` - 服务正常

---

### 2. 获取 A股新股信息

获取当前可申购和未来 14 天内即将开放申购的 A股新股信息。

**请求**：
```
GET /api/a-stock
```

**响应示例**：
```json
{
  "success": true,
  "market": "A股",
  "data": "# A股新股发行信息\n\n**生成时间**: 2026-01-29 10:30:45\n**新股数量**: 3 只\n\n---\n\n## 当前可申购的新股\n\n### XX科技股份有限公司（688123）\n\n| 项目 | 信息 |\n|------|------|\n| **申购代码** | 788123 |\n| **申购日期** | 2026-01-25至2026-01-25 |\n...",
  "subscribable_count": 2,
  "future_count": 5
}
```

**字段说明**：
| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| market | string | 市场类型，固定为 "A股" |
| data | string | Markdown 格式的新股详细信息 |
| subscribable_count | number | 当前可申购的新股数量 |
| future_count | number | 未来 14 天内即将开放申购的新股数量 |

**状态码**：
- `200 OK` - 成功获取数据
- `503 Service Unavailable` - 后端服务超时或不可用
- `500 Internal Server Error` - 内部服务错误

**性能指标**：
- 响应时间：2-5 秒（取决于 akshare API）
- 超时时间：30 秒

---

### 3. 获取港股新股信息

获取当前可申购和未来 14 天内即将开放申购的港股新股信息。

**请求**：
```
GET /api/hk-stock
```

**响应示例**：
```json
{
  "success": true,
  "market": "港股",
  "data": "# 港股新股发行信息\n\n**生成时间**: 2026-01-29 10:30:45\n**新股数量**: 2 只\n\n---\n\n## 当前可申购的新股\n\n### 腾讯控股有限公司（00700）\n\n| 项目 | 信息 |\n|------|------|\n| **股票代码** | 00700 |\n| **申购日期** | 2026-01-25至2026-01-30 |\n...",
  "subscribable_count": 1,
  "future_count": 3
}
```

**字段说明**：
| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功 |
| market | string | 市场类型，固定为 "港股" |
| data | string | Markdown 格式的新股详细信息 |
| subscribable_count | number | 当前可申购的新股数量 |
| future_count | number | 未来 14 天内即将开放申购的新股数量 |

**状态码**：
- `200 OK` - 成功获取数据
- `503 Service Unavailable` - 后端服务超时或不可用
- `500 Internal Server Error` - 内部服务错误

**性能指标**：
- 响应时间：10-30 秒（需要爬取网页，有反爬间隔）
- 超时时间：30 秒

---

## 后端服务接口

以下接口仅用于内部网络通信，建议通过 Gateway 访问。

### A股服务（端口 8001）

#### 健康检查

**请求**：
```
GET http://localhost:8001/health
```

**响应**：
```json
{
  "status": "ok",
  "service": "a-stock",
  "timestamp": "2026-01-29T10:30:45.123456"
}
```

#### 获取新股信息

**请求**：
```
GET http://localhost:8001/api/stocks
```

**响应**：与 Gateway `/api/a-stock` 相同

---

### 港股服务（端口 8002）

#### 健康检查

**请求**：
```
GET http://localhost:8002/health
```

**响应**：
```json
{
  "status": "ok",
  "service": "hk-stock",
  "timestamp": "2026-01-29T10:30:45.123456"
}
```

#### 获取新股信息

**请求**：
```
GET http://localhost:8002/api/stocks
```

**响应**：与 Gateway `/api/hk-stock` 相同

---

## 响应格式

### 成功响应

所有成功响应都遵循以下格式：

```json
{
  "success": true,
  "market": "A股/港股",
  "data": "Markdown 格式的新股信息",
  "subscribable_count": N,
  "future_count": M
}
```

### Markdown 格式说明

`data` 字段包含完整的 Markdown 格式新股信息，结构如下：

```markdown
# [市场]新股发行信息

**生成时间**: YYYY-MM-DD HH:MM:SS
**新股数量**: X 只

---

## 当前可申购的新股

### 股票名称（股票代码）

| 项目 | 信息 |
|------|------|
| **申购代码** | XXXXXX |
| **申购日期** | YYYY-MM-DD至YYYY-MM-DD |
| **发行价格** | XX.XX元 |
| ... | ... |

---

## 未来14天即将开放申购的新股

...（同上格式）
```

### 错误响应

错误响应格式：

```json
{
  "error": "错误描述信息"
}
```

**常见错误**：
- `"服务请求超时"` - Gateway 到后端服务的请求超时（>30秒）
- `"服务暂时不可用"` - 后端服务不可用或网络错误
- `"内部服务错误"` - 未预期的内部错误

---

## 错误处理

### HTTP 状态码

| 状态码 | 说明 | 处理建议 |
|--------|------|----------|
| 200 OK | 成功 | 正常处理响应数据 |
| 500 Internal Server Error | 内部错误 | 检查日志，稍后重试 |
| 503 Service Unavailable | 服务不可用 | 检查后端服务状态，稍后重试 |

### 超时处理

**Gateway 超时**：
- 超时时间：30 秒
- 处理方式：返回 503 状态码和错误信息
- 建议：客户端应实现重试机制

**数据获取超时**：
- A股：10 秒（可配置）
- 港股：可配置（默认 10 秒）

### 重试策略

**推荐重试策略**：
1. 首次请求失败后，等待 5 秒重试
2. 第二次失败后，等待 10 秒重试
3. 第三次失败后，等待 30 秒重试
4. 超过 3 次失败后，记录错误并停止重试

---

## 部署说明

### 环境要求

- Docker 20.10+
- Docker Compose 3.8+
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

### 快速启动

#### 1. 构建镜像

```bash
bash scripts/build.sh
```

#### 2. 启动服务

```bash
bash scripts/start.sh
```

#### 3. 验证服务

```bash
# 测试健康检查
curl http://localhost:8010/health

# 测试 A股接口
curl http://localhost:8010/api/a-stock

# 测试港股接口
curl http://localhost:8010/api/hk-stock
```

### 配置说明

编辑 `docker/.env` 文件自定义配置：

```bash
# 日志级别
LOG_LEVEL=INFO

# Gateway 配置
GATEWAY_PORT=8010
TIMEOUT=30

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

# 查看 Gateway 日志
docker-compose -f docker/docker-compose.yml logs -f gateway

# 查看 A股服务日志
docker-compose -f docker/docker-compose.yml logs -f a_stock_service

# 查看港股服务日志
docker-compose -f docker/docker-compose.yml logs -f hk_stock_service
```

### 停止服务

```bash
bash scripts/stop.sh
```

---

## 使用示例

### cURL

#### A股新股信息

```bash
curl http://localhost:8010/api/a-stock
```

#### 港股新股信息

```bash
curl http://localhost:8010/api/hk-stock
```

### Python (requests)

```python
import requests

# 获取 A股新股信息
response = requests.get("http://localhost:8010/api/a-stock")
data = response.json()

if data["success"]:
    print(f"市场: {data['market']}")
    print(f"可申购: {data['subscribable_count']} 只")
    print(f"未来: {data['future_count']} 只")
    print(f"详细信息:\n{data['data']}")
else:
    print(f"错误: {data.get('error', '未知错误')}")
```

### n8n 2.x

**节点配置**：
1. 添加 **HTTP Request** 节点
2. 配置：
   - Method: `GET`
   - URL: `http://your-server:8010/api/a-stock`
   - Authentication: `None`

**后续处理**：
- 使用 JSON 数据的 `data` 字段（Markdown 格式）
- 使用 `subscribable_count` 和 `future_count` 进行条件判断
- 添加 IF 节点：`subscribable_count > 0` 时推送到钉钉

### JavaScript (fetch)

```javascript
// 获取 A股新股信息
fetch("http://localhost:8010/api/a-stock")
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(`市场: ${data.market}`);
      console.log(`可申购: ${data.subscribable_count} 只`);
      console.log(`未来: ${data.future_count} 只`);
      console.log(`详细信息:\n${data.data}`);
    } else {
      console.error(`错误: ${data.error}`);
    }
  })
  .catch(error => {
    console.error(`请求失败: ${error}`);
  });
```

---

## 性能优化建议

### 客户端优化

1. **缓存数据**：新股信息更新不频繁，可以缓存 5-10 分钟
2. **并发请求**：A股和港股接口可以并发请求
3. **超时设置**：客户端建议设置 60 秒超时（大于 Gateway 的 30 秒）

### 服务端优化

1. **水平扩展**：通过增加 Gateway 和后端服务实例扩展
2. **负载均衡**：使用 nginx 或 Traefik 进行负载均衡
3. **缓存机制**：后端服务添加 Redis 缓存，减少 API 调用

---

## 安全建议

### 生产环境部署

1. **添加认证**：
   - API Key 认证
   - JWT Token 认证
   - OAuth 2.0

2. **启用 HTTPS**：
   - 使用 nginx 反向代理
   - 配置 SSL 证书（Let's Encrypt）

3. **限流保护**：
   - 使用 slowapi 或类似库
   - 每分钟最多 60 次请求

4. **CORS 配置**：
   ```python
   from fastapi.middleware.cors import CORSMiddleware

   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-domain.com"],
       allow_methods=["GET"],
       allow_headers=["*"],
   )
   ```

5. **日志脱敏**：
   - 避免记录敏感信息
   - 定期清理日志

---

## 监控和告警

### 推荐监控指标

1. **服务可用性**：
   - Gateway 健康检查
   - 后端服务健康检查

2. **性能指标**：
   - 响应时间（P50、P95、P99）
   - 请求成功率
   - 错误率

3. **业务指标**：
   - 每日请求量
   - A股/新股数量变化

### 监控工具

- Prometheus + Grafana
- Datadog
- New Relic

---

## 常见问题

### Q1: 为什么港股接口响应很慢？

**A1**: 港股数据通过网页抓取获取，有 5 秒的反爬间隔，且需要访问详情页补充信息，响应时间通常在 10-30 秒。这是正常现象。

### Q2: 如何提高响应速度？

**A2**:
1. 使用客户端缓存，避免频繁请求
2. 服务端添加 Redis 缓存
3. 后台定时任务预加载数据

### Q3: 接口有调用频率限制吗？

**A3**: 目前没有限制，但建议客户端控制请求频率，避免对数据源造成压力。生产环境建议添加限流机制。

### Q4: 如何获取所有新股（不过滤）？

**A4**: 当前版本只返回筛选后的数据（当前可申购 + 未来14天）。如需获取所有数据，请使用命令行工具版本。

### Q5: 数据更新频率是多少？

**A5**:
- A股：akshare 实时更新（工作日交易时间）
- 港股：新浪财经每日更新
- 建议：客户端每天早上 9:00 请求一次即可

---

## 附录

### 相关文档

- [产品需求文档(PRD)](./需求文档.md)
- [技术设计文档(TDD)](./技术设计文档.md)
- [数据字典](./数据字典.md)
- [文档索引](./文档索引.md)
- [FastAPI 部署指南](./FASTAPI_DEPLOYMENT.md)

### 技术支持

- **Issues**: [GitHub Issues](https://github.com/your-repo/new-index-info/issues)
- **Email**: your-email@example.com

### 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v2.0.0 | 2026-01-29 | 初始版本，FastAPI RESTful API |

---

**文档结束**

© 2026 新股发行信息获取系统 | v2.0.0
