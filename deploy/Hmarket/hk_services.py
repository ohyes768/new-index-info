"""
港股新股服务模块

包含港股新股的所有业务逻辑：日志、数据获取、数据处理、格式化
"""

import logging
import sys
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from hk_models import HKNewStockInfo


# ============================================================================
# 日志工具
# ============================================================================

def setup_logger(
    name: str = "hk-new-stock",
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
    log_file = log_dir / f"hk-new-stock-{datetime.now().strftime('%Y-%m-%d')}.log"
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
# 港股数据获取服务
# ============================================================================

class HKDataFetcher:
    """港股新股数据获取器（优化版）"""

    def __init__(self, timeout: int = 10, min_interval: int = 5):
        """初始化港股数据获取器

        Args:
            timeout: 请求超时时间（秒）
            min_interval: 最小请求间隔（秒），防止被封禁
        """
        self.base_url = "http://vip.stock.finance.sina.com.cn/q/view/hk_IPOList.php"
        self.timeout = timeout
        self.min_interval = min_interval
        self.last_request_time = 0
        self.logger = get_logger()

        # 随机User-Agent池
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        ]

    def fetch_hk_new_stocks(self) -> List[HKNewStockInfo]:
        """获取港股新股数据（主方法）

        Returns:
            List[HKNewStockInfo]: 港股新股信息列表
        """
        self.logger.info("开始获取港股新股数据...")

        try:
            # 请求频率限制
            self._rate_limit()

            # 发送请求
            headers = self._get_headers()
            response = requests.get(
                self.base_url,
                headers=headers,
                timeout=self.timeout
            )

            # 关键：设置正确的编码（新浪财经使用 GBK 编码）
            response.encoding = 'gbk'

            self.last_request_time = time.time()
            self.logger.info(f"成功获取页面，状态码: {response.status_code}")

            # 解析HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # 查找所有表格
            tables = soup.find_all('table')
            if len(tables) < 2:
                self.logger.error(f"未找到足够的数据表格，只找到{len(tables)}个，页面结构可能已变化")
                return []

            # 使用第二个表格（索引1），第一个表格是导航菜单
            table = tables[1]
            self.logger.debug(f"找到{len(tables)}个表格，使用第2个表格进行解析")

            # 解析表格数据
            stocks = self._parse_table(table)
            self.logger.info(f"成功解析 {len(stocks)} 条港股新股数据")

            return stocks

        except requests.exceptions.Timeout:
            self.logger.error(f"请求超时（{self.timeout}秒）")
            return []
        except requests.exceptions.RequestException as e:
            self.logger.error(f"网络请求失败: {e}")
            return []
        except Exception as e:
            self.logger.error(f"获取数据时出错: {e}", exc_info=True)
            return []

    def _rate_limit(self):
        """请求频率限制，避免被封禁"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed + random.uniform(0.5, 1.5)
            self.logger.info(f"等待 {sleep_time:.2f} 秒后继续...")
            time.sleep(sleep_time)

    def _get_headers(self) -> dict:
        """获取随机请求头

        Returns:
            dict: 请求头字典
        """
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def _parse_table(self, table) -> List[HKNewStockInfo]:
        """解析表格数据

        Args:
            table: BeautifulSoup表格对象

        Returns:
            List[HKNewStockInfo]: 港股新股信息列表

        表格结构：
        0: 股票代码
        1: 股票名称
        2: 招股价(HK$)
        3: 招股数(股)
        4: 募资额(百万)
        5: 招股日期
        6: 上市日期
        7-9: 现价/升跌/升跌幅 (不需要)
        """
        stocks = []
        rows = table.find_all('tr')

        # 跳过表头（第一行，在thead中）
        for row in rows:
            # 检查是否在tbody中（跳过thead和tfoot）
            parent_tbody = row.find_parent('tbody')
            if not parent_tbody:
                continue

            # 获取所有列（可能是td或th）
            cols = row.find_all(['td', 'th'])

            if len(cols) < 7:
                self.logger.debug(f"列数不足，跳过该行: {len(cols)}列")
                continue

            try:
                # 提取数据
                stock_code = cols[0].text.strip()
                stock_name = cols[1].text.strip()
                offer_price_range = cols[2].text.strip() if len(cols) > 2 else ""
                offer_shares = cols[3].text.strip() if len(cols) > 3 else ""
                raised_amount_raw = cols[4].text.strip() if len(cols) > 4 else ""
                subscription_date_raw = cols[5].text.strip() if len(cols) > 5 else ""
                listing_date_raw = cols[6].text.strip() if len(cols) > 6 else ""

                # 验证基本字段
                if not stock_code or not stock_name:
                    continue

                # 跳过无效行（如tfoot中的行）
                if stock_code == "注" or "注" in stock_code:
                    continue

                # 处理募资额（原始单位：百万港元，转换为实际金额）
                raised_amount = None
                if raised_amount_raw and raised_amount_raw != "0.00":
                    try:
                        # 将百万港元转换为港元（乘以1,000,000）
                        amount_million = float(raised_amount_raw.strip())
                        amount_hkd = amount_million * 1000000
                        raised_amount = str(int(amount_hkd))
                    except ValueError:
                        raised_amount = raised_amount_raw

                # 解析申购日期（可能是区间，如"2025-12-31至2026-01-06"）
                subscription_date = None
                subscription_date_range = None  # 新增：保存原始日期范围
                if subscription_date_raw and subscription_date_raw != "--":
                    # 保存原始日期范围字符串
                    subscription_date_range = subscription_date_raw.strip()

                    # 提取第一个日期用于筛选
                    date_for_parsing = subscription_date_raw
                    if "至" in subscription_date_raw:
                        date_for_parsing = subscription_date_raw.split("至")[0]
                    subscription_date = self._parse_date(date_for_parsing.strip())

                # 解析上市日期
                listing_date = None
                if listing_date_raw and listing_date_raw != "--":
                    listing_date = self._parse_date(listing_date_raw.strip())

                # 创建对象
                stock = HKNewStockInfo(
                    stock_code=stock_code,
                    stock_name=stock_name,
                    offer_price_range=offer_price_range if offer_price_range else None,
                    raised_amount=raised_amount,
                    offer_shares=offer_shares if offer_shares else None,
                    subscription_ratio=None,  # 当前表格中没有认购倍数
                    subscription_date=subscription_date,
                    subscription_date_range=subscription_date_range,  # 新增：保存日期范围
                    listing_date=listing_date,
                )

                stocks.append(stock)
                self.logger.debug(f"成功解析: {stock_code} - {stock_name}")

            except Exception as e:
                self.logger.warning(f"解析行数据失败: {e}")
                continue

        return stocks

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串

        Args:
            date_str: 日期字符串（格式如 "2025-05-122025-05-15" 或 "2025-05-20"）

        Returns:
            Optional[datetime]: 解析后的日期对象
        """
        if not date_str or date_str == "--":
            return None

        try:
            # 新浪财经的日期格式可能是 "2025-05-122025-05-15"（申购日期区间）
            # 或者 "2025-05-20"（单个日期）
            # 我们取第一个日期

            # 移除空格
            date_str = date_str.strip()

            # 如果包含空格，取第一个日期
            if " " in date_str:
                date_str = date_str.split()[0]

            # 尝试多种日期格式
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y%m%d"):
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

        except Exception as e:
            self.logger.debug(f"日期解析失败: {date_str}, 错误: {e}")

        return None


# ============================================================================
# 港股数据处理服务
# ============================================================================

class HKDataProcessor:
    """港股新股数据处理服务"""

    def __init__(self):
        """初始化数据处理服务"""
        self.logger = get_logger()

    def filter_subscribable_stocks(self, stocks: List[HKNewStockInfo]) -> List[HKNewStockInfo]:
        """筛选当前可申购的港股新股

        筛选条件：申购日期范围内包含今天的新股

        Args:
            stocks: 港股新股信息列表

        Returns:
            List[HKNewStockInfo]: 筛选后的港股新股列表
        """
        self.logger.info("开始筛选当前可申购的港股新股...")

        today = datetime.now().date()
        filtered_stocks = []

        for stock in stocks:
            if not stock.subscription_date_range:
                continue

            # 解析日期范围字符串
            start_date, end_date = self._parse_date_range(stock.subscription_date_range)

            if start_date is None or end_date is None:
                continue

            # 筛选条件：今天在申购日期范围内
            if start_date <= today <= end_date:
                filtered_stocks.append(stock)
                self.logger.debug(f"符合条件: {stock.stock_code} - {stock.stock_name} ({start_date} 至 {end_date})")

        self.logger.info(f"筛选完成，找到 {len(filtered_stocks)} 只当前可申购的港股新股")

        # 按申购日期排序
        filtered_stocks.sort(
            key=lambda x: x.subscription_date or datetime.min
        )

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
            self.logger.debug(f"日期范围解析失败: {date_range_str}, 错误: {e}")
            return None, None

    def group_by_date(self, stocks: List[HKNewStockInfo]) -> dict:
        """按上市日期分组

        Args:
            stocks: 港股新股信息列表

        Returns:
            dict: 按日期分组的港股新股字典
        """
        grouped = {}

        for stock in stocks:
            # 使用上市日期分组
            target_date = stock.listing_date if stock.listing_date else stock.subscription_date

            if target_date is None:
                continue

            date_str = target_date.strftime("%Y-%m-%d")

            if date_str not in grouped:
                grouped[date_str] = []

            grouped[date_str].append(stock)

        return grouped

    def validate_data(self, stocks: List[HKNewStockInfo]) -> List[HKNewStockInfo]:
        """验证数据完整性

        Args:
            stocks: 港股新股信息列表

        Returns:
            List[HKNewStockInfo]: 验证通过的港股新股列表
        """
        self.logger.info("开始验证数据完整性...")

        valid_stocks = []

        for stock in stocks:
            # 基本字段验证
            if not stock.stock_code or not stock.stock_name:
                self.logger.warning(f"股票代码或名称为空，跳过: {stock}")
                continue

            # 至少需要有申购日期或上市日期之一
            if not stock.subscription_date and not stock.listing_date:
                self.logger.warning(f"申购日期和上市日期均为空，跳过: {stock.stock_code}")
                continue

            valid_stocks.append(stock)

        self.logger.info(f"数据验证完成，有效数据 {len(valid_stocks)}/{len(stocks)} 条")

        return valid_stocks


# ============================================================================
# 港股Markdown格式化服务
# ============================================================================

class HKMarkdownFormatter:
    """港股新股 Markdown 格式化服务"""

    def __init__(self):
        self.logger = get_logger()

    def format_new_stocks(self, stocks: List[HKNewStockInfo]) -> str:
        """格式化港股新股信息为 Markdown

        Args:
            stocks: 港股新股信息列表

        Returns:
            str: Markdown 格式的文本
        """
        self.logger.info("开始格式化港股新股信息...")

        if not stocks:
            return self._format_empty()

        # 构建 Markdown
        lines = []

        # 标题
        lines.append("# 当前可申购的港股新股发行信息")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**新股数量**: {len(stocks)} 只")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 按日期分组
        processor = HKDataProcessor()
        grouped = processor.group_by_date(stocks)

        # 遍历每个日期
        for date_str, date_stocks in sorted(grouped.items()):
            lines.append(f"## {date_str}")
            lines.append("")

            for stock in date_stocks:
                lines.extend(self._format_stock(stock))
                lines.append("")

        markdown = "\n".join(lines)

        self.logger.info("Markdown 格式化完成")
        return markdown

    def _format_stock(self, stock: HKNewStockInfo) -> List[str]:
        """格式化单只港股信息

        Args:
            stock: 港股新股信息

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
        lines.append(f"| **股票代码** | {stock.stock_code} |")

        # 优先使用日期范围，如果没有则使用单个日期
        if stock.subscription_date_range:
            lines.append(f"| **申购日期** | {stock.subscription_date_range} |")
        elif stock.subscription_date:
            lines.append(f"| **申购日期** | {stock.subscription_date.strftime('%Y-%m-%d')} |")

        if stock.listing_date:
            lines.append(f"| **上市日期** | {stock.listing_date.strftime('%Y-%m-%d')} |")

        lines.append(f"| **招股价** | {stock.get_formatted_price()} |")

        if stock.offer_shares:
            lines.append(f"| **发售股数** | {stock.get_formatted_shares()} |")

        if stock.raised_amount:
            lines.append(f"| **集资额** | {stock.get_formatted_raised_amount()} |")

        if stock.subscription_ratio:
            lines.append(f"| **认购倍数** | {stock.subscription_ratio} |")

        lines.append(f"| **上市地点** | 港交所 |")

        lines.append("")

        return lines

    def _format_empty(self) -> str:
        """格式化空数据情况

        Returns:
            str: 空数据的 Markdown
        """
        lines = []
        lines.append("# 当前可申购的港股新股发行信息")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 暂无新股信息")
        lines.append("")
        lines.append("当前暂无可申购的港股新股。")

        return "\n".join(lines)
