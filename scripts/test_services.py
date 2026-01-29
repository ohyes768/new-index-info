"""
Quick Test Script - Test core services without starting API servers

This script tests the data fetching and processing logic directly.
"""

import sys
from pathlib import Path

# Save original sys.path
original_path = sys.path.copy()

# Add project root to Python path
project_root = Path(__file__).parent.parent

print("=" * 60)
print("  New Stock Info API - Core Services Test")
print("=" * 60)
print()

# =============================================================================
# Test 1: A-Stock Service
# =============================================================================

print("\n" + "=" * 60)
print("Test 1: A-Stock Service")
print("=" * 60)
print()

try:
    # Reset to original path and add A-Stock service path
    sys.path = original_path.copy()
    sys.path.insert(0, str(project_root / "backend" / "a_stock_service"))

    from services import DataFetcher, DataProcessor, MarkdownFormatter
    from models import NewStockInfo

    print("[Step 1] Initializing A-Stock services...")
    fetcher = DataFetcher(timeout=10, max_retries=3)
    processor = DataProcessor()
    formatter = MarkdownFormatter()
    print("[OK] Services initialized")
    print()

    print("[Step 2] Fetching A-Stock data (may take 2-5 seconds)...")
    stocks = fetcher.fetch_new_stocks()
    print(f"[OK] Fetched {len(stocks)} stock records")
    print()

    if stocks:
        print("[Step 3] Validating data...")
        valid_stocks = processor.validate_data(stocks)
        print(f"[OK] {len(valid_stocks)} valid records")
        print()

        print("[Step 4] Filtering subscribable stocks...")
        subscribable = processor.filter_subscribable_stocks(valid_stocks)
        print(f"[OK] Found {len(subscribable)} subscribable stocks")
        if subscribable:
            print(f"  Example: {subscribable[0].stock_name} ({subscribable[0].stock_code})")
        print()

        print("[Step 5] Filtering future stocks...")
        future = processor.filter_future_unopened_stocks(valid_stocks, future_days=14)
        print(f"[OK] Found {len(future)} future stocks")
        if future:
            print(f"  Example: {future[0].stock_name} ({future[0].stock_code})")
        print()

        print("[Step 6] Formatting output...")
        markdown = formatter.format_new_stocks(subscribable, future)
        print(f"[OK] Generated {len(markdown)} characters of Markdown")
        print()

        # Show first 500 characters
        print("[Preview] First 500 characters of output:")
        print("-" * 60)
        print(markdown[:500] + "..." if len(markdown) > 500 else markdown)
        print("-" * 60)
    else:
        print("[WARN] No stock data found")

    print()
    print("[SUCCESS] A-Stock Service test completed!")

except Exception as e:
    print(f"[ERROR] A-Stock Service test failed: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# Test 2: HK-Stock Service
# =============================================================================

print("\n" + "=" * 60)
print("Test 2: HK-Stock Service")
print("=" * 60)
print()

try:
    # Reset to original path and add HK-Stock service path
    sys.path = original_path.copy()
    sys.path.insert(0, str(project_root / "backend" / "hk_stock_service"))

    # Clear all related module caches to avoid conflicts
    modules_to_clear = ['services', 'models']
    for mod in list(sys.modules.keys()):
        for m in modules_to_clear:
            if mod.startswith(m):
                del sys.modules[mod]

    # Import models first to avoid conflicts
    from models import HKNewStockInfo

    # Then import services
    from services import HKDataFetcher, HKDataProcessor, HKMarkdownFormatter

    print("[Step 1] Initializing HK-Stock services...")
    fetcher = HKDataFetcher(timeout=10, min_interval=5)
    processor = HKDataProcessor()
    formatter = HKMarkdownFormatter()
    print("[OK] Services initialized")
    print()

    print("[Step 2] Fetching HK-Stock data (may take 10-30 seconds)...")
    print("[INFO] Please be patient, web scraping requires interval delays...")
    stocks = fetcher.fetch_hk_new_stocks()
    print(f"[OK] Fetched {len(stocks)} stock records")
    print()

    if stocks:
        print("[Step 3] Validating data...")
        valid_stocks = processor.validate_data(stocks)
        print(f"[OK] {len(valid_stocks)} valid records")
        print()

        print("[Step 4] Filtering subscribable stocks...")
        subscribable = processor.filter_subscribable_stocks(valid_stocks)
        print(f"[OK] Found {len(subscribable)} subscribable stocks")
        if subscribable:
            print(f"  Example: {subscribable[0].stock_name} ({subscribable[0].stock_code})")
        print()

        print("[Step 5] Filtering future stocks...")
        future = processor.filter_future_unopened_stocks(valid_stocks, future_days=14)
        print(f"[OK] Found {len(future)} future stocks")
        if future:
            print(f"  Example: {future[0].stock_name} ({future[0].stock_code})")
        print()

        print("[Step 6] Formatting output...")
        markdown = formatter.format_new_stocks(subscribable, future)
        print(f"[OK] Generated {len(markdown)} characters of Markdown")
        print()

        # Show first 500 characters
        print("[Preview] First 500 characters of output:")
        print("-" * 60)
        print(markdown[:500] + "..." if len(markdown) > 500 else markdown)
        print("-" * 60)
    else:
        print("[WARN] No stock data found")

    print()
    print("[SUCCESS] HK-Stock Service test completed!")

except Exception as e:
    print(f"[ERROR] HK-Stock Service test failed: {e}")
    import traceback
    traceback.print_exc()

# =============================================================================
# Summary
# =============================================================================

print("\n" + "=" * 60)
print("  Test Summary")
print("=" * 60)
print()
print("All core services have been tested!")
print()
print("Next steps:")
print("  1. If tests passed: Services are working correctly")
print("  2. If tests failed: Check error messages above")
print("  3. To start API servers: Run Python directly or use Docker")
print()
print("=" * 60)
