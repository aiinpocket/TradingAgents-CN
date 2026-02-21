#!/usr/bin/env python3
"""
測試增強的分析歷史功能
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_load_analysis_results():
    """測試加載分析結果功能"""
    try:
        from web.components.analysis_results import load_analysis_results
        
        print("🔍 測試加載分析結果...")
        
        # 測試基本加載
        results = load_analysis_results(limit=10)
        print(f"✅ 成功加載 {len(results)} 個分析結果")
        
        if results:
            # 檢查結果結構
            first_result = results[0]
            required_fields = ['analysis_id', 'timestamp', 'stock_symbol', 'status']
            
            for field in required_fields:
                if field in first_result:
                    print(f"✅ 字段 '{field}' 存在")
                else:
                    print(f"❌ 字段 '{field}' 缺失")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def test_comparison_functions():
    """測試對比功能"""
    try:
        from web.components.analysis_results import (
            calculate_text_similarity,
            get_report_content
        )
        
        print("🔍 測試對比功能...")
        
        # 測試文本相似度計算
        text1 = "這是一個測試文本"
        text2 = "這是另一個測試文本"
        similarity = calculate_text_similarity(text1, text2)
        print(f"✅ 文本相似度計算: {similarity:.2f}")
        
        # 測試報告內容獲取
        mock_result = {
            'source': 'file_system',
            'reports': {
                'final_trade_decision': '買入建議'
            }
        }
        
        content = get_report_content(mock_result, 'final_trade_decision')
        print(f"✅ 報告內容獲取: {content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def test_chart_functions():
    """測試圖表功能"""
    try:
        import pandas as pd
        from web.components.analysis_results import (
            render_comprehensive_dashboard,
            render_time_distribution_charts
        )
        
        print("🔍 測試圖表功能...")
        
        # 創建模擬數據
        mock_data = []
        for i in range(10):
            mock_data.append({
                'timestamp': datetime.now() - timedelta(days=i),
                'stock_symbol': f'00000{i % 3}',
                'status': 'completed' if i % 2 == 0 else 'failed',
                'analysts_count': 3,
                'research_depth': 5,
                'tags_count': 2,
                'summary_length': 100 + i * 10,
                'date': (datetime.now() - timedelta(days=i)).date(),
                'hour': 10 + i % 12,
                'weekday': i % 7
            })
        
        df = pd.DataFrame(mock_data)
        print(f"✅ 創建模擬數據: {len(df)} 條記錄")
        
        # 注意：這裡只是測試函數是否可以導入，實際渲染需要Streamlit環境
        print("✅ 圖表函數導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False


def create_test_data():
    """創建測試數據"""
    try:
        print("🔍 創建測試數據...")
        
        # 確保測試數據目錄存在
        test_data_dir = project_root / "data" / "analysis_results" / "detailed" / "TEST001"
        test_date_dir = test_data_dir / "2025-07-31" / "reports"
        test_date_dir.mkdir(parents=True, exist_ok=True)
        
        # 創建測試報告
        test_reports = {
            'final_trade_decision.md': '# 測試交易決策\n\n建議買入',
            'fundamentals_report.md': '# 測試基本面分析\n\n公司基本面良好',
            'market_report.md': '# 測試技術分析\n\n技術指標顯示上漲趨勢'
        }
        
        for filename, content in test_reports.items():
            report_file = test_date_dir / filename
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✅ 測試數據創建成功: {test_date_dir}")
        return True
        
    except Exception as e:
        print(f"❌ 創建測試數據失敗: {e}")
        return False


def main():
    """主測試函數"""
    print("🚀 開始測試增強的分析歷史功能")
    print("=" * 50)
    
    tests = [
        ("創建測試數據", create_test_data),
        ("加載分析結果", test_load_analysis_results),
        ("對比功能", test_comparison_functions),
        ("圖表功能", test_chart_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 測試: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通過")
        else:
            print(f"❌ {test_name} 失敗")
    
    print("\n" + "=" * 50)
    print(f"📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 所有測試通過！")
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查代碼")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
