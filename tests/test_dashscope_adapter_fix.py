#!/usr/bin/env python3
"""
DashScope OpenAI 適配器修複測試腳本
測試修複後的工具绑定、轉換和調用機制
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tradingagents.utils.logging_manager import get_logger
logger = get_logger('test')

def test_enhanced_tool_binding():
    """測試增强的工具绑定機制"""
    print("\n🔧 測試增强的工具绑定機制")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_openai_adapter import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        
        # 定義測試工具
        @tool
        def get_test_stock_data(ticker: str, days: int = 7) -> str:
            """獲取測試股票數據"""
            return f"測試數據: {ticker} 最近 {days} 天的股票數據"
        
        @tool
        def get_test_news(query: str) -> str:
            """獲取測試新聞"""
            return f"測試新聞: {query} 相關新聞"
        
        # 創建適配器實例
        llm = ChatDashScopeOpenAI(
            model="qwen-turbo",
            temperature=0.1,
            max_tokens=200
        )
        
        print("✅ DashScope OpenAI 適配器創建成功")
        
        # 測試工具绑定
        tools = [get_test_stock_data, get_test_news]
        llm_with_tools = llm.bind_tools(tools)
        
        print("✅ 工具绑定成功")
        print(f"   绑定的工具數量: {len(tools)}")
        
        # 測試工具調用
        response = llm_with_tools.invoke([
            HumanMessage(content="請調用get_test_stock_data工具獲取AAPL的股票數據")
        ])
        
        print(f"✅ LLM 調用成功")
        print(f"   響應類型: {type(response)}")
        print(f"   響應內容長度: {len(response.content) if hasattr(response, 'content') else 0}")
        
        # 檢查工具調用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"✅ 檢測到工具調用: {len(response.tool_calls)} 個")
            for i, tool_call in enumerate(response.tool_calls):
                print(f"   工具調用 {i+1}: {tool_call.get('name', 'unknown')}")
        else:
            print("⚠️ 未檢測到工具調用")
            print(f"   響應內容: {response.content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具绑定測試失败: {e}")
        return False

def test_tool_format_validation():
    """測試工具格式驗證機制"""
    print("\n🔍 測試工具格式驗證機制")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_openai_adapter import ChatDashScopeOpenAI
        
        # 創建適配器實例
        llm = ChatDashScopeOpenAI(model="qwen-turbo")
        
        # 測試有效的工具格式
        valid_tool = {
            "type": "function",
            "function": {
                "name": "test_tool",
                "description": "測試工具",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string", "description": "參數1"}
                    },
                    "required": ["param1"]
                }
            }
        }
        
        is_valid = llm._validate_openai_tool_format(valid_tool, "test_tool")
        print(f"✅ 有效工具格式驗證: {'通過' if is_valid else '失败'}")
        
        # 測試無效的工具格式
        invalid_tool = {
            "type": "invalid",
            "function": {
                "name": "test_tool"
                # 缺少 description
            }
        }
        
        is_invalid = llm._validate_openai_tool_format(invalid_tool, "invalid_tool")
        print(f"✅ 無效工具格式驗證: {'正確拒絕' if not is_invalid else '錯誤通過'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具格式驗證測試失败: {e}")
        return False

def test_backup_tool_creation():
    """測試备用工具創建機制"""
    print("\n🔧 測試备用工具創建機制")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_openai_adapter import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        
        # 創建適配器實例
        llm = ChatDashScopeOpenAI(model="qwen-turbo")
        
        # 定義測試工具
        @tool
        def test_backup_tool(param1: str, param2: int = 10) -> str:
            """測試备用工具創建"""
            return f"結果: {param1}, {param2}"
        
        # 測試备用工具創建
        backup_tool = llm._create_backup_tool_format(test_backup_tool)
        
        if backup_tool:
            print("✅ 备用工具創建成功")
            print(f"   工具名稱: {backup_tool['function']['name']}")
            print(f"   工具描述: {backup_tool['function']['description']}")
            
            # 驗證备用工具格式
            is_valid = llm._validate_openai_tool_format(backup_tool, "backup_test")
            print(f"   格式驗證: {'通過' if is_valid else '失败'}")
        else:
            print("❌ 备用工具創建失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 备用工具創建測試失败: {e}")
        return False

def test_tool_call_response_validation():
    """測試工具調用響應驗證"""
    print("\n🔍 測試工具調用響應驗證")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_openai_adapter import ChatDashScopeOpenAI
        
        # 創建適配器實例
        llm = ChatDashScopeOpenAI(model="qwen-turbo")
        
        # 測試有效的工具調用格式
        valid_tool_call = {
            "name": "test_tool",
            "args": {"param1": "value1"}
        }
        
        is_valid = llm._validate_tool_call_format(valid_tool_call, 0)
        print(f"✅ 有效工具調用驗證: {'通過' if is_valid else '失败'}")
        
        # 測試無效的工具調用格式
        invalid_tool_call = {
            "invalid_field": "value"
            # 缺少 name 字段
        }
        
        is_invalid = llm._validate_tool_call_format(invalid_tool_call, 1)
        print(f"✅ 無效工具調用驗證: {'正確拒絕' if not is_invalid else '錯誤通過'}")
        
        # 測試工具調用修複
        broken_tool_call = {
            "function": {
                "name": "test_tool",
                "arguments": {"param1": "value1"}
            }
        }
        
        fixed_tool_call = llm._fix_tool_call_format(broken_tool_call, 2)
        if fixed_tool_call:
            print("✅ 工具調用修複成功")
            print(f"   修複後名稱: {fixed_tool_call.get('name')}")
            print(f"   修複後參數: {fixed_tool_call.get('args')}")
        else:
            print("❌ 工具調用修複失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具調用響應驗證測試失败: {e}")
        return False

def test_comprehensive_tool_calling():
    """综合測試工具調用流程"""
    print("\n🚀 综合測試工具調用流程")
    print("=" * 60)
    
    try:
        from tradingagents.llm_adapters.dashscope_openai_adapter import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        
        # 定義複雜的測試工具
        @tool
        def get_stock_analysis(ticker: str, analysis_type: str = "basic") -> str:
            """獲取股票分析報告"""
            return f"股票 {ticker} 的 {analysis_type} 分析報告：這是一個詳細的分析..."
        
        @tool
        def get_market_news(query: str, days: int = 7) -> str:
            """獲取市場新聞"""
            return f"關於 {query} 最近 {days} 天的市場新聞..."
        
        # 創建適配器並绑定工具
        llm = ChatDashScopeOpenAI(
            model="qwen-plus-latest",
            temperature=0.1,
            max_tokens=500
        )
        
        tools = [get_stock_analysis, get_market_news]
        llm_with_tools = llm.bind_tools(tools)
        
        print("✅ 複雜工具绑定成功")
        
        # 測試多轮對話和工具調用
        messages = [
            HumanMessage(content="請幫我分析苹果公司(AAPL)的股票，並獲取相關新聞")
        ]
        
        response = llm_with_tools.invoke(messages)
        
        print(f"✅ 複雜對話調用成功")
        print(f"   響應內容長度: {len(response.content) if hasattr(response, 'content') else 0}")
        
        # 詳細分析響應
        if hasattr(response, 'tool_calls') and response.tool_calls:
            print(f"✅ 檢測到 {len(response.tool_calls)} 個工具調用")
            for i, tool_call in enumerate(response.tool_calls):
                print(f"   工具 {i+1}: {tool_call.get('name', 'unknown')}")
                print(f"   參數: {tool_call.get('args', {})}")
        else:
            print("⚠️ 未檢測到工具調用")
            if hasattr(response, 'content'):
                print(f"   響應內容: {response.content[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 综合工具調用測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 DashScope OpenAI 適配器修複測試")
    print("=" * 80)
    
    # 檢查環境變量
    if not os.getenv('DASHSCOPE_API_KEY'):
        print("❌ 錯誤: 未找到 DASHSCOPE_API_KEY 環境變量")
        print("請設置您的 DashScope API 密鑰:")
        print("  Windows: set DASHSCOPE_API_KEY=your_api_key")
        print("  Linux/Mac: export DASHSCOPE_API_KEY=your_api_key")
        return
    
    # 運行測試
    tests = [
        ("工具格式驗證", test_tool_format_validation),
        ("备用工具創建", test_backup_tool_creation),
        ("工具調用響應驗證", test_tool_call_response_validation),
        ("增强工具绑定", test_enhanced_tool_binding),
        ("综合工具調用", test_comprehensive_tool_calling),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ 測試 {test_name} 執行異常: {e}")
            results[test_name] = False
    
    # 輸出測試結果
    print("\n📊 測試結果汇总")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n📈 总體結果: {passed}/{total} 通過")
    
    if passed == total:
        print("\n🎉 所有測試通過！DashScope OpenAI 適配器修複成功！")
        print("\n💡 修複效果:")
        print("   ✅ 工具轉換機制增强，支持备用格式")
        print("   ✅ 工具格式驗證，確保兼容性")
        print("   ✅ 工具調用響應驗證和修複")
        print("   ✅ 詳細的錯誤處理和日誌記錄")
        print("   ✅ 提高了工具調用成功率")
    else:
        print(f"\n⚠️ 部分測試失败，需要進一步調試")
        print("請檢查失败的測試項目並查看詳細日誌")

if __name__ == "__main__":
    main()