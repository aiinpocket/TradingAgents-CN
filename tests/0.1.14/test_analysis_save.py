#!/usr/bin/env python3
"""
測試分析結果保存功能
模擬分析完成後的保存過程
"""

import sys
import os
from datetime import datetime

# 添加項目路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

def create_mock_analysis_results():
    """創建模擬的分析結果數據"""
    return {
        'stock_symbol': 'TEST123',
        'analysis_date': '2025-07-31',
        'analysts': ['market_analyst', 'fundamentals_analyst', 'trader_agent'],
        'research_depth': 3,
        'state': {
            'market_report': """# TEST123 股票技術分析報告

##  價格趨勢分析
當前股價呈現上漲趨勢，技術指標向好。

##  技術指標
- RSI: 65.2 (偏強)
- MACD: 金叉向上
- 成交量: 放量上漲

##  操作建議
建議在回調時買入，目標價位上漲15%。
""",
            'fundamentals_report': """# TEST123 基本面分析報告

##  財務狀況
公司財務狀況良好，盈利能力強。

##  關鍵指標
- ROE: 18.5%
- PE: 15.2倍
- 淨利潤增長: 15.2%

##  投資價值
估值合理，具有投資價值。
""",
            'final_trade_decision': """# TEST123 最終交易決策

##  投資建議
**行動**: 買入
**置信度**: 85%
**目標價格**: 上漲15-20%

##  決策依據
基於技術面和基本面綜合分析，建議買入。
"""
        },
        'decision': {
            'action': 'buy',
            'confidence': 0.85,
            'target_price': 'up 15-20%',
            'reasoning': '技術面和基本面都支持買入決策'
        },
        'summary': 'TEST123股票綜合分析顯示具有良好投資潛力，建議買入。'
    }

def test_save_analysis_result():
    """測試保存分析結果"""
    print(" 測試分析結果保存功能")
    print("=" * 40)
    
    try:
        # 匯入保存函數
        from web.components.analysis_results import save_analysis_result
        
        # 創建模擬數據
        analysis_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stock_symbol = "TEST123"
        analysts = ['market_analyst', 'fundamentals_analyst', 'trader_agent']
        research_depth = 3
        result_data = create_mock_analysis_results()
        
        print(f" 測試數據:")
        print(f"   分析ID: {analysis_id}")
        print(f"   股票代碼: {stock_symbol}")
        print(f"   分析師: {analysts}")
        print(f"   研究深度: {research_depth}")
        
        # 執行保存
        print(f"\n 開始保存分析結果...")
        success = save_analysis_result(
            analysis_id=analysis_id,
            stock_symbol=stock_symbol,
            analysts=analysts,
            research_depth=research_depth,
            result_data=result_data,
            status="completed"
        )
        
        if success:
            print(" 分析結果保存成功！")
            
            # 檢查文件是否創建
            print(f"\n 檢查保存的文件:")
            
            # 檢查JSON 檔案
            from web.components.analysis_results import get_analysis_results_dir
            results_dir = get_analysis_results_dir()
            json_file = results_dir / f"analysis_{analysis_id}.json"
            
            if json_file.exists():
                print(f" JSON 檔案已創建: {json_file}")
            else:
                print(f" JSON 檔案未找到: {json_file}")
            
            # 檢查詳細報告目錄
            import os
            from pathlib import Path
            
            # 獲取項目根目錄
            project_root = Path(__file__).parent
            results_dir_env = os.getenv("TRADINGAGENTS_RESULTS_DIR", "./data/analysis_results")
            
            if not os.path.isabs(results_dir_env):
                detailed_results_dir = project_root / results_dir_env
            else:
                detailed_results_dir = Path(results_dir_env)
            
            analysis_date = datetime.now().strftime('%Y-%m-%d')
            reports_dir = detailed_results_dir / stock_symbol / analysis_date / "reports"
            
            print(f" 詳細報告目錄: {reports_dir}")
            
            if reports_dir.exists():
                print(" 詳細報告目錄已創建")
                
                # 列出報告檔案
                report_files = list(reports_dir.glob("*.md"))
                if report_files:
                    print(f" 報告檔案 ({len(report_files)} 個):")
                    for file in report_files:
                        print(f"   - {file.name}")
                else:
                    print(" 報告目錄存在但無文件")
            else:
                print(f" 詳細報告目錄未創建: {reports_dir}")
            
        else:
            print(" 分析結果保存失敗")
        
        return success
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mongodb_save():
    """測試MongoDB保存"""
    print(f"\n 測試MongoDB保存...")
    
    try:
        from web.utils.mongodb_report_manager import mongodb_report_manager
        
        if not mongodb_report_manager.connected:
            print(" MongoDB未連接")
            return False
        
        # 獲取當前記錄數
        before_count = len(mongodb_report_manager.get_analysis_reports(limit=1000))
        print(f" 保存前MongoDB記錄數: {before_count}")
        
        # 執行測試保存
        test_save_analysis_result()
        
        # 獲取保存後記錄數
        after_count = len(mongodb_report_manager.get_analysis_reports(limit=1000))
        print(f" 保存後MongoDB記錄數: {after_count}")
        
        if after_count > before_count:
            print(" MongoDB記錄增加，保存成功")
            return True
        else:
            print(" MongoDB記錄數未增加")
            return False
            
    except Exception as e:
        print(f" MongoDB測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print(" 分析結果保存功能測試")
    print("=" * 50)
    
    # 測試基本保存功能
    save_success = test_save_analysis_result()
    
    # 測試MongoDB保存
    mongodb_success = test_mongodb_save()
    
    print(f"\n 測試完成")
    print(f" 檔案保存: {' 成功' if save_success else ' 失敗'}")
    print(f" MongoDB保存: {' 成功' if mongodb_success else ' 失敗'}")

if __name__ == "__main__":
    main()
