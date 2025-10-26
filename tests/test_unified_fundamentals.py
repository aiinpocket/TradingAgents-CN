#!/usr/bin/env python3
"""
測試統一基本面分析工具
驗證新的統一工具方案是否有效
"""

import os
import sys

def test_unified_tool_directly():
    """直接測試統一基本面分析工具"""
    print("🔧 直接測試統一基本面分析工具...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 測試不同類型的股票
        test_cases = [
            ("0700.HK", "港股"),
            ("9988.HK", "港股"),
            ("000001", "中國A股"),
            ("AAPL", "美股"),
        ]
        
        for ticker, expected_type in test_cases:
            print(f"\n📊 測試 {ticker} ({expected_type}):")
            
            try:
                result = toolkit.get_stock_fundamentals_unified.invoke({
                    'ticker': ticker,
                    'start_date': '2025-06-14',
                    'end_date': '2025-07-14',
                    'curr_date': '2025-07-14'
                })
                
                print(f"  ✅ 工具調用成功")
                print(f"  結果長度: {len(result)}")
                print(f"  結果前200字符: {result[:200]}...")
                
                # 檢查結果是否包含預期內容
                if expected_type in result:
                    print(f"  ✅ 結果包含正確的股票類型")
                else:
                    print(f"  ⚠️ 結果未包含預期的股票類型")
                
                # 檢查是否包含貨币信息
                if any(currency in result for currency in ['¥', 'HK$', '$']):
                    print(f"  ✅ 結果包含貨币信息")
                else:
                    print(f"  ⚠️ 結果未包含貨币信息")
                    
            except Exception as e:
                print(f"  ❌ 工具調用失败: {e}")
                return False
        
        print("✅ 統一工具直接測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 統一工具直接測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fundamentals_analyst_with_unified_tool():
    """測試基本面分析師使用統一工具"""
    print("\n🔧 測試基本面分析師使用統一工具...")
    
    try:
        from tradingagents.agents.analysts.fundamentals_analyst import create_fundamentals_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        
        # 檢查API密鑰
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("⚠️ 未找到DASHSCOPE_API_KEY，跳過LLM測試")
            return True
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 創建工具包
        toolkit = Toolkit(config)
        
        # 創建LLM
        llm = ChatDashScopeOpenAI(
            model="qwen-turbo",
            temperature=0.1,
            max_tokens=1000
        )
        
        # 創建基本面分析師
        analyst = create_fundamentals_analyst(llm, toolkit)
        
        # 測試港股
        state = {
            "trade_date": "2025-07-14",
            "company_of_interest": "0700.HK",
            "messages": []
        }
        
        print(f"  測試港股基本面分析: {state['company_of_interest']}")
        
        # 調用分析師
        result = analyst(state)
        
        print(f"  ✅ 基本面分析師調用完成")
        print(f"  結果類型: {type(result)}")
        
        if isinstance(result, dict) and 'fundamentals_report' in result:
            report = result['fundamentals_report']
            print(f"  報告長度: {len(report)}")
            print(f"  報告前200字符: {report[:200]}...")
            
            # 檢查報告质量
            if len(report) > 200:
                print(f"  ✅ 報告長度合格（>200字符）")
            else:
                print(f"  ⚠️ 報告長度偏短（{len(report)}字符）")
            
            # 檢查是否包含港币相關內容
            if 'HK$' in report or '港币' in report or '港元' in report:
                print(f"  ✅ 報告包含港币計價")
            else:
                print(f"  ⚠️ 報告未包含港币計價")
        else:
            print(f"  ❌ 未找到基本面報告")
            return False
        
        print("✅ 基本面分析師統一工具測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 基本面分析師統一工具測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stock_type_detection():
    """測試股票類型檢測"""
    print("\n🔧 測試股票類型檢測...")
    
    try:
        from tradingagents.utils.stock_utils import StockUtils
        
        test_cases = [
            ("0700.HK", "港股", "港币", "HK$"),
            ("9988.HK", "港股", "港币", "HK$"),
            ("000001", "中國A股", "人民币", "¥"),
            ("600036", "中國A股", "人民币", "¥"),
            ("AAPL", "美股", "美元", "$"),
        ]
        
        for ticker, expected_market, expected_currency, expected_symbol in test_cases:
            market_info = StockUtils.get_market_info(ticker)
            
            print(f"  {ticker}:")
            print(f"    市場: {market_info['market_name']}")
            print(f"    貨币: {market_info['currency_name']} ({market_info['currency_symbol']})")
            
            # 驗證結果
            if (expected_market in market_info['market_name'] and 
                market_info['currency_name'] == expected_currency and
                market_info['currency_symbol'] == expected_symbol):
                print(f"    ✅ 识別正確")
            else:
                print(f"    ❌ 识別錯誤")
                return False
        
        print("✅ 股票類型檢測測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 股票類型檢測測試失败: {e}")
        return False


def main():
    """主測試函數"""
    print("🔧 統一基本面分析工具測試")
    print("=" * 60)
    
    tests = [
        test_stock_type_detection,
        test_unified_tool_directly,
        test_fundamentals_analyst_with_unified_tool,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ 測試失败: {test.__name__}")
        except Exception as e:
            print(f"❌ 測試異常: {test.__name__} - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！統一基本面分析工具方案成功")
        print("\n📋 方案優势:")
        print("✅ 簡化了工具選擇逻辑")
        print("✅ 工具內部自動识別股票類型")
        print("✅ 避免了LLM工具調用混乱")
        print("✅ 統一的系統提示和處理流程")
        print("✅ 更容易維護和擴展")
        return True
    else:
        print("⚠️ 部分測試失败，需要進一步檢查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
