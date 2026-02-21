#!/usr/bin/env python3
"""
測試新的在線工具配置系統
驗證環境變量和配置文件的集成
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_online_tools_config():
    """測試在線工具配置"""
    print(" 測試在線工具配置系統")
    print("=" * 60)
    
    # 1. 檢查環境變量
    print("\n 環境變量檢查:")
    env_vars = {
        'ONLINE_TOOLS_ENABLED': os.getenv('ONLINE_TOOLS_ENABLED', '未設置'),
        'ONLINE_NEWS_ENABLED': os.getenv('ONLINE_NEWS_ENABLED', '未設置'),
        'REALTIME_DATA_ENABLED': os.getenv('REALTIME_DATA_ENABLED', '未設置'),
        'OPENAI_ENABLED': os.getenv('OPENAI_ENABLED', '未設置'),
    }
    
    for var, value in env_vars.items():
        status = "" if value != "未設置" else ""
        print(f"   {status} {var}: {value}")
    
    # 2. 測試配置文件讀取
    print("\n 配置文件測試:")
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config_items = {
            'online_tools': DEFAULT_CONFIG.get('online_tools'),
            'online_news': DEFAULT_CONFIG.get('online_news'), 
            'realtime_data': DEFAULT_CONFIG.get('realtime_data'),
        }
        
        for key, value in config_items.items():
            print(f"    {key}: {value}")
            
    except Exception as e:
        print(f"    配置文件讀取失敗: {e}")
        return False
    
    # 3. 測試配置邏輯
    print("\n 配置邏輯驗證:")
    
    # 檢查在線工具總開關
    online_tools = DEFAULT_CONFIG.get('online_tools', False)
    online_news = DEFAULT_CONFIG.get('online_news', False)
    realtime_data = DEFAULT_CONFIG.get('realtime_data', False)
    
    print(f"    在線工具總開關: {' 啟用' if online_tools else ' 禁用'}")
    print(f"    在線新聞工具: {' 啟用' if online_news else ' 禁用'}")
    print(f"    實時數據獲取: {' 啟用' if realtime_data else ' 禁用'}")
    
    # 4. 配置建議
    print("\n 配置建議:")
    if not online_tools and not realtime_data:
        print("    當前為離線模式，適合開發和測試，節省API成本")
    elif online_tools and realtime_data:
        print("    當前為完全在線模式，會消耗較多API配額")
    else:
        print("    當前為混合模式，部分功能在線，部分離線")
    
    if online_news and not online_tools:
        print("    建議：新聞工具已啟用但總開關關閉，可能導致功能衝突")
    
    return True

def test_toolkit_integration():
    """測試工具包集成"""
    print("\n 工具包集成測試:")
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建工具包實例
        toolkit = Toolkit(config=DEFAULT_CONFIG)
        print("    Toolkit實例創建成功")
        
        # 檢查在線工具可用性
        online_tools = [
            'get_google_news',
            'get_reddit_news', 
            'get_reddit_stock_info',
            'get_chinese_social_sentiment'
        ]
        
        available_tools = []
        for tool_name in online_tools:
            if hasattr(toolkit, tool_name):
                available_tools.append(tool_name)
                print(f"    {tool_name} 可用")
            else:
                print(f"    {tool_name} 不可用")
        
        print(f"\n    可用在線工具: {len(available_tools)}/{len(online_tools)}")
        
        return len(available_tools) > 0
        
    except Exception as e:
        print(f"    工具包集成測試失敗: {e}")
        return False

def show_config_examples():
    """顯示配置示例"""
    print("\n 配置示例:")
    print("=" * 60)
    
    examples = {
        "開發模式 (離線)": {
            "ONLINE_TOOLS_ENABLED": "false",
            "ONLINE_NEWS_ENABLED": "false", 
            "REALTIME_DATA_ENABLED": "false",
            "說明": "完全離線，使用緩存數據，節省成本"
        },
        "測試模式 (部分在線)": {
            "ONLINE_TOOLS_ENABLED": "false",
            "ONLINE_NEWS_ENABLED": "true",
            "REALTIME_DATA_ENABLED": "false", 
            "說明": "新聞在線，數據離線，平衡功能和成本"
        },
        "生產模式 (完全在線)": {
            "ONLINE_TOOLS_ENABLED": "true",
            "ONLINE_NEWS_ENABLED": "true",
            "REALTIME_DATA_ENABLED": "true",
            "說明": "完全在線，獲取最新數據，適合實盤交易"
        }
    }
    
    for mode, config in examples.items():
        print(f"\n {mode}:")
        for key, value in config.items():
            if key == "說明":
                print(f"    {value}")
            else:
                print(f"   {key}={value}")

def main():
    """主測試函數"""
    print(" 在線工具配置系統測試")
    print("=" * 70)
    
    # 運行測試
    config_success = test_online_tools_config()
    toolkit_success = test_toolkit_integration()
    
    # 顯示配置示例
    show_config_examples()
    
    # 總結
    print("\n 測試總結:")
    print("=" * 60)
    print(f"   配置系統: {' 正常' if config_success else ' 異常'}")
    print(f"   工具包集成: {' 正常' if toolkit_success else ' 異常'}")
    
    if config_success and toolkit_success:
        print("\n 在線工具配置系統運行正常！")
        print(" 您現在可以通過環境變量靈活控制在線/離線模式")
    else:
        print("\n 發現問題，請檢查配置")
    
    return config_success and toolkit_success

if __name__ == "__main__":
    main()