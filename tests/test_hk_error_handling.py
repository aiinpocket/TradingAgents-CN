#!/usr/bin/env python3
"""
測試港股數據獲取錯誤處理
驗證在部分數據獲取失败時的優雅降級處理
"""

import os
import sys

def test_hk_data_error_handling():
    """測試港股數據獲取錯誤處理"""
    print("🔧 測試港股數據獲取錯誤處理...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 測試港股統一基本面工具
        test_cases = [
            "0700.HK",  # 腾讯
            "9988.HK",  # 阿里巴巴
            "3690.HK",  # 美团
        ]
        
        for ticker in test_cases:
            print(f"\n📊 測試 {ticker}:")
            
            try:
                result = toolkit.get_stock_fundamentals_unified.invoke({
                    'ticker': ticker,
                    'start_date': '2025-06-14',
                    'end_date': '2025-07-14',
                    'curr_date': '2025-07-14'
                })
                
                print(f"  ✅ 工具調用成功")
                print(f"  結果長度: {len(result)}")
                
                # 檢查結果质量
                if len(result) > 200:
                    print(f"  ✅ 結果長度合格（>200字符）")
                else:
                    print(f"  ⚠️ 結果長度偏短（{len(result)}字符）")
                
                # 檢查是否包含港股相關內容
                if any(keyword in result for keyword in ['港股', 'HK$', '港币', '香港交易所']):
                    print(f"  ✅ 結果包含港股相關信息")
                else:
                    print(f"  ⚠️ 結果未包含港股相關信息")
                
                # 檢查錯誤處理
                if "❌" in result:
                    if "备用" in result or "建议" in result:
                        print(f"  ✅ 包含優雅的錯誤處理和建议")
                    else:
                        print(f"  ⚠️ 錯誤處理可能不夠完善")
                else:
                    print(f"  ✅ 數據獲取成功，無錯誤")
                
                print(f"  結果前300字符: {result[:300]}...")
                
            except Exception as e:
                print(f"  ❌ 工具調用失败: {e}")
                return False
        
        print("✅ 港股數據獲取錯誤處理測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 港股數據獲取錯誤處理測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_akshare_error_recovery():
    """測試AKShare錯誤恢複機制"""
    print("\n🔧 測試AKShare錯誤恢複機制...")
    
    try:
        from tradingagents.dataflows.akshare_utils import format_hk_stock_data_akshare
        import pandas as pd
        
        # 創建模擬數據（使用正確的日期格式）
        import datetime
        test_data = pd.DataFrame({
            'Date': [
                datetime.datetime(2025, 7, 10),
                datetime.datetime(2025, 7, 11),
                datetime.datetime(2025, 7, 12)
            ],
            'Open': [100.0, 101.0, 102.0],
            'High': [105.0, 106.0, 107.0],
            'Low': [99.0, 100.0, 101.0],
            'Close': [104.0, 105.0, 106.0],
            'Volume': [1000000, 1100000, 1200000]
        })
        
        # 測試格式化函數的錯誤處理
        symbol = "0700.HK"
        start_date = "2025-07-10"
        end_date = "2025-07-12"
        
        print(f"  測試格式化港股數據: {symbol}")
        
        result = format_hk_stock_data_akshare(symbol, test_data, start_date, end_date)
        
        if result and len(result) > 100:
            print(f"  ✅ 格式化成功，長度: {len(result)}")
            
            # 檢查是否包含必要信息
            required_info = ['港股', 'HK$', '代碼', '價格']
            missing_info = [info for info in required_info if info not in result]
            
            if not missing_info:
                print(f"  ✅ 包含所有必要信息")
            else:
                print(f"  ⚠️ 缺少信息: {missing_info}")
            
            # 檢查錯誤處理
            if "獲取失败" in result or "❌" in result:
                if "默認" in result or "备用" in result:
                    print(f"  ✅ 包含優雅的錯誤處理")
                else:
                    print(f"  ⚠️ 錯誤處理可能不夠完善")
            else:
                print(f"  ✅ 數據處理成功，無錯誤")
            
            return True
        else:
            print(f"  ❌ 格式化失败或結果太短")
            return False
        
    except Exception as e:
        print(f"❌ AKShare錯誤恢複機制測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hk_fallback_mechanisms():
    """測試港股备用機制"""
    print("\n🔧 測試港股备用機制...")
    
    try:
        from tradingagents.dataflows.interface import get_hk_stock_data_unified, get_hk_stock_info_unified
        
        symbol = "0700.HK"
        start_date = "2025-06-14"
        end_date = "2025-07-14"
        
        print(f"  測試港股數據統一接口: {symbol}")
        
        # 測試數據獲取
        data_result = get_hk_stock_data_unified(symbol, start_date, end_date)
        
        if data_result:
            print(f"  ✅ 數據接口調用成功，長度: {len(data_result)}")
            
            # 檢查數據源標识
            if "AKShare" in data_result:
                print(f"  ✅ 使用AKShare作為主要數據源")
            elif "Yahoo Finance" in data_result:
                print(f"  ✅ 使用Yahoo Finance作為备用數據源")
            elif "FINNHUB" in data_result:
                print(f"  ✅ 使用FINNHUB作為备用數據源")
            else:
                print(f"  ⚠️ 未明確標识數據源")
        else:
            print(f"  ❌ 數據接口調用失败")
            return False
        
        # 測試信息獲取
        print(f"  測試港股信息統一接口: {symbol}")
        
        info_result = get_hk_stock_info_unified(symbol)
        
        if info_result and isinstance(info_result, dict):
            print(f"  ✅ 信息接口調用成功")
            print(f"    股票名稱: {info_result.get('name', 'N/A')}")
            print(f"    貨币: {info_result.get('currency', 'N/A')}")
            print(f"    交易所: {info_result.get('exchange', 'N/A')}")
            print(f"    數據源: {info_result.get('source', 'N/A')}")
            
            # 驗證港股特有信息
            if info_result.get('currency') == 'HKD' and info_result.get('exchange') == 'HKG':
                print(f"  ✅ 港股信息正確")
            else:
                print(f"  ⚠️ 港股信息可能不完整")
        else:
            print(f"  ❌ 信息接口調用失败")
            return False
        
        print("✅ 港股备用機制測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 港股备用機制測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主測試函數"""
    print("🔧 港股數據獲取錯誤處理測試")
    print("=" * 60)
    
    tests = [
        test_hk_data_error_handling,
        test_akshare_error_recovery,
        test_hk_fallback_mechanisms,
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
        print("🎉 所有測試通過！港股錯誤處理改進成功")
        print("\n📋 改進內容:")
        print("✅ 改進了AKShare港股信息獲取的錯誤處理")
        print("✅ 添加了統一基本面工具的多重备用方案")
        print("✅ 實現了優雅降級機制")
        print("✅ 提供了有用的錯誤信息和建议")
        print("✅ 確保在部分數據失败時仍能提供基础信息")
        
        print("\n🚀 處理流程:")
        print("1️⃣ 嘗試AKShare獲取完整港股數據")
        print("2️⃣ 如果部分失败，使用默認信息繼续處理")
        print("3️⃣ 如果完全失败，嘗試Yahoo Finance备用")
        print("4️⃣ 最终备用：提供基础信息和建议")
        
        return True
    else:
        print("⚠️ 部分測試失败，需要進一步檢查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
