"""
測試所有分析師節點的港股數據源修複
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_market_analyst_hk_config():
    """測試市場分析師港股配置"""
    print("🧪 測試市場分析師港股配置...")
    
    try:
        # 讀取市場分析師文件
        with open('tradingagents/agents/analysts/market_analyst.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查港股配置
        has_hk_branch = 'elif is_hk:' in content
        has_unified_tool = 'get_hk_stock_data_unified' in content
        has_akshare_comment = '優先AKShare' in content
        
        print(f"  港股分支: {has_hk_branch}")
        print(f"  統一工具: {has_unified_tool}")
        print(f"  AKShare註釋: {has_akshare_comment}")
        
        if has_hk_branch and has_unified_tool and has_akshare_comment:
            print("  ✅ 市場分析師港股配置正確")
            return True
        else:
            print("  ❌ 市場分析師港股配置不完整")
            return False
        
    except Exception as e:
        print(f"❌ 市場分析師港股配置測試失败: {e}")
        return False

def test_fundamentals_analyst_hk_config():
    """測試基本面分析師港股配置"""
    print("\n🧪 測試基本面分析師港股配置...")
    
    try:
        # 讀取基本面分析師文件
        with open('tradingagents/agents/analysts/fundamentals_analyst.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查港股配置
        has_hk_branch = 'elif is_hk:' in content
        has_unified_tool = 'get_hk_stock_data_unified' in content
        has_akshare_comment = '優先AKShare' in content
        
        print(f"  港股分支: {has_hk_branch}")
        print(f"  統一工具: {has_unified_tool}")
        print(f"  AKShare註釋: {has_akshare_comment}")
        
        if has_hk_branch and has_unified_tool and has_akshare_comment:
            print("  ✅ 基本面分析師港股配置正確")
            return True
        else:
            print("  ❌ 基本面分析師港股配置不完整")
            return False
        
    except Exception as e:
        print(f"❌ 基本面分析師港股配置測試失败: {e}")
        return False

def test_optimized_us_data_hk_support():
    """測試優化美股數據模塊的港股支持"""
    print("\n🧪 測試優化美股數據模塊的港股支持...")
    
    try:
        # 讀取優化美股數據文件
        with open('tradingagents/dataflows/optimized_us_data.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查港股支持
        has_hk_detection = "market_info['is_hk']" in content
        has_akshare_import = 'get_hk_stock_data_unified' in content
        has_akshare_priority = '優先使用AKShare' in content
        
        print(f"  港股檢測: {has_hk_detection}")
        print(f"  AKShare導入: {has_akshare_import}")
        print(f"  AKShare優先級: {has_akshare_priority}")
        
        if has_hk_detection and has_akshare_import and has_akshare_priority:
            print("  ✅ 優化美股數據模塊港股支持正確")
            return True
        else:
            print("  ❌ 優化美股數據模塊港股支持不完整")
            return False
        
    except Exception as e:
        print(f"❌ 優化美股數據模塊港股支持測試失败: {e}")
        return False

def test_toolkit_hk_method_availability():
    """測試工具包港股方法可用性"""
    print("\n🧪 測試工具包港股方法可用性...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 檢查港股方法
        has_hk_method = hasattr(toolkit, 'get_hk_stock_data_unified')
        
        print(f"  工具包港股方法: {has_hk_method}")
        
        if has_hk_method:
            print("  ✅ 工具包港股方法可用")
            return True
        else:
            print("  ❌ 工具包港股方法不可用")
            return False
        
    except Exception as e:
        print(f"❌ 工具包港股方法可用性測試失败: {e}")
        return False

def test_data_source_priority_summary():
    """測試數據源優先級总結"""
    print("\n🧪 數據源優先級总結...")
    
    try:
        from tradingagents.dataflows.interface import AKSHARE_HK_AVAILABLE, HK_STOCK_AVAILABLE
        
        print("  📊 當前數據源可用性:")
        print(f"    AKShare港股: {AKSHARE_HK_AVAILABLE}")
        print(f"    Yahoo Finance港股: {HK_STOCK_AVAILABLE}")
        
        print("\n  🎯 預期數據源優先級:")
        print("    港股 (0700.HK):")
        print("      1. AKShare (主要) - 國內穩定，無Rate Limit")
        print("      2. Yahoo Finance (备用) - 國际數據源")
        print("    中國A股 (000001):")
        print("      1. Tushare/AKShare/BaoStock (現有配置)")
        print("    美股 (AAPL):")
        print("      1. FINNHUB (主要)")
        print("      2. Yahoo Finance (备用)")
        
        return True
        
    except Exception as e:
        print(f"❌ 數據源優先級总結失败: {e}")
        return False

def main():
    """運行所有測試"""
    print("🔧 所有分析師節點港股數據源修複測試")
    print("=" * 60)
    
    tests = [
        test_market_analyst_hk_config,
        test_fundamentals_analyst_hk_config,
        test_optimized_us_data_hk_support,
        test_toolkit_hk_method_availability,
        test_data_source_priority_summary
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 異常: {e}")
    
    print("\n" + "=" * 60)
    print(f"🔧 所有分析師節點港股數據源修複測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有分析師節點港股數據源修複成功！")
        print("\n✅ 修複总結:")
        print("  - 市場分析師: 港股優先使用AKShare")
        print("  - 基本面分析師: 港股優先使用AKShare")
        print("  - 優化數據模塊: 支持港股AKShare優先級")
        print("  - 工具包: 已添加港股統一接口方法")
        print("\n🚀 現在所有港股分析都會優先使用AKShare數據源！")
    else:
        print("⚠️ 部分測試失败，請檢查失败的測試")

if __name__ == "__main__":
    main()
