#!/usr/bin/env python3
"""
測試執行診斷腳本
逐步檢查測試腳本闪退的原因
"""

import sys
import os
import traceback

def step1_basic_check():
    """步骤1: 基本環境檢查"""
    print("🔍 步骤1: 基本環境檢查")
    print("-" * 40)
    
    try:
        print(f"✅ Python版本: {sys.version}")
        print(f"✅ Python路徑: {sys.executable}")
        print(f"✅ 工作目錄: {os.getcwd()}")
        print(f"✅ 虛擬環境: {os.environ.get('VIRTUAL_ENV', '未激活')}")
        return True
    except Exception as e:
        print(f"❌ 基本檢查失败: {e}")
        return False

def step2_path_check():
    """步骤2: 路徑檢查"""
    print("\n🔍 步骤2: 路徑檢查")
    print("-" * 40)
    
    try:
        # 檢查項目根目錄
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        print(f"✅ 項目根目錄: {project_root}")
        
        # 檢查關键目錄
        key_dirs = ['tradingagents', 'tests', 'cli']
        for dir_name in key_dirs:
            dir_path = os.path.join(project_root, dir_name)
            if os.path.exists(dir_path):
                print(f"✅ {dir_name}目錄: 存在")
            else:
                print(f"❌ {dir_name}目錄: 不存在")
        
        # 添加到Python路徑
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
            print(f"✅ 已添加項目根目錄到Python路徑")
        
        return True
    except Exception as e:
        print(f"❌ 路徑檢查失败: {e}")
        traceback.print_exc()
        return False

def step3_import_check():
    """步骤3: 導入檢查"""
    print("\n🔍 步骤3: 導入檢查")
    print("-" * 40)
    
    imports = [
        ("langchain_core.messages", "HumanMessage"),
        ("langchain_core.tools", "tool"),
        ("tradingagents.llm_adapters", "ChatDashScopeOpenAI"),
        ("tradingagents.config.config_manager", "token_tracker")
    ]
    
    success_count = 0
    for module, item in imports:
        try:
            exec(f"from {module} import {item}")
            print(f"✅ {module}.{item}: 導入成功")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module}.{item}: 導入失败 - {e}")
        except Exception as e:
            print(f"⚠️ {module}.{item}: 導入異常 - {e}")
    
    print(f"\n📊 導入結果: {success_count}/{len(imports)} 成功")
    return success_count == len(imports)

def step4_env_check():
    """步骤4: 環境變量檢查"""
    print("\n🔍 步骤4: 環境變量檢查")
    print("-" * 40)
    
    try:
        # 檢查關键環境變量
        env_vars = [
            "DASHSCOPE_API_KEY",
            "TUSHARE_TOKEN",
            "OPENAI_API_KEY"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                print(f"✅ {var}: 已設置 ({value[:10]}...)")
            else:
                print(f"⚠️ {var}: 未設置")
        
        return True
    except Exception as e:
        print(f"❌ 環境變量檢查失败: {e}")
        return False

def step5_simple_llm_test():
    """步骤5: 簡單LLM測試"""
    print("\n🔍 步骤5: 簡單LLM測試")
    print("-" * 40)
    
    try:
        # 檢查API密鑰
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("⚠️ DASHSCOPE_API_KEY未設置，跳過LLM測試")
            return True
        
        print("🔄 導入LLM適配器...")
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        print("✅ LLM適配器導入成功")
        
        print("🔄 創建LLM實例...")
        llm = ChatDashScopeOpenAI(
            model="qwen-turbo",
            temperature=0.1,
            max_tokens=50
        )
        print("✅ LLM實例創建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 簡單LLM測試失败: {e}")
        traceback.print_exc()
        return False

def step6_tool_binding_test():
    """步骤6: 工具绑定測試"""
    print("\n🔍 步骤6: 工具绑定測試")
    print("-" * 40)
    
    try:
        # 檢查API密鑰
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("⚠️ DASHSCOPE_API_KEY未設置，跳過工具绑定測試")
            return True
        
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        
        print("🔄 定義測試工具...")
        @tool
        def test_tool(text: str) -> str:
            """測試工具"""
            return f"工具返回: {text}"
        
        print("🔄 創建LLM並绑定工具...")
        llm = ChatDashScopeOpenAI(model="qwen-turbo", max_tokens=50)
        llm_with_tools = llm.bind_tools([test_tool])
        print("✅ 工具绑定成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具绑定測試失败: {e}")
        traceback.print_exc()
        return False

def step7_actual_call_test():
    """步骤7: 實际調用測試"""
    print("\n🔍 步骤7: 實际調用測試")
    print("-" * 40)
    
    try:
        # 檢查API密鑰
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("⚠️ DASHSCOPE_API_KEY未設置，跳過實际調用測試")
            return True
        
        from tradingagents.llm_adapters import ChatDashScopeOpenAI
        from langchain_core.tools import tool
        from langchain_core.messages import HumanMessage
        
        @tool
        def test_tool(text: str) -> str:
            """測試工具"""
            return f"工具返回: {text}"
        
        print("🔄 創建LLM並绑定工具...")
        llm = ChatDashScopeOpenAI(model="qwen-turbo", max_tokens=100)
        llm_with_tools = llm.bind_tools([test_tool])
        
        print("🔄 發送測試請求...")
        response = llm_with_tools.invoke([
            HumanMessage(content="請回複：測試成功")
        ])
        
        print(f"✅ 調用成功")
        print(f"   響應類型: {type(response)}")
        print(f"   響應長度: {len(response.content)}字符")
        print(f"   響應內容: {response.content[:100]}...")
        
        # 檢查工具調用
        tool_calls = getattr(response, 'tool_calls', [])
        print(f"   工具調用數量: {len(tool_calls)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 實际調用測試失败: {e}")
        traceback.print_exc()
        return False

def main():
    """主診斷函數"""
    print("🔬 測試執行診斷")
    print("=" * 60)
    print("💡 目標: 找出測試腳本闪退的原因")
    print("=" * 60)
    
    # 運行所有診斷步骤
    steps = [
        ("基本環境檢查", step1_basic_check),
        ("路徑檢查", step2_path_check),
        ("導入檢查", step3_import_check),
        ("環境變量檢查", step4_env_check),
        ("簡單LLM測試", step5_simple_llm_test),
        ("工具绑定測試", step6_tool_binding_test),
        ("實际調用測試", step7_actual_call_test)
    ]
    
    results = []
    for step_name, step_func in steps:
        print(f"\n{'='*60}")
        try:
            result = step_func()
            results.append((step_name, result))
            
            if not result:
                print(f"\n❌ {step_name}失败，停止後续測試")
                break
                
        except Exception as e:
            print(f"\n❌ {step_name}異常: {e}")
            traceback.print_exc()
            results.append((step_name, False))
            break
    
    # 总結
    print(f"\n{'='*60}")
    print("📋 診斷总結")
    print("=" * 60)
    
    passed = 0
    for step_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{step_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n📊 診斷結果: {passed}/{total} 通過")
    
    if passed == total:
        print("\n🎉 所有診斷通過！")
        print("測試腳本應该可以正常運行")
    else:
        print(f"\n⚠️ 在第{passed+1}步失败")
        print("請根據錯誤信息修複問題")
    
    # 防止腳本闪退
    print("\n" + "="*60)
    print("診斷完成！按回車键退出...")
    try:
        input()
    except:
        pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n💥 主函數異常: {e}")
        traceback.print_exc()
        print("\n按回車键退出...")
        try:
            input()
        except:
            pass
