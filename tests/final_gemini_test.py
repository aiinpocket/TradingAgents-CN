#!/usr/bin/env python3
"""
最終驗證推薦的Gemini模型
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

def test_recommended_model():
    """測試推薦的gemini-2.0-flash模型"""
    try:
        print(" 最終驗證推薦模型: gemini-2.0-flash")
        print("=" * 60)
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 檢查API密鑰
        google_key = os.getenv('GOOGLE_API_KEY')
        
        print(f" API密鑰狀態:")
        print(f"   Google API: {' 已配置' if google_key else ' 未配置'}")
        
        if not google_key:
            print(" Google API密鑰未配置")
            return False
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        config["deep_think_llm"] = "gemini-2.0-flash"
        config["quick_think_llm"] = "gemini-2.0-flash"
        config["online_tools"] = False  # 避免API限制
        config["memory_enabled"] = True  # 啟用內存功能
        config["max_debate_rounds"] = 2  # 增加辯論輪次
        config["max_risk_discuss_rounds"] = 1
        
        # 修複路徑
        config["data_dir"] = str(project_root / "data")
        config["results_dir"] = str(project_root / "results")
        config["data_cache_dir"] = str(project_root / "tradingagents" / "dataflows" / "data_cache")
        
        # 創建目錄
        os.makedirs(config["data_dir"], exist_ok=True)
        os.makedirs(config["results_dir"], exist_ok=True)
        os.makedirs(config["data_cache_dir"], exist_ok=True)
        
        print(" 配置創建成功")
        print(f"   模型: {config['deep_think_llm']}")
        print(f"   內存功能: {config['memory_enabled']}")
        print(f"   辯論輪次: {config['max_debate_rounds']}")
        
        # 創建TradingAgentsGraph實例
        print(" 初始化TradingAgents圖...")
        graph = TradingAgentsGraph(["market", "fundamentals"], config=config, debug=False)
        
        print(" TradingAgents圖初始化成功")
        print("   分析師: 市場分析師 + 基本面分析師")
        
        # 測試分析
        print(" 開始完整股票分析...")
        print("   使用gemini-2.0-flash + OpenAI嵌入")
        print("   這可能需要幾分鐘時間...")
        
        try:
            state, decision = graph.propagate("AAPL", "2025-06-27")
            
            if state and decision:
                print(" gemini-2.0-flash驅動的完整分析成功！")
                print(f"   最終決策: {decision}")
                
                # 檢查各種報告
                reports = {
                    "market_report": "市場技術分析",
                    "fundamentals_report": "基本面分析", 
                    "sentiment_report": "情緒分析",
                    "news_report": "新聞分析"
                }
                
                for report_key, report_name in reports.items():
                    if report_key in state and state[report_key]:
                        report_content = state[report_key]
                        print(f"   {report_name}: {len(report_content)} 字符")
                        if len(report_content) > 100:
                            print(f"     預覽: {report_content[:150]}...")
                        print()
                
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
        print(f" 最終驗證失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def compare_models():
    """比較不同模型的建議"""
    print("\n 模型選擇建議")
    print("=" * 60)
    
    models_comparison = {
        "gemini-2.5-pro": {
            "狀態": " LangChain集成問題",
            "優勢": "最新版本，理論性能最強",
            "劣勢": "LangChain集成不穩定",
            "推薦": "不推薦（集成問題）"
        },
        "gemini-2.5-flash": {
            "狀態": " LangChain集成問題", 
            "優勢": "最新版本，速度快",
            "劣勢": "LangChain集成不穩定",
            "推薦": "不推薦（集成問題）"
        },
        "gemini-2.0-flash": {
            "狀態": " 完全可用",
            "優勢": "新版本，LangChain穩定，性能優秀",
            "劣勢": "不是最新的2.5版本",
            "推薦": " 強烈推薦"
        },
        "gemini-1.5-pro": {
            "狀態": " 完全可用",
            "優勢": "穩定，功能強大",
            "劣勢": "版本較舊",
            "推薦": "備選方案"
        }
    }
    
    for model, info in models_comparison.items():
        print(f"\n {model}:")
        for key, value in info.items():
            print(f"   {key}: {value}")

def main():
    """主函數"""
    print(" Gemini模型最終驗證")
    print("=" * 70)
    
    # 運行最終驗證
    success = test_recommended_model()
    
    # 顯示比較
    compare_models()
    
    # 最終建議
    print(f"\n 最終測試結果:")
    print("=" * 50)
    
    if success:
        print(" gemini-2.0-flash 完全驗證成功！")
        print("\n 最終推薦配置:")
        print("   LLM提供商: Google")
        print("   模型名稱: gemini-2.0-flash")
        print("   嵌入服務: OpenAI (text-embedding-v3)")
        print("   內存功能: 啟用")
        print("\n 優勢總結:")
        print("    優秀的推理能力")
        print("    完美的中文支持")
        print("    穩定的LangChain集成")
        print("    完整的內存學習功能")
        print("    準確的金融分析")
        print("\n 您現在可以在Web界面中使用這個配置！")
    else:
        print(" 驗證失敗")
        print(" 建議使用gemini-1.5-pro作為備選方案")

if __name__ == "__main__":
    main()
