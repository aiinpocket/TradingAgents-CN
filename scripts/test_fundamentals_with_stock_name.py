#!/usr/bin/env python3
"""
測試基本面分析是否能正確獲取股票名稱
驗證修複後的股票信息獲取功能
"""

import sys
import os

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_fundamentals_stock_name():
    """測試基本面分析中的股票名稱獲取"""
    print("🔍 測試基本面分析中的股票名稱獲取")
    print("=" * 50)
    
    # 測試股票代碼
    test_codes = ["603985", "000001", "300033"]
    
    for code in test_codes:
        print(f"\n📊 測試股票代碼: {code}")
        print("-" * 30)
        
        try:
            # 1. 獲取股票數據
            print(f"🔍 步骤1: 獲取股票數據...")
            from tradingagents.dataflows.interface import get_china_stock_data_unified
            stock_data = get_china_stock_data_unified(code, "2025-07-01", "2025-07-17")
            print(f"✅ 股票數據獲取完成，長度: {len(stock_data) if stock_data else 0}")
            
            # 2. 生成基本面報告
            print(f"🔍 步骤2: 生成基本面報告...")
            from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
            analyzer = OptimizedChinaDataProvider()
            
            fundamentals_report = analyzer._generate_fundamentals_report(code, stock_data)
            print(f"✅ 基本面報告生成完成，長度: {len(fundamentals_report)}")
            
            # 3. 檢查股票名稱
            print(f"🔍 步骤3: 檢查股票名稱...")
            if "股票名稱**: 未知公司" in fundamentals_report:
                print("❌ 仍然顯示'未知公司'")
            elif f"股票名稱**: 股票{code}" in fundamentals_report:
                print("❌ 仍然顯示默認股票名稱")
            else:
                # 提取股票名稱
                lines = fundamentals_report.split('\n')
                for line in lines:
                    if "**股票名稱**:" in line:
                        company_name = line.split(':')[1].strip()
                        print(f"✅ 成功獲取股票名稱: {company_name}")
                        break
                else:
                    print("❌ 未找到股票名稱行")
            
            # 4. 顯示報告前几行
            print(f"📄 報告前10行:")
            report_lines = fundamentals_report.split('\n')[:10]
            for line in report_lines:
                print(f"   {line}")
                
        except Exception as e:
            print(f"❌ 測試{code}失败: {e}")
            import traceback
            traceback.print_exc()

def test_stock_info_direct():
    """直接測試股票信息獲取"""
    print("\n🔍 直接測試股票信息獲取")
    print("=" * 50)
    
    test_code = "603985"  # 恒润股份
    
    try:
        # 測試統一接口
        from tradingagents.dataflows.interface import get_china_stock_info_unified
        stock_info = get_china_stock_info_unified(test_code)
        print(f"✅ 統一接口結果:")
        print(stock_info)
        
        # 測試DataSourceManager
        from tradingagents.dataflows.data_source_manager import get_data_source_manager
        manager = get_data_source_manager()
        manager_result = manager.get_stock_info(test_code)
        print(f"\n✅ DataSourceManager結果:")
        print(manager_result)
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

def test_fundamentals_with_fallback():
    """測試基本面分析的降級機制"""
    print("\n🔍 測試基本面分析的降級機制")
    print("=" * 50)
    
    # 測試不存在的股票代碼
    fake_code = "999999"
    
    try:
        print(f"📊 測試不存在的股票代碼: {fake_code}")
        
        # 1. 獲取股票數據（應该會降級）
        from tradingagents.dataflows.interface import get_china_stock_data_unified
        stock_data = get_china_stock_data_unified(fake_code, "2025-07-01", "2025-07-17")
        print(f"✅ 股票數據: {stock_data[:100] if stock_data else 'None'}...")
        
        # 2. 生成基本面報告
        from tradingagents.dataflows.optimized_china_data import OptimizedChinaDataProvider
        analyzer = OptimizedChinaDataProvider()
        
        fundamentals_report = analyzer._generate_fundamentals_report(fake_code, stock_data)
        
        # 3. 檢查是否使用了降級機制
        if "數據來源: akshare" in fundamentals_report or "數據來源: baostock" in fundamentals_report:
            print("✅ 基本面分析成功使用了降級機制")
        else:
            print("❌ 基本面分析未使用降級機制")
        
        # 4. 顯示報告前几行
        print(f"📄 報告前5行:")
        report_lines = fundamentals_report.split('\n')[:5]
        for line in report_lines:
            print(f"   {line}")
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

def test_complete_fundamentals_flow():
    """測試完整的基本面分析流程"""
    print("\n🔍 測試完整的基本面分析流程")
    print("=" * 50)
    
    test_code = "603985"  # 恒润股份
    
    try:
        # 模擬完整的基本面分析調用
        from tradingagents.agents.utils.agent_utils import AgentUtils
        
        print(f"📊 調用統一基本面分析工具...")
        result = AgentUtils.get_stock_fundamentals_unified(
            ticker=test_code,
            start_date="2025-07-01",
            end_date="2025-07-17",
            curr_date="2025-07-17"
        )
        
        print(f"✅ 基本面分析完成，結果長度: {len(result)}")
        
        # 檢查是否包含正確的股票名稱
        if "恒润股份" in result:
            print("✅ 基本面分析包含正確的股票名稱: 恒润股份")
        elif "未知公司" in result:
            print("❌ 基本面分析仍顯示'未知公司'")
        elif f"股票{test_code}" in result:
            print("❌ 基本面分析仍顯示默認股票名稱")
        else:
            print("🤔 無法確定股票名稱狀態")
        
        # 顯示結果前几行
        print(f"📄 基本面分析結果前10行:")
        result_lines = result.split('\n')[:10]
        for line in result_lines:
            print(f"   {line}")
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 基本面分析股票名稱獲取測試")
    print("=" * 80)
    print("📝 此測試驗證基本面分析是否能正確獲取股票名稱")
    print("=" * 80)
    
    # 1. 測試基本面分析中的股票名稱
    test_fundamentals_stock_name()
    
    # 2. 直接測試股票信息獲取
    test_stock_info_direct()
    
    # 3. 測試降級機制
    test_fundamentals_with_fallback()
    
    # 4. 測試完整流程
    test_complete_fundamentals_flow()
    
    print("\n📋 測試总結")
    print("=" * 60)
    print("✅ 基本面分析股票名稱獲取測試完成")
    print("🎯 現在基本面分析應该能顯示:")
    print("   - **股票名稱**: 恒润股份 (而不是'未知公司')")
    print("   - **所屬行業**: 电气設备 (而不是'未知')")
    print("   - **所屬地区**: 江苏 (而不是'未知')")
