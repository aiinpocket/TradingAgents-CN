#!/usr/bin/env python3
"""
測試所有API密鑰功能
包括Google API和Reddit API
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

def check_all_api_keys():
    """檢查所有API密鑰配置"""
    print("🔑 檢查API密鑰配置")
    print("=" * 50)
    
    api_keys = {
        'DASHSCOPE_API_KEY': '阿里百炼API',
        'FINNHUB_API_KEY': '金融數據API', 
        'GOOGLE_API_KEY': 'Google API',
        'REDDIT_CLIENT_ID': 'Reddit客戶端ID',
        'REDDIT_CLIENT_SECRET': 'Reddit客戶端密鑰',
        'REDDIT_USER_AGENT': 'Reddit用戶代理'
    }
    
    configured_apis = []
    missing_apis = []
    
    for key, name in api_keys.items():
        value = os.getenv(key)
        if value:
            print(f"✅ {name}: 已配置 ({value[:10]}...)")
            configured_apis.append(name)
        else:
            print(f"❌ {name}: 未配置")
            missing_apis.append(name)
    
    print(f"\n📊 配置狀態:")
    print(f"  已配置: {len(configured_apis)}/{len(api_keys)}")
    print(f"  缺失: {len(missing_apis)}")
    
    return configured_apis, missing_apis

def test_google_api():
    """測試Google API"""
    try:
        print("\n🧪 測試Google API")
        print("=" * 50)
        
        google_key = os.getenv('GOOGLE_API_KEY')
        if not google_key:
            print("❌ Google API密鑰未配置")
            return False
        
        # 這里可以添加具體的Google API測試
        # 例如Google News API或Google Search API
        print("✅ Google API密鑰已配置")
        print("💡 提示: 需要根據具體使用的Google服務進行測試")
        
        return True
        
    except Exception as e:
        print(f"❌ Google API測試失败: {e}")
        return False

def test_reddit_api():
    """測試Reddit API"""
    try:
        print("\n🧪 測試Reddit API")
        print("=" * 50)
        
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT')
        
        if not all([client_id, client_secret, user_agent]):
            print("❌ Reddit API配置不完整")
            print(f"  CLIENT_ID: {'✅' if client_id else '❌'}")
            print(f"  CLIENT_SECRET: {'✅' if client_secret else '❌'}")
            print(f"  USER_AGENT: {'✅' if user_agent else '❌'}")
            return False
        
        # 測試Reddit API連接
        try:
            import praw
            
            reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            
            # 測試獲取一個簡單的subreddit信息
            subreddit = reddit.subreddit('investing')
            print(f"✅ Reddit API連接成功")
            print(f"  測試subreddit: {subreddit.display_name}")
            print(f"  订阅者數量: {subreddit.subscribers:,}")
            
            return True
            
        except ImportError:
            print("⚠️ praw庫未安裝，無法測試Reddit API")
            print("💡 運行: pip install praw")
            return False
        except Exception as e:
            print(f"❌ Reddit API連接失败: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Reddit API測試失败: {e}")
        return False

def test_tradingagents_with_new_apis():
    """測試TradingAgents是否能使用新的API"""
    try:
        print("\n🧪 測試TradingAgents集成")
        print("=" * 50)
        
        # 檢查TradingAgents是否支持這些API
        from tradingagents.dataflows import interface
        
        # 檢查可用的數據流工具
        print("📊 檢查可用的數據獲取工具:")
        
        # 檢查Google相關工具
        try:
            from tradingagents.dataflows.googlenews_utils import get_google_news
            print("✅ Google News工具可用")
        except ImportError:
            print("❌ Google News工具不可用")
        
        # 檢查Reddit相關工具  
        try:
            from tradingagents.dataflows.reddit_utils import get_reddit_sentiment
            print("✅ Reddit情绪分析工具可用")
        except ImportError:
            print("❌ Reddit情绪分析工具不可用")
        
        return True
        
    except Exception as e:
        print(f"❌ TradingAgents集成測試失败: {e}")
        return False

def test_social_media_analyst():
    """測試社交媒體分析師是否能使用Reddit數據"""
    try:
        print("\n🧪 測試社交媒體分析師")
        print("=" * 50)
        
        # 檢查社交媒體分析師
        from tradingagents.agents.analysts.social_media_analyst import create_social_media_analyst
        from tradingagents.llm_adapters import ChatDashScope
        
        # 創建模型實例
        llm = ChatDashScope(model="qwen-plus")
        
        # 這里需要toolkit實例，暂時跳過實际測試
        print("✅ 社交媒體分析師模塊可用")
        print("💡 需要完整的toolkit實例才能進行實际測試")
        
        return True
        
    except Exception as e:
        print(f"❌ 社交媒體分析師測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 全面API測試")
    print("=" * 60)
    
    # 檢查API密鑰配置
    configured, missing = check_all_api_keys()
    
    # 測試各個API
    results = {}
    
    if 'Google API' in configured:
        results['Google API'] = test_google_api()
    
    if all(api in configured for api in ['Reddit客戶端ID', 'Reddit客戶端密鑰']):
        results['Reddit API'] = test_reddit_api()
    
    # 測試TradingAgents集成
    results['TradingAgents集成'] = test_tradingagents_with_new_apis()
    results['社交媒體分析師'] = test_social_media_analyst()
    
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
        print("🎉 所有測試通過！")
    else:
        print("⚠️ 部分測試失败，請檢查配置")

if __name__ == "__main__":
    main()
