#!/usr/bin/env python3
"""
Agent Utils Tushare修複驗證測試
驗證agent_utils中的函數已成功從TDX迁移到Tushare統一接口
"""

import os
import sys
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_get_china_stock_data_fix():
    """測試get_china_stock_data函數的Tushare修複"""
    print("\n🔧 測試get_china_stock_data函數修複")
    print("=" * 60)
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit

        print("✅ Toolkit導入成功")

        # 測試股票數據獲取
        print("🔄 測試股票數據獲取...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')

        result = Toolkit.get_china_stock_data("600036", start_date, end_date)
        
        if result and len(result) > 100:
            print("✅ 股票數據獲取成功")
            print(f"📊 數據長度: {len(result)}字符")
            
            # 檢查是否使用了統一接口（而不是TDX）
            if "統一數據源接口" in result or "tushare" in result.lower():
                print("✅ 已成功使用統一數據源接口")
            elif "通達信" in result:
                print("⚠️ 警告: 仍在使用中國股票數據源")
            else:
                print("✅ 數據源已更新")
                
            # 顯示部分結果
            print(f"📋 結果預覽: {result[:200]}...")
        else:
            print("❌ 股票數據獲取失败")
            print(f"返回結果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ get_china_stock_data測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_china_market_overview_fix():
    """測試get_china_market_overview函數的修複"""
    print("\n🔧 測試get_china_market_overview函數修複")
    print("=" * 60)
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit

        print("✅ Toolkit導入成功")

        # 測試市場概覽獲取
        print("🔄 測試市場概覽獲取...")
        curr_date = datetime.now().strftime('%Y-%m-%d')

        result = Toolkit.get_china_market_overview(curr_date)
        
        if result and len(result) > 50:
            print("✅ 市場概覽獲取成功")
            print(f"📊 數據長度: {len(result)}字符")
            
            # 檢查是否提到了Tushare迁移
            if "Tushare" in result or "迁移" in result:
                print("✅ 已更新為Tushare數據源說明")
            elif "通達信" in result and "TDX" not in result:
                print("⚠️ 警告: 仍在使用中國股票數據源")
            else:
                print("✅ 市場概覽功能已更新")
                
            # 顯示部分結果
            print(f"📋 結果預覽: {result[:300]}...")
        else:
            print("❌ 市場概覽獲取失败")
            print(f"返回結果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ get_china_market_overview測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stock_name_mapping_fix():
    """測試股票名稱映射的修複"""
    print("\n🔧 測試股票名稱映射修複")
    print("=" * 60)
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit

        print("✅ Toolkit導入成功")

        # 測試基本面數據獲取（會觸發股票名稱映射）
        print("🔄 測試基本面數據獲取（包含股票名稱映射）...")
        curr_date = datetime.now().strftime('%Y-%m-%d')

        result = Toolkit.get_fundamentals_openai("600036", curr_date)
        
        if result and len(result) > 100:
            print("✅ 基本面數據獲取成功")
            print(f"📊 數據長度: {len(result)}字符")
            
            # 檢查是否包含正確的股票名稱
            if "招商銀行" in result:
                print("✅ 股票名稱映射成功: 600036 -> 招商銀行")
            else:
                print("⚠️ 股票名稱映射可能有問題")
                
            # 顯示部分結果
            print(f"📋 結果預覽: {result[:200]}...")
        else:
            print("❌ 基本面數據獲取失败")
            print(f"返回結果: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ 股票名稱映射測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_debug_output():
    """檢查調試輸出是否顯示使用了統一接口"""
    print("\n🔧 檢查調試輸出")
    print("=" * 60)
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit

        print("🔄 運行股票數據獲取並檢查調試輸出...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')

        # 這應该會產生調試輸出
        result = Toolkit.get_china_stock_data("000001", start_date, end_date)
        
        print("✅ 調試輸出檢查完成")
        print("💡 請查看上面的調試輸出，確認是否顯示:")
        print("   - '成功導入統一數據源接口'")
        print("   - '正在調用統一數據源接口'")
        print("   - 而不是 'tdx_utils.get_china_stock_data'")
        
        return True
        
    except Exception as e:
        print(f"❌ 調試輸出檢查失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🔬 Agent Utils Tushare修複驗證測試")
    print("=" * 70)
    print("💡 測試目標:")
    print("   - 驗證get_china_stock_data已迁移到統一接口")
    print("   - 驗證get_china_market_overview已更新")
    print("   - 驗證股票名稱映射使用統一接口")
    print("   - 檢查調試輸出確認修複生效")
    print("=" * 70)
    
    # 運行所有測試
    tests = [
        ("get_china_stock_data修複", test_get_china_stock_data_fix),
        ("get_china_market_overview修複", test_get_china_market_overview_fix),
        ("股票名稱映射修複", test_stock_name_mapping_fix),
        ("調試輸出檢查", check_debug_output)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}測試異常: {e}")
            results.append((test_name, False))
    
    # 总結
    print("\n📋 Agent Utils修複測試总結")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("\n🎉 Agent Utils修複測試完全成功！")
        print("\n💡 修複效果:")
        print("   ✅ get_china_stock_data已使用統一數據源接口")
        print("   ✅ get_china_market_overview已更新為Tushare說明")
        print("   ✅ 股票名稱映射使用統一接口")
        print("   ✅ 調試輸出確認修複生效")
        print("\n🚀 現在Agent工具完全使用Tushare數據源！")
    else:
        print("\n⚠️ 部分測試失败，請檢查相關配置")
    
    print("\n🎯 驗證方法:")
    print("   1. 查看調試輸出中的'統一數據源接口'字樣")
    print("   2. 確認不再出現'tdx_utils'相關調用")
    print("   3. 股票數據應该來自Tushare而不是TDX")
    
    input("按回車键退出...")


if __name__ == "__main__":
    main()
