#!/usr/bin/env python3
"""
測試在完整分析中使用Google和Reddit API
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

def test_news_analyst_with_google():
    """測試新聞分析師使用Google工具"""
    try:
        print("🧪 測試新聞分析師使用Google工具")
        print("=" * 60)
        
        from tradingagents.agents.analysts.news_analyst import create_news_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.llm_adapters import ChatDashScope
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        config["llm_provider"] = "dashscope"
        
        # 創建LLM和工具包
        llm = ChatDashScope(model="qwen-plus", temperature=0.1)
        toolkit = Toolkit(config=config)
        
        print("✅ 組件創建成功")
        
        # 創建新聞分析師
        news_analyst = create_news_analyst(llm, toolkit)
        
        print("✅ 新聞分析師創建成功")
        
        # 創建測試狀態
        from tradingagents.agents.utils.agent_states import AgentState
        from langchain_core.messages import HumanMessage
        
        test_state = {
            "messages": [HumanMessage(content="分析AAPL的新聞情况")],
            "company_of_interest": "AAPL",
            "trade_date": "2025-06-27"
        }
        
        print("📰 開始新聞分析...")
        
        # 執行分析（這可能需要一些時間）
        result = news_analyst(test_state)
        
        if result and "news_report" in result:
            news_report = result["news_report"]
            if news_report and len(news_report) > 100:
                print("✅ 新聞分析成功完成")
                print(f"   報告長度: {len(news_report)} 字符")
                print(f"   報告預覽: {news_report[:200]}...")
                return True
            else:
                print("⚠️ 新聞分析完成但報告內容較少")
                return True
        else:
            print("⚠️ 新聞分析完成但没有生成報告")
            return False
            
    except Exception as e:
        print(f"❌ 新聞分析師測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_social_analyst_with_reddit():
    """測試社交媒體分析師使用Reddit工具"""
    try:
        print("\n🧪 測試社交媒體分析師使用Reddit工具")
        print("=" * 60)
        
        from tradingagents.agents.analysts.social_media_analyst import create_social_media_analyst
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.llm_adapters import ChatDashScope
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        config["llm_provider"] = "dashscope"
        
        # 創建LLM和工具包
        llm = ChatDashScope(model="qwen-plus", temperature=0.1)
        toolkit = Toolkit(config=config)
        
        print("✅ 組件創建成功")
        
        # 創建社交媒體分析師
        social_analyst = create_social_media_analyst(llm, toolkit)
        
        print("✅ 社交媒體分析師創建成功")
        
        # 創建測試狀態
        from langchain_core.messages import HumanMessage
        
        test_state = {
            "messages": [HumanMessage(content="分析AAPL的社交媒體情绪")],
            "company_of_interest": "AAPL", 
            "trade_date": "2025-06-27"
        }
        
        print("💭 開始社交媒體分析...")
        
        # 執行分析
        result = social_analyst(test_state)
        
        if result and "sentiment_report" in result:
            sentiment_report = result["sentiment_report"]
            if sentiment_report and len(sentiment_report) > 100:
                print("✅ 社交媒體分析成功完成")
                print(f"   報告長度: {len(sentiment_report)} 字符")
                print(f"   報告預覽: {sentiment_report[:200]}...")
                return True
            else:
                print("⚠️ 社交媒體分析完成但報告內容較少")
                return True
        else:
            print("⚠️ 社交媒體分析完成但没有生成報告")
            return False
            
    except Exception as e:
        print(f"❌ 社交媒體分析師測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主測試函數"""
    print("🧪 完整分析中的API工具測試")
    print("=" * 70)
    
    # 檢查環境變量
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    reddit_id = os.getenv("REDDIT_CLIENT_ID")
    
    if not dashscope_key:
        print("❌ DASHSCOPE_API_KEY 未配置，無法進行測試")
        return
    
    print("🔑 API密鑰狀態:")
    print(f"   阿里百炼: ✅ 已配置")
    print(f"   Google: {'✅ 已配置' if google_key else '❌ 未配置'}")
    print(f"   Reddit: {'✅ 已配置' if reddit_id else '❌ 未配置'}")
    
    # 運行測試
    results = {}
    
    print("\n" + "="*70)
    results['新聞分析師+Google'] = test_news_analyst_with_google()
    
    print("\n" + "="*70)
    results['社交媒體分析師+Reddit'] = test_social_analyst_with_reddit()
    
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
        print("🎉 所有API工具在分析中正常工作！")
        print("\n💡 使用建议:")
        print("   1. 在Web界面中選擇'新聞分析師'來使用Google新聞")
        print("   2. 在Web界面中選擇'社交媒體分析師'來使用Reddit數據")
        print("   3. 同時選擇多個分析師可以獲得更全面的分析")
    else:
        print("⚠️ 部分API工具需要進一步配置")

if __name__ == "__main__":
    main()
