"""
A股新股信息服务 - FastAPI 主入口

提供 A股新股信息的 RESTful API
"""

import os
import sys
from datetime import datetime
from typing import Final

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from config import config
from services import DataFetcher, DataProcessor, MarkdownFormatter

# 常量定义
DEFAULT_PORT: Final = 8001
FUTURE_DAYS: Final = 14
SERVICE_NAME: Final = "A股"


app = FastAPI(
    title=config.APP_NAME,
    version=config.VERSION,
    docs_url=None,
    redoc_url=None
)


def log_info(message: str) -> None:
    """统一的日志输出函数"""
    print(f"INFO: [{datetime.now()}] {message}", file=sys.stderr)


def log_error(message: str) -> None:
    """统一的错误日志输出函数"""
    print(f"ERROR: {message}", file=sys.stderr)


@app.get("/health")
async def health_check() -> dict:
    """健康检查端点"""
    return {
        "status": "ok",
        "service": "a-stock",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/stocks")
async def get_new_stocks() -> dict:
    """获取 A股新股信息

    Returns:
        包含新股信息的响应，字段包括:
        - success: 是否成功
        - market: 市场类型
        - data: Markdown 格式的新股信息
        - subscribable_count: 当前可申购新股数量
        - future_count: 未来新股数量
    """
    try:
        log_info(f"收到 {SERVICE_NAME} 新股信息请求")

        fetcher = DataFetcher(
            timeout=config.FETCH_TIMEOUT,
            max_retries=config.MAX_RETRIES
        )
        stocks = fetcher.fetch_new_stocks()

        if not stocks:
            log_info("未获取到新股数据")
            return {
                "success": True,
                "market": SERVICE_NAME,
                "data": "",
                "subscribable_count": 0,
                "future_count": 0
            }

        processor = DataProcessor()
        valid_stocks = processor.validate_data(stocks)
        subscribable_stocks = processor.filter_subscribable_stocks(valid_stocks)
        future_stocks = processor.filter_future_unopened_stocks(valid_stocks, future_days=FUTURE_DAYS)

        # 补充详细信息（仅对筛选后的股票）
        all_stocks = subscribable_stocks + future_stocks
        if all_stocks:
            all_stocks = fetcher._enrich_stock_info(all_stocks)

        formatter = MarkdownFormatter()
        markdown = formatter.format_new_stocks(subscribable_stocks, future_stocks)

        log_info(f"成功返回 {SERVICE_NAME} 数据 - 可申购: {len(subscribable_stocks)}, 未来: {len(future_stocks)}")

        return {
            "success": True,
            "market": SERVICE_NAME,
            "data": markdown,
            "subscribable_count": len(subscribable_stocks),
            "future_count": len(future_stocks)
        }

    except Exception as e:
        log_error(f"获取 {SERVICE_NAME} 数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc) -> JSONResponse:
    """全局异常处理器"""
    log_error(f"未处理的异常: {exc}")
    return JSONResponse(status_code=500, content={"error": "服务暂时不可用"})


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
