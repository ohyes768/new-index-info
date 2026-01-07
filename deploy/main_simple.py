"""
新股发行信息获取系统 - 主入口（单文件版本）

自动获取未来10天内的新股发行信息，并输出为 Markdown 格式

依赖：
    - pip install akshare pandas

使用：
    python main.py
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
            markdown = formatter.format_new_stocks([])
            print(markdown)
            return

        # 2. 处理数据
        logger.info("步骤 2/5: 验证和筛选数据")
        processor = DataProcessor(future_days=10)
        valid_stocks = processor.validate_data(stocks)
        future_stocks = processor.filter_future_stocks(valid_stocks)

        # 3. 补充详细信息（只对筛选后的少数股票）
        logger.info(f"步骤 3/5: 补充 {len(future_stocks)} 只新股的详细信息")
        if future_stocks:
            future_stocks = fetcher._enrich_stock_info(future_stocks)

        # 4. 格式化输出
        logger.info("步骤 4/5: 格式化为 Markdown")
        formatter = MarkdownFormatter()
        markdown = formatter.format_new_stocks(future_stocks)

        # 5. 输出到控制台（供 n8n 读取）
        logger.info("步骤 5/5: 输出到控制台")
        print(markdown)

        logger.info("=" * 60)
        logger.info(f"程序执行完成，共获取 {len(future_stocks)} 只新股")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
