#!/usr/bin/env python3
"""
測試工具包中的Google和Reddit工具
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

def test_toolkit_tools():
    """測試工具包中的工具"""
    try:
        print(" 測試工具包中的Google和Reddit工具")
        print("=" * 60)
        
        # 正確導入Toolkit
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        
        # 創建工具包實例
        toolkit = Toolkit(config=config)
        
        print(" Toolkit實例創建成功")
        
        # 檢查所有可用方法
        all_methods = [method for method in dir(toolkit) if not method.startswith('_')]
        print(f" 工具包總方法數: {len(all_methods)}")
        
        # 查找Google相關方法
        google_methods = [m for m in all_methods if 'google' in m.lower()]
        print(f" Google相關方法: {google_methods}")
        
        # 查找Reddit相關方法
        reddit_methods = [m for m in all_methods if 'reddit' in m.lower()]
        print(f" Reddit相關方法: {reddit_methods}")
        
        # 查找新聞相關方法
        news_methods = [m for m in all_methods if 'news' in m.lower()]
        print(f" 新聞相關方法: {news_methods}")
        
        # 測試具體的Google工具
        if hasattr(toolkit, 'get_google_news'):
            print("\n get_google_news 方法存在")
            try:
                # 測試調用
                print(" 測試Google新聞獲取...")
                news = toolkit.get_google_news(
                    query="Apple AAPL",
                    curr_date="2025-06-27",
                    look_back_days=3
                )
                if news and len(news) > 100:
                    print(f" Google新聞獲取成功 ({len(news)} 字符)")
                else:
                    print(" Google新聞獲取成功但內容較少")
            except Exception as e:
                print(f" Google新聞測試失敗: {e}")
        else:
            print(" get_google_news 方法不存在")
        
        # 測試Reddit工具
        reddit_tools = ['get_reddit_global_news', 'get_reddit_company_news', 'get_reddit_stock_info', 'get_reddit_news']
        
        for tool_name in reddit_tools:
            if hasattr(toolkit, tool_name):
                print(f" {tool_name} 方法存在")
            else:
                print(f" {tool_name} 方法不存在")
        
        # 顯示所有方法（用於調試）
        print(f"\n 所有可用方法:")
        for i, method in enumerate(sorted(all_methods), 1):
            print(f"  {i:2d}. {method}")
        
        return True
        
    except Exception as e:
        print(f" 工具包測試失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_social_news_analysts():
    """測試社交媒體和新聞分析師是否能使用這些工具"""
    try:
        print("\n 測試分析師工具集成")
        print("=" * 60)
        
        # 檢查社交媒體分析師
        try:
            from tradingagents.agents.analysts.social_media_analyst import create_social_media_analyst
            print(" 社交媒體分析師模塊可用")
        except ImportError as e:
            print(f" 社交媒體分析師導入失敗: {e}")
        
        # 檢查新聞分析師
        try:
            from tradingagents.agents.analysts.news_analyst import create_news_analyst
            print(" 新聞分析師模塊可用")
        except ImportError as e:
            print(f" 新聞分析師導入失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f" 分析師測試失敗: {e}")
        return False

def check_data_requirements():
    """檢查數據要求"""
    print("\n 檢查數據要求")
    print("=" * 60)
    
    # 檢查Reddit數據目錄
    reddit_data_paths = [
        "tradingagents/dataflows/data_cache/reddit_data",
        "data/reddit_data",
        "reddit_data"
    ]
    
    reddit_data_found = False
    for path in reddit_data_paths:
        reddit_path = Path(path)
        if reddit_path.exists():
            print(f" Reddit數據目錄找到: {reddit_path}")
            subdirs = [d.name for d in reddit_path.iterdir() if d.is_dir()]
            if subdirs:
                print(f"   子目錄: {subdirs}")
                reddit_data_found = True
            else:
                print("   目錄為空")
            break
    
    if not reddit_data_found:
        print(" Reddit數據目錄未找到")
        print(" Reddit工具需要預先下載的數據文件")
        print("   可能的解決方案:")
        print("   1. 下載Reddit數據集")
        print("   2. 配置正確的數據路徑")
        print("   3. 使用在線Reddit API（如果支持）")
    
    # 檢查Google API要求
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key:
        print(" Google API密鑰已配置")
        print(" Google新聞工具使用網页抓取，不需要API密鑰")
    else:
        print(" Google API密鑰未配置")
        print(" 但Google新聞工具仍可能正常工作（使用網页抓取）")

def main():
    """主測試函數"""
    print(" 工具包Google和Reddit工具測試")
    print("=" * 70)
    
    # 檢查API密鑰狀態
    print(" API密鑰狀態:")
    google_key = os.getenv('GOOGLE_API_KEY')
    reddit_id = os.getenv('REDDIT_CLIENT_ID')
    print(f"   Google API: {' 已配置' if google_key else ' 未配置'}")
    print(f"   Reddit API: {' 已配置' if reddit_id else ' 未配置'}")
    
    # 運行測試
    results = {}
    
    results['工具包工具'] = test_toolkit_tools()
    results['分析師集成'] = test_social_news_analysts()
    
    # 檢查數據要求
    check_data_requirements()
    
    # 總結結果
    print(f"\n 測試結果總結:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = " 通過" if success else " 失敗"
        print(f"  {test_name}: {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n 總體結果: {successful_tests}/{total_tests} 測試通過")

if __name__ == "__main__":
    main()
