"""
港股数据获取服务

负责从新浪财经获取港股新股数据
"""

import sys
import time
import random
from datetime import datetime
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from models import HKNewStockInfo


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
        print("INFO: 开始获取港股新股数据...", file=sys.stderr)

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
            print(f"INFO: 成功获取页面，状态码: {response.status_code}", file=sys.stderr)

            # 解析HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # 查找所有表格
            tables = soup.find_all('table')
            if len(tables) < 2:
                print(f"ERROR: 未找到足够的数据表格，只找到{len(tables)}个，页面结构可能已变化", file=sys.stderr)
                return []

            # 使用第二个表格（索引1），第一个表格是导航菜单
            table = tables[1]
            print(f"DEBUG: 找到{len(tables)}个表格，使用第2个表格进行解析", file=sys.stderr)

            # 解析表格数据
            stocks = self._parse_table(table)
            print(f"INFO: 成功解析 {len(stocks)} 条港股新股数据", file=sys.stderr)

            return stocks

        except requests.exceptions.Timeout:
            print(f"ERROR: 请求超时（{self.timeout}秒）", file=sys.stderr)
            return []
        except requests.exceptions.RequestException as e:
            print(f"ERROR: 网络请求失败: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"ERROR: 获取数据时出错: {e}", file=sys.stderr)
            return []

    def _rate_limit(self):
        """请求频率限制，避免被封禁"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed + random.uniform(0.5, 1.5)
            print(f"INFO: 等待 {sleep_time:.2f} 秒后继续...", file=sys.stderr)
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

    def _fetch_stock_detail(self, stock_code: str) -> tuple:
        """获取单个股票的详情页信息

        Args:
            stock_code: 股票代码

        Returns:
            tuple: (板块, 公司简介)
        """
        url = f"http://vip.stock.finance.sina.com.cn/q/view/hk_IPOProfile.php?symbol={stock_code}"

        try:
            # 请求频率限制
            self._rate_limit()

            # 发送请求
            headers = self._get_headers()
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.encoding = 'gbk'

            # 解析HTML
            soup = BeautifulSoup(response.text, 'lxml')

            # 查找所有表格
            tables = soup.find_all('table')

            for table in tables:
                rows = table.find_all('tr')

                # 跳过太小的表格
                if len(rows) < 10:
                    continue

                industry = ""
                company_intro = ""

                # 遍历行，查找板块和公司简介
                for row in rows:
                    cells = row.find_all(['td', 'th'])

                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True) if len(cells) > 1 else ""

                        if label == '板块':
                            industry = value
                        elif label == '公司简介':
                            company_intro = value
                            # 找到公司简介后就可以返回了（通常在板块后面）
                            if industry or company_intro:
                                return industry, company_intro

                # 如果在这个表格中找到了数据，返回
                if industry or company_intro:
                    return industry, company_intro

            return "", ""

        except Exception as e:
            print(f"ERROR: 获取股票 {stock_code} 详情页失败: {e}", file=sys.stderr)
            return "", ""

    def enrich_stocks_detail(self, stocks: List[HKNewStockInfo]) -> List[HKNewStockInfo]:
        """批量补充股票的详情信息（板块和公司简介）

        Args:
            stocks: 港股新股列表

        Returns:
            List[HKNewStockInfo]: 补充了详情信息的股票列表
        """
        if not stocks:
            return stocks

        print(f"INFO: 开始补充 {len(stocks)} 只港股的详细信息（板块、公司简介）...", file=sys.stderr)

        for i, stock in enumerate(stocks, 1):
            print(f"DEBUG: 正在获取第 {i}/{len(stocks)} 只股票的详情: {stock.stock_code}", file=sys.stderr)

            # 获取详情
            industry, company_intro = self._fetch_stock_detail(stock.stock_code)

            # 更新股票信息
            if industry:
                stock.industry = industry
            if company_intro:
                stock.company_intro = company_intro

            print(f"DEBUG: 股票 {stock.stock_code} - 板块: {industry if industry else '无'}, 公司简介: {len(company_intro)} 字符", file=sys.stderr)

        print(f"INFO: 详细信息补充完成", file=sys.stderr)
        return stocks

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
                print(f"DEBUG: 列数不足，跳过该行: {len(cols)}列", file=sys.stderr)
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

            except Exception as e:
                print(f"WARNING: 解析行数据失败: {e}", file=sys.stderr)
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
            print(f"DEBUG: 日期解析失败: {date_str}, 错误: {e}", file=sys.stderr)

        return None
