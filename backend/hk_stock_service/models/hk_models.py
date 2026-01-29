"""
港股新股信息数据模型

定义港股新股发行信息的强类型数据结构
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class HKNewStockInfo:
    """港股新股信息模型

    包含港股新股发行的所有关键信息

    Attributes:
        stock_code: 股票代码（如 "00700"）
        stock_name: 股票名称（中文，如 "腾讯控股"）
        stock_name_en: 股票英文名称
        offer_price_range: 招股价区间（如 "250.00-280.00"）
        raised_amount: 集资额（港元，字符串格式）
        offer_shares: 发售股数（股）
        subscription_ratio: 认购倍数
        subscription_date: 申购日期（datetime对象，用于筛选）
        subscription_date_range: 申购日期范围（原始字符串，如 "2025-12-31至2026-01-06"）
        listing_date: 上市日期（datetime对象）
        market: 市场（默认"港股"）
        industry: 所属行业
        company_intro: 公司简介
    """
    stock_code: str
    stock_name: str
    stock_name_en: Optional[str] = None
    offer_price_range: Optional[str] = None
    raised_amount: Optional[str] = None
    offer_shares: Optional[str] = None
    subscription_ratio: Optional[str] = None
    subscription_date: Optional[datetime] = None
    subscription_date_range: Optional[str] = None  # 新增：保存原始日期范围
    listing_date: Optional[datetime] = None
    market: str = "港股"
    industry: str = ""
    company_intro: str = ""

    def is_price_determined(self) -> bool:
        """判断招股价是否已确定

        Returns:
            bool: 价格是否已确定
        """
        if not self.offer_price_range:
            return False

        # 如果是区间，说明价格已确定
        return True

    def get_formatted_price(self) -> str:
        """获取格式化的招股价字符串

        Returns:
            str: 格式化的价格（如 "250.00-280.00港元" 或 "待定"）
        """
        if self.is_price_determined():
            return f"{self.offer_price_range}港元"
        return "待定"

    def get_formatted_shares(self) -> str:
        """获取格式化的发售股数

        Returns:
            str: 格式化的股数（如 "1,000万股"）
        """
        if not self.offer_shares:
            return "待定"

        try:
            # 尝试格式化数字
            shares = float(self.offer_shares.replace(",", ""))
            if shares >= 100000000:
                return f"{shares/100000000:.2f}亿股"
            elif shares >= 10000:
                return f"{shares/10000:.0f}万股"
            else:
                return f"{shares:.0f}股"
        except (ValueError, AttributeError):
            return self.offer_shares

    def get_formatted_raised_amount(self) -> str:
        """获取格式化的集资额

        Returns:
            str: 格式化的集资额（如 "15.5亿港元"）
        """
        if not self.raised_amount:
            return "待定"

        # 移除已有格式并重新格式化
        try:
            # 移除逗号和单位
            amount_str = str(self.raised_amount).replace(",", "").replace("HK$", "").strip()
            amount = float(amount_str)

            if amount >= 100000000:
                return f"{amount/100000000:.2f}亿港元"
            elif amount >= 10000:
                return f"{amount/10000:.0f}万港元"
            else:
                return f"{amount:.0f}港元"
        except (ValueError, AttributeError):
            return f"{self.raised_amount}港元"
