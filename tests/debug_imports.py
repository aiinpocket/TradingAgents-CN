#!/usr/bin/env python3
"""
調試導入問題
"""

import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_google_news_import():
    """測試Google News工具導入"""
    print("🧪 測試Google News工具導入")
    print("=" * 50)
    
    try:
        # 嘗試不同的導入方式
        print("1. 嘗試導入googlenews_utils模塊...")
        from tradingagents.dataflows import googlenews_utils
        print("✅ googlenews_utils模塊導入成功")
        
        # 檢查模塊中的函數
        print("2. 檢查模塊中的函數...")
        functions = [attr for attr in dir(googlenews_utils) if not attr.startswith('_')]
        print(f"   可用函數: {functions}")
        
        # 嘗試導入特定函數
        print("3. 嘗試導入特定函數...")
        if hasattr(googlenews_utils, 'get_google_news'):
            print("✅ get_google_news函數存在")
        else:
            print("❌ get_google_news函數不存在")
            
        if hasattr(googlenews_utils, 'getNewsData'):
            print("✅ getNewsData函數存在")
        else:
            print("❌ getNewsData函數不存在")
            
        return True
        
    except ImportError as e:
        print(f"❌ 導入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False

def test_reddit_import():
    """測試Reddit工具導入"""
    print("\n🧪 測試Reddit工具導入")
    print("=" * 50)
    
    try:
        # 嘗試不同的導入方式
        print("1. 嘗試導入reddit_utils模塊...")
        from tradingagents.dataflows import reddit_utils
        print("✅ reddit_utils模塊導入成功")
        
        # 檢查模塊中的函數
        print("2. 檢查模塊中的函數...")
        functions = [attr for attr in dir(reddit_utils) if not attr.startswith('_')]
        print(f"   可用函數: {functions}")
        
        # 嘗試導入特定函數
        print("3. 嘗試導入特定函數...")
        if hasattr(reddit_utils, 'get_reddit_sentiment'):
            print("✅ get_reddit_sentiment函數存在")
        else:
            print("❌ get_reddit_sentiment函數不存在")
            
        # 檢查其他可能的函數名
        possible_functions = ['get_reddit_data', 'fetch_reddit_posts', 'analyze_reddit_sentiment']
        for func_name in possible_functions:
            if hasattr(reddit_utils, func_name):
                print(f"✅ {func_name}函數存在")
            
        return True
        
    except ImportError as e:
        print(f"❌ 導入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False

def check_dependencies():
    """檢查依賴庫"""
    print("\n🧪 檢查依賴庫")
    print("=" * 50)
    
    dependencies = {
        'requests': 'HTTP請求庫',
        'beautifulsoup4': 'HTML解析庫',
        'praw': 'Reddit API庫',
        'tenacity': '重試機制庫'
    }
    
    for package, description in dependencies.items():
        try:
            if package == 'beautifulsoup4':
                import bs4
                print(f"✅ {description}: 已安裝")
            else:
                __import__(package)
                print(f"✅ {description}: 已安裝")
        except ImportError:
            print(f"❌ {description}: 未安裝 (pip install {package})")

def check_actual_file_contents():
    """檢查實际文件內容"""
    print("\n🧪 檢查實际文件內容")
    print("=" * 50)
    
    # 檢查Google News文件
    try:
        google_file = Path("tradingagents/dataflows/googlenews_utils.py")
        if google_file.exists():
            print(f"✅ Google News文件存在: {google_file}")
            with open(google_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'def ' in content:
                    # 提取函數定義
                    import re
                    functions = re.findall(r'def (\w+)\(', content)
                    print(f"   文件中的函數: {functions}")
                else:
                    print("   文件中没有函數定義")
        else:
            print(f"❌ Google News文件不存在: {google_file}")
    except Exception as e:
        print(f"❌ 檢查Google News文件失败: {e}")
    
    # 檢查Reddit文件
    try:
        reddit_file = Path("tradingagents/dataflows/reddit_utils.py")
        if reddit_file.exists():
            print(f"✅ Reddit文件存在: {reddit_file}")
            with open(reddit_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'def ' in content:
                    # 提取函數定義
                    import re
                    functions = re.findall(r'def (\w+)\(', content)
                    print(f"   文件中的函數: {functions}")
                else:
                    print("   文件中没有函數定義")
        else:
            print(f"❌ Reddit文件不存在: {reddit_file}")
    except Exception as e:
        print(f"❌ 檢查Reddit文件失败: {e}")

def main():
    """主函數"""
    print("🔍 診斷工具導入問題")
    print("=" * 60)
    
    # 檢查依賴庫
    check_dependencies()
    
    # 檢查文件內容
    check_actual_file_contents()
    
    # 測試導入
    google_success = test_google_news_import()
    reddit_success = test_reddit_import()
    
    print(f"\n📊 診斷結果:")
    print(f"  Google News工具: {'✅ 可用' if google_success else '❌ 不可用'}")
    print(f"  Reddit工具: {'✅ 可用' if reddit_success else '❌ 不可用'}")

if __name__ == "__main__":
    main()
