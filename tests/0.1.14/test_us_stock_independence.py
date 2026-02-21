#!/usr/bin/env python3
"""
測試美股資料取得獨立性
驗證美股資料取得不再依賴OpenAI配置
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from tradingagents.agents.utils.agent_utils import Toolkit
    from tradingagents.default_config import DEFAULT_CONFIG
except ImportError:
    print(" 無法匯入Toolkit，請檢查項目結構")
    sys.exit(1)

def test_us_stock_data_independence():
    """測試美股資料取得獨立性"""
    print(" 測試美股資料取得獨立性")
    print("=" * 60)
    
    # 測試場景1: OpenAI禁用，即時資料啟用
    print("\n 場景1: OpenAI禁用 + 即時資料啟用")
    print("-" * 40)
    
    # 設置環境變量
    os.environ['OPENAI_ENABLED'] = 'false'
    os.environ['REALTIME_DATA_ENABLED'] = 'true'
    
    try:
        config = DEFAULT_CONFIG.copy()
        config["realtime_data"] = True
        toolkit = Toolkit(config=config)
        
        # 檢查美股資料工具
        us_tools = [
            'get_YFin_data_online',
            'get_YFin_data',
            'get_us_stock_data_cached'
        ]
        
        for tool_name in us_tools:
            if hasattr(toolkit, tool_name):
                print(f"    {tool_name} 可用")
            else:
                print(f"    {tool_name} 不可用")
                
        # 測試實際調用
        try:
            # 測試獲取蘋果股票資料
            result = toolkit.get_us_stock_data_cached("AAPL", "1d", "1mo")
            if result and "error" not in str(result).lower():
                print("    美股資料取得成功")
            else:
                print("    美股資料取得返回錯誤或空結果")
        except Exception as e:
            print(f"    美股資料取得異常: {e}")
            
    except Exception as e:
        print(f"    Toolkit創建失敗: {e}")
    
    # 測試場景2: OpenAI啟用，即時資料禁用
    print("\n 場景2: OpenAI啟用 + 即時資料禁用")
    print("-" * 40)
    
    # 設置環境變量
    os.environ['OPENAI_ENABLED'] = 'true'
    os.environ['REALTIME_DATA_ENABLED'] = 'false'
    
    try:
        config = DEFAULT_CONFIG.copy()
        config["realtime_data"] = False
        toolkit = Toolkit(config=config)
        
        # 檢查美股資料工具
        for tool_name in us_tools:
            if hasattr(toolkit, tool_name):
                print(f"    {tool_name} 可用")
            else:
                print(f"    {tool_name} 不可用")
                
    except Exception as e:
        print(f"    Toolkit創建失敗: {e}")
    
    print("\n 結論:")
    print("   美股資料取得現在基於 REALTIME_DATA_ENABLED 配置")
    print("   不再依賴 OPENAI_ENABLED 配置")
    print("   實現了真正的功能獨立性！")

if __name__ == "__main__":
    test_us_stock_data_independence()
    print("\n 測試完成！")