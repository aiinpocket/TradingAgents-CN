#!/usr/bin/env python3
"""
快速集成測試 - 驗證複制的文件是否正常工作
"""

import os
import sys
import traceback
from datetime import datetime

print("🚀 TradingAgents 集成測試")
print("=" * 40)

# 測試1：檢查文件是否存在
print("\n📁 檢查複制的文件...")
files_to_check = [
    'tradingagents/dataflows/cache_manager.py',
    'tradingagents/dataflows/optimized_us_data.py',
    'tradingagents/dataflows/config.py'
]

for file_path in files_to_check:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {file_path} (大小: {size:,} 字節)")
    else:
        print(f"❌ {file_path} (文件不存在)")

# 測試2：檢查Python語法
print("\n🐍 檢查Python語法...")
for file_path in files_to_check:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {file_path} 語法正確")
        except SyntaxError as e:
            print(f"❌ {file_path} 語法錯誤: {e}")
        except Exception as e:
            print(f"⚠️ {file_path} 檢查失敗: {e}")

# 測試3：嘗試導入模塊
print("\n📦 測試模塊導入...")

# 測試緩存管理器
try:
    from tradingagents.dataflows.cache_manager import get_cache, StockDataCache
    print("✅ cache_manager 導入成功")
    
    # 創建緩存實例
    cache = get_cache()
    print(f"✅ 緩存實例創建成功: {type(cache).__name__}")
    
    # 檢查緩存目錄
    if hasattr(cache, 'cache_dir'):
        print(f"📁 緩存目錄: {cache.cache_dir}")
        if cache.cache_dir.exists():
            print("✅ 緩存目錄已創建")
        else:
            print("⚠️ 緩存目錄不存在")
    
except Exception as e:
    print(f"❌ cache_manager 導入失敗: {e}")
    traceback.print_exc()

# 測試優化美股數據
try:
    from tradingagents.dataflows.optimized_us_data import get_optimized_us_data_provider
    print("✅ optimized_us_data 導入成功")
    
    # 創建數據提供器
    provider = get_optimized_us_data_provider()
    print(f"✅ 數據提供器創建成功: {type(provider).__name__}")
    
except Exception as e:
    print(f"❌ optimized_us_data 導入失敗: {e}")
    traceback.print_exc()

# 測試配置模塊
try:
    from tradingagents.dataflows.config import get_config
    print("✅ config 導入成功")
    
    # 獲取配置
    config = get_config()
    print(f"✅ 配置獲取成功: {type(config).__name__}")
    
except Exception as e:
    print(f"❌ config 導入失敗: {e}")
    traceback.print_exc()

# 測試4：基本功能測試
print("\n💾 測試緩存基本功能...")
try:
    cache = get_cache()
    
    # 測試數據保存
    test_data = f"測試數據 - {datetime.now()}"
    cache_key = cache.save_stock_data(
        symbol="TEST",
        data=test_data,
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_source="integration_test"
    )
    print(f"✅ 數據保存成功: {cache_key}")
    
    # 測試數據加載
    loaded_data = cache.load_stock_data(cache_key)
    if loaded_data == test_data:
        print("✅ 數據加載成功，內容匹配")
    else:
        print(f"❌ 數據不匹配")
        print(f"  期望: {test_data}")
        print(f"  實際: {loaded_data}")
    
    # 測試緩存查找
    found_key = cache.find_cached_stock_data(
        symbol="TEST",
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_source="integration_test"
    )
    
    if found_key:
        print(f"✅ 緩存查找成功: {found_key}")
    else:
        print("❌ 緩存查找失敗")
    
except Exception as e:
    print(f"❌ 緩存功能測試失敗: {e}")
    traceback.print_exc()

# 測試5：性能測試
print("\n⚡ 簡單性能測試...")
try:
    import time
    
    cache = get_cache()
    
    # 保存測試
    start_time = time.time()
    cache_key = cache.save_stock_data(
        symbol="PERF",
        data="性能測試數據",
        start_date="2024-01-01",
        end_date="2024-12-31",
        data_source="perf_test"
    )
    save_time = time.time() - start_time
    
    # 加載測試
    start_time = time.time()
    data = cache.load_stock_data(cache_key)
    load_time = time.time() - start_time
    
    print(f"📊 保存時間: {save_time:.4f}秒")
    print(f"⚡ 加載時間: {load_time:.4f}秒")
    
    if load_time < 0.1:
        print("✅ 緩存性能良好 (<0.1秒)")
    else:
        print("⚠️ 緩存性能需要優化")
    
except Exception as e:
    print(f"❌ 性能測試失敗: {e}")

# 測試6：緩存統計
print("\n📊 緩存統計信息...")
try:
    cache = get_cache()
    stats = cache.get_cache_stats()
    
    print("緩存統計:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
except Exception as e:
    print(f"❌ 緩存統計失敗: {e}")

print("\n" + "=" * 40)
print("🎉 集成測試完成!")
print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 生成測試報告
print("\n📋 測試總結:")
print("1. 文件複制: 檢查文件是否正確複制")
print("2. 語法檢查: 驗證Python語法正確性")
print("3. 模塊導入: 測試模塊是否可以正常導入")
print("4. 功能測試: 驗證緩存基本功能")
print("5. 性能測試: 檢查緩存性能")
print("6. 統計信息: 獲取緩存使用統計")

print("\n🎯 下一步:")
print("1. 如果測試通過，可以開始清理中文內容")
print("2. 添加英文文件和註釋")
print("3. 創建完整的測試用例")
print("4. 準備性能基準報告")
print("5. 聯系上游項目維護者")
