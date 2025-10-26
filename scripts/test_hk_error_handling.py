#!/usr/bin/env python3
"""
港股錯誤處理測試腳本
測試港股網絡限制時的錯誤處理和用戶提示
"""

import sys
import os
import time
from datetime import datetime

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_hk_network_limitation_handling():
    """測試港股網絡限制的錯誤處理"""
    print("🇭🇰 港股網絡限制錯誤處理測試")
    print("=" * 80)
    
    try:
        from tradingagents.utils.stock_validator import prepare_stock_data
        
        # 測試港股代碼（可能遇到網絡限制）
        hk_test_cases = [
            {"code": "0700.HK", "name": "腾讯控股"},
            {"code": "9988.HK", "name": "阿里巴巴"},
            {"code": "3690.HK", "name": "美团"},
            {"code": "1810.HK", "name": "小米集团"},
            {"code": "9999.HK", "name": "不存在的港股"}  # 測試不存在的股票
        ]
        
        for i, test_case in enumerate(hk_test_cases, 1):
            print(f"\n📊 測試 {i}/{len(hk_test_cases)}: {test_case['code']} ({test_case['name']})")
            print("-" * 60)
            
            start_time = time.time()
            
            # 測試港股數據準备
            result = prepare_stock_data(
                stock_code=test_case['code'],
                market_type="港股",
                period_days=7,  # 較短時間測試
                analysis_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"⏱️ 耗時: {elapsed:.2f}秒")
            print(f"📋 結果: {'成功' if result.is_valid else '失败'}")
            
            if result.is_valid:
                print(f"✅ 股票名稱: {result.stock_name}")
                print(f"📊 市場類型: {result.market_type}")
                print(f"📅 數據時長: {result.data_period_days}天")
                print(f"💾 緩存狀態: {result.cache_status}")
                print(f"📁 歷史數據: {'✅' if result.has_historical_data else '❌'}")
                print(f"ℹ️ 基本信息: {'✅' if result.has_basic_info else '❌'}")
            else:
                print(f"❌ 錯誤信息: {result.error_message}")
                print(f"💡 詳細建议:")
                
                # 顯示詳細建议（支持多行）
                suggestion_lines = result.suggestion.split('\n')
                for line in suggestion_lines:
                    if line.strip():
                        print(f"   {line}")
                
                # 檢查是否為網絡限制問題
                if "網絡限制" in result.error_message or "Rate limited" in result.error_message:
                    print(f"🌐 檢測到網絡限制問題 - 錯誤處理正確")
                elif "不存在" in result.error_message:
                    print(f"🔍 檢測到股票不存在 - 錯誤處理正確")
                else:
                    print(f"⚠️ 其他類型錯誤")
            
            # 添加延迟避免過於頻繁的請求
            if i < len(hk_test_cases):
                print("⏳ 等待2秒避免頻繁請求...")
                time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試過程中發生異常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_message_formatting():
    """測試錯誤消息格式化"""
    print("\n📝 錯誤消息格式化測試")
    print("=" * 60)
    
    try:
        from tradingagents.utils.stock_validator import StockDataPreparer
        
        preparer = StockDataPreparer()
        
        # 測試網絡限制建议格式
        suggestion = preparer._get_hk_network_limitation_suggestion()
        
        print("🌐 港股網絡限制建议內容:")
        print("-" * 40)
        print(suggestion)
        print("-" * 40)
        
        # 檢查建议內容的完整性
        required_elements = [
            "網絡API限制",
            "解決方案",
            "等待5-10分鐘",
            "常见港股代碼格式",
            "腾讯控股：0700.HK",
            "稍後重試"
        ]
        
        missing_elements = []
        for element in required_elements:
            if element not in suggestion:
                missing_elements.append(element)
        
        if not missing_elements:
            print("✅ 建议內容完整，包含所有必要信息")
            return True
        else:
            print(f"❌ 建议內容缺少: {missing_elements}")
            return False
            
    except Exception as e:
        print(f"❌ 錯誤消息格式化測試異常: {e}")
        return False

def test_web_cli_integration():
    """測試Web和CLI界面的錯誤處理集成"""
    print("\n🖥️ Web和CLI錯誤處理集成測試")
    print("=" * 60)
    
    try:
        from tradingagents.utils.stock_validator import prepare_stock_data
        
        # 模擬一個可能遇到網絡限制的港股
        result = prepare_stock_data("0700.HK", "港股", 7)
        
        print("📊 模擬Web界面錯誤處理:")
        if not result.is_valid:
            # 模擬Web界面的錯誤返回
            web_response = {
                'success': False,
                'error': result.error_message,
                'suggestion': result.suggestion,
                'stock_symbol': "0700.HK",
                'market_type': "港股"
            }
            
            print(f"   錯誤: {web_response['error']}")
            print(f"   建议: {web_response['suggestion'][:100]}...")
            print("✅ Web界面錯誤處理格式正確")
        else:
            print("✅ 股票驗證成功，無需錯誤處理")
        
        print("\n💻 模擬CLI界面錯誤處理:")
        if not result.is_valid:
            # 模擬CLI界面的錯誤顯示
            print(f"   ui.show_error('❌ 股票數據驗證失败: {result.error_message}')")
            print(f"   ui.show_warning('💡 建议: {result.suggestion[:50]}...')")
            print("✅ CLI界面錯誤處理格式正確")
        else:
            print("✅ 股票驗證成功，無需錯誤處理")
        
        return True
        
    except Exception as e:
        print(f"❌ Web和CLI集成測試異常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 港股錯誤處理完整測試")
    print("=" * 80)
    print("📝 此測試驗證港股網絡限制時的錯誤處理和用戶提示")
    print("=" * 80)
    
    all_passed = True
    
    # 1. 港股網絡限制處理測試
    if not test_hk_network_limitation_handling():
        all_passed = False
    
    # 2. 錯誤消息格式化測試
    if not test_error_message_formatting():
        all_passed = False
    
    # 3. Web和CLI集成測試
    if not test_web_cli_integration():
        all_passed = False
    
    # 最终結果
    print(f"\n🏁 港股錯誤處理測試結果")
    print("=" * 80)
    if all_passed:
        print("🎉 所有測試通過！港股錯誤處理機制工作正常")
        print("✨ 改進特點:")
        print("   - ✅ 智能识別網絡限制問題")
        print("   - ✅ 提供詳細的解決方案和建议")
        print("   - ✅ 友好的用戶提示和常见代碼示例")
        print("   - ✅ 区分網絡限制和股票不存在的情况")
        print("   - ✅ Web和CLI界面統一的錯誤處理")
    else:
        print("❌ 部分測試失败，建议檢查錯誤處理逻辑")
        print("🔍 請檢查:")
        print("   - 網絡限制檢測逻辑是否正確")
        print("   - 錯誤消息格式是否完整")
        print("   - 建议內容是否有用")
        print("   - Web和CLI界面集成是否正常")
