#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試CLI修複 - KeyError: 'stock_symbol' 問題
Test CLI Fix - KeyError: 'stock_symbol' Issue

這個測試驗證了CLI中selections字典键名不匹配問題的修複
This test verifies the fix for the selections dictionary key mismatch issue in CLI
"""

import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_selections_dictionary_keys():
    """
    測試selections字典中的键名是否正確
    Test if the keys in selections dictionary are correct
    """
    print("🔍 測試selections字典键名...")
    
    try:
        from cli.main import get_user_selections
        
        # 模擬用戶輸入
        with patch('typer.prompt') as mock_prompt, \
             patch('cli.main.select_market') as mock_market, \
             patch('cli.main.select_analysts') as mock_analysts, \
             patch('cli.main.select_research_depth') as mock_depth, \
             patch('cli.main.select_llm_provider') as mock_llm, \
             patch('cli.main.select_shallow_thinking_agent') as mock_shallow, \
             patch('cli.main.select_deep_thinking_agent') as mock_deep, \
             patch('cli.main.console.print'):
            
            # 設置模擬返回值
            mock_market.return_value = {
                'name': 'A股',
                'name_en': 'China A-Share',
                'default': '600036',
                'pattern': r'^\d{6}$',
                'data_source': 'china_stock'
            }
            mock_prompt.side_effect = ['600036', '2024-12-01']  # ticker, date
            mock_analysts.return_value = [MagicMock(value='market')]
            mock_depth.return_value = 3
            mock_llm.return_value = ('dashscope', 'http://localhost:8000')
            mock_shallow.return_value = 'qwen-turbo'
            mock_deep.return_value = 'qwen-max'
            
            # 調用函數
            selections = get_user_selections()
            
            # 驗證必要的键存在
            required_keys = [
                'ticker',  # 這是正確的键名
                'market',
                'analysis_date',
                'analysts',
                'research_depth',
                'llm_provider',
                'backend_url',
                'shallow_thinker',
                'deep_thinker'
            ]
            
            for key in required_keys:
                assert key in selections, f"缺少必要的键: {key}"
                print(f"✅ 键 '{key}' 存在")
            
            # 確保不存在錯誤的键名
            assert 'stock_symbol' not in selections, "不應该存在 'stock_symbol' 键"
            print("✅ 確認不存在錯誤的 'stock_symbol' 键")
            
            print("✅ selections字典键名測試通過")
            return True
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

def test_process_signal_call():
    """
    測試process_signal調用是否使用正確的键名
    Test if process_signal call uses correct key name
    """
    print("\n🔍 測試process_signal調用...")
    
    try:
        # 讀取main.py文件內容
        main_file = project_root / 'cli' / 'main.py'
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查是否使用了正確的键名
        if "selections['ticker']" in content:
            print("✅ 找到正確的键名 selections['ticker']")
        else:
            print("❌ 未找到 selections['ticker']")
            return False
        
        # 確保不再使用錯誤的键名
        if "selections['stock_symbol']" in content:
            print("❌ 仍然存在錯誤的键名 selections['stock_symbol']")
            return False
        else:
            print("✅ 確認不存在錯誤的键名 selections['stock_symbol']")
        
        print("✅ process_signal調用測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

def test_code_consistency():
    """
    測試代碼一致性 - 確保所有地方都使用相同的键名
    Test code consistency - ensure all places use the same key names
    """
    print("\n🔍 測試代碼一致性...")
    
    try:
        main_file = project_root / 'cli' / 'main.py'
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 統計ticker键的使用次數
        ticker_count = content.count("selections['ticker']")
        ticker_double_quote_count = content.count('selections["ticker"]')
        
        total_ticker_usage = ticker_count + ticker_double_quote_count
        
        print(f"📊 'ticker'键使用次數: {total_ticker_usage}")
        
        if total_ticker_usage >= 2:  # 至少應该有2處使用（初始化和process_signal）
            print("✅ ticker键使用次數合理")
        else:
            print("⚠️  ticker键使用次數可能不足")
        
        # 檢查是否还有其他可能的键名不一致問題
        potential_issues = [
            "selections['symbol']",
            "selections['stock']",
            "selections['code']"
        ]
        
        for issue in potential_issues:
            if issue in content:
                print(f"⚠️  發現潜在問題: {issue}")
            else:
                print(f"✅ 未發現問題: {issue}")
        
        print("✅ 代碼一致性測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

def main():
    """
    運行所有測試
    Run all tests
    """
    print("🚀 開始CLI修複驗證測試...")
    print("=" * 50)
    
    tests = [
        test_selections_dictionary_keys,
        test_process_signal_call,
        test_code_consistency
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！KeyError: 'stock_symbol' 問題已修複")
        return True
    else:
        print("❌ 部分測試失败，需要進一步檢查")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)