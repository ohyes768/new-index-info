"""
配置管理

从环境变量加载配置
"""

import os
from typing import Optional


class Config:
    """应用配置类"""

    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # 后端服务地址
    A_STOCK_SERVICE_URL: str = os.getenv("A_STOCK_SERVICE_URL", "http://a_stock_service:8001")
    HK_STOCK_SERVICE_URL: str = os.getenv("HK_STOCK_SERVICE_URL", "http://hk_stock_service:8002")

    # 请求超时配置
    TIMEOUT: int = int(os.getenv("TIMEOUT", "30"))

    # 服务配置
    APP_NAME: str = "新股信息 API Gateway"
    VERSION: str = "1.0.0"


# 全局配置实例
config = Config()
