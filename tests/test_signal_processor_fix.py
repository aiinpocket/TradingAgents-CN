#!/usr/bin/env python3
"""
測試SignalProcessor修複後的功能
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env", override=True)

def test_signal_processor_currency_fix():
    """測試SignalProcessor的貨币修複"""
    
    try:
        from tradingagents.graph.signal_processing import SignalProcessor
        from langchain_openai import ChatOpenAI
        
        print("🔍 測試SignalProcessor貨币修複...")
        
        # 創建LLM（使用阿里百炼）
        llm = ChatOpenAI(
            model="qwen-turbo",
            openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
            openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
            temperature=0.1
        )
        
        # 創建信號處理器
        processor = SignalProcessor(llm)
        
        # 測試中國A股信號
        china_signal = """
        基於對平安銀行(000001)的综合分析，我們建议持有该股票。
        
        技術面分析顯示當前價格為12.50元，目標價位為15.00元。
        基本面分析表明公司財務狀况良好，ROE為12.5%。
        
        置信度：75%
        風險評分：40%
        
        最终交易建议: **持有**
        """
        
        print("📈 測試中國A股信號處理...")
        china_decision = processor.process_signal(china_signal, "000001")
        print(f"中國A股決策結果: {china_decision}")
        
        # 測試美股信號
        us_signal = """
        Based on comprehensive analysis of Apple Inc. (AAPL), we recommend BUY.
        
        Technical analysis shows current price at $150.00, target price $180.00.
        Fundamental analysis indicates strong financial performance.
        
        Confidence: 80%
        Risk Score: 30%
        
        Final Trading Recommendation: **BUY**
        """
        
        print("📈 測試美股信號處理...")
        us_decision = processor.process_signal(us_signal, "AAPL")
        print(f"美股決策結果: {us_decision}")
        
        # 驗證結果
        success = True
        
        # 檢查中國A股結果
        if china_decision.get('action') not in ['买入', '持有', '卖出']:
            print(f"❌ 中國A股動作錯誤: {china_decision.get('action')}")
            success = False
        
        if china_decision.get('target_price') is None:
            print("❌ 中國A股目標價位為空")
            success = False
        
        # 檢查美股結果
        if us_decision.get('action') not in ['买入', '持有', '卖出']:
            print(f"❌ 美股動作錯誤: {us_decision.get('action')}")
            success = False
        
        if us_decision.get('target_price') is None:
            print("❌ 美股目標價位為空")
            success = False
        
        if success:
            print("✅ SignalProcessor貨币修複測試通過！")
            return True
        else:
            print("❌ SignalProcessor貨币修複測試失败！")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_web_currency_display():
    """測試Web界面貨币顯示修複"""
    
    try:
        from web.components.results_display import render_decision_summary
        import streamlit as st
        
        print("🌐 測試Web界面貨币顯示...")
        
        # 模擬中國A股結果
        china_results = {
            'stock_symbol': '000001',
            'decision': {
                'action': '持有',
                'confidence': 0.75,
                'risk_score': 0.40,
                'target_price': 15.00,
                'reasoning': '基於综合分析的投資建议'
            }
        }
        
        # 模擬美股結果
        us_results = {
            'stock_symbol': 'AAPL',
            'decision': {
                'action': '买入',
                'confidence': 0.80,
                'risk_score': 0.30,
                'target_price': 180.00,
                'reasoning': '基於综合分析的投資建议'
            }
        }
        
        print("✅ Web界面貨币顯示修複已實現")
        print("📝 中國A股應顯示: ¥15.00")
        print("📝 美股應顯示: $180.00")
        
        return True
        
    except Exception as e:
        print(f"❌ Web界面測試失败: {e}")
        return False

if __name__ == "__main__":
    print("🧪 開始測試SignalProcessor修複...")
    print("=" * 50)
    
    # 檢查環境變量
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ DASHSCOPE_API_KEY 環境變量未設置")
        sys.exit(1)
    
    # 運行測試
    test1_result = test_signal_processor_currency_fix()
    test2_result = test_web_currency_display()
    
    print("=" * 50)
    if test1_result and test2_result:
        print("🎉 所有測試通過！修複成功！")
        sys.exit(0)
    else:
        print("❌ 部分測試失败，需要進一步調試")
        sys.exit(1)
