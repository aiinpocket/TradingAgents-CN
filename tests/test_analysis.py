#!/usr/bin/env python3
"""
簡化的分析測試腳本
用於驗證TradingAgents核心功能是否正常工作
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

def test_basic_imports():
    """測試基本導入"""
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        print(" 基本導入成功")
        return True
    except Exception as e:
        print(f" 基本導入失敗: {e}")
        return False

def test_environment_variables():
    """測試環境變量"""
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    
    print(f"FINNHUB_API_KEY: {'已設置' if finnhub_key else '未設置'}")
    
    return bool(finnhub_key)

def test_graph_initialization():
    """測試圖初始化"""
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config["deep_think_llm"] = "gpt-4o"
        config["quick_think_llm"] = "gpt-4o"
        config["memory_enabled"] = True
        config["online_tools"] = True
        
        # 修複路徑
        config["data_dir"] = str(project_root / "data")
        config["results_dir"] = str(project_root / "results")
        config["data_cache_dir"] = str(project_root / "tradingagents" / "dataflows" / "data_cache")
        
        # 創建目錄
        os.makedirs(config["data_dir"], exist_ok=True)
        os.makedirs(config["results_dir"], exist_ok=True)
        os.makedirs(config["data_cache_dir"], exist_ok=True)
        
        # 初始化圖
        graph = TradingAgentsGraph(["market"], config=config, debug=True)
        print(" 圖初始化成功")
        return True, graph
    except Exception as e:
        print(f" 圖初始化失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False, None

def test_simple_analysis():
    """測試簡單分析"""
    success, graph = test_graph_initialization()
    if not success:
        return False
    
    try:
        print(" 開始簡單分析測試...")
        # 執行簡單分析
        state, decision = graph.propagate("AAPL", "2025-06-27")
        print(" 分析完成")
        print(f"決策: {decision}")
        return True
    except Exception as e:
        print(f" 分析失敗: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主測試函數"""
    print(" TradingAgents 功能測試")
    print("=" * 50)
    
    # 測試基本導入
    print("\n1. 測試基本導入...")
    if not test_basic_imports():
        return
    
    # 測試環境變量
    print("\n2. 測試環境變量...")
    if not test_environment_variables():
        print(" 環境變量未正確配置")
        return
    
    # 測試圖初始化
    print("\n3. 測試圖初始化...")
    success, graph = test_graph_initialization()
    if not success:
        return
    
    # 測試簡單分析
    print("\n4. 測試簡單分析...")
    if test_simple_analysis():
        print("\n 所有測試通過！")
    else:
        print("\n 分析測試失敗")

if __name__ == "__main__":
    main()
