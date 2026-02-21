#!/usr/bin/env python3
"""
測試Gemini 2.5 Pro模型
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

def test_gemini_25_pro_basic():
    """測試Gemini 2.5 Pro基礎功能"""
    try:
        print("🧪 測試Gemini 2.5 Pro基礎功能")
        print("=" * 60)
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # 檢查API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            print("❌ Google API密鑰未配置")
            return False
        
        print(f"✅ Google API密鑰已配置: {google_api_key[:20]}...")
        
        # 創建Gemini 2.5 Pro實例
        print("🚀 創建Gemini 2.5 Pro實例...")
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.1,
            max_tokens=1500,
            google_api_key=google_api_key
        )
        
        print("✅ Gemini 2.5 Pro實例創建成功")
        
        # 測試中文股票分析
        print("📊 測試中文股票分析...")
        response = llm.invoke("""
        請用中文分析蘋果公司(AAPL)的投資價值。請從以下幾個方面進行分析：
        
        1. 公司基本面分析
        2. 技術創新能力
        3. 市場競爭地位
        4. 財務健康狀況
        5. 投資風險評估
        6. 投資建議
        
        請提供詳細的分析和推理過程。
        """)
        
        if response and response.content:
            print("✅ 中文股票分析成功")
            print(f"   響應長度: {len(response.content)} 字符")
            print(f"   響應預覽: {response.content[:300]}...")
            return True
        else:
            print("❌ 中文股票分析失敗")
            return False
            
    except Exception as e:
        print(f"❌ Gemini 2.5 Pro基礎測試失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_gemini_25_pro_tradingagents():
    """測試Gemini 2.5 Pro在TradingAgents中的使用"""
    try:
        print("\n🧪 測試Gemini 2.5 Pro在TradingAgents中的使用")
        print("=" * 60)
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        config["deep_think_llm"] = "gemini-2.5-pro"
        config["quick_think_llm"] = "gemini-2.5-pro"
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
        print(f"   模型: gemini-2.5-pro")
        print(f"   內存功能: {config['memory_enabled']}")
        
        # 創建TradingAgentsGraph實例
        print("🚀 初始化TradingAgents圖...")
        graph = TradingAgentsGraph(["market"], config=config, debug=False)
        
        print("✅ TradingAgents圖初始化成功")
        
        # 測試分析
        print("📊 開始Gemini 2.5 Pro股票分析...")
        print("   這可能需要幾分鐘時間...")
        
        try:
            state, decision = graph.propagate("AAPL", "2025-06-27")
            
            if state and decision:
                print("✅ Gemini 2.5 Pro驅動的股票分析成功！")
                print(f"   最終決策: {decision}")
                
                # 檢查各種報告
                reports = ["market_report", "sentiment_report", "news_report", "fundamentals_report"]
                for report_name in reports:
                    if report_name in state and state[report_name]:
                        report_content = state[report_name]
                        print(f"   {report_name}: {len(report_content)} 字符")
                        if len(report_content) > 100:
                            print(f"   預覽: {report_content[:150]}...")
                        print()
                
                return True
            else:
                print("❌ 分析完成但結果為空")
                return False
                
        except Exception as e:
            print(f"❌ 股票分析失敗: {e}")
            import traceback
            print(traceback.format_exc())
            return False
            
    except Exception as e:
        print(f"❌ TradingAgents測試失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_gemini_25_pro_complex_reasoning():
    """測試Gemini 2.5 Pro的複雜推理能力"""
    try:
        print("\n🧪 測試Gemini 2.5 Pro複雜推理能力")
        print("=" * 60)
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # 創建實例
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            temperature=0.1,
            max_tokens=2000,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        # 複雜推理測試
        complex_prompt = """
        請進行複雜的投資分析推理：
        
        場景設定：
        - 時間：2025年6月
        - 美聯儲政策：剛剛降息25個基點
        - 通脹率：2.8%，呈下降趨勢
        - 中美關系：貿易緊張局勢有所緩解
        - AI發展：ChatGPT和其他AI工具快速普及
        - 地緣政治：俄烏衝突持續，中東局勢緊張
        
        請分析在這種複雜的宏觀環境下，以下三只股票的投資價值排序：
        1. 蘋果公司(AAPL) - 消費電子+AI
        2. 英偉達(NVDA) - AI芯片領導者
        3. 微軟(MSFT) - 雲計算+AI軟體
        
        要求：
        1. 分析每只股票在當前環境下的優勢和劣勢
        2. 考慮宏觀經濟因素對各股票的影響
        3. 評估AI發展對各公司的長期影響
        4. 提供投資優先級排序和理由
        5. 給出具體的投資建議和風險提示
        
        請用中文提供詳細的邏輯推理過程。
        """
        
        print("🧠 開始複雜推理測試...")
        response = llm.invoke(complex_prompt)
        
        if response and response.content and len(response.content) > 800:
            print("✅ 複雜推理測試成功")
            print(f"   響應長度: {len(response.content)} 字符")
            print(f"   響應預覽: {response.content[:400]}...")
            return True
        else:
            print("❌ 複雜推理測試失敗：響應過短或無內容")
            return False
            
    except Exception as e:
        print(f"❌ 複雜推理測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 Gemini 2.5 Pro完整測試")
    print("=" * 70)
    
    # 檢查環境變量
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ Google API密鑰未配置")
        print("💡 請在.env文件中設置 GOOGLE_API_KEY")
        return
    
    # 運行測試
    results = {}
    
    print("第1步: 基礎功能測試")
    print("-" * 30)
    results['基礎功能'] = test_gemini_25_pro_basic()
    
    print("\n第2步: 複雜推理測試")
    print("-" * 30)
    results['複雜推理'] = test_gemini_25_pro_complex_reasoning()
    
    print("\n第3步: TradingAgents集成測試")
    print("-" * 30)
    results['TradingAgents集成'] = test_gemini_25_pro_tradingagents()
    
    # 總結結果
    print(f"\n📊 Gemini 2.5 Pro測試結果總結:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"  {test_name}: {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 總體結果: {successful_tests}/{total_tests} 測試通過")
    
    if successful_tests == total_tests:
        print("🎉 Gemini 2.5 Pro完全可用！")
        print("\n💡 Gemini 2.5 Pro優勢:")
        print("   🧠 更強的推理能力")
        print("   📊 更好的複雜分析")
        print("   🌍 優秀的多語言支持")
        print("   💰 更準確的金融分析")
        print("   🔍 更深入的洞察力")
        print("\n🚀 使用建議:")
        print("   1. 在Web界面中選擇'Google'作為LLM提供商")
        print("   2. 使用模型名稱: gemini-2.5-pro")
        print("   3. 適合複雜的投資分析任務")
        print("   4. 可以處理多因素綜合分析")
    elif successful_tests >= 2:
        print("⚠️ Gemini 2.5 Pro大部分功能可用")
        print("💡 可以用於基礎分析，部分高級功能可能需要調整")
    else:
        print("❌ Gemini 2.5 Pro不可用")
        print("💡 請檢查API密鑰權限和網絡連接")

if __name__ == "__main__":
    main()
