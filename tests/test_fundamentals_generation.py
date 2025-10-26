#!/usr/bin/env python3
"""
基本面報告生成測試
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_fundamentals_generation():
    """測試基本面報告生成過程"""
    print("\n🔍 基本面報告生成測試")
    print("=" * 80)
    
    # 測試分眾傳媒 002027
    test_ticker = "002027"
    print(f"📊 測試股票代碼: {test_ticker} (分眾傳媒)")
    
    try:
        # 設置日誌級別
        from tradingagents.utils.logging_init import get_logger
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        print(f"\n🔧 步骤1: 獲取股票數據...")
        
        # 獲取股票數據
        from tradingagents.dataflows.interface import get_china_stock_data_tushare
        stock_data = get_china_stock_data_tushare(test_ticker, "2025-07-01", "2025-07-15")
        
        print(f"✅ 股票數據獲取完成，長度: {len(stock_data) if stock_data else 0}")
        print(f"📄 股票數據前200字符: {stock_data[:200] if stock_data else 'None'}")
        
        print(f"\n🔧 步骤2: 生成基本面報告...")
        
        # 生成基本面報告
        from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
        analyzer = OptimizedChinaDataProvider()
        
        fundamentals_report = analyzer._generate_fundamentals_report(test_ticker, stock_data)
        
        print(f"\n✅ 基本面報告生成完成")
        print(f"📊 報告長度: {len(fundamentals_report) if fundamentals_report else 0}")
        
        # 檢查報告中的股票代碼
        if fundamentals_report:
            print(f"\n🔍 檢查報告中的股票代碼...")
            if "002027" in fundamentals_report:
                print("✅ 報告中包含正確的股票代碼 002027")
                # 統計出現次數
                count_002027 = fundamentals_report.count("002027")
                print(f"   002027 出現次數: {count_002027}")
            else:
                print("❌ 報告中不包含正確的股票代碼 002027")
                
            if "002021" in fundamentals_report:
                print("⚠️ 報告中包含錯誤的股票代碼 002021")
                # 統計出現次數
                count_002021 = fundamentals_report.count("002021")
                print(f"   002021 出現次數: {count_002021}")
                
                # 找出錯誤代碼的位置
                import re
                positions = [m.start() for m in re.finditer("002021", fundamentals_report)]
                print(f"   002021 出現位置: {positions}")
                
                # 顯示錯誤代碼周围的文本
                for pos in positions[:3]:  # 只顯示前3個位置
                    start = max(0, pos - 50)
                    end = min(len(fundamentals_report), pos + 50)
                    context = fundamentals_report[start:end]
                    print(f"   位置 {pos} 周围文本: ...{context}...")
            else:
                print("✅ 報告中不包含錯誤的股票代碼 002021")
                
            # 顯示報告的前1000字符
            print(f"\n📄 報告前1000字符:")
            print("-" * 80)
            print(fundamentals_report[:1000])
            print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_industry_info():
    """測試行業信息獲取"""
    print("\n🔧 測試行業信息獲取")
    print("=" * 80)
    
    test_ticker = "002027"
    
    try:
        from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
        analyzer = OptimizedChinaDataProvider()
        
        print(f"🔧 測試 _get_industry_info...")
        industry_info = analyzer._get_industry_info(test_ticker)
        print(f"📊 行業信息: {industry_info}")
        
        print(f"\n🔧 測試 _estimate_financial_metrics...")
        financial_metrics = analyzer._estimate_financial_metrics(test_ticker, "¥7.67")
        print(f"📊 財務指標: {financial_metrics}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 開始基本面報告生成測試")
    
    # 測試1: 行業信息獲取
    success1 = test_industry_info()
    
    # 測試2: 完整基本面報告生成
    success2 = test_fundamentals_generation()
    
    if success1 and success2:
        print("\n✅ 所有測試通過")
    else:
        print("\n❌ 部分測試失败")
