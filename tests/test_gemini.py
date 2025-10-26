#!/usr/bin/env python3
"""
測試Google Gemini模型
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

def check_gemini_setup():
    """檢查Gemini模型設置"""
    print("🔍 檢查Gemini模型設置")
    print("=" * 50)
    
    # 檢查API密鑰
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if google_api_key:
        print(f"✅ Google API密鑰已配置: {google_api_key[:20]}...")
    else:
        print("❌ Google API密鑰未配置")
        print("💡 請在.env文件中設置 GOOGLE_API_KEY")
        return False
    
    # 檢查依賴庫
    try:
        import google.generativeai as genai
        print("✅ google-generativeai庫已安裝")
    except ImportError:
        print("❌ google-generativeai庫未安裝")
        print("💡 運行: pip install google-generativeai")
        return False
    
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        print("✅ langchain-google-genai庫已安裝")
    except ImportError:
        print("❌ langchain-google-genai庫未安裝")
        print("💡 運行: pip install langchain-google-genai")
        return False
    
    return True

def test_gemini_direct():
    """直接測試Gemini API"""
    try:
        print("\n🧪 直接測試Gemini API")
        print("=" * 50)
        
        import google.generativeai as genai
        
        # 配置API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=google_api_key)
        
        # 創建模型實例
        model = genai.GenerativeModel('gemini-pro')
        
        print("✅ Gemini模型實例創建成功")
        
        # 測試生成內容
        print("📝 測試內容生成...")
        response = model.generate_content("請用中文簡單介紹一下苹果公司(Apple Inc.)的業務")
        
        if response and response.text:
            print("✅ Gemini API調用成功")
            print(f"   響應長度: {len(response.text)} 字符")
            print(f"   響應預覽: {response.text[:200]}...")
            return True
        else:
            print("❌ Gemini API調用失败：無響應內容")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_gemini_langchain():
    """測試通過LangChain使用Gemini"""
    try:
        print("\n🧪 測試LangChain Gemini集成")
        print("=" * 50)
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # 創建LangChain Gemini實例
        llm = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.1,
            max_tokens=1000,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        print("✅ LangChain Gemini實例創建成功")
        
        # 測試調用
        print("📝 測試LangChain調用...")
        response = llm.invoke("請用中文分析一下當前科技股的投資前景，重點關註人工智能領域")
        
        if response and response.content:
            print("✅ LangChain Gemini調用成功")
            print(f"   響應長度: {len(response.content)} 字符")
            print(f"   響應預覽: {response.content[:200]}...")
            return True
        else:
            print("❌ LangChain Gemini調用失败：無響應內容")
            return False
            
    except Exception as e:
        print(f"❌ LangChain Gemini測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_gemini_in_tradingagents():
    """測試在TradingAgents中使用Gemini"""
    try:
        print("\n🧪 測試TradingAgents中的Gemini集成")
        print("=" * 50)
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建使用Gemini的配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        config["deep_think_llm"] = "gemini-pro"
        config["quick_think_llm"] = "gemini-pro"
        config["online_tools"] = True
        config["memory_enabled"] = True
        
        # 修複路徑
        config["data_dir"] = str(project_root / "data")
        config["results_dir"] = str(project_root / "results")
        config["data_cache_dir"] = str(project_root / "tradingagents" / "dataflows" / "data_cache")
        
        # 創建目錄
        os.makedirs(config["data_dir"], exist_ok=True)
        os.makedirs(config["results_dir"], exist_ok=True)
        os.makedirs(config["data_cache_dir"], exist_ok=True)
        
        print("✅ 配置創建成功")
        print(f"   LLM提供商: {config['llm_provider']}")
        print(f"   深度思考模型: {config['deep_think_llm']}")
        print(f"   快速思考模型: {config['quick_think_llm']}")
        
        # 創建TradingAgentsGraph實例
        print("🚀 初始化TradingAgents圖...")
        graph = TradingAgentsGraph(["market"], config=config, debug=False)
        
        print("✅ TradingAgents圖初始化成功")
        
        # 測試簡單分析
        print("📊 測試簡單股票分析...")
        try:
            state, decision = graph.propagate("AAPL", "2025-06-27")
            
            if state and decision:
                print("✅ Gemini驱動的股票分析成功")
                print(f"   決策結果: {decision}")
                
                # 檢查市場報告
                if "market_report" in state and state["market_report"]:
                    market_report = state["market_report"]
                    print(f"   市場報告長度: {len(market_report)} 字符")
                    print(f"   報告預覽: {market_report[:200]}...")
                
                return True
            else:
                print("❌ 分析完成但結果為空")
                return False
                
        except Exception as e:
            print(f"❌ 股票分析失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ TradingAgents Gemini集成測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主測試函數"""
    print("🧪 Google Gemini模型測試")
    print("=" * 60)
    
    # 檢查設置
    if not check_gemini_setup():
        print("\n❌ Gemini設置不完整，無法繼续測試")
        return
    
    # 運行測試
    results = {}
    
    results['Gemini直接API'] = test_gemini_direct()
    results['LangChain集成'] = test_gemini_langchain()
    results['TradingAgents集成'] = test_gemini_in_tradingagents()
    
    # 总結結果
    print(f"\n📊 測試結果总結:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 总體結果: {successful_tests}/{total_tests} 測試通過")
    
    if successful_tests == total_tests:
        print("🎉 Gemini模型完全可用！")
        print("\n💡 使用建议:")
        print("   1. 可以在Web界面配置中選擇Google作為LLM提供商")
        print("   2. 可以選擇gemini-pro作為分析模型")
        print("   3. Gemini在多語言支持方面表現優秀")
    elif successful_tests > 0:
        print("⚠️ Gemini部分功能可用，建议檢查失败的測試")
    else:
        print("❌ Gemini模型不可用，請檢查API密鑰和網絡連接")

if __name__ == "__main__":
    main()
