"""
新股发行信息获取系统 - 主入口（单文件版本）

自动获取当前可申购和未来14天即将开放申购的新股发行信息，并输出为 JSON 格式

依赖：
    - pip install akshare pandas

使用：
    python main_simple.py
"""

import sys
import json
from services import DataFetcher, DataProcessor, MarkdownFormatter, setup_logger


def main():
    """主函数"""
    # 设置日志（输出到 stderr，避免干扰核心输出）
    logger = setup_logger()

    print("=" * 60, file=sys.stderr)
    print("新股发行信息获取系统启动", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    try:
        # 1. 获取数据
        print("DEBUG: 步骤 1/5: 获取新股数据", file=sys.stderr)
        fetcher = DataFetcher()
        stocks = fetcher.fetch_new_stocks()

        if not stocks:
            print("DEBUG: 未获取到任何新股数据", file=sys.stderr)
            # 即使没有数据，也要输出空报告
            formatter = MarkdownFormatter()
            markdown = formatter.format_new_stocks([], [])
            # 输出 JSON 格式
            result = {
                "success": True,
                "market": "A股",
                "data": markdown,
                "subscribable_count": 0,
                "future_count": 0
            }
            print(json.dumps(result, ensure_ascii=False))
            return

        # 2. 处理数据
        print("DEBUG: 步骤 2/5: 验证和筛选数据", file=sys.stderr)
        processor = DataProcessor()
        valid_stocks = processor.validate_data(stocks)

        # 筛选当前可申购的新股
        subscribable_stocks = processor.filter_subscribable_stocks(valid_stocks)
        print(f"DEBUG: 找到 {len(subscribable_stocks)} 只当前可申购的新股", file=sys.stderr)

        # 筛选未来14天未开放申购的新股
        future_stocks = processor.filter_future_unopened_stocks(valid_stocks, future_days=14)
        print(f"DEBUG: 找到 {len(future_stocks)} 只未来14天即将开放申购的新股", file=sys.stderr)

        # 3. 补充详细信息（只对筛选后的少数股票）
        print("DEBUG: 步骤 3/5: 补充详细信息", file=sys.stderr)
        all_stocks = subscribable_stocks + future_stocks
        if all_stocks:
            all_stocks = fetcher._enrich_stock_info(all_stocks)

        # 4. 格式化输出
        print("DEBUG: 步骤 4/5: 格式化为 Markdown", file=sys.stderr)
        formatter = MarkdownFormatter()
        markdown = formatter.format_new_stocks(subscribable_stocks, future_stocks)

        # 5. 输出到控制台（供 n8n 读取）
        print("DEBUG: 步骤 5/5: 输出到控制台", file=sys.stderr)

        # 输出 JSON 格式
        result = {
            "success": True,
            "market": "A股",
            "data": markdown,
            "subscribable_count": len(subscribable_stocks),
            "future_count": len(future_stocks)
        }
        print(json.dumps(result, ensure_ascii=False))

        print("=" * 60, file=sys.stderr)
        total_stocks = len(subscribable_stocks) + len(future_stocks)
        print(f"DEBUG: 程序执行完成，共获取 {total_stocks} 只新股", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

    except Exception as e:
        print(f"ERROR: 程序运行出错: {e}", file=sys.stderr)
        # 输出错误信息
        error_result = {
            "success": False,
            "market": "A股",
            "error": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False))
        raise


if __name__ == "__main__":
    main()
