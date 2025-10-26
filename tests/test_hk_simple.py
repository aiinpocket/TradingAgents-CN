"""
簡單的港股功能測試
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_basic():
    """基本測試"""
    print("🧪 開始基本港股功能測試...")
    
    try:
        # 測試股票工具類
        from tradingagents.utils.stock_utils import StockUtils
        
        # 測試港股代碼识別
        test_cases = [
            "0700.HK",  # 腾讯
            "9988.HK",  # 阿里巴巴
            "3690.HK",  # 美团
            "000001",   # 平安銀行
            "AAPL"      # 苹果
        ]
        
        for ticker in test_cases:
            market_info = StockUtils.get_market_info(ticker)
            print(f"  {ticker}: {market_info['market_name']} ({market_info['currency_name']} {market_info['currency_symbol']})")
        
        print("✅ 基本測試通過")
        return True
        
    except Exception as e:
        print(f"❌ 基本測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_basic()
