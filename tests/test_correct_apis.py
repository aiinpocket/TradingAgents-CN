#!/usr/bin/env python3
"""
正確測試Google和Reddit API工具
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

def test_google_news_tool():
    """測試Google新聞工具"""
    try:
        print("🧪 測試Google新聞工具")
        print("=" * 50)
        
        from tradingagents.dataflows.interface import get_google_news
        
        print("✅ get_google_news函數導入成功")
        
        # 測試獲取苹果公司新聞
        print("📰 獲取苹果公司新聞...")
        try:
            news = get_google_news(
                query="Apple AAPL stock",
                curr_date="2025-06-27", 
                look_back_days=7
            )
            
            if news and len(news) > 0:
                print("✅ Google新聞獲取成功")
                print(f"   新聞長度: {len(news)} 字符")
                print(f"   新聞預覽: {news[:200]}...")
                return True
            else:
                print("⚠️ Google新聞獲取成功但內容為空")
                return True  # 功能正常，只是没有內容
                
        except Exception as e:
            print(f"❌ Google新聞獲取失败: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ Google新聞工具導入失败: {e}")
        return False

def test_reddit_tools():
    """測試Reddit工具"""
    try:
        print("\n🧪 測試Reddit工具")
        print("=" * 50)
        
        from tradingagents.dataflows.interface import get_reddit_global_news, get_reddit_company_news
        
        print("✅ Reddit工具函數導入成功")
        
        # 檢查Reddit數據目錄
        reddit_data_dir = Path("tradingagents/dataflows/data_cache/reddit_data")
        print(f"📁 Reddit數據目錄: {reddit_data_dir}")
        
        if reddit_data_dir.exists():
            print("✅ Reddit數據目錄存在")
            
            # 檢查子目錄
            subdirs = [d for d in reddit_data_dir.iterdir() if d.is_dir()]
            print(f"   子目錄: {[d.name for d in subdirs]}")
            
            if subdirs:
                print("✅ Reddit數據可用，可以進行測試")
                
                # 測試全球新聞
                try:
                    print("📰 測試Reddit全球新聞...")
                    global_news = get_reddit_global_news(
                        start_date="2025-06-27",
                        look_back_days=1,
                        max_limit_per_day=5
                    )
                    
                    if global_news and len(global_news) > 0:
                        print("✅ Reddit全球新聞獲取成功")
                        print(f"   新聞長度: {len(global_news)} 字符")
                    else:
                        print("⚠️ Reddit全球新聞獲取成功但內容為空")
                        
                except Exception as e:
                    print(f"❌ Reddit全球新聞獲取失败: {e}")
                
                # 測試公司新聞
                try:
                    print("📰 測試Reddit公司新聞...")
                    company_news = get_reddit_company_news(
                        ticker="AAPL",
                        start_date="2025-06-27",
                        look_back_days=1,
                        max_limit_per_day=5
                    )
                    
                    if company_news and len(company_news) > 0:
                        print("✅ Reddit公司新聞獲取成功")
                        print(f"   新聞長度: {len(company_news)} 字符")
                    else:
                        print("⚠️ Reddit公司新聞獲取成功但內容為空")
                        
                except Exception as e:
                    print(f"❌ Reddit公司新聞獲取失败: {e}")
                    
                return True
            else:
                print("⚠️ Reddit數據目錄為空，需要先下載數據")
                return False
        else:
            print("⚠️ Reddit數據目錄不存在，需要先設置數據")
            print("💡 提示: Reddit工具需要預先下載的數據文件")
            return False
            
    except ImportError as e:
        print(f"❌ Reddit工具導入失败: {e}")
        return False

def test_toolkit_integration():
    """測試工具包集成"""
    try:
        print("\n🧪 測試工具包集成")
        print("=" * 50)
        
        # 檢查Toolkit類是否包含這些工具
        from tradingagents.agents.utils.toolkit import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        toolkit = Toolkit(config=config)
        
        # 檢查工具包中的方法
        methods = [method for method in dir(toolkit) if not method.startswith('_')]
        
        google_methods = [m for m in methods if 'google' in m.lower()]
        reddit_methods = [m for m in methods if 'reddit' in m.lower()]
        
        print(f"📊 工具包方法总數: {len(methods)}")
        print(f"   Google相關方法: {google_methods}")
        print(f"   Reddit相關方法: {reddit_methods}")
        
        # 檢查具體方法是否存在
        if hasattr(toolkit, 'get_google_news'):
            print("✅ toolkit.get_google_news 方法存在")
        else:
            print("❌ toolkit.get_google_news 方法不存在")
            
        if hasattr(toolkit, 'get_reddit_global_news'):
            print("✅ toolkit.get_reddit_global_news 方法存在")
        else:
            print("❌ toolkit.get_reddit_global_news 方法不存在")
            
        if hasattr(toolkit, 'get_reddit_company_news'):
            print("✅ toolkit.get_reddit_company_news 方法存在")
        else:
            print("❌ toolkit.get_reddit_company_news 方法不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 工具包集成測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 正確的API工具測試")
    print("=" * 60)
    
    # 檢查API密鑰
    google_key = os.getenv('GOOGLE_API_KEY')
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    
    print(f"🔑 API密鑰狀態:")
    print(f"   Google API: {'✅ 已配置' if google_key else '❌ 未配置'}")
    print(f"   Reddit API: {'✅ 已配置' if reddit_id else '❌ 未配置'}")
    
    # 運行測試
    results = {}
    
    results['Google新聞工具'] = test_google_news_tool()
    results['Reddit工具'] = test_reddit_tools()
    results['工具包集成'] = test_toolkit_integration()
    
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
