"""
測試港股驗證修複
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_hk_validation():
    """測試港股驗證"""
    print("🧪 測試港股驗證修複...")
    
    try:
        from web.utils.analysis_runner import validate_analysis_params
        
        # 測試用例
        test_cases = [
            # (股票代碼, 市場類型, 應該通過驗證)
            ("0700.HK", "港股", True),
            ("9988.HK", "港股", True),
            ("3690.HK", "港股", True),
            ("0700", "港股", True),
            ("9988", "港股", True),
            ("3690", "港股", True),
            ("AAPL", "港股", False),  # 美股代碼
            ("000001", "港股", False),  # A股代碼
            ("00", "港股", False),  # 太短
            ("12345", "港股", False),  # 太長
            ("ABC.HK", "港股", False),  # 非數字
        ]
        
        passed = 0
        total = len(test_cases)
        
        for symbol, market_type, should_pass in test_cases:
            is_valid, errors = validate_analysis_params(
                stock_symbol=symbol,
                analysis_date="2025-07-14",
                analysts=["market"],
                research_depth=3,
                market_type=market_type
            )

            validation_passed = is_valid
            
            if validation_passed == should_pass:
                print(f"  ✅ {symbol} ({market_type}): {'通過' if validation_passed else '失敗'}")
                passed += 1
            else:
                print(f"  ❌ {symbol} ({market_type}): 期望{'通過' if should_pass else '失敗'}, 實際{'通過' if validation_passed else '失敗'}")
                if errors:
                    print(f"      錯誤: {errors}")
        
        print(f"\n驗證測試結果: {passed}/{total} 通過")
        
        if passed == total:
            print("🎉 所有驗證測試通過！")
            return True
        else:
            print("⚠️ 部分驗證測試失敗")
            return False
        
    except Exception as e:
        print(f"❌ 驗證測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_case():
    """測試具體的0700.HK案例"""
    print("\n🧪 測試具體的0700.HK案例...")
    
    try:
        from web.utils.analysis_runner import validate_analysis_params
        
        # 測試0700.HK
        is_valid, errors = validate_analysis_params(
            stock_symbol="0700.HK",
            analysis_date="2025-07-14",
            analysts=["market", "fundamentals"],
            research_depth=3,
            market_type="港股"
        )

        print(f"  股票代碼: 0700.HK")
        print(f"  市場類型: 港股")
        print(f"  驗證結果: {'通過' if is_valid else '失敗'}")

        if not is_valid:
            print(f"  錯誤信息: {errors}")
            return False
        else:
            print("  ✅ 0700.HK驗證通過！")
            return True
        
    except Exception as e:
        print(f"❌ 具體案例測試失敗: {e}")
        return False

def test_regex_patterns():
    """測試正則表達式模式"""
    print("\n🧪 測試正則表達式模式...")
    
    try:
        import re
        
        # 測試港股正則模式（支持4-5位數字）
        hk_pattern = r'^\d{4,5}\.HK$'
        digit_pattern = r'^\d{4}$'
        
        test_symbols = [
            "0700.HK",
            "9988.HK", 
            "3690.HK",
            "0700",
            "9988",
            "3690",
            "AAPL",
            "000001",
            "ABC.HK"
        ]
        
        for symbol in test_symbols:
            symbol_upper = symbol.upper()
            hk_match = re.match(hk_pattern, symbol_upper)
            digit_match = re.match(digit_pattern, symbol)
            
            matches = bool(hk_match or digit_match)
            
            print(f"  {symbol}: HK格式={bool(hk_match)}, 數字格式={bool(digit_match)}, 總體匹配={matches}")
        
        return True
        
    except Exception as e:
        print(f"❌ 正則表達式測試失敗: {e}")
        return False

def main():
    """運行所有測試"""
    print("🔧 港股驗證修複測試")
    print("=" * 40)
    
    tests = [
        test_regex_patterns,
        test_specific_case,
        test_hk_validation
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 異常: {e}")
    
    print("\n" + "=" * 40)
    print(f"🔧 修複測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 港股驗證修複成功！")
        print("\n現在可以正常使用0700.HK進行分析了")
    else:
        print("⚠️ 修複可能不完整，請檢查失敗的測試")

if __name__ == "__main__":
    main()
