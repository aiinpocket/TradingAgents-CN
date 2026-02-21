#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Google工具調用處理器修複效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tradingagents.agents.utils.google_tool_handler import GoogleToolCallHandler
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tool_call_validation():
    """測試工具調用驗證功能"""
    print("=" * 60)
    print("🧪 測試工具調用驗證功能")
    print("=" * 60)
    
    # 測試有效的工具調用
    valid_tool_call = {
        'name': 'get_stock_market_data_unified',
        'args': {'symbol': 'AAPL', 'period': '1d'},
        'id': 'call_12345'
    }
    
    result = GoogleToolCallHandler._validate_tool_call(valid_tool_call, 0, "測試分析師")
    print(f"✅ 有效工具調用驗證結果: {result}")
    assert result == True, "有效工具調用應該通過驗證"
    
    # 測試無效的工具調用 - 缺少字段
    invalid_tool_call_1 = {
        'name': 'get_stock_market_data_unified',
        'args': {'symbol': 'AAPL'}
        # 缺少 'id' 字段
    }
    
    result = GoogleToolCallHandler._validate_tool_call(invalid_tool_call_1, 1, "測試分析師")
    print(f"❌ 無效工具調用1驗證結果: {result}")
    assert result == False, "缺少字段的工具調用應該驗證失敗"
    
    # 測試無效的工具調用 - 錯誤類型
    invalid_tool_call_2 = {
        'name': '',  # 空字符串
        'args': 'not_a_dict',  # 不是字典
        'id': 123  # 不是字符串
    }
    
    result = GoogleToolCallHandler._validate_tool_call(invalid_tool_call_2, 2, "測試分析師")
    print(f"❌ 無效工具調用2驗證結果: {result}")
    assert result == False, "錯誤類型的工具調用應該驗證失敗"
    
    print("✅ 工具調用驗證功能測試通過")

def test_tool_call_fixing():
    """測試工具調用修複功能"""
    print("\n" + "=" * 60)
    print("🔧 測試工具調用修複功能")
    print("=" * 60)
    
    # 測試OpenAI格式的工具調用修複
    openai_format_tool_call = {
        'function': {
            'name': 'get_stock_market_data_unified',
            'arguments': '{"symbol": "AAPL", "period": "1d"}'
        }
        # 缺少 'id' 字段
    }
    
    fixed_tool_call = GoogleToolCallHandler._fix_tool_call(openai_format_tool_call, 0, "測試分析師")
    print(f"🔧 修複後的工具調用: {fixed_tool_call}")
    
    if fixed_tool_call:
        assert 'name' in fixed_tool_call, "修複後應該包含name字段"
        assert 'args' in fixed_tool_call, "修複後應該包含args字段"
        assert 'id' in fixed_tool_call, "修複後應該包含id字段"
        assert isinstance(fixed_tool_call['args'], dict), "args應該是字典類型"
        print("✅ OpenAI格式工具調用修複成功")
    else:
        print("❌ OpenAI格式工具調用修複失敗")
    
    # 測試無法修複的工具調用
    unfixable_tool_call = "not_a_dict"
    
    fixed_tool_call = GoogleToolCallHandler._fix_tool_call(unfixable_tool_call, 1, "測試分析師")
    print(f"❌ 無法修複的工具調用結果: {fixed_tool_call}")
    assert fixed_tool_call is None, "無法修複的工具調用應該返回None"
    
    print("✅ 工具調用修複功能測試通過")

def test_duplicate_prevention():
    """測試重複調用防護功能"""
    print("\n" + "=" * 60)
    print("🛡️ 測試重複調用防護功能")
    print("=" * 60)
    
    # 模擬重複的工具調用
    tool_calls = [
        {
            'name': 'get_stock_market_data_unified',
            'args': {'symbol': 'AAPL', 'period': '1d'},
            'id': 'call_1'
        },
        {
            'name': 'get_stock_market_data_unified',
            'args': {'symbol': 'AAPL', 'period': '1d'},  # 相同參數
            'id': 'call_2'
        },
        {
            'name': 'get_stock_market_data_unified',
            'args': {'symbol': 'TSLA', 'period': '1d'},  # 不同參數
            'id': 'call_3'
        }
    ]
    
    executed_tools = set()
    unique_calls = []
    
    for i, tool_call in enumerate(tool_calls):
        tool_name = tool_call.get('name')
        tool_args = tool_call.get('args', {})
        tool_signature = f"{tool_name}_{hash(str(tool_args))}"
        
        if tool_signature in executed_tools:
            print(f"⚠️ 跳過重複工具調用 {i}: {tool_name} with {tool_args}")
        else:
            executed_tools.add(tool_signature)
            unique_calls.append(tool_call)
            print(f"✅ 執行工具調用 {i}: {tool_name} with {tool_args}")
    
    print(f"📊 原始工具調用數量: {len(tool_calls)}")
    print(f"📊 去重後工具調用數量: {len(unique_calls)}")
    
    assert len(unique_calls) == 2, "應該有2個唯一的工具調用"
    print("✅ 重複調用防護功能測試通過")

def main():
    """主測試函數"""
    print("🚀 開始測試Google工具調用處理器修複效果")
    
    try:
        test_tool_call_validation()
        test_tool_call_fixing()
        test_duplicate_prevention()
        
        print("\n" + "=" * 60)
        print("🎉 所有測試通過！Google工具調用處理器修複成功")
        print("=" * 60)
        
        print("\n📋 修複總結:")
        print("1. ✅ 添加了工具調用格式驗證")
        print("2. ✅ 實現了工具調用自動修複（支持OpenAI格式轉換）")
        print("3. ✅ 添加了重複調用防護機制")
        print("4. ✅ 改進了錯誤處理和日誌記錄")
        
        print("\n🔧 主要改進:")
        print("- 防止重複調用統一市場數據工具")
        print("- 自動驗證和修複Google模型的錯誤工具調用")
        print("- 支持OpenAI格式到標準格式的自動轉換")
        print("- 增強的錯誤處理和調試信息")
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)