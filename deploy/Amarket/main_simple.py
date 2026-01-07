"""
新股发行信息获取系统 - 主入口（单文件版本）

自动获取当前可申购和未来14天即将开放申购的新股发行信息，并输出为 Markdown 格式

依赖：
    - pip install akshare pandas

使用：
    python main_simple.py
"""

from services import DataFetcher, DataProcessor, MarkdownFormatter, setup_logger


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger()

    logger.info("=" * 60)
    logger.info("新股发行信息获取系统启动")
    logger.info("=" * 60)

    try:
        # 1. 获取数据
        logger.info("步骤 1/5: 获取新股数据")
        fetcher = DataFetcher()
        stocks = fetcher.fetch_new_stocks()

        if not stocks:
            logger.warning("未获取到任何新股数据")
            # 即使没有数据，也要输出空报告
            formatter = MarkdownFormatter()
            markdown = formatter.format_new_stocks([], [])
            print(markdown)
            return

        # 2. 处理数据
        logger.info("步骤 2/5: 验证和筛选数据")
        processor = DataProcessor()
        valid_stocks = processor.validate_data(stocks)

        # 筛选当前可申购的新股
        subscribable_stocks = processor.filter_subscribable_stocks(valid_stocks)
        logger.info(f"找到 {len(subscribable_stocks)} 只当前可申购的新股")

        # 筛选未来14天未开放申购的新股
        future_stocks = processor.filter_future_unopened_stocks(valid_stocks, future_days=14)
        logger.info(f"找到 {len(future_stocks)} 只未来14天即将开放申购的新股")

        # 3. 补充详细信息（只对筛选后的少数股票）
        logger.info(f"步骤 3/5: 补充详细信息")
        all_stocks = subscribable_stocks + future_stocks
        if all_stocks:
            all_stocks = fetcher._enrich_stock_info(all_stocks)

        # 4. 格式化输出
        logger.info("步骤 4/5: 格式化为 Markdown")
        formatter = MarkdownFormatter()
        markdown = formatter.format_new_stocks(subscribable_stocks, future_stocks)

        # 5. 输出到控制台（供 n8n 读取）
        logger.info("步骤 5/5: 输出到控制台")
        print(markdown)

        logger.info("=" * 60)
        total_stocks = len(subscribable_stocks) + len(future_stocks)
        logger.info(f"程序执行完成，共获取 {total_stocks} 只新股")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
