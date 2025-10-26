#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from web.utils.analysis_runner import run_stock_analysis

def test_analysis_fix():
    """測試基本面分析師修複是否有效"""
    try:
        # 運行股票分析
        result = run_stock_analysis(
            stock_symbol='000001',
            analysis_date=1,
            analysts=['market', 'fundamentals'],
            research_depth=1,
            llm_provider='dashscope',
            llm_model='qwen-plus',
            market_type='A股'
        )
        
        print(f"Analysis completed: {'success' if result['success'] else 'failed'}")
        
        if result['success']:
            state = result['state']
            market_report = state.get('market_report', '')
            fundamentals_report = state.get('fundamentals_report', '')
            
            print(f"Market report length: {len(market_report)}")
            print(f"Fundamentals report length: {len(fundamentals_report)}")
            
            # 檢查報告是否有實际內容
            if len(market_report) > 0:
                print("✅ Market report has content")
            else:
                print("❌ Market report is empty")
                
            if len(fundamentals_report) > 0:
                print("✅ Fundamentals report has content")
            else:
                print("❌ Fundamentals report is empty")
                
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Test failed with exception: {e}")

if __name__ == '__main__':
    test_analysis_fix()