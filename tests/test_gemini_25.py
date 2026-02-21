#!/usr/bin/env python3
"""
測試Gemini 2.5 Flash和Pro模型
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

# Gemini 2.5模型列表
GEMINI_25_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro", 
    "gemini-2.5-flash-002",
    "gemini-2.5-pro-002"
]

def test_gemini_25_availability():
    """測試Gemini 2.5模型的可用性"""
    print("🧪 測試Gemini 2.5模型可用性")
    print("=" * 60)
    
    try:
        import google.generativeai as genai
        
        # 配置API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            print("❌ Google API密鑰未配置")
            return []
        
        genai.configure(api_key=google_api_key)
        
        # 獲取所有可用模型
        print("📋 獲取所有可用模型...")
        all_models = genai.list_models()
        
        available_25_models = []
        
        print("🔍 檢查Gemini 2.5模型:")
        for model_name in GEMINI_25_MODELS:
            found = False
            for model in all_models:
                if model_name in model.name:
                    print(f"✅ {model_name}: 可用")
                    print(f"   完整名稱: {model.name}")
                    print(f"   顯示名稱: {model.display_name}")
                    print(f"   支持方法: {model.supported_generation_methods}")
                    available_25_models.append(model.name)
                    found = True
                    break
            
            if not found:
                print(f"❌ {model_name}: 不可用")
        
        return available_25_models
        
    except Exception as e:
        print(f"❌ 檢查模型可用性失敗: {e}")
        return []

def test_specific_gemini_25_model(model_name):
    """測試特定的Gemini 2.5模型"""
    try:
        print(f"\n🧪 測試模型: {model_name}")
        print("=" * 60)
        
        import google.generativeai as genai
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # 配置API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=google_api_key)
        
        # 測試1: 直接API
        print("📝 測試直接API...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                "請用中文分析蘋果公司(AAPL)的投資價值，包括技術創新、市場地位和財務狀況"
            )
            
            if response and response.text:
                print("✅ 直接API調用成功")
                print(f"   響應長度: {len(response.text)} 字符")
                print(f"   響應預覽: {response.text[:200]}...")
                direct_success = True
            else:
                print("❌ 直接API調用失敗：無響應內容")
                direct_success = False
        except Exception as e:
            print(f"❌ 直接API調用失敗: {e}")
            direct_success = False
        
        # 測試2: LangChain集成
        print("\n📝 測試LangChain集成...")
        try:
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.1,
                max_tokens=1000,
                google_api_key=google_api_key
            )
            
            response = llm.invoke(
                "請用中文分析當前人工智能行業的投資機會，重點關註大型科技公司的AI戰略"
            )
            
            if response and response.content:
                print("✅ LangChain調用成功")
                print(f"   響應長度: {len(response.content)} 字符")
                print(f"   響應預覽: {response.content[:200]}...")
                langchain_success = True
            else:
                print("❌ LangChain調用失敗：無響應內容")
                langchain_success = False
        except Exception as e:
            print(f"❌ LangChain調用失敗: {e}")
            langchain_success = False
        
        # 測試3: 複雜推理能力
        print("\n📝 測試複雜推理能力...")
        try:
            complex_prompt = """
            請用中文進行複雜的股票分析推理：
            
            假設場景：
            - 當前時間：2025年6月
            - 美聯儲剛剛降息0.25%
            - 中美貿易關系有所緩解
            - AI技術快速發展
            - 通脹率降至2.5%
            
            請分析在這種宏觀環境下，蘋果公司(AAPL)的投資價值，包括：
            1. 宏觀經濟因素的影響
            2. 行業競爭態勢
            3. 公司特有優勢
            4. 風險因素
            5. 投資建議和目標價位
            
            請提供詳細的邏輯推理過程。
            """
            
            response = llm.invoke(complex_prompt)
            
            if response and response.content and len(response.content) > 500:
                print("✅ 複雜推理測試成功")
                print(f"   響應長度: {len(response.content)} 字符")
                print(f"   響應預覽: {response.content[:300]}...")
                complex_success = True
            else:
                print("❌ 複雜推理測試失敗：響應過短或無內容")
                complex_success = False
        except Exception as e:
            print(f"❌ 複雜推理測試失敗: {e}")
            complex_success = False
        
        return direct_success, langchain_success, complex_success
        
    except Exception as e:
        print(f"❌ 模型測試失敗: {e}")
        return False, False, False

def test_gemini_25_in_tradingagents(model_name):
    """測試Gemini 2.5在TradingAgents中的使用"""
    try:
        print(f"\n🧪 測試{model_name}在TradingAgents中的使用")
        print("=" * 60)
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        config["deep_think_llm"] = model_name
        config["quick_think_llm"] = model_name
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
        print(f"   模型: {model_name}")
        print(f"   內存功能: {config['memory_enabled']}")
        
        # 創建TradingAgentsGraph實例
        print("🚀 初始化TradingAgents圖...")
        graph = TradingAgentsGraph(["market"], config=config, debug=False)
        
        print("✅ TradingAgents圖初始化成功")
        
        # 測試分析
        print("📊 開始股票分析...")
        
        try:
            state, decision = graph.propagate("AAPL", "2025-06-27")
            
            if state and decision:
                print(f"✅ {model_name}驅動的股票分析成功！")
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
            print(f"❌ 股票分析失敗: {e}")
            return False
            
    except Exception as e:
        print(f"❌ TradingAgents測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 Gemini 2.5模型測試")
    print("=" * 70)
    
    # 檢查API密鑰
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ Google API密鑰未配置")
        return
    
    print(f"✅ Google API密鑰已配置: {google_api_key[:20]}...")
    
    # 檢查可用的Gemini 2.5模型
    available_models = test_gemini_25_availability()
    
    if not available_models:
        print("\n❌ 沒有找到可用的Gemini 2.5模型")
        return
    
    print(f"\n🎯 找到 {len(available_models)} 個可用的Gemini 2.5模型")
    
    # 測試每個可用模型
    best_model = None
    best_score = 0
    
    for model_name in available_models:
        print(f"\n{'='*70}")
        
        # 基礎功能測試
        direct, langchain, complex = test_specific_gemini_25_model(model_name)
        score = sum([direct, langchain, complex])
        
        print(f"\n📊 {model_name} 基礎測試結果:")
        print(f"   直接API: {'✅' if direct else '❌'}")
        print(f"   LangChain: {'✅' if langchain else '❌'}")
        print(f"   複雜推理: {'✅' if complex else '❌'}")
        print(f"   得分: {score}/3")
        
        if score > best_score:
            best_score = score
            best_model = model_name
        
        # 如果基礎功能全部通過，測試TradingAgents集成
        if score == 3:
            tradingagents_success = test_gemini_25_in_tradingagents(model_name)
            if tradingagents_success:
                print(f"   TradingAgents: ✅")
                total_score = score + 1
            else:
                print(f"   TradingAgents: ❌")
                total_score = score
            
            print(f"   總得分: {total_score}/4")
    
    # 最終推薦
    print(f"\n📊 最終測試結果:")
    print("=" * 50)
    print(f"  最佳模型: {best_model}")
    print(f"  最高得分: {best_score}/3")
    
    if best_score >= 2:
        print(f"\n🎉 推薦使用: {best_model}")
        print(f"\n💡 配置建議:")
        print(f"   1. 在Web界面中選擇'Google'作為LLM提供商")
        print(f"   2. 使用模型名稱: {best_model}")
        print(f"   3. Gemini 2.5具有更強的推理和分析能力")
        print(f"   4. 支持更複雜的金融分析任務")
    else:
        print(f"\n⚠️ 所有Gemini 2.5模型測試不理想")
        print(f"   建議檢查API密鑰權限和網絡連接")

if __name__ == "__main__":
    main()
