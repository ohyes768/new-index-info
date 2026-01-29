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

    # 数据获取配置
    FETCH_TIMEOUT: int = int(os.getenv("FETCH_TIMEOUT", "10"))
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    # 服务配置
    APP_NAME: str = "A股新股信息服务"
    VERSION: str = "1.0.0"


# 全局配置实例
config = Config()
