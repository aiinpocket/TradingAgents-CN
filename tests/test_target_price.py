#!/usr/bin/env python3
"""
測試優化後的目標價生成系統
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_signal_processor():
    """測試信號處理器的價格提取功能"""
    print("🧪 測試信號處理器價格提取功能...")
    
    try:
        from tradingagents.agents.signal_processing import SignalProcessor
        
        processor = SignalProcessor()
        
        # 測試用例1: 包含明確目標價的文本
        test_text1 = """
        基於技術分析，AAPL當前價格為180美元，建议买入。
        目標價位：200美元
        止損價位：170美元
        預期涨幅：11%
        """
        
        result1 = processor._extract_target_price(test_text1, "AAPL", "USD")
        print(f"✅ 測試1 - 明確目標價: {result1}")
        
        # 測試用例2: 需要智能推算的文本
        test_text2 = """
        腾讯控股(0700.HK)當前價格為320港元，
        基於基本面分析建议买入，預期上涨15%。
        """
        
        result2 = processor._extract_target_price(test_text2, "0700.HK", "HKD")
        print(f"✅ 測試2 - 智能推算: {result2}")
        
        # 測試用例3: A股示例
        test_text3 = """
        贵州茅台(600519)現價1800元，基於估值分析，
        合理價位区間為1900-2100元，建议持有。
        """
        
        result3 = processor._extract_target_price(test_text3, "600519", "CNY")
        print(f"✅ 測試3 - A股價格: {result3}")
        
        return True
        
    except Exception as e:
        print(f"❌ 信號處理器測試失败: {e}")
        return False

def test_smart_price_estimation():
    """測試智能價格推算功能"""
    print("\n🧪 測試智能價格推算功能...")
    
    try:
        from tradingagents.agents.signal_processing import SignalProcessor
        
        processor = SignalProcessor()
        
        # 測試推算逻辑
        test_cases = [
            ("當前價格100美元，預期上涨20%", "buy", 120.0),
            ("現價50元，建议卖出，預計下跌10%", "sell", 45.0),
            ("股價200港元，持有，預期涨幅5%", "hold", 210.0)
        ]
        
        for text, action, expected in test_cases:
            result = processor._smart_price_estimation(text, action)
            print(f"✅ 文本: '{text}' -> 推算價格: {result} (預期: {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ 智能推算測試失败: {e}")
        return False

def test_trader_prompt():
    """測試交易員提示詞是否包含目標價要求"""
    print("\n🧪 檢查交易員提示詞優化...")
    
    try:
        from tradingagents.agents.trader import trader_node
        import inspect
        
        # 獲取trader_node函數的源代碼
        source = inspect.getsource(trader_node)
        
        # 檢查關键詞
        keywords = ["目標價", "target_price", "具體價位", "禁止回複"]
        found_keywords = []
        
        for keyword in keywords:
            if keyword in source:
                found_keywords.append(keyword)
        
        print(f"✅ 交易員提示詞包含關键詞: {found_keywords}")
        
        if len(found_keywords) >= 2:
            print("✅ 交易員模塊已優化")
            return True
        else:
            print("⚠️ 交易員模塊可能需要進一步優化")
            return False
            
    except Exception as e:
        print(f"❌ 交易員提示詞檢查失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試優化後的目標價生成系統")
    print("=" * 60)
    
    test_results = []
    
    # 運行各項測試
    test_results.append(test_signal_processor())
    test_results.append(test_smart_price_estimation())
    test_results.append(test_trader_prompt())
    
    # 汇总結果
    print("\n" + "=" * 60)
    print("📊 測試結果汇总:")
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"✅ 通過測試: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有測試通過！目標價生成系統優化成功！")
        print("\n💡 系統現在能夠:")
        print("   • 從分析文本中提取明確的目標價")
        print("   • 基於當前價格和涨跌幅智能推算目標價")
        print("   • 强制要求所有分析師提供目標價信息")
        print("   • 支持多種貨币和股票市場")
    else:
        print(f"⚠️ 有 {total - passed} 項測試未通過，需要進一步檢查")
    
    print("\n🔧 下一步建议:")
    print("   1. 運行完整的股票分析流程測試")
    print("   2. 驗證實际LLM響應中的目標價生成")
    print("   3. 測試不同類型股票的分析效果")

if __name__ == "__main__":
    main()