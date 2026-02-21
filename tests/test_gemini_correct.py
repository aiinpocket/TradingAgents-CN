#!/usr/bin/env python3
"""
使用正確的模型名稱測試Gemini
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

# 推薦的模型列表（按優先級排序）
RECOMMENDED_MODELS = [
    "gemini-2.0-flash",      # 最新的2.0版本
    "gemini-1.5-flash",      # 穩定的1.5版本
    "gemini-1.5-pro",        # 更強大的1.5版本
    "gemini-2.5-flash",      # 2.5版本
]

def test_model(model_name):
    """測試特定模型"""
    try:
        print(f"\n 測試模型: {model_name}")
        print("=" * 60)
        
        import google.generativeai as genai
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # 配置API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=google_api_key)
        
        # 測試1: 直接API
        print(" 測試直接API...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("請用中文簡單介紹一下蘋果公司的主要業務")
            
            if response and response.text:
                print(" 直接API調用成功")
                print(f"   響應長度: {len(response.text)} 字符")
                print(f"   響應預覽: {response.text[:150]}...")
                direct_success = True
            else:
                print(" 直接API調用失敗：無響應內容")
                direct_success = False
        except Exception as e:
            print(f" 直接API調用失敗: {e}")
            direct_success = False
        
        # 測試2: LangChain集成
        print("\n 測試LangChain集成...")
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.1,
                max_tokens=500,
                google_api_key=google_api_key
            )
            
            response = llm.invoke("請用中文分析蘋果公司的投資價值，包括優勢和風險")
            
            if response and response.content:
                print(" LangChain調用成功")
                print(f"   響應長度: {len(response.content)} 字符")
                print(f"   響應預覽: {response.content[:150]}...")
                langchain_success = True
            else:
                print(" LangChain調用失敗：無響應內容")
                langchain_success = False
        except Exception as e:
            print(f" LangChain調用失敗: {e}")
            langchain_success = False
        
        return direct_success, langchain_success
        
    except Exception as e:
        print(f" 模型測試失敗: {e}")
        return False, False

def test_tradingagents_with_gemini(model_name):
    """測試TradingAgents中使用Gemini"""
    try:
        print(f"\n 測試TradingAgents中使用 {model_name}")
        print("=" * 60)
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建使用Gemini的配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        config["deep_think_llm"] = model_name
        config["quick_think_llm"] = model_name
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
        
        print(" 配置創建成功")
        print(f"   模型: {model_name}")
        
        # 創建TradingAgentsGraph實例
        print(" 初始化TradingAgents圖...")
        graph = TradingAgentsGraph(["market"], config=config, debug=False)
        
        print(" TradingAgents圖初始化成功")
        
        # 測試簡單分析
        print(" 測試股票分析...")
        try:
            state, decision = graph.propagate("AAPL", "2025-06-27")
            
            if state and decision:
                print(" Gemini驅動的股票分析成功")
                print(f"   決策結果: {decision}")
                
                # 檢查市場報告
                if "market_report" in state and state["market_report"]:
                    market_report = state["market_report"]
                    print(f"   市場報告長度: {len(market_report)} 字符")
                    print(f"   報告預覽: {market_report[:150]}...")
                
                return True
            else:
                print(" 分析完成但結果為空")
                return False
                
        except Exception as e:
            print(f" 股票分析失敗: {e}")
            return False
            
    except Exception as e:
        print(f" TradingAgents集成測試失敗: {e}")
        return False

def main():
    """主函數"""
    print(" Gemini模型完整測試")
    print("=" * 70)
    
    # 檢查API密鑰
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print(" Google API密鑰未配置")
        return
    
    print(f" Google API密鑰已配置: {google_api_key[:20]}...")
    
    # 測試推薦的模型
    best_model = None
    best_score = 0
    
    for model_name in RECOMMENDED_MODELS:
        print(f"\n{'='*70}")
        print(f" 測試模型: {model_name}")
        
        direct_success, langchain_success = test_model(model_name)
        
        # 計算得分
        score = int(direct_success) + int(langchain_success)
        
        print(f"\n {model_name} 測試結果:")
        print(f"   直接API: {' 通過' if direct_success else ' 失敗'}")
        print(f"   LangChain: {' 通過' if langchain_success else ' 失敗'}")
        print(f"   得分: {score}/2")
        
        if score > best_score:
            best_score = score
            best_model = model_name
        
        # 如果找到完全可用的模型，就使用它
        if score == 2:
            print(f"\n 找到完全可用的模型: {model_name}")
            break
    
    # 使用最佳模型測試TradingAgents
    if best_model and best_score > 0:
        print(f"\n{'='*70}")
        print(f" 使用最佳模型測試TradingAgents: {best_model}")
        
        tradingagents_success = test_tradingagents_with_gemini(best_model)
        
        # 最終總結
        print(f"\n 最終測試結果總結:")
        print("=" * 50)
        print(f"  最佳模型: {best_model}")
        print(f"  基礎功能得分: {best_score}/2")
        print(f"  TradingAgents集成: {' 通過' if tradingagents_success else ' 失敗'}")
        
        if best_score == 2 and tradingagents_success:
            print(f"\n Gemini模型 {best_model} 完全可用！")
            print(f"\n 使用建議:")
            print(f"   1. 在Web界面配置中選擇Google作為LLM提供商")
            print(f"   2. 使用模型名稱: {best_model}")
            print(f"   3. 可以進行完整的股票分析")
            print(f"   4. 支持中文輸入和輸出")
        else:
            print(f"\n 模型部分可用，建議檢查網絡連接和API配額")
    else:
        print(f"\n 所有推薦模型都不可用，請檢查API密鑰和網絡連接")

if __name__ == "__main__":
    main()
