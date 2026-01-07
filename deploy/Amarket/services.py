"""
服务模块

包含所有业务逻辑服务：日志、数据获取、数据处理、格式化
"""

import logging
import sys
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
from models import NewStockInfo


# ============================================================================
# 日志工具
# ============================================================================

def setup_logger(
    name: str = "new-index-info",
    level: int = logging.INFO,
    log_dir: Optional[Path] = None
) -> logging.Logger:
    """设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_dir: 日志文件目录，默认为 logs/

    Returns:
        logging.Logger: 配置好的日志记录器
    """
    if log_dir is None:
        log_dir = Path("logs")

    log_dir.mkdir(parents=True, exist_ok=True)

    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 避免重复添加 handler
    if logger.handlers:
        return logger

    # 日志格式
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器（每天一个文件）
    log_file = log_dir / f"new-index-info-{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# 全局日志记录器
_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """获取全局日志记录器"""
    global _logger

    if _logger is None:
        _logger = setup_logger()

    return _logger


# ============================================================================
# 数据获取服务
# ============================================================================

class DataFetcher:
    """数据获取服务类"""

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """初始化数据获取服务

        Args:
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = get_logger()

    def fetch_new_stocks(self) -> List[NewStockInfo]:
        """获取新股发行信息

        Returns:
            List[NewStockInfo]: 新股信息列表

        Raises:
            Exception: 当数据获取失败时
        """
        print("INFO: 开始获取新股发行信息...", file=sys.stderr)

        try:
            # 调用 akshare API 获取新股数据
            df = ak.stock_new_ipo_cninfo()

            if df is None or df.empty:
                print("WARNING: 未获取到新股数据", file=sys.stderr)
                return []

            print(f"INFO: 成功获取到 {len(df)} 条新股原始数据", file=sys.stderr)
            print(f"DEBUG: 数据列: {df.columns.tolist()}", file=sys.stderr)

            # 转换为 NewStockInfo 对象列表
            new_stocks = self._parse_dataframe(df)

            print(f"INFO: 成功解析 {len(new_stocks)} 条新股信息", file=sys.stderr)
            return new_stocks

        except Exception as e:
            print(f"ERROR: 获取新股数据时出错: {e}", file=sys.stderr)
            raise

    def _parse_dataframe(self, df: pd.DataFrame) -> List[NewStockInfo]:
        """解析 DataFrame 为 NewStockInfo 对象列表

        Args:
            df: akshare 返回的 DataFrame

        Returns:
            List[NewStockInfo]: 新股信息列表
        """
        new_stocks = []

        for _, row in df.iterrows():
            try:
                # 获取原始申购日期和网上申购日期
                issue_date_raw = row.get("申购日期")
                # 使用列索引直接访问，避免中文列名问题
                online_start = row.iloc[9]  # 网上申购日期
                online_end = row.iloc[10]   # 网上申购日期结束

                # 组合日期范围字符串
                issue_date_range = None
                if pd.notna(online_start) and pd.notna(online_end):
                    # 如果有开始和结束日期，组合成范围
                    start_str = str(online_start)[:10]
                    end_str = str(online_end)[:10]
                    issue_date_range = f"{start_str}至{end_str}"
                    # print(f"DEBUG: 股票 {row.get('证券简称')}: 组合日期范围 {issue_date_range}", file=sys.stderr)
                elif pd.notna(online_end):
                    # 如果只有结束日期，使用结束日期作为范围
                    end_str = str(online_end)[:10]
                    issue_date_range = f"{end_str}至{end_str}"
                    # print(f"DEBUG: 股票 {row.get('证券简称')}: 使用结束日期作为范围 {issue_date_range}", file=sys.stderr)
                elif pd.notna(issue_date_raw):
                    # 如果只有单个日期，使用该日期作为范围
                    date_str = str(issue_date_raw)[:10] if len(str(issue_date_raw)) >= 10 else str(issue_date_raw)
                    issue_date_range = f"{date_str}至{date_str}"
                    # print(f"DEBUG: 股票 {row.get('证券简称')}: 使用单个日期作为范围 {issue_date_range}", file=sys.stderr)

                # 根据实际返回字段进行解析
                # 字段映射基于 ak.stock_new_ipo_cninfo() 的返回结果
                stock_info = NewStockInfo(
                    stock_code=str(row.get("证劵代码", "")),
                    stock_name=str(row.get("证券简称", "")),
                    issue_date=self._parse_date(issue_date_raw),
                    issue_date_range=issue_date_range,  # 新增：保存组合后的日期范围
                    subscription_code=str(row.get("证劵代码", "")),  # 申购代码通常与股票代码相同
                    issue_price=self._parse_float(row.get("发行价")),
                    issue_quantity=self._parse_float(row.get("总发行数量")),
                    subscription_limit=self._parse_float(row.get("网上申购上限")),
                    lottery_rate=self._format_lottery_rate(row.get("上网发行中签率")),
                    listing_date=self._parse_date(row.get("上市日期")),
                    market=self._determine_market(str(row.get("证劵代码", ""))),
                    company_intro="",  # 该API不提供公司简介
                    industry="",       # 该API不提供行业信息
                    underwriter=""     # 该API不提供主承销商信息
                )
                new_stocks.append(stock_info)

            except Exception as e:
                print(f"WARNING: 解析单条数据时出错: {e}, 行数据: {row.to_dict()}", file=sys.stderr)
                continue

        return new_stocks

    def _enrich_stock_info(self, stocks: List[NewStockInfo]) -> List[NewStockInfo]:
        """补充股票的行业和简介信息

        Args:
            stocks: 新股信息列表

        Returns:
            List[NewStockInfo]: 补充信息后的新股列表
        """
        print("INFO: 开始补充股票详细信息...", file=sys.stderr)

        for stock in stocks:
            try:
                # 调用API获取公司简介
                df_profile = ak.stock_profile_cninfo(symbol=stock.stock_code)

                if df_profile is not None and not df_profile.empty:
                    # 获取行业
                    industry = df_profile.iloc[0].get("所属行业", "")
                    if industry:
                        stock.industry = str(industry)

                    # 获取公司简介（直接使用主营业务）
                    intro = df_profile.iloc[0].get("主营业务", "")

                    if intro and not pd.isna(intro):
                        # 限制简介长度，避免过长
                        intro_str = str(intro).strip()
                        if len(intro_str) > 500:
                            intro_str = intro_str[:500] + "..."
                        stock.company_intro = intro_str

                    print(f"DEBUG: 成功补充 {stock.stock_code} 的详细信息", file=sys.stderr)

            except Exception as e:
                print(f"WARNING: 补充 {stock.stock_code} 的详细信息时出错: {e}", file=sys.stderr)
                continue

        return stocks

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """解析日期字符串

        Args:
            date_str: 日期字符串

        Returns:
            Optional[datetime]: 解析后的日期对象
        """
        if pd.isna(date_str) or not date_str:
            return None

        try:
            # 尝试多种日期格式
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
                try:
                    return datetime.strptime(str(date_str), fmt)
                except ValueError:
                    continue
        except Exception as e:
            print(f"DEBUG: 日期解析失败: {date_str}, 错误: {e}", file=sys.stderr)

        return None

    def _parse_float(self, value: any) -> Optional[float]:
        """解析浮点数

        Args:
            value: 待解析的值

        Returns:
            Optional[float]: 解析后的浮点数
        """
        if pd.isna(value) or value is None or value == "":
            return None

        try:
            # 去除单位（如 "万股"）
            if isinstance(value, str):
                value = value.replace("万股", "").replace("万", "").strip()

            return float(value)
        except (ValueError, TypeError):
            return None

    def _format_lottery_rate(self, value: any) -> Optional[str]:
        """格式化中签率

        Args:
            value: 中签率值（可能是小数或百分比）

        Returns:
            Optional[str]: 格式化后的中签率字符串
        """
        if pd.isna(value) or value is None or value == "":
            return None

        try:
            rate = float(value)
            # 如果是小于1的小数，转换为百分比
            if rate < 1:
                return f"{rate * 100:.4f}"
            else:
                return f"{rate:.4f}"
        except (ValueError, TypeError):
            return str(value) if value else None

    def _determine_market(self, stock_code: str) -> str:
        """根据股票代码判断市场

        Args:
            stock_code: 股票代码

        Returns:
            str: 详细市场信息（"上海-主板"、"上海-科创板"、"深圳-主板"、"深圳-创业板"、"北交所"等）
        """
        if stock_code.startswith("60"):
            return "上海-主板"
        elif stock_code.startswith("68"):
            return "上海-科创板"
        elif stock_code.startswith("00"):
            return "深圳-主板"
        elif stock_code.startswith("30"):
            return "深圳-创业板"
        elif stock_code.startswith(("8", "4", "92", "93")):
            return "北交所"
        return ""


# ============================================================================
# 数据处理服务
# ============================================================================

class DataProcessor:
    """数据处理服务类"""

    def __init__(self):
        """初始化数据处理服务"""
        self.logger = get_logger()

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


# ============================================================================
# Markdown 格式化服务
# ============================================================================

class MarkdownFormatter:
    """Markdown 格式化服务类"""

    def __init__(self):
        self.logger = get_logger()

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
