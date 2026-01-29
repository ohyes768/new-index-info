"""
新股信息 API Gateway - FastAPI 主入口

统一入口，路由转发到后端服务
"""

import os
from datetime import datetime
from typing import Final

import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config import config
from utils.logger import setup_logger

# 常量定义
DEFAULT_PORT: Final = 8000
SERVICE_TIMEOUT: Final = config.TIMEOUT


app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    docs_url=None,
    redoc_url=None
)

logger = setup_logger(level=config.LOG_LEVEL)


async def proxy_request(service_url: str, service_name: str, path: str = "/api/stocks") -> JSONResponse:
    """代理请求到后端服务

    Args:
        service_url: 后端服务地址
        service_name: 服务名称（用于日志）
        path: 请求路径

    Returns:
        JSONResponse: 代理的响应结果
    """
    try:
        logger.info(f"收到 {service_name} 新股信息请求")

        async with httpx.AsyncClient(timeout=SERVICE_TIMEOUT) as client:
            response = await client.get(f"{service_url}{path}")
            logger.info(f"{service_name} 服务响应状态码: {response.status_code}")
            return JSONResponse(content=response.json(), status_code=response.status_code)

    except httpx.TimeoutException:
        logger.error(f"{service_name} 服务请求超时")
        return JSONResponse(content={"error": "服务请求超时"}, status_code=503)
    except httpx.RequestError as e:
        logger.error(f"{service_name} 服务请求失败: {e}")
        return JSONResponse(content={"error": "服务暂时不可用"}, status_code=503)
    except Exception as e:
        logger.error(f"未预期的错误: {e}")
        return JSONResponse(content={"error": "内部服务错误"}, status_code=500)


@app.get("/health")
async def health_check() -> dict:
    """Gateway 健康检查端点"""
    return {
        "status": "ok",
        "service": "gateway",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/a-stock")
async def get_a_stock() -> JSONResponse:
    """代理 A股新股信息请求，转发请求到 A股后端服务"""
    return await proxy_request(config.A_STOCK_SERVICE_URL, "A股")


@app.get("/api/hk-stock")
async def get_hk_stock() -> JSONResponse:
    """代理港股新股信息请求，转发请求到港股后端服务"""
    return await proxy_request(config.HK_STOCK_SERVICE_URL, "港股")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc) -> JSONResponse:
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(status_code=500, content={"error": "内部服务错误"})


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", str(DEFAULT_PORT)))

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level=config.LOG_LEVEL.lower(),
        access_log=True
    )
