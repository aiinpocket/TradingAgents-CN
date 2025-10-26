#!/usr/bin/env python3
"""
驗證配置是否正確
"""

import os
import sys

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("🔧 驗證.env配置")
print("=" * 30)

# 檢查啟用開關
mongodb_enabled = os.getenv("MONGODB_ENABLED", "false")
redis_enabled = os.getenv("REDIS_ENABLED", "false")

print(f"MONGODB_ENABLED: {mongodb_enabled}")
print(f"REDIS_ENABLED: {redis_enabled}")

# 使用强健的布爾值解析（兼容Python 3.13+）
try:
    from tradingagents.config.env_utils import parse_bool_env
    mongodb_bool = parse_bool_env("MONGODB_ENABLED", False)
    redis_bool = parse_bool_env("REDIS_ENABLED", False)
    print("✅ 使用强健的布爾值解析")
except ImportError:
    # 回退到原始方法
    mongodb_bool = mongodb_enabled.lower() == "true"
    redis_bool = redis_enabled.lower() == "true"
    print("⚠️ 使用傳統布爾值解析")

print(f"MongoDB啟用: {mongodb_bool}")
print(f"Redis啟用: {redis_bool}")

if not mongodb_bool and not redis_bool:
    print("✅ 默認配置：數據庫都未啟用，系統将使用文件緩存")
else:
    print("⚠️ 有數據庫啟用，系統将嘗試連接數據庫")

print("\n💡 配置說明:")
print("- MONGODB_ENABLED=false (默認)")
print("- REDIS_ENABLED=false (默認)")
print("- 系統使用文件緩存，無需數據庫")
print("- 如需啟用數據庫，修改.env文件中的對應值為true")
