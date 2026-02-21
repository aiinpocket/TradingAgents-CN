#!/usr/bin/env python3
"""
快速集成測試 - 驗證複制的檔案是否正常工作
"""

import os
import sys
import traceback
from datetime import datetime

print(" TradingAgents 集成測試")
print("=" * 40)

# 測試1：檢查檔案是否存在
print("\n 檢查複制的檔案...")
files_to_check = [
    'tradingagents/dataflows/cache_manager.py',
    'tradingagents/dataflows/optimized_us_data.py',
    'tradingagents/dataflows/config.py'
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f" {file_path} (大小: {size:,} 位元組)")
    else:
        print(f" {file_path} (檔案不存在)")

# 測試2：檢查Python語法
print("\n 檢查Python語法...")
for file_path in files_to_check:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f" {file_path} 語法正確")
        except SyntaxError as e:
            print(f" {file_path} 語法錯誤: {e}")
        except Exception as e:
            print(f" {file_path} 檢查失敗: {e}")

# 測試3：嘗試匯入模組
print("\n 測試模組匯入...")

# 測試快取管理器
try:
    from tradingagents.dataflows.cache_manager import get_cache, StockDataCache
    print(" cache_manager 匯入成功")
    
    # 創建快取實例
    cache = get_cache()
    print(f" 快取實例創建成功: {type(cache).__name__}")
    
    # 檢查快取目錄
    if hasattr(cache, 'cache_dir'):
        print(f" 快取目錄: {cache.cache_dir}")
        if cache.cache_dir.exists():
            print(" 快取目錄已創建")
        else:
            print(" 快取目錄不存在")
    
except Exception as e:
    print(f" cache_manager 匯入失敗: {e}")
    traceback.print_exc()

# 測試優化美股資料
try:
    from tradingagents.dataflows.optimized_us_data import get_optimized_us_data_provider
    print(" optimized_us_data 匯入成功")
    
    # 創建資料提供器
    provider = get_optimized_us_data_provider()
    print(f" 資料提供器創建成功: {type(provider).__name__}")
    
except Exception as e:
    print(f" optimized_us_data 匯入失敗: {e}")
    traceback.print_exc()

# 測試配置模組
try:
    from tradingagents.dataflows.config import get_config
    print(" config 匯入成功")
    
    # 取得配置
    config = get_config()
    print(f" 配置取得成功: {type(config).__name__}")
    
except Exception as e:
    print(f" config 匯入失敗: {e}")
    traceback.print_exc()

# 測試4：基本功能測試
print("\n 測試快取基本功能...")
try:
    cache = get_cache()
    
    # 測試資料保存
    test_data = f"測試資料 - {datetime.now()}"
    cache_key = cache.save_stock_data(
        symbol="TEST",
        data=test_data,
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_source="integration_test"
    )
    print(f" 資料保存成功: {cache_key}")
    
    # 測試資料載入
    loaded_data = cache.load_stock_data(cache_key)
    if loaded_data == test_data:
        print(" 資料載入成功，內容匹配")
    else:
        print(f" 資料不匹配")
        print(f"  期望: {test_data}")
        print(f"  實際: {loaded_data}")
    
    # 測試快取查找
    found_key = cache.find_cached_stock_data(
        symbol="TEST",
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_source="integration_test"
    )
    
    if found_key:
        print(f" 快取查找成功: {found_key}")
    else:
        print(" 快取查找失敗")
    
except Exception as e:
    print(f" 快取功能測試失敗: {e}")
    traceback.print_exc()

# 測試5：性能測試
print("\n 簡單性能測試...")
try:
    import time
    
    cache = get_cache()
    
    # 保存測試
    start_time = time.time()
    cache_key = cache.save_stock_data(
        symbol="PERF",
        data="性能測試資料",
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_source="perf_test"
    )
    save_time = time.time() - start_time
    
    # 載入測試
    start_time = time.time()
    data = cache.load_stock_data(cache_key)
    load_time = time.time() - start_time
    
    print(f" 保存時間: {save_time:.4f}秒")
    print(f" 載入時間: {load_time:.4f}秒")
    
    if load_time < 0.1:
        print(" 快取性能良好 (<0.1秒)")
    else:
        print(" 快取性能需要優化")
    
except Exception as e:
    print(f" 性能測試失敗: {e}")

# 測試6：快取統計
print("\n 快取統計資訊...")
try:
    cache = get_cache()
    stats = cache.get_cache_stats()
    
    print("快取統計:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
except Exception as e:
    print(f" 快取統計失敗: {e}")

print("\n" + "=" * 40)
print(" 集成測試完成!")
print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 生成測試報告
print("\n 測試總結:")
print("1. 檔案複制: 檢查檔案是否正確複制")
print("2. 語法檢查: 驗證Python語法正確性")
print("3. 模組匯入: 測試模組是否可以正常匯入")
print("4. 功能測試: 驗證快取基本功能")
print("5. 性能測試: 檢查快取性能")
print("6. 統計資訊: 取得快取使用統計")

print("\n 下一步:")
print("1. 如果測試通過，可以開始清理中文內容")
print("2. 添加英文檔案和註釋")
print("3. 創建完整的測試用例")
print("4. 準備性能基準報告")
print("5. 聯系上游項目維護者")
