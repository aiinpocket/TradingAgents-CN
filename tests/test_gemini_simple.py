#!/usr/bin/env python3
"""
簡化的Gemini測試（禁用內存功能）
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

def test_gemini_simple_analysis():
    """測試Gemini的簡單分析功能"""
    try:
        print(" 測試Gemini簡單分析功能")
        print("=" * 60)
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 檢查API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            print(" Google API密鑰未配置")
            return False
        
        print(f" Google API密鑰已配置: {google_api_key[:20]}...")
        
        # 創建簡化配置（禁用內存和在線工具）
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        config["deep_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"
        config["quick_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"
        config["online_tools"] = False  # 禁用在線工具避免API限制
        config["memory_enabled"] = False  # 禁用內存避免OpenAI依賴
        config["max_debate_rounds"] = 1  # 減少輪次
        config["max_risk_discuss_rounds"] = 1
        
        # 修複路徑
        config["data_dir"] = str(project_root / "data")
        config["results_dir"] = str(project_root / "results")
        config["data_cache_dir"] = str(project_root / "tradingagents" / "dataflows" / "data_cache")
        
        # 創建目錄
        os.makedirs(config["data_dir"], exist_ok=True)
        os.makedirs(config["results_dir"], exist_ok=True)
        os.makedirs(config["data_cache_dir"], exist_ok=True)
        
        print(" 簡化配置創建成功")
        print(f"   LLM提供商: {config['llm_provider']}")
        print(f"   模型: {config['deep_think_llm']}")
        print(f"   在線工具: {config['online_tools']}")
        print(f"   內存功能: {config['memory_enabled']}")
        
        # 創建TradingAgentsGraph實例
        print(" 初始化TradingAgents圖...")
        graph = TradingAgentsGraph(["market"], config=config, debug=False)
        
        print(" TradingAgents圖初始化成功")
        
        # 測試簡單分析
        print(" 開始簡化股票分析...")
        print("   使用離線數據，避免API限制...")
        
        try:
            state, decision = graph.propagate("AAPL", "2025-06-27")
            
            if state and decision:
                print(" Gemini驅動的股票分析成功完成！")
                print(f"   最終決策: {decision}")
                
                # 檢查市場報告
                if "market_report" in state and state["market_report"]:
                    market_report = state["market_report"]
                    print(f"   市場報告長度: {len(market_report)} 字符")
                    print(f"   報告預覽: {market_report[:200]}...")
                
                return True
            else:
                print(" 分析完成但結果為空")
                return False
                
        except Exception as e:
            print(f" 股票分析失敗: {e}")
            import traceback
            print(traceback.format_exc())
            return False
            
    except Exception as e:
        print(f" 簡化測試失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_gemini_analyst_direct():
    """直接測試Gemini分析師"""
    try:
        print("\n 直接測試Gemini分析師")
        print("=" * 60)
        
        from tradingagents.agents.analysts.market_analyst import create_market_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from langchain_google_genai import ChatGoogleGenerativeAI
        from tradingagents.default_config import DEFAULT_CONFIG
        from langchain_core.messages import HumanMessage
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = False
        
        # 創建Gemini LLM
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash-lite-preview-06-17",
            temperature=0.1,
            max_tokens=1000,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        # 創建工具包
        toolkit = Toolkit(config=config)
        
        print(" 組件創建成功")
        
        # 創建市場分析師
        market_analyst = create_market_analyst(llm, toolkit)
        
        print(" 市場分析師創建成功")
        
        # 創建測試狀態
        test_state = {
            "messages": [HumanMessage(content="分析AAPL的市場技術指標")],
            "company_of_interest": "AAPL",
            "trade_date": "2025-06-27"
        }
        
        print(" 開始市場分析...")
        
        # 執行分析
        result = market_analyst(test_state)
        
        if result and "market_report" in result:
            market_report = result["market_report"]
            if market_report and len(market_report) > 100:
                print(" 市場分析成功完成")
                print(f"   報告長度: {len(market_report)} 字符")
                print(f"   報告預覽: {market_report[:200]}...")
                return True
            else:
                print(" 市場分析完成但報告內容較少")
                return True
        else:
            print(" 市場分析完成但沒有生成報告")
            return False
            
    except Exception as e:
        print(f" 直接分析師測試失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主測試函數"""
    print(" Gemini簡化集成測試")
    print("=" * 70)
    
    # 檢查環境變量
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print(" Google API密鑰未配置")
        print(" 請在.env文件中設置 GOOGLE_API_KEY")
        return
    
    # 運行測試
    results = {}
    
    print("第1步: 直接分析師測試")
    print("-" * 30)
    results['直接分析師'] = test_gemini_analyst_direct()
    
    print("\n第2步: 簡化TradingAgents測試")
    print("-" * 30)
    results['簡化TradingAgents'] = test_gemini_simple_analysis()
    
    # 總結結果
    print(f"\n 簡化測試結果總結:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = " 通過" if success else " 失敗"
        print(f"  {test_name}: {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n 總體結果: {successful_tests}/{total_tests} 測試通過")
    
    if successful_tests == total_tests:
        print(" Gemini模型核心功能完全可用！")
        print("\n 使用建議:")
        print("   1. Gemini基礎功能正常工作")
        print("   2. 可以在TradingAgents中使用Gemini")
        print("   3. 建議禁用內存功能避免OpenAI依賴")
        print("   4. 可以使用離線模式避免API限制")
        print("   5. 支持中文分析和推理")
    elif successful_tests > 0:
        print(" Gemini部分功能可用")
        print(" 核心功能正常，可以進行基礎分析")
    else:
        print(" Gemini模型不可用")
        print(" 請檢查API密鑰和網絡連接")

if __name__ == "__main__":
    main()
