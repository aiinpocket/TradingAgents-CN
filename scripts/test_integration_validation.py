#!/usr/bin/env python3
"""
集成驗證測試腳本
測試Web和CLI界面中的股票數據預獲取功能是否正常工作
"""

import sys
import os
import time
from datetime import datetime

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_web_integration():
    """測試Web界面集成"""
    print("🌐 測試Web界面集成")
    print("=" * 60)
    
    try:
        # 導入Web分析運行器
        from web.utils.analysis_runner import run_stock_analysis
        
        # 模擬Web界面的進度更新函數
        progress_messages = []
        
        def mock_update_progress(message, current=None, total=None):
            progress_messages.append(message)
            if current and total:
                print(f"📊 進度 {current}/{total}: {message}")
            else:
                print(f"📊 {message}")
        
        # 測試有效股票代碼
        print("\n🧪 測試有效股票代碼: 000001 (A股)")
        start_time = time.time()
        
        try:
            result = run_stock_analysis(
                stock_symbol="000001",
                market_type="A股",
                analysts=["fundamentals"],
                research_depth="快速",
                llm_provider="dashscope",
                llm_model="qwen-plus-latest",
                analysis_date=datetime.now().strftime('%Y-%m-%d'),
                progress_callback=mock_update_progress
            )
            
            elapsed = time.time() - start_time
            
            if result and result.get('success'):
                print(f"✅ Web集成測試成功 (耗時: {elapsed:.2f}秒)")
                print(f"📋 分析結果: {result.get('stock_symbol')} - {result.get('session_id')}")
                return True
            else:
                print(f"❌ Web集成測試失败: {result.get('error', '未知錯誤')}")
                return False
                
        except Exception as e:
            print(f"❌ Web集成測試異常: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ 無法導入Web模塊: {e}")
        return False

def test_cli_integration():
    """測試CLI界面集成"""
    print("\n💻 測試CLI界面集成")
    print("=" * 60)
    
    try:
        # 導入CLI相關模塊
        from cli.main import get_ticker
        
        # 模擬A股市場配置
        a_stock_market = {
            "name": "A股",
            "name_en": "A-Share",
            "default": "000001",
            "examples": ["000001 (平安銀行)", "600519 (贵州茅台)", "000858 (五粮液)"],
            "format": "6位數字 (如: 000001)",
            "pattern": r'^\d{6}$',
            "data_source": "china_stock"
        }
        
        # 測試股票代碼格式驗證
        print("\n🧪 測試股票代碼格式驗證")
        import re
        
        test_codes = [
            ("000001", True, "平安銀行"),
            ("600519", True, "贵州茅台"),
            ("999999", True, "格式正確但不存在"),
            ("00001", False, "位數不足"),
            ("AAPL", False, "美股代碼"),
            ("", False, "空代碼")
        ]
        
        validation_success = 0
        for code, should_pass, description in test_codes:
            matches = bool(re.match(a_stock_market["pattern"], code))
            status = "✅" if matches == should_pass else "❌"
            print(f"  {code}: {status} ({description})")
            if matches == should_pass:
                validation_success += 1
        
        print(f"\n📊 格式驗證成功率: {validation_success}/{len(test_codes)} ({validation_success/len(test_codes)*100:.1f}%)")
        
        # 測試數據預獲取功能
        print("\n🧪 測試CLI數據預獲取功能")
        from tradingagents.utils.stock_validator import prepare_stock_data
        
        result = prepare_stock_data("000001", "A股", 7)  # 測試7天數據
        
        if result.is_valid:
            print(f"✅ CLI數據預獲取成功: {result.stock_name}")
            print(f"📊 緩存狀態: {result.cache_status}")
            return True
        else:
            print(f"❌ CLI數據預獲取失败: {result.error_message}")
            return False
            
    except Exception as e:
        print(f"❌ CLI集成測試異常: {e}")
        return False

def test_error_handling():
    """測試錯誤處理"""
    print("\n🚨 測試錯誤處理")
    print("=" * 60)
    
    try:
        from tradingagents.utils.stock_validator import prepare_stock_data
        
        # 測試不存在的股票代碼
        error_tests = [
            ("999999", "A股", "不存在的A股"),
            ("9999.HK", "港股", "不存在的港股"),
            ("ZZZZ", "美股", "不存在的美股"),
            ("", "A股", "空代碼"),
            ("ABC123", "A股", "格式錯誤")
        ]
        
        error_handling_success = 0
        
        for code, market, description in error_tests:
            print(f"\n🧪 測試: {description} ({code})")
            
            result = prepare_stock_data(code, market, 7)
            
            if not result.is_valid:
                print(f"✅ 正確识別錯誤: {result.error_message}")
                if result.suggestion:
                    print(f"💡 建议: {result.suggestion}")
                error_handling_success += 1
            else:
                print(f"❌ 未能识別錯誤，錯誤地認為股票存在")
        
        print(f"\n📊 錯誤處理成功率: {error_handling_success}/{len(error_tests)} ({error_handling_success/len(error_tests)*100:.1f}%)")
        return error_handling_success == len(error_tests)
        
    except Exception as e:
        print(f"❌ 錯誤處理測試異常: {e}")
        return False

def test_performance():
    """測試性能表現"""
    print("\n⚡ 測試性能表現")
    print("=" * 60)
    
    try:
        from tradingagents.utils.stock_validator import prepare_stock_data
        
        # 測試多個股票的性能
        performance_tests = [
            ("000001", "A股", "平安銀行"),
            ("600519", "A股", "贵州茅台"),
            ("AAPL", "美股", "苹果公司")
        ]
        
        total_time = 0
        success_count = 0
        
        for code, market, name in performance_tests:
            print(f"\n🚀 性能測試: {name} ({code})")
            
            start_time = time.time()
            result = prepare_stock_data(code, market, 7)
            elapsed = time.time() - start_time
            
            total_time += elapsed
            
            if result.is_valid:
                print(f"✅ 成功 (耗時: {elapsed:.2f}秒)")
                success_count += 1
                
                if elapsed < 5:
                    print("🚀 性能優秀")
                elif elapsed < 15:
                    print("⚡ 性能良好")
                else:
                    print("⚠️ 性能較慢")
            else:
                print(f"❌ 失败: {result.error_message}")
        
        avg_time = total_time / len(performance_tests)
        print(f"\n📊 性能总結:")
        print(f"   成功率: {success_count}/{len(performance_tests)} ({success_count/len(performance_tests)*100:.1f}%)")
        print(f"   平均耗時: {avg_time:.2f}秒")
        print(f"   总耗時: {total_time:.2f}秒")
        
        return success_count >= len(performance_tests) * 0.8  # 80%成功率
        
    except Exception as e:
        print(f"❌ 性能測試異常: {e}")
        return False

if __name__ == "__main__":
    print("🧪 股票數據預獲取集成測試")
    print("=" * 80)
    print("📝 此測試驗證Web和CLI界面中的股票驗證功能是否正常工作")
    print("=" * 80)
    
    all_passed = True
    
    # 1. Web界面集成測試
    if not test_web_integration():
        all_passed = False
    
    # 2. CLI界面集成測試
    if not test_cli_integration():
        all_passed = False
    
    # 3. 錯誤處理測試
    if not test_error_handling():
        all_passed = False
    
    # 4. 性能測試
    if not test_performance():
        all_passed = False
    
    # 最终結果
    print(f"\n🏁 集成測試結果")
    print("=" * 80)
    if all_passed:
        print("🎉 所有集成測試通過！股票數據預獲取功能已成功集成到Web和CLI界面")
        print("✨ 功能特點:")
        print("   - ✅ 在分析開始前驗證股票是否存在")
        print("   - ✅ 預先獲取和緩存歷史數據和基本信息")
        print("   - ✅ 避免對假股票代碼執行完整分析流程")
        print("   - ✅ 提供友好的錯誤提示和建议")
        print("   - ✅ 良好的性能表現")
    else:
        print("❌ 部分集成測試失败，建议檢查和優化")
        print("🔍 請檢查:")
        print("   - Web和CLI界面的導入路徑是否正確")
        print("   - 數據源連接是否正常")
        print("   - 網絡連接是否穩定")
        print("   - 相關依賴是否正確安裝")
