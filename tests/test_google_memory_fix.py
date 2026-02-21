#!/usr/bin/env python3
"""
測試修複後的Google AI內存功能
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

def test_google_memory_fixed():
    """測試修複後的Google AI內存功能"""
    try:
        print("🧪 測試修複後的Google AI內存功能")
        print("=" * 60)
        
        from tradingagents.agents.utils.memory import FinancialSituationMemory
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 檢查API密鑰
        google_key = os.getenv('GOOGLE_API_KEY')
        
        print(f"🔑 API密鑰狀態:")
        print(f"   Google API: {'✅ 已配置' if google_key else '❌ 未配置'}")
        
        if not google_key:
            print("❌ Google API密鑰未配置，無法測試")
            return False
        
        # 創建Google AI配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        
        print("\n📊 創建Google AI內存實例...")
        memory = FinancialSituationMemory("test_google_memory", config)
        
        print(f"✅ 內存實例創建成功")
        print(f"   LLM提供商: {memory.llm_provider}")
        print(f"   嵌入模型: {memory.embedding}")
        print(f"   客戶端類型: {type(memory.client)}")
        
        # 測試嵌入功能
        print("\n📝 測試嵌入功能...")
        test_text = "蘋果公司股票在高通脹環境下的投資價值分析"
        
        try:
            embedding = memory.get_embedding(test_text)
            print(f"✅ 嵌入生成成功")
            print(f"   嵌入維度: {len(embedding)}")
            print(f"   嵌入預覽: {embedding[:5]}...")
            
            # 測試記憶存儲
            print("\n💾 測試記憶存儲...")
            memory.add_situations([
                ("高通脹環境，利率上升，科技股承壓", "建議關注現金流穩定的大型科技公司，如蘋果、微軟等"),
                ("市場波動加劇，投資者情緒謹慎", "建議分散投資，關注防禦性板塊")
            ])
            print("✅ 記憶存儲成功")
            
            # 測試記憶檢索
            print("\n🔍 測試記憶檢索...")
            similar_memories = memory.get_memories("通脹上升時期的科技股投資", n_matches=2)
            print(f"✅ 記憶檢索成功")
            print(f"   檢索到 {len(similar_memories)} 條相關記憶")

            for i, mem in enumerate(similar_memories, 1):
                situation = mem['matched_situation']
                recommendation = mem['recommendation']
                score = mem['similarity_score']
                print(f"   記憶{i} (相似度: {score:.3f}):")
                print(f"     情況: {situation}")
                print(f"     建議: {recommendation}")
            
            return True
            
        except Exception as e:
            print(f"❌ 嵌入功能測試失敗: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Google AI內存測試失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_google_tradingagents_with_memory():
    """測試帶內存的Google AI TradingAgents"""
    try:
        print("\n🧪 測試帶內存的Google AI TradingAgents")
        print("=" * 60)
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 檢查API密鑰
        google_key = os.getenv('GOOGLE_API_KEY')
        
        if not google_key:
            print("❌ Google API密鑰未配置")
            return False
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        config["deep_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"
        config["quick_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"
        config["online_tools"] = False  # 避免API限制
        config["memory_enabled"] = True  # 啟用內存功能
        config["max_debate_rounds"] = 1
        config["max_risk_discuss_rounds"] = 1
        
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
        print(f"   模型: {config['deep_think_llm']}")
        print(f"   內存功能: {config['memory_enabled']}")
        
        # 創建TradingAgentsGraph實例
        print("🚀 初始化帶內存的TradingAgents圖...")
        graph = TradingAgentsGraph(["market"], config=config, debug=False)
        
        print("✅ TradingAgents圖初始化成功")
        
        # 測試分析
        print("📊 開始帶內存的股票分析...")
        
        try:
            state, decision = graph.propagate("AAPL", "2025-06-27")
            
            if state and decision:
                print("✅ 帶內存的Gemini股票分析成功！")
                print(f"   最終決策: {decision}")
                
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
            print(f"❌ 帶內存的股票分析失敗: {e}")
            import traceback
            print(traceback.format_exc())
            return False
            
    except Exception as e:
        print(f"❌ 帶內存的TradingAgents測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 Google AI內存功能修複測試")
    print("=" * 70)
    
    # 運行測試
    results = {}
    
    results['內存功能'] = test_google_memory_fixed()
    results['完整TradingAgents'] = test_google_tradingagents_with_memory()
    
    # 總結結果
    print(f"\n📊 測試結果總結:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 總體結果: {successful_tests}/{total_tests} 測試通過")
    
    if successful_tests == total_tests:
        print("🎉 Google AI內存功能修複成功！")
        print("\n💡 現在可以使用的功能:")
        print("   ✅ Google Gemini作為主要LLM")
        print("   ✅ 阿里百煉作為嵌入服務")
        print("   ✅ 完整的內存和學習功能")
        print("   ✅ 中文分析和推理")
        print("   ✅ 歷史經驗學習")
    elif successful_tests > 0:
        print("⚠️ 部分功能可用")
        if results['內存功能'] and not results['完整TradingAgents']:
            print("💡 內存功能正常，但完整流程有其他問題")
    else:
        print("❌ 修複失敗，請檢查API密鑰配置")

if __name__ == "__main__":
    main()
