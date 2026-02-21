#!/usr/bin/env python3
"""
測試格式化修複
"""

import sys
from pathlib import Path

# 新增項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_format_analysis_results():
    """測試分析結果格式化函式"""
    
    from web.utils.analysis_runner import format_analysis_results
    
    print(" 測試分析結果格式化")
    print("=" * 50)
    
    # 測試案例1: decision 是字串
    print("測試案例1: decision 是字串")
    results1 = {
        'stock_symbol': 'AAPL',
        'analysis_date': '2025-06-27',
        'analysts': ['market', 'fundamentals'],
        'research_depth': 3,
        'llm_model': 'gpt-4o',
        'state': {
            'market_report': '技術分析報告...',
            'fundamentals_report': '基本面分析報告...'
        },
        'decision': 'BUY',  # 字串格式
        'success': True,
        'error': None
    }
    
    try:
        formatted1 = format_analysis_results(results1)
        print(" 字串decision格式化成功")
        print(f"  決策: {formatted1['decision']['action']}")
        print(f"  推理: {formatted1['decision']['reasoning']}")
    except Exception as e:
        print(f" 字串decision格式化失敗: {e}")
    
    print()
    
    # 測試案例2: decision 是字典
    print("測試案例2: decision 是字典")
    results2 = {
        'stock_symbol': 'AAPL',
        'analysis_date': '2025-06-27',
        'analysts': ['market', 'fundamentals'],
        'research_depth': 3,
        'llm_model': 'gpt-4o',
        'state': {
            'market_report': '技術分析報告...',
            'fundamentals_report': '基本面分析報告...'
        },
        'decision': {  # 字典格式
            'action': 'SELL',
            'confidence': 0.8,
            'risk_score': 0.4,
            'target_price': 180.0,
            'reasoning': '基於技術分析，建議賣出'
        },
        'success': True,
        'error': None
    }
    
    try:
        formatted2 = format_analysis_results(results2)
        print(" 字典decision格式化成功")
        print(f"  決策: {formatted2['decision']['action']}")
        print(f"  置信度: {formatted2['decision']['confidence']}")
        print(f"  推理: {formatted2['decision']['reasoning']}")
    except Exception as e:
        print(f" 字典decision格式化失敗: {e}")
    
    print()
    
    # 測試案例3: decision 是其他類型
    print("測試案例3: decision 是其他類型")
    results3 = {
        'stock_symbol': 'AAPL',
        'analysis_date': '2025-06-27',
        'analysts': ['market', 'fundamentals'],
        'research_depth': 3,
        'llm_model': 'gpt-4o',
        'state': {
            'market_report': '技術分析報告...',
            'fundamentals_report': '基本面分析報告...'
        },
        'decision': 123,  # 數字類型
        'success': True,
        'error': None
    }
    
    try:
        formatted3 = format_analysis_results(results3)
        print(" 其他類型decision格式化成功")
        print(f"  決策: {formatted3['decision']['action']}")
        print(f"  推理: {formatted3['decision']['reasoning']}")
    except Exception as e:
        print(f" 其他類型decision格式化失敗: {e}")
    
    print()
    
    # 測試案例4: 失敗的結果
    print("測試案例4: 失敗的結果")
    results4 = {
        'stock_symbol': 'AAPL',
        'success': False,
        'error': '分析失敗'
    }
    
    try:
        formatted4 = format_analysis_results(results4)
        print(" 失敗結果格式化成功")
        print(f"  成功: {formatted4['success']}")
        print(f"  錯誤: {formatted4['error']}")
    except Exception as e:
        print(f" 失敗結果格式化失敗: {e}")

def main():
    """主測試函式"""
    print(" 格式化修複測試")
    print("=" * 60)
    
    test_format_analysis_results()
    
    print("\n 測試完成！")

if __name__ == "__main__":
    main()
