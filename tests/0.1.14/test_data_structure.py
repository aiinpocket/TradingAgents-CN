#!/usr/bin/env python3
"""
測試資料結構腳本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

def test_data_structure():
    """測試分析結果資料結構"""
    try:
        from web.components.analysis_results import load_analysis_results
        
        print(" 測試分析結果資料結構...")
        
        # 載入分析結果
        results = load_analysis_results(limit=5)
        
        print(f" 找到 {len(results)} 個分析結果")
        
        if results:
            result = results[0]
            print(f"\n 第一個結果的資料結構:")
            print(f"   analysis_id: {result.get('analysis_id', 'missing')}")
            print(f"   source: {result.get('source', 'missing')}")
            print(f"   stock_symbol: {result.get('stock_symbol', 'missing')}")
            print(f"   reports字段存在: {'reports' in result}")
            
            if 'reports' in result:
                reports = result['reports']
                print(f"   reports內容: {list(reports.keys())}")
                
                # 顯示第一個報告的前100個字符
                if reports:
                    first_report_key = list(reports.keys())[0]
                    first_report_content = reports[first_report_key]
                    print(f"   {first_report_key} 內容預覽:")
                    print(f"   {first_report_content[:200]}...")
            else:
                print("    reports字段不存在")
                print(f"   可用字段: {list(result.keys())}")
        
        return results
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_data_structure()
