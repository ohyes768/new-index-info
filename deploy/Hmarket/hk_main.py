"""
港股新股发行信息获取系统 - 主入口

自动获取未来10天内的港股新股发行信息，并输出为 Markdown 格式

依赖：
    - pip install requests beautifulsoup4 lxml

使用：
    python hk_main.py
"""

from hk_services import HKDataFetcher, HKDataProcessor, HKMarkdownFormatter, setup_logger


def main():
    """主函数"""
    # 设置日志
    logger = setup_logger()

    logger.info("=" * 60)
    logger.info("港股新股发行信息获取系统启动")
    logger.info("=" * 60)

    try:
        # 1. 获取数据
        logger.info("步骤 1/4: 获取港股新股数据")
        fetcher = HKDataFetcher()
        stocks = fetcher.fetch_hk_new_stocks()

        if not stocks:
            logger.warning("未获取到任何港股新股数据")
            # 即使没有数据，也要输出空报告
            formatter = HKMarkdownFormatter()
            markdown = formatter.format_new_stocks([])
            print(markdown)
            return

        # 2. 处理数据
        logger.info("步骤 2/4: 验证和筛选数据")
        processor = HKDataProcessor(future_days=10)
        valid_stocks = processor.validate_data(stocks)
        future_stocks = processor.filter_future_stocks(valid_stocks)

        # 3. 格式化输出
        logger.info("步骤 3/4: 格式化为 Markdown")
        formatter = HKMarkdownFormatter()
        markdown = formatter.format_new_stocks(future_stocks)

        # 4. 输出到控制台（供 n8n 读取）
        logger.info("步骤 4/4: 输出到控制台")
        print(markdown)

        logger.info("=" * 60)
        logger.info(f"程序执行完成，共获取 {len(future_stocks)} 只港股新股")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
