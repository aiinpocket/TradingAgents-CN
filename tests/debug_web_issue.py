"""
調試Web界面顯示"True"的問題
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_form_data_structure():
    """測試表單數據結構"""
    print(" 測試表單數據結構...")
    
    try:
        # 模擬表單數據
        form_data_submitted = {
            'submitted': True,
            'stock_symbol': '0700.HK',
            'market_type': '港股',
            'analysis_date': '2025-07-14',
            'analysts': ['market', 'fundamentals'],
            'research_depth': 3,
            'include_sentiment': True,
            'include_risk_assessment': True,
            'custom_prompt': ''
        }
        
        form_data_not_submitted = {
            'submitted': False
        }
        
        print("  提交時的表單數據:")
        for key, value in form_data_submitted.items():
            print(f"    {key}: {value} ({type(value).__name__})")
        
        print("\n  未提交時的表單數據:")
        for key, value in form_data_not_submitted.items():
            print(f"    {key}: {value} ({type(value).__name__})")
        
        # 檢查條件判斷
        if form_data_submitted.get('submitted', False):
            print("\n   提交條件判斷正確")
        else:
            print("\n   提交條件判斷錯誤")
        
        if form_data_not_submitted.get('submitted', False):
            print("   未提交條件判斷錯誤")
        else:
            print("   未提交條件判斷正確")
        
        return True
        
    except Exception as e:
        print(f" 表單數據結構測試失敗: {e}")
        return False

def test_validation_function():
    """測試驗證函數"""
    print("\n 測試驗證函數...")
    
    try:
        from web.utils.analysis_runner import validate_analysis_params
        
        # 測試港股驗證
        errors = validate_analysis_params(
            stock_symbol="0700.HK",
            analysis_date="2025-07-14",
            analysts=["market", "fundamentals"],
            research_depth=3,
            market_type="港股"
        )
        
        print(f"  港股驗證結果: {errors}")
        
        if not errors:
            print("   港股驗證通過")
        else:
            print(f"   港股驗證失敗: {errors}")
            return False
        
        return True
        
    except Exception as e:
        print(f" 驗證函數測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis_runner_import():
    """測試分析運行器導入"""
    print("\n 測試分析運行器導入...")
    
    try:
        from web.utils.analysis_runner import run_stock_analysis, validate_analysis_params, format_analysis_results
        print("   分析運行器導入成功")
        
        # 測試函數簽名
        import inspect
        
        sig = inspect.signature(run_stock_analysis)
        print(f"  run_stock_analysis 參數: {list(sig.parameters.keys())}")
        
        sig = inspect.signature(validate_analysis_params)
        print(f"  validate_analysis_params 參數: {list(sig.parameters.keys())}")
        
        return True
        
    except Exception as e:
        print(f" 分析運行器導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_components():
    """測試Streamlit組件"""
    print("\n 測試Streamlit組件...")
    
    try:
        # 測試組件導入
        from web.components.analysis_form import render_analysis_form
        from web.components.results_display import render_results
        
        print("   Streamlit組件導入成功")
        
        return True
        
    except Exception as e:
        print(f" Streamlit組件測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_potential_output_sources():
    """檢查可能的輸出源"""
    print("\n 檢查可能的輸出源...")
    
    # 檢查可能輸出"True"的地方
    potential_sources = [
        "表單提交狀態直接輸出",
        "布爾值轉換為字符串",
        "調試語句殘留",
        "異常處理中的輸出",
        "Streamlit組件的意外輸出"
    ]
    
    for source in potential_sources:
        print(f"   檢查: {source}")
    
    print("\n   建議檢查:")
    print("    1. 搜索代碼中的 st.write(True) 或類似語句")
    print("    2. 檢查是否有 print(True) 語句")
    print("    3. 查看是否有布爾值被意外顯示")
    print("    4. 檢查表單組件的返回值處理")
    
    return True

def main():
    """運行所有調試測試"""
    print(" 開始調試Web界面'True'顯示問題")
    print("=" * 50)
    
    tests = [
        test_form_data_structure,
        test_validation_function,
        test_analysis_runner_import,
        test_streamlit_components,
        check_potential_output_sources
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f" 測試 {test_func.__name__} 異常: {e}")
    
    print("\n" + "=" * 50)
    print(f" 調試測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print(" 所有測試通過，問題可能在Streamlit運行時環境")
    else:
        print(" 發現問題，請檢查失敗的測試項")
    
    print("\n 解決建議:")
    print("1. 重啟Streamlit應用")
    print("2. 清除瀏覽器緩存")
    print("3. 檢查是否有殘留的調試輸出")
    print("4. 確認所有組件正確導入")

if __name__ == "__main__":
    main()
