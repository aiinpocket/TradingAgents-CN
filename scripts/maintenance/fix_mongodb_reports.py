#!/usr/bin/env python3
"""
修復MongoDB中不一致的分析報告資料結構

這個指令碼用於修復MongoDB中保存的分析報告資料結構不一致的問題。
主要解決以下問題：
1. 缺少reports欄位的檔案
2. reports欄位為空或None的檔案
3. 欄位結構不標準的檔案

使用方法：
python scripts/maintenance/fix_mongodb_reports.py
"""

import sys
import os
from pathlib import Path

# 新增專案根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
from datetime import datetime
from typing import Dict, List, Any

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """主函式"""
    print(" MongoDB分析報告資料修復工具")
    print("=" * 50)
    
    try:
        # 匯入MongoDB管理器
        from web.utils.mongodb_report_manager import MongoDBReportManager
        
        # 建立MongoDB管理器實例
        mongodb_manager = MongoDBReportManager()
        
        if not mongodb_manager.connected:
            print(" MongoDB未連接，無法執行修復")
            return False
        
        print(f" MongoDB連接成功")
        
        # 1. 檢查當前資料狀態
        print(f"\n 檢查當前資料狀態...")
        all_reports = mongodb_manager.get_all_reports(limit=1000)
        print(f" 總報告數量: {len(all_reports)}")
        
        # 統計不一致的報告
        inconsistent_count = 0
        missing_reports_count = 0
        empty_reports_count = 0
        
        for report in all_reports:
            if 'reports' not in report:
                inconsistent_count += 1
                missing_reports_count += 1
            elif not report.get('reports') or report.get('reports') == {}:
                inconsistent_count += 1
                empty_reports_count += 1
        
        print(f" 不一致報告數量: {inconsistent_count}")
        print(f"   - 缺少reports欄位: {missing_reports_count}")
        print(f"   - reports欄位為空: {empty_reports_count}")
        
        if inconsistent_count == 0:
            print(" 所有報告資料結構一致，無需修復")
            return True
        
        # 2. 詢問使用者是否繼續修復
        print(f"\n 準備修復 {inconsistent_count} 個不一致的報告")
        response = input("是否繼續修復？(y/N): ").strip().lower()
        
        if response not in ['y', 'yes']:
            print(" 使用者取消修復操作")
            return False
        
        # 3. 執行修復
        print(f"\n 開始修復不一致的報告...")
        success = mongodb_manager.fix_inconsistent_reports()
        
        if success:
            print(" 修復完成")
            
            # 4. 驗證修復結果
            print(f"\n 驗證修復結果...")
            updated_reports = mongodb_manager.get_all_reports(limit=1000)
            
            # 重新統計
            final_inconsistent_count = 0
            for report in updated_reports:
                if 'reports' not in report or not isinstance(report.get('reports'), dict):
                    final_inconsistent_count += 1
            
            print(f" 修復後不一致報告數量: {final_inconsistent_count}")
            
            if final_inconsistent_count == 0:
                print(" 所有報告資料結構已修復完成！")
                return True
            else:
                print(f" 仍有 {final_inconsistent_count} 個報告需要手動處理")
                return False
        else:
            print(" 修復失敗")
            return False
            
    except ImportError as e:
        print(f" 匯入錯誤: {e}")
        print("請確保MongoDB相關依賴已安裝")
        return False
    except Exception as e:
        print(f" 修復過程出錯: {e}")
        logger.error(f"修復異常: {e}")
        return False

def show_report_details():
    """顯示報告詳細資訊（除錯用）"""
    try:
        from web.utils.mongodb_report_manager import MongoDBReportManager
        
        mongodb_manager = MongoDBReportManager()
        if not mongodb_manager.connected:
            print(" MongoDB未連接")
            return
        
        reports = mongodb_manager.get_all_reports(limit=10)
        
        print(f"\n 最近10個報告的詳細資訊:")
        print("=" * 80)
        
        for i, report in enumerate(reports, 1):
            print(f"\n{i}. 報告ID: {report.get('analysis_id', 'N/A')}")
            print(f"   股票代碼: {report.get('stock_symbol', 'N/A')}")
            print(f"   時間戳: {report.get('timestamp', 'N/A')}")
            print(f"   分析師: {report.get('analysts', [])}")
            print(f"   研究深度: {report.get('research_depth', 'N/A')}")
            print(f"   狀態: {report.get('status', 'N/A')}")
            print(f"   來源: {report.get('source', 'N/A')}")
            
            # 檢查reports欄位
            reports_field = report.get('reports')
            if reports_field is None:
                print(f"   Reports欄位:  缺失")
            elif isinstance(reports_field, dict):
                if reports_field:
                    print(f"   Reports欄位:  存在 ({len(reports_field)} 個報告)")
                    for report_type in reports_field.keys():
                        print(f"     - {report_type}")
                else:
                    print(f"   Reports欄位:  空字典")
            else:
                print(f"   Reports欄位:  類型錯誤 ({type(reports_field)})")
            
            print("-" * 60)
            
    except Exception as e:
        print(f" 顯示報告詳情失敗: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="修復MongoDB分析報告資料結構")
    parser.add_argument("--details", action="store_true", help="顯示報告詳細資訊")
    parser.add_argument("--fix", action="store_true", help="執行修復操作")
    
    args = parser.parse_args()
    
    if args.details:
        show_report_details()
    elif args.fix:
        success = main()
        sys.exit(0 if success else 1)
    else:
        # 預設執行修復
        success = main()
        sys.exit(0 if success else 1)
