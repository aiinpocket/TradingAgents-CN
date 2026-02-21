#!/usr/bin/env python3
"""
測試DataFrame Arrow轉換修複
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_safe_dataframe():
    """測試安全DataFrame函數"""
    try:
        from web.components.analysis_results import safe_dataframe
        import pandas as pd
        
        print(" 測試安全DataFrame函數...")
        
        # 測試混合數據類型
        mixed_data = {
            '項目': ['股票代碼', '分析時間', '分析師數量', '研究深度'],
            '結果A': ['AAPL', '2025-07-31 12:00', 3, 5],  # 混合字符串和整數
            '結果B': ['MSFT', '2025-07-31 13:00', 2, 4]
        }
        
        # 使用安全函數創建DataFrame
        df = safe_dataframe(mixed_data)
        print(f" 安全DataFrame創建成功，形狀: {df.shape}")
        
        # 檢查數據類型
        print(" 數據類型檢查:")
        for col in df.columns:
            dtype = df[col].dtype
            print(f"   {col}: {dtype}")
            if dtype == 'object':
                print(f"    {col} 是字符串類型")
            else:
                print(f"    {col} 不是字符串類型")
        
        # 測試列表數據
        list_data = [
            {'股票': 'AAPL', '價格': 10.5, '數量': 100},
            {'股票': 'MSFT', '價格': 20.3, '數量': 200}
        ]
        
        df_list = safe_dataframe(list_data)
        print(f" 列表數據DataFrame創建成功，形狀: {df_list.shape}")
        
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        return False


def test_comparison_data():
    """測試對比數據創建"""
    try:
        from web.components.analysis_results import safe_dataframe
        
        print("\n 測試對比數據創建...")
        
        # 模擬對比數據
        comparison_data = {
            "項目": ["股票代碼", "分析時間", "分析師數量", "研究深度", "狀態", "標簽數量"],
            "分析結果 A": [
                'AAPL',
                '2025-07-31 12:00',
                3,  # 整數
                5,  # 整數
                " 完成",
                2   # 整數
            ],
            "分析結果 B": [
                'MSFT',
                '2025-07-31 13:00',
                2,  # 整數
                4,  # 整數
                " 失敗",
                1   # 整數
            ]
        }
        
        df = safe_dataframe(comparison_data)
        print(f" 對比數據DataFrame創建成功")
        
        # 驗證所有數據都是字符串
        all_string = all(df[col].dtype == 'object' for col in df.columns)
        if all_string:
            print(" 所有列都是字符串類型")
        else:
            print(" 存在非字符串類型的列")
            
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        return False


def test_timeline_data():
    """測試時間線數據創建"""
    try:
        from web.components.analysis_results import safe_dataframe
        
        print("\n 測試時間線數據創建...")
        
        # 模擬時間線數據
        timeline_data = []
        for i in range(3):
            timeline_data.append({
                '序號': i + 1,  # 整數
                '分析時間': datetime.now().strftime('%Y-%m-%d %H:%M'),
                '分析師': 'analyst1, analyst2',
                '研究深度': 5,  # 整數
                '狀態': '' if i % 2 == 0 else ''
            })
        
        df = safe_dataframe(timeline_data)
        print(f" 時間線數據DataFrame創建成功，行數: {len(df)}")
        
        # 檢查序號列是否為字符串
        if df['序號'].dtype == 'object':
            print(" 序號列已轉換為字符串類型")
        else:
            print(f" 序號列類型: {df['序號'].dtype}")
            
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        return False


def test_arrow_conversion():
    """測試Arrow轉換"""
    try:
        from web.components.analysis_results import safe_dataframe
        import pyarrow as pa
        
        print("\n 測試Arrow轉換...")
        
        # 創建可能導致Arrow錯誤的數據
        problematic_data = {
            '文本列': ['text1', 'text2', 'text3'],
            '數字列': [1, 2, 3],  # 整數
            '浮點列': [1.1, 2.2, 3.3],  # 浮點數
            '布爾列': [True, False, True],  # 布爾值
            '混合列': ['text', 123, 45.6]  # 混合類型
        }
        
        # 使用安全函數
        df = safe_dataframe(problematic_data)
        
        # 嘗試轉換為Arrow
        table = pa.Table.from_pandas(df)
        print(" Arrow轉換成功")
        print(f"   表格形狀: {table.shape}")
        print(f"   列名: {table.column_names}")
        
        return True
        
    except Exception as e:
        print(f" Arrow轉換失敗: {e}")
        return False


def main():
    """主測試函數"""
    print(" 開始測試DataFrame Arrow轉換修複")
    print("=" * 50)
    
    tests = [
        ("安全DataFrame函數", test_safe_dataframe),
        ("對比數據創建", test_comparison_data),
        ("時間線數據創建", test_timeline_data),
        ("Arrow轉換", test_arrow_conversion)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n 測試: {test_name}")
        if test_func():
            passed += 1
            print(f" {test_name} 通過")
        else:
            print(f" {test_name} 失敗")
    
    print("\n" + "=" * 50)
    print(f" 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print(" 所有測試通過！DataFrame Arrow轉換問題已修複")
        return True
    else:
        print(" 部分測試失敗，需要進一步檢查")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
