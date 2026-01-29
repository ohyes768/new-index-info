"""
数据获取服务

负责从 akshare 获取新股数据
"""

import sys
import akshare as ak
import pandas as pd
from datetime import datetime
from typing import List
from models import NewStockInfo


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
                elif pd.notna(online_end):
                    # 如果只有结束日期，使用结束日期作为范围
                    end_str = str(online_end)[:10]
                    issue_date_range = f"{end_str}至{end_str}"
                elif pd.notna(issue_date_raw):
                    # 如果只有单个日期，使用该日期作为范围
                    date_str = str(issue_date_raw)[:10] if len(str(issue_date_raw)) >= 10 else str(issue_date_raw)
                    issue_date_range = f"{date_str}至{date_str}"

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

    def _parse_date(self, date_str):
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

    def _parse_float(self, value) -> float:
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

    def _format_lottery_rate(self, value) -> str:
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
