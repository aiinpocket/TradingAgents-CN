#!/usr/bin/env python3
"""
DeepSeek V3集成測試
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

def test_deepseek_availability():
    """測試DeepSeek可用性"""
    print("🔍 測試DeepSeek V3可用性...")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    enabled = os.getenv("DEEPSEEK_ENABLED", "false").lower() == "true"
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    print(f"API Key: {'✅ 已設置' if api_key else '❌ 未設置'}")
    print(f"Base URL: {base_url}")
    print(f"啟用狀態: {'✅ 已啟用' if enabled else '❌ 未啟用'}")
    
    if not api_key:
        print("\n⚠️ 請在.env文件中設置DEEPSEEK_API_KEY")
        print("📝 獲取地址: https://platform.deepseek.com/")
        print("💡 註意：需要註冊DeepSeek账號並創建API Key")
        return False
    
    if not enabled:
        print("\n⚠️ 請在.env文件中設置DEEPSEEK_ENABLED=true")
        return False
    
    return True

def test_deepseek_adapter():
    """測試DeepSeek適配器"""
    print("\n🧪 測試DeepSeek適配器...")
    
    try:
        from tradingagents.llm.deepseek_adapter import DeepSeekAdapter, create_deepseek_adapter
        
        # 測試適配器創建
        adapter = create_deepseek_adapter(model="deepseek-chat")
        print("✅ 適配器創建成功")
        
        # 測試模型信息
        model_info = adapter.get_model_info()
        print(f"✅ 模型信息: {model_info['provider']} - {model_info['model']}")
        print(f"✅ 上下文長度: {model_info['context_length']}")
        
        # 測試可用模型列表
        models = DeepSeekAdapter.get_available_models()
        print(f"✅ 可用模型: {list(models.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 適配器測試失败: {e}")
        return False

def test_deepseek_connection():
    """測試DeepSeek連接"""
    print("\n🔗 測試DeepSeek連接...")
    
    try:
        from tradingagents.llm.deepseek_adapter import create_deepseek_adapter
        from langchain.schema import HumanMessage
        
        # 創建適配器
        adapter = create_deepseek_adapter(model="deepseek-chat")
        
        # 測試簡單對話
        messages = [HumanMessage(content="你好，請簡單介紹一下股票投資的基本概念，控制在50字以內")]
        response = adapter.chat(messages)
        print(f"✅ 模型響應: {response[:100]}...")
        
        # 測試連接
        connection_ok = adapter.test_connection()
        print(f"✅ 連接測試: {'成功' if connection_ok else '失败'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 連接測試失败: {e}")
        return False

def test_deepseek_tools():
    """測試DeepSeek工具調用"""
    print("\n🛠️ 測試工具調用功能...")
    
    try:
        from langchain.tools import tool
        from tradingagents.llm.deepseek_adapter import create_deepseek_adapter
        
        # 定義測試工具
        @tool
        def get_stock_price(symbol: str) -> str:
            """獲取股票價格"""
            return f"股票{symbol}的當前價格是$150.00"
        
        @tool
        def get_market_news(symbol: str) -> str:
            """獲取市場新聞"""
            return f"股票{symbol}的最新消息：公司業绩良好，分析師看好前景"
        
        # 創建適配器
        adapter = create_deepseek_adapter(model="deepseek-chat")
        
        # 創建智能體
        tools = [get_stock_price, get_market_news]
        system_prompt = "你是一個專業的股票分析助手，可以使用工具獲取股票信息並進行分析。請用中文回答。"
        
        agent = adapter.create_agent(tools, system_prompt, verbose=True)
        print("✅ 智能體創建成功")
        
        # 測試工具調用
        result = agent.invoke({"input": "請幫我查詢AAPL的股價和最新消息"})
        print(f"✅ 工具調用成功: {result['output'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具調用測試失败: {e}")
        return False

def test_deepseek_trading_graph():
    """測試DeepSeek在交易圖中的集成"""
    print("\n📊 測試交易圖集成...")
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        # 創建DeepSeek配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "deepseek"
        config["deep_think_llm"] = "deepseek-chat"
        config["quick_think_llm"] = "deepseek-chat"
        config["max_debate_rounds"] = 1  # 减少測試時間
        config["online_tools"] = False   # 禁用在線工具以加快測試
        
        # 創建交易圖
        ta = TradingAgentsGraph(debug=True, config=config)
        print("✅ 交易圖創建成功")
        
        # 註意：這里不執行實际分析，只測試初始化
        print("✅ DeepSeek集成到交易圖成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 交易圖集成測試失败: {e}")
        return False

def test_deepseek_models():
    """測試不同DeepSeek模型"""
    print("\n🎯 測試不同DeepSeek模型...")
    
    try:
        from tradingagents.llm.deepseek_adapter import create_deepseek_adapter
        
        models_to_test = ["deepseek-chat"]  # 仅測試最適合股票分析的模型
        
        for model in models_to_test:
            try:
                adapter = create_deepseek_adapter(model=model)
                info = adapter.get_model_info()
                print(f"✅ {model}: {info['context_length']} 上下文")
            except Exception as e:
                print(f"⚠️ {model}: 測試失败 - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🎯 DeepSeek V3集成測試")
    print("=" * 50)
    
    tests = [
        ("可用性檢查", test_deepseek_availability),
        ("適配器測試", test_deepseek_adapter),
        ("連接測試", test_deepseek_connection),
        ("工具調用", test_deepseek_tools),
        ("交易圖集成", test_deepseek_trading_graph),
        ("模型測試", test_deepseek_models),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}測試異常: {e}")
            results.append((test_name, False))
    
    # 总結結果
    print("\n" + "="*50)
    print("📋 測試結果总結:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总計: {passed}/{len(results)} 項測試通過")
    
    if passed == len(results):
        print("\n🎉 所有測試通過！DeepSeek V3集成成功！")
        print("\n📝 下一步:")
        print("1. 在.env文件中配置您的DeepSeek API密鑰")
        print("2. 設置DEEPSEEK_ENABLED=true啟用DeepSeek")
        print("3. 在Web界面或CLI中選擇DeepSeek模型")
        print("4. 享受高性價比的AI分析服務")
    else:
        print(f"\n⚠️ {len(results) - passed} 項測試失败，請檢查配置和依賴")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
