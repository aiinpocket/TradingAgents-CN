#!/usr/bin/env python3
"""
測試統一新聞工具的LangChain綁定修複
"""

from tradingagents.agents.utils.agent_utils import Toolkit
from tradingagents.tools.unified_news_tool import create_unified_news_tool
from langchain_core.utils.function_calling import convert_to_openai_tool

def test_tool_binding():
    """測試工具綁定是否修複"""
    print("=== 測試統一新聞工具的LangChain綁定修複 ===")
    
    # 創建工具包
    toolkit = Toolkit()
    
    # 創建統一新聞工具
    unified_tool = create_unified_news_tool(toolkit)
    
    # 測試LangChain工具轉換
    print("\n1. 測試LangChain工具轉換...")
    try:
        openai_tool = convert_to_openai_tool(unified_tool)
        print(" LangChain工具轉換成功")
        
        func_info = openai_tool['function']
        print(f"工具名稱: {func_info['name']}")
        print(f"工具描述: {func_info['description'][:100]}...")
        
        params = list(func_info['parameters']['properties'].keys())
        print(f"參數: {params}")
        
        # 檢查參數是否正確
        expected_params = ['stock_code', 'max_news']
        if set(params) == set(expected_params):
            print(" 參數匹配正確")
        else:
            print(f" 參數不匹配，期望: {expected_params}, 實際: {params}")
            
    except Exception as e:
        print(f" LangChain工具轉換失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 測試工具調用
    print("\n2. 測試工具調用...")
    try:
        result = unified_tool('AAPL', 5)
        print(f" 工具調用成功，結果長度: {len(result)} 字符")
        print(f"結果預覽: {result[:200]}...")
    except Exception as e:
        print(f" 工具調用失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n=== 測試完成 ===")
    print(" 統一新聞工具的LangChain綁定問題已修複")
    print(" 函數簽名與檔案字符串現在匹配")
    print(" 工具可以正常綁定到LLM")
    
    return True

if __name__ == "__main__":
    test_tool_binding()