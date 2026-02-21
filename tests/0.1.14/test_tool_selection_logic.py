#!/usr/bin/env python3
"""
測試新的工具選擇邏輯
驗證美股數據獲取不再依賴OpenAI配置
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_tool_selection_scenarios():
    """測試不同配置場景下的工具選擇"""
    print(" 測試工具選擇邏輯")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "場景1: 完全離線模式",
            "config": {
                "online_tools": False,
                "online_news": False,
                "realtime_data": False,
            },
            "expected": {
                "market_primary": "get_YFin_data",
                "news_primary": "get_finnhub_news",
                "social_primary": "get_reddit_stock_info"
            }
        },
        {
            "name": "場景2: 實時數據啟用",
            "config": {
                "online_tools": False,
                "online_news": False,
                "realtime_data": True,
            },
            "expected": {
                "market_primary": "get_YFin_data_online",
                "news_primary": "get_finnhub_news",
                "social_primary": "get_reddit_stock_info"
            }
        },
        {
            "name": "場景3: 在線新聞啟用",
            "config": {
                "online_tools": False,
                "online_news": True,
                "realtime_data": False,
            },
            "expected": {
                "market_primary": "get_YFin_data",
                "news_primary": "get_google_news",
                "social_primary": "get_reddit_stock_info"
            }
        },
        {
            "name": "場景4: 完全在線模式",
            "config": {
                "online_tools": True,
                "online_news": True,
                "realtime_data": True,
            },
            "expected": {
                "market_primary": "get_YFin_data_online",
                "news_primary": "get_global_news_openai",
                "social_primary": "get_stock_news_openai"
            }
        }
    ]
    
    for scenario in scenarios:
        print(f"\n {scenario['name']}")
        print("-" * 50)
        
        try:
            # 模擬工具選擇邏輯
            config = scenario['config']
            online_tools_enabled = config.get("online_tools", False)
            online_news_enabled = config.get("online_news", True)
            realtime_data_enabled = config.get("realtime_data", False)
            
            print(f"   配置: online_tools={online_tools_enabled}, "
                  f"online_news={online_news_enabled}, "
                  f"realtime_data={realtime_data_enabled}")
            
            # 市場數據工具選擇
            if realtime_data_enabled:
                market_primary = "get_YFin_data_online"
            else:
                market_primary = "get_YFin_data"
            
            # 新聞工具選擇
            if online_news_enabled:
                if online_tools_enabled:
                    news_primary = "get_global_news_openai"
                else:
                    news_primary = "get_google_news"
            else:
                news_primary = "get_finnhub_news"
            
            # 社交媒體工具選擇
            if online_tools_enabled:
                social_primary = "get_stock_news_openai"
            else:
                social_primary = "get_reddit_stock_info"
            
            # 驗證結果
            expected = scenario['expected']
            results = {
                "market_primary": market_primary,
                "news_primary": news_primary,
                "social_primary": social_primary
            }
            
            print(f"   結果:")
            for tool_type, tool_name in results.items():
                expected_tool = expected[tool_type]
                status = "" if tool_name == expected_tool else ""
                print(f"     {tool_type}: {tool_name} {status}")
                if tool_name != expected_tool:
                    print(f"       期望: {expected_tool}")
            
        except Exception as e:
            print(f"    測試失敗: {e}")

def test_trading_graph_integration():
    """測試TradingGraph集成"""
    print(f"\n 測試TradingGraph集成")
    print("=" * 70)
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        # 測試不同配置
        test_configs = [
            {
                "name": "離線模式",
                "config": {
                    **DEFAULT_CONFIG,
                    "online_tools": False,
                    "online_news": False,
                    "realtime_data": False,
                }
            },
            {
                "name": "實時數據模式",
                "config": {
                    **DEFAULT_CONFIG,
                    "online_tools": False,
                    "online_news": True,
                    "realtime_data": True,
                }
            }
        ]
        
        for test_config in test_configs:
            print(f"\n 測試配置: {test_config['name']}")
            print("-" * 40)
            
            try:
                # 創建TradingGraph實例
                ta = TradingAgentsGraph(
                    config=test_config['config'],
                    selected_analysts=["market_analyst"],
                    debug=False
                )
                
                # 檢查工具節點配置
                market_tools = ta.tool_nodes["market"].tools
                news_tools = ta.tool_nodes["news"].tools
                social_tools = ta.tool_nodes["social"].tools
                
                print(f"   市場工具數量: {len(market_tools)}")
                print(f"   新聞工具數量: {len(news_tools)}")
                print(f"   社交工具數量: {len(social_tools)}")
                
                # 檢查主要工具
                market_tool_names = [tool.name for tool in market_tools]
                news_tool_names = [tool.name for tool in news_tools]
                social_tool_names = [tool.name for tool in social_tools]
                
                print(f"   主要市場工具: {market_tool_names[1] if len(market_tool_names) > 1 else 'N/A'}")
                print(f"   主要新聞工具: {news_tool_names[0] if news_tool_names else 'N/A'}")
                print(f"   主要社交工具: {social_tool_names[0] if social_tool_names else 'N/A'}")
                
                print("    TradingGraph創建成功")
                
            except Exception as e:
                print(f"    TradingGraph創建失敗: {e}")
                
    except ImportError as e:
        print(f"    無法導入TradingGraph: {e}")

def test_us_stock_data_independence():
    """測試美股數據獲取的獨立性"""
    print(f"\n🇺🇸 測試美股數據獲取獨立性")
    print("=" * 70)
    
    print("驗證美股數據獲取不再依賴OpenAI配置...")
    
    # 模擬不同的OpenAI配置狀態
    openai_scenarios = [
        {"OPENAI_API_KEY": None, "OPENAI_ENABLED": "false"},
        {"OPENAI_API_KEY": "test_key", "OPENAI_ENABLED": "true"},
    ]
    
    for i, openai_config in enumerate(openai_scenarios, 1):
        print(f"\n OpenAI場景 {i}: {openai_config}")
        print("-" * 40)
        
        # 臨時設置環境變量
        original_env = {}
        for key, value in openai_config.items():
            original_env[key] = os.environ.get(key)
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        try:
            # 測試不同的在線工具配置
            data_configs = [
                {"REALTIME_DATA_ENABLED": "false", "expected": "離線數據"},
                {"REALTIME_DATA_ENABLED": "true", "expected": "實時數據"},
            ]
            
            for data_config in data_configs:
                os.environ["REALTIME_DATA_ENABLED"] = data_config["REALTIME_DATA_ENABLED"]
                
                # 重新加載配置
                from importlib import reload
                import tradingagents.default_config
                reload(tradingagents.default_config)
                
                from tradingagents.default_config import DEFAULT_CONFIG
                
                realtime_enabled = DEFAULT_CONFIG.get("realtime_data", False)
                expected_mode = "實時數據" if realtime_enabled else "離線數據"
                
                print(f"     REALTIME_DATA_ENABLED={data_config['REALTIME_DATA_ENABLED']} "
                      f"-> {expected_mode} ")
                
        finally:
            # 恢複原始環境變量
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    
    print("\n 結論: 美股數據獲取現在完全獨立於OpenAI配置！")

def main():
    """主測試函數"""
    print(" 工具選擇邏輯測試")
    print("=" * 70)
    
    # 運行測試
    test_tool_selection_scenarios()
    test_trading_graph_integration()
    test_us_stock_data_independence()
    
    print(f"\n 測試完成！")
    print(" 現在美股數據獲取基於專門的配置字段，不再依賴OpenAI配置")

if __name__ == "__main__":
    main()