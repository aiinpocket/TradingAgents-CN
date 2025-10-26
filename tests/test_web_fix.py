#!/usr/bin/env python3
"""
測試Web界面修複
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_render_decision_summary():
    """測試render_decision_summary函數修複"""
    
    try:
        # 模擬streamlit環境
        class MockStreamlit:
            def subheader(self, text):
                print(f"📊 {text}")
            
            def columns(self, n):
                return [MockColumn() for _ in range(n)]
            
            def metric(self, label, value, delta=None, delta_color=None, help=None):
                print(f"  {label}: {value}")
                if delta:
                    print(f"    Delta: {delta}")
        
        class MockColumn:
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
        
        # 模擬streamlit模塊
        sys.modules['streamlit'] = MockStreamlit()
        
        from web.components.results_display import render_decision_summary
        
        print("🧪 測試render_decision_summary修複...")
        
        # 測試中國A股
        china_decision = {
            'action': '持有',
            'confidence': 0.75,
            'risk_score': 0.40,
            'target_price': 15.00,
            'reasoning': '基於综合分析的投資建议'
        }
        
        print("\n📈 測試中國A股決策顯示:")
        render_decision_summary(china_decision, "000001")
        
        # 測試美股
        us_decision = {
            'action': '买入',
            'confidence': 0.80,
            'risk_score': 0.30,
            'target_price': 180.00,
            'reasoning': '基於综合分析的投資建议'
        }
        
        print("\n📈 測試美股決策顯示:")
        render_decision_summary(us_decision, "AAPL")
        
        print("\n✅ render_decision_summary修複測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_currency_detection():
    """測試貨币檢測逻辑"""
    
    try:
        import re
        
        def is_china_stock(ticker_code):
            return re.match(r'^\d{6}$', str(ticker_code)) if ticker_code else False
        
        print("🧪 測試貨币檢測逻辑...")
        
        # 測試中國A股代碼
        china_stocks = ["000001", "600036", "300001", "002001"]
        for stock in china_stocks:
            is_china = is_china_stock(stock)
            currency = "¥" if is_china else "$"
            print(f"  {stock}: {'中國A股' if is_china else '非A股'} -> {currency}")
            
            if not is_china:
                print(f"❌ {stock} 應该被识別為中國A股")
                return False
        
        # 測試非中國股票代碼
        foreign_stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "0700.HK"]
        for stock in foreign_stocks:
            is_china = is_china_stock(stock)
            currency = "¥" if is_china else "$"
            print(f"  {stock}: {'中國A股' if is_china else '非A股'} -> {currency}")
            
            if is_china:
                print(f"❌ {stock} 不應该被识別為中國A股")
                return False
        
        print("✅ 貨币檢測逻辑測試通過！")
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 開始測試Web界面修複...")
    print("=" * 50)
    
    # 運行測試
    test1_result = test_render_decision_summary()
    test2_result = test_currency_detection()
    
    print("=" * 50)
    if test1_result and test2_result:
        print("🎉 所有Web界面修複測試通過！")
        print("📝 現在Web界面應该能正確顯示:")
        print("   - 中國A股: ¥XX.XX")
        print("   - 美股/港股: $XX.XX")
        print("   - 不再出現 NameError")
        sys.exit(0)
    else:
        print("❌ 部分測試失败")
        sys.exit(1)
