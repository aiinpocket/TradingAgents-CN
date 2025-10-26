#!/usr/bin/env python3
"""
阿里百炼大模型集成測試腳本
用於驗證 TradingAgents 中的阿里百炼集成是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加載 .env 文件
load_dotenv()

def test_import():
    """測試導入是否正常"""
    print("🔍 測試1: 檢查模塊導入...")
    try:
        from tradingagents.llm_adapters import ChatDashScope
        print("✅ ChatDashScope 導入成功")
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        print("✅ TradingAgentsGraph 導入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 導入失败: {e}")
        return False

def test_api_key():
    """測試API密鑰配置"""
    print("\n🔍 測試2: 檢查API密鑰配置...")
    
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    
    if not dashscope_key:
        print("❌ 未找到 DASHSCOPE_API_KEY 環境變量")
        print("💡 請設置: set DASHSCOPE_API_KEY=your_api_key")
        return False
    else:
        print(f"✅ DASHSCOPE_API_KEY: {dashscope_key[:10]}...")
    
    if not finnhub_key:
        print("❌ 未找到 FINNHUB_API_KEY 環境變量")
        print("💡 請設置: set FINNHUB_API_KEY=your_api_key")
        return False
    else:
        print(f"✅ FINNHUB_API_KEY: {finnhub_key[:10]}...")
    
    return True

def test_dashscope_connection():
    """測試阿里百炼連接"""
    print("\n🔍 測試3: 檢查阿里百炼連接...")
    
    try:
        import dashscope
        from dashscope import Generation
        
        # 設置API密鑰
        dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')
        
        # 測試簡單調用
        response = Generation.call(
            model="qwen-turbo",
            messages=[{"role": "user", "content": "你好，請回複'連接成功'"}],
            result_format="message"
        )
        
        if response.status_code == 200:
            content = response.output.choices[0].message.content
            print(f"✅ 阿里百炼連接成功: {content}")
            return True
        else:
            print(f"❌ 阿里百炼連接失败: {response.code} - {response.message}")
            return False
            
    except Exception as e:
        print(f"❌ 阿里百炼連接測試失败: {e}")
        return False

def test_langchain_adapter():
    """測試LangChain適配器"""
    print("\n🔍 測試4: 檢查LangChain適配器...")
    
    try:
        from tradingagents.llm_adapters import ChatDashScope
        from langchain_core.messages import HumanMessage
        
        # 創建適配器實例
        llm = ChatDashScope(model="qwen-turbo")
        
        # 測試調用
        messages = [HumanMessage(content="請回複'適配器工作正常'")]
        response = llm.invoke(messages)
        
        print(f"✅ LangChain適配器工作正常: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ LangChain適配器測試失败: {e}")
        return False

def test_trading_graph_config():
    """測試TradingGraph配置"""
    print("\n🔍 測試5: 檢查TradingGraph配置...")
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建阿里百炼配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "dashscope"
        config["deep_think_llm"] = "qwen-plus"
        config["quick_think_llm"] = "qwen-turbo"
        
        # 嘗試初始化（不運行分析）
        ta = TradingAgentsGraph(debug=False, config=config)
        
        print("✅ TradingGraph 配置成功")
        print(f"   深度思考模型: {config['deep_think_llm']}")
        print(f"   快速思考模型: {config['quick_think_llm']}")
        return True
        
    except Exception as e:
        print(f"❌ TradingGraph 配置失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 阿里百炼大模型集成測試")
    print("=" * 50)
    
    tests = [
        test_import,
        test_api_key,
        test_dashscope_connection,
        test_langchain_adapter,
        test_trading_graph_config,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ 測試異常: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！阿里百炼集成工作正常")
        print("\n💡 下一步:")
        print("   1. 運行 python demo_dashscope.py 進行完整測試")
        print("   2. 或使用 python -m cli.main analyze 啟動交互式分析")
    else:
        print("⚠️  部分測試失败，請檢查配置")
        print("\n🔧 故障排除:")
        print("   1. 確認已安裝 dashscope: pip install dashscope")
        print("   2. 檢查API密鑰是否正確設置")
        print("   3. 確認網絡連接正常")
        print("   4. 查看詳細錯誤信息")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
