"""
数据处理服务

负责新股数据的筛选、验证和分组
"""

import sys
from datetime import datetime, timedelta
from typing import List
from models import NewStockInfo


class DataProcessor:
    """数据处理服务类"""

    def __init__(self):
        """初始化数据处理服务"""
        pass

    def filter_subscribable_stocks(self, stocks: List[NewStockInfo]) -> List[NewStockInfo]:
        """筛选当前可申购的新股

        筛选条件：申购日期范围内包含今天的新股

        Args:
            stocks: 新股信息列表

        Returns:
            List[NewStockInfo]: 筛选后的新股列表
        """
        print("INFO: 开始筛选当前可申购的新股...", file=sys.stderr)

        today = datetime.now().date()
        filtered_stocks = []

        for stock in stocks:
            if not stock.issue_date_range:
                continue

            # 解析日期范围字符串
            start_date, end_date = self._parse_date_range(stock.issue_date_range)

            if start_date is None or end_date is None:
                continue

            # 筛选条件：今天在申购日期范围内
            if start_date <= today <= end_date:
                filtered_stocks.append(stock)
                print(f"DEBUG: 符合条件: {stock.stock_code} - {stock.stock_name} ({start_date} 至 {end_date})", file=sys.stderr)

        print(f"INFO: 筛选完成，找到 {len(filtered_stocks)} 只当前可申购的新股", file=sys.stderr)

        # 按申购日期排序
        filtered_stocks.sort(key=lambda x: x.issue_date or datetime.min)

        return filtered_stocks

    def filter_future_unopened_stocks(self, stocks: List[NewStockInfo], future_days: int = 14) -> List[NewStockInfo]:
        """筛选未来指定天数内还未开放申购的新股

        筛选条件：申购开始日期在今天之后，且在未来指定天数内

        Args:
            stocks: 新股信息列表
            future_days: 查询未来天数，默认14天

        Returns:
            List[NewStockInfo]: 筛选后的新股列表
        """
        print(f"INFO: 开始筛选未来 {future_days} 天内未开放申购的新股...", file=sys.stderr)

        today = datetime.now().date()
        future_date = today + timedelta(days=future_days)
        filtered_stocks = []

        for stock in stocks:
            if not stock.issue_date_range:
                continue

            # 解析日期范围字符串
            start_date, end_date = self._parse_date_range(stock.issue_date_range)

            if start_date is None or end_date is None:
                continue

            # 筛选条件：申购开始日期在今天之后，且在未来指定天数内
            if today < start_date <= future_date:
                filtered_stocks.append(stock)
                print(f"DEBUG: 符合条件: {stock.stock_code} - {stock.stock_name} ({start_date} 至 {end_date})", file=sys.stderr)

        print(f"INFO: 筛选完成，找到 {len(filtered_stocks)} 只未来 {future_days} 天内未开放申购的新股", file=sys.stderr)

        # 按申购日期排序
        filtered_stocks.sort(key=lambda x: x.issue_date or datetime.min)

        return filtered_stocks

    def _parse_date_range(self, date_range_str: str):
        """解析日期范围字符串

        Args:
            date_range_str: 日期范围字符串，格式如 "2025-12-23至2025-12-24"

        Returns:
            tuple: (开始日期, 结束日期) 的 date 对象元组，解析失败返回 (None, None)
        """
        if not date_range_str or "至" not in date_range_str:
            return None, None

        try:
            parts = date_range_str.split("至")
            if len(parts) != 2:
                return None, None

            start_str = parts[0].strip()[:10]
            end_str = parts[1].strip()[:10]

            start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_str, "%Y-%m-%d").date()

            return start_date, end_date

        except Exception as e:
            print(f"DEBUG: 日期范围解析失败: {date_range_str}, 错误: {e}", file=sys.stderr)
            return None, None

    def group_by_date(self, stocks: List[NewStockInfo]) -> dict:
        """按发行日期分组

        Args:
            stocks: 新股信息列表

        Returns:
            dict: 按日期分组的新股字典
        """
        grouped = {}

        for stock in stocks:
            if stock.issue_date is None:
                continue

            date_str = stock.issue_date.strftime("%Y-%m-%d")

            if date_str not in grouped:
                grouped[date_str] = []

            grouped[date_str].append(stock)

        return grouped

    def validate_data(self, stocks: List[NewStockInfo]) -> List[NewStockInfo]:
        """验证数据完整性

        Args:
            stocks: 新股信息列表

        Returns:
            List[NewStockInfo]: 验证通过的新股列表
        """
        print("INFO: 开始验证数据完整性...", file=sys.stderr)

        valid_stocks = []

        for stock in stocks:
            # 基本字段验证
            if not stock.stock_code or not stock.stock_name:
                print(f"WARNING: 股票代码或名称为空，跳过: {stock}", file=sys.stderr)
                continue

            if not stock.issue_date:
                print(f"WARNING: 发行日期为空，跳过: {stock.stock_code}", file=sys.stderr)
                continue

            valid_stocks.append(stock)

        print(f"INFO: 数据验证完成，有效数据 {len(valid_stocks)}/{len(stocks)} 条", file=sys.stderr)

        return valid_stocks
