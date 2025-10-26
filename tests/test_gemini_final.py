#!/usr/bin/env python3
"""
最终測試修複後的Gemini集成
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

def test_gemini_tradingagents():
    """測試修複後的Gemini与TradingAgents集成"""
    try:
        print("🧪 測試修複後的Gemini与TradingAgents集成")
        print("=" * 60)
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 檢查API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            print("❌ Google API密鑰未配置")
            return False
        
        print(f"✅ Google API密鑰已配置: {google_api_key[:20]}...")
        
        # 創建使用Gemini的配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        config["deep_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"
        config["quick_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"
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
        print("📊 開始股票分析...")
        print("   這可能需要几分鐘時間...")
        
        try:
            state, decision = graph.propagate("AAPL", "2025-06-27")
            
            if state and decision:
                print("✅ Gemini驱動的股票分析成功完成！")
                print(f"   最终決策: {decision}")
                
                # 檢查各種報告
                reports = ["market_report", "sentiment_report", "news_report", "fundamentals_report"]
                for report_name in reports:
                    if report_name in state and state[report_name]:
                        report_content = state[report_name]
                        print(f"   {report_name}: {len(report_content)} 字符")
                        print(f"   預覽: {report_content[:100]}...")
                        print()
                
                return True
            else:
                print("❌ 分析完成但結果為空")
                return False
                
        except Exception as e:
            print(f"❌ 股票分析失败: {e}")
            import traceback
            print(traceback.format_exc())
            return False
            
    except Exception as e:
        print(f"❌ TradingAgents集成測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_gemini_basic():
    """基础Gemini功能測試"""
    try:
        print("🧪 基础Gemini功能測試")
        print("=" * 50)
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # 創建LangChain Gemini實例
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite-preview-06-17",
            temperature=0.1,
            max_tokens=500,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        print("✅ Gemini實例創建成功")
        
        # 測試中文對話
        print("📝 測試中文對話...")
        response = llm.invoke("請用中文分析一下當前人工智能技術的發展趋势")
        
        if response and response.content:
            print("✅ 中文對話測試成功")
            print(f"   響應長度: {len(response.content)} 字符")
            print(f"   響應預覽: {response.content[:200]}...")
            return True
        else:
            print("❌ 中文對話測試失败")
            return False
            
    except Exception as e:
        print(f"❌ 基础功能測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 Gemini最终集成測試")
    print("=" * 70)
    
    # 檢查環境變量
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ Google API密鑰未配置")
        print("💡 請在.env文件中設置 GOOGLE_API_KEY")
        return
    
    # 運行測試
    results = {}
    
    print("第1步: 基础功能測試")
    print("-" * 30)
    results['基础功能'] = test_gemini_basic()
    
    print("\n第2步: TradingAgents集成測試")
    print("-" * 30)
    results['TradingAgents集成'] = test_gemini_tradingagents()
    
    # 总結結果
    print(f"\n📊 最终測試結果总結:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 总體結果: {successful_tests}/{total_tests} 測試通過")
    
    if successful_tests == total_tests:
        print("🎉 Gemini模型完全集成成功！")
        print("\n💡 使用建议:")
        print("   1. 在Web界面中選擇'Google'作為LLM提供商")
        print("   2. 使用模型名稱: gemini-2.0-flash")
        print("   3. 可以進行完整的中文股票分析")
        print("   4. 支持所有分析師類型")
        print("   5. Gemini在多語言和推理能力方面表現優秀")
    elif successful_tests > 0:
        print("⚠️ Gemini部分功能可用")
        if results['基础功能'] and not results['TradingAgents集成']:
            print("💡 基础功能正常，但TradingAgents集成有問題")
            print("   建议檢查配置和依賴")
    else:
        print("❌ Gemini模型不可用")
        print("💡 請檢查API密鑰、網絡連接和依賴安裝")

if __name__ == "__main__":
    main()
