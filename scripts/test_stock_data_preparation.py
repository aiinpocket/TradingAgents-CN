#!/usr/bin/env python3
"""
股票數據預獲取功能測試腳本
驗證新的股票數據準备機制是否正常工作
"""

import sys
import os
import time
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_stock_data_preparation():
    """測試股票數據預獲取功能"""
    print("🧪 股票數據預獲取功能測試")
    print("=" * 80)
    
    try:
        from tradingagents.utils.stock_validator import prepare_stock_data, get_stock_preparation_message
        
        # 測試用例
        test_cases = [
            # A股測試
            {"code": "000001", "market": "A股", "name": "平安銀行", "should_exist": True},
            {"code": "603985", "market": "A股", "name": "恒润股份", "should_exist": True},
            {"code": "999999", "market": "A股", "name": "不存在的股票", "should_exist": False},
            
            # 港股測試
            {"code": "0700.HK", "market": "港股", "name": "腾讯控股", "should_exist": True},
            {"code": "9988.HK", "market": "港股", "name": "阿里巴巴", "should_exist": True},
            {"code": "9999.HK", "market": "港股", "name": "不存在的港股", "should_exist": False},
            
            # 美股測試
            {"code": "AAPL", "market": "美股", "name": "苹果公司", "should_exist": True},
            {"code": "TSLA", "market": "美股", "name": "特斯拉", "should_exist": True},
            {"code": "ZZZZ", "market": "美股", "name": "不存在的美股", "should_exist": False},
        ]
        
        success_count = 0
        total_count = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📊 測試 {i}/{total_count}: {test_case['code']} ({test_case['market']})")
            print("-" * 60)
            
            start_time = time.time()
            
            # 測試數據準备
            result = prepare_stock_data(
                stock_code=test_case['code'],
                market_type=test_case['market'],
                period_days=30,  # 測試30天數據
                analysis_date=datetime.now().strftime('%Y-%m-%d')
            )
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            print(f"⏱️ 耗時: {elapsed:.2f}秒")
            print(f"📋 結果: {'成功' if result.is_valid else '失败'}")
            
            if result.is_valid:
                print(f"📈 股票名稱: {result.stock_name}")
                print(f"📊 市場類型: {result.market_type}")
                print(f"📅 數據時長: {result.data_period_days}天")
                print(f"💾 緩存狀態: {result.cache_status}")
                print(f"📁 歷史數據: {'✅' if result.has_historical_data else '❌'}")
                print(f"ℹ️ 基本信息: {'✅' if result.has_basic_info else '❌'}")
            else:
                print(f"❌ 錯誤信息: {result.error_message}")
                print(f"💡 建议: {result.suggestion}")
            
            # 驗證結果是否符合預期
            if result.is_valid == test_case['should_exist']:
                print("✅ 測試通過")
                success_count += 1
            else:
                expected = "存在" if test_case['should_exist'] else "不存在"
                actual = "存在" if result.is_valid else "不存在"
                print(f"❌ 測試失败: 預期{expected}，實际{actual}")
            
            # 測試便捷函數
            message = get_stock_preparation_message(
                test_case['code'], 
                test_case['market'], 
                30
            )
            print(f"📝 便捷函數消息: {message[:100]}...")
        
        # 測試总結
        print(f"\n📋 測試总結")
        print("=" * 60)
        print(f"✅ 成功: {success_count}/{total_count}")
        print(f"❌ 失败: {total_count - success_count}/{total_count}")
        print(f"📊 成功率: {success_count/total_count*100:.1f}%")
        
        if success_count == total_count:
            print("🎉 所有測試通過！股票數據預獲取功能正常工作")
            return True
        else:
            print("⚠️ 部分測試失败，需要檢查功能實現")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程中發生異常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_format_validation():
    """測試格式驗證功能"""
    print("\n🔍 格式驗證測試")
    print("=" * 60)
    
    try:
        from tradingagents.utils.stock_validator import prepare_stock_data
        
        format_tests = [
            # 格式正確的測試
            {"code": "000001", "market": "A股", "should_pass": True},
            {"code": "0700.HK", "market": "港股", "should_pass": True},
            {"code": "AAPL", "market": "美股", "should_pass": True},
            
            # 格式錯誤的測試
            {"code": "00001", "market": "A股", "should_pass": False},  # 5位數字
            {"code": "ABC.HK", "market": "港股", "should_pass": False},  # 字母
            {"code": "123", "market": "美股", "should_pass": False},  # 數字
            {"code": "", "market": "A股", "should_pass": False},  # 空字符串
        ]
        
        format_success = 0
        
        for i, test in enumerate(format_tests, 1):
            print(f"\n📝 格式測試 {i}: '{test['code']}' ({test['market']})")
            
            result = prepare_stock_data(test['code'], test['market'])
            
            # 格式錯誤應该在數據獲取前就被拦截
            format_passed = not (result.error_message and "格式錯誤" in result.error_message)
            
            if format_passed == test['should_pass']:
                print("✅ 格式驗證通過")
                format_success += 1
            else:
                print(f"❌ 格式驗證失败: {result.error_message}")
        
        print(f"\n📊 格式驗證成功率: {format_success}/{len(format_tests)} ({format_success/len(format_tests)*100:.1f}%)")
        return format_success == len(format_tests)
        
    except Exception as e:
        print(f"❌ 格式驗證測試異常: {e}")
        return False

def test_performance():
    """測試性能表現"""
    print("\n⚡ 性能測試")
    print("=" * 60)
    
    try:
        from tradingagents.utils.stock_validator import prepare_stock_data
        
        # 測試真實股票的性能
        performance_tests = [
            {"code": "000001", "market": "A股"},
            {"code": "0700.HK", "market": "港股"},
            {"code": "AAPL", "market": "美股"},
        ]
        
        for test in performance_tests:
            print(f"\n🚀 性能測試: {test['code']} ({test['market']})")
            
            start_time = time.time()
            result = prepare_stock_data(test['code'], test['market'], period_days=7)  # 較短時間測試
            end_time = time.time()
            
            elapsed = end_time - start_time
            print(f"⏱️ 耗時: {elapsed:.2f}秒")
            
            if elapsed > 30:
                print("⚠️ 性能較慢，可能需要優化")
            elif elapsed > 15:
                print("⚡ 性能一般")
            else:
                print("🚀 性能良好")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能測試異常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 股票數據預獲取功能完整測試")
    print("=" * 80)
    print("📝 此測試驗證新的股票數據預獲取和驗證機制")
    print("=" * 80)
    
    all_passed = True
    
    # 1. 主要功能測試
    if not test_stock_data_preparation():
        all_passed = False
    
    # 2. 格式驗證測試
    if not test_format_validation():
        all_passed = False
    
    # 3. 性能測試
    if not test_performance():
        all_passed = False
    
    # 最终結果
    print(f"\n🏁 最终測試結果")
    print("=" * 80)
    if all_passed:
        print("🎉 所有測試通過！股票數據預獲取功能可以投入使用")
        print("✨ 功能特點:")
        print("   - 支持A股、港股、美股數據預獲取")
        print("   - 自動緩存歷史數據和基本信息")
        print("   - 智能格式驗證和錯誤提示")
        print("   - 合理的性能表現")
    else:
        print("❌ 部分測試失败，建议檢查和優化功能實現")
        print("🔍 請檢查:")
        print("   - 數據源連接是否正常")
        print("   - 網絡連接是否穩定")
        print("   - 相關依賴是否正確安裝")
