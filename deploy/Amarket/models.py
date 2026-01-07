"""
新股信息数据模型

定义新股发行信息的强类型数据结构
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NewStockInfo:
    """新股信息模型

    包含新股发行的所有关键信息

    Attributes:
        stock_code: 股票代码（如 "301001"）
        stock_name: 股票名称（如 "XYZ科技"）
        issue_date: 发行日期（datetime对象，用于筛选）
        issue_date_range: 发行日期范围（原始字符串，如 "2025-12-30至2026-01-05"）
        subscription_code: 申购代码（如 "301001"）
        issue_price: 发行价格（元，可能为None表示待定）
        issue_quantity: 发行数量（万股）
        subscription_limit: 申购上限（万股）
        lottery_rate: 中签率（% ，如 "0.03"）
        listing_date: 上市日期（datetime对象，可能为None）
        market: 上市地点（"上海"或"深圳"）
        company_intro: 公司简介
        industry: 所属行业
        underwriter: 主承销商
    """
    stock_code: str
    stock_name: str
    issue_date: datetime
    subscription_code: str
    issue_date_range: Optional[str] = None  # 新增：保存原始日期范围
    issue_price: Optional[float] = None
    issue_quantity: Optional[float] = None
    subscription_limit: Optional[float] = None
    lottery_rate: Optional[str] = None
    listing_date: Optional[datetime] = None
    market: str = ""
    company_intro: str = ""
    industry: str = ""
    underwriter: str = ""

    def get_market_code(self) -> str:
        """获取市场代码

        Returns:
            str: 市场代码（"SH"或"SZ"）
        """
        if self.stock_code.startswith("6") or self.stock_code.startswith("60"):
            return "SH"
        elif self.stock_code.startswith("0") or self.stock_code.startswith("3"):
            return "SZ"
        return ""

    def is_price_determined(self) -> bool:
        """判断发行价格是否已确定

        Returns:
            bool: 价格是否已确定
        """
        return self.issue_price is not None and self.issue_price > 0

    def get_formatted_price(self) -> str:
        """获取格式化的发行价格字符串

        Returns:
            str: 格式化的价格（如 "15.80元" 或 "待定"）
        """
        if self.is_price_determined():
            return f"{self.issue_price:.2f}元"
        return "待定"
