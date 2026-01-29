"""
Markdown 格式化服务

负责将新股数据格式化为 Markdown 文本
"""

import sys
from datetime import datetime
from typing import List
from models import NewStockInfo
from .processor import DataProcessor


class MarkdownFormatter:
    """Markdown 格式化服务类"""

    def __init__(self):
        pass

    def format_new_stocks(self, subscribable_stocks: List[NewStockInfo], future_stocks: List[NewStockInfo] = None) -> str:
        """格式化新股信息为 Markdown，分类展示

        Args:
            subscribable_stocks: 当前可申购的新股列表
            future_stocks: 未来未开放申购的新股列表

        Returns:
            str: Markdown 格式的文本
        """
        print("INFO: 开始格式化新股信息...", file=sys.stderr)

        # 如果两类股票都为空，返回空数据格式
        if not subscribable_stocks and not future_stocks:
            return self._format_empty()

        # 构建 Markdown
        lines = []

        # 总标题
        lines.append("# A股新股发行信息")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # 第一部分：当前可申购的新股
        if subscribable_stocks:
            lines.append("---")
            lines.append("")
            lines.append("## 一、当前可申购的新股")
            lines.append("")
            lines.append(f"**数量**: {len(subscribable_stocks)} 只")
            lines.append("")

            # 按日期分组
            processor = DataProcessor()
            grouped = processor.group_by_date(subscribable_stocks)

            # 遍历每个日期
            for date_str, date_stocks in sorted(grouped.items()):
                lines.append(f"### {date_str}")
                lines.append("")

                for stock in date_stocks:
                    lines.extend(self._format_stock(stock))
                    lines.append("")

        # 第二部分：未来未开放申购的新股
        if future_stocks:
            lines.append("---")
            lines.append("")
            lines.append("## 二、未来14天即将开放申购的新股")
            lines.append("")
            lines.append(f"**数量**: {len(future_stocks)} 只")
            lines.append("")

            # 按日期分组
            processor = DataProcessor()
            grouped = processor.group_by_date(future_stocks)

            # 遍历每个日期
            for date_str, date_stocks in sorted(grouped.items()):
                lines.append(f"### {date_str}")
                lines.append("")

                for stock in date_stocks:
                    lines.extend(self._format_stock(stock))
                    lines.append("")

        markdown = "\n".join(lines)

        print("INFO: Markdown 格式化完成", file=sys.stderr)
        return markdown

    def _format_stock(self, stock: NewStockInfo) -> List[str]:
        """格式化单只股票信息

        Args:
            stock: 新股信息

        Returns:
            List[str]: Markdown 行列表
        """
        lines = []

        # 股票基本信息
        lines.append(f"### {stock.stock_name}（{stock.stock_code}）")
        lines.append("")

        # 信息表格
        lines.append("| 项目 | 信息 |")
        lines.append("|------|------|")
        lines.append(f"| **申购代码** | {stock.subscription_code} |")

        # 优先使用日期范围，如果没有则使用单个日期
        if stock.issue_date_range:
            lines.append(f"| **申购日期** | {stock.issue_date_range} |")
        elif stock.issue_date:
            lines.append(f"| **申购日期** | {stock.issue_date.strftime('%Y-%m-%d')} |")

        lines.append(f"| **发行价格** | {stock.get_formatted_price()} |")

        if stock.issue_quantity:
            lines.append(f"| **发行数量** | {stock.issue_quantity:.0f}万股 |")

        if stock.subscription_limit:
            lines.append(f"| **申购上限** | {stock.subscription_limit:.0f}万股 |")

        if stock.lottery_rate:
            lines.append(f"| **中签率** | {stock.lottery_rate}% |")

        if stock.listing_date:
            lines.append(f"| **上市日期** | {stock.listing_date.strftime('%Y-%m-%d')} |")

        lines.append(f"| **上市地点** | {stock.market} |")
        lines.append(f"| **所属行业** | {stock.industry} |")

        # 公司简介（如果有）
        if stock.company_intro:
            lines.append(f"| **公司简介** | {stock.company_intro} |")

        lines.append("")

        return lines

    def _format_empty(self) -> str:
        """格式化空数据情况

        Returns:
            str: 空数据的 Markdown
        """
        lines = []
        lines.append("# A股新股发行信息")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 暂无新股信息")
        lines.append("")
        lines.append("当前暂无可申购的新股，未来14天也无即将开放申购的新股。")

        return "\n".join(lines)
