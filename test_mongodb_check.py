#!/usr/bin/env python3
"""
檢查MongoDB中的分析記錄
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 導入MongoDB報告管理器
try:
    from web.utils.mongodb_report_manager import mongodb_report_manager
    print(f"✅ MongoDB報告管理器導入成功")
except ImportError as e:
    print(f"❌ MongoDB報告管理器導入失敗: {e}")
    sys.exit(1)

def check_mongodb_connection():
    """檢查MongoDB連接狀態"""
    print(f"\n🔍 檢查MongoDB連接狀態...")
    print(f"連接狀態: {mongodb_report_manager.connected}")
    
    if not mongodb_report_manager.connected:
        print(f"❌ MongoDB未連接")
        return False
    
    print(f"✅ MongoDB連接正常")
    return True

def check_analysis_records():
    """檢查分析記錄"""
    print(f"\n📊 檢查分析記錄...")
    
    try:
        # 獲取所有記錄
        all_reports = mongodb_report_manager.get_all_reports(limit=50)
        print(f"總記錄數: {len(all_reports)}")
        
        if not all_reports:
            print(f"⚠️ MongoDB中沒有分析記錄")
            return
        
        # 顯示最近的記錄
        print(f"\n📋 最近的分析記錄:")
        for i, report in enumerate(all_reports[:5]):
            print(f"\n記錄 {i+1}:")
            print(f"  分析ID: {report.get('analysis_id', 'N/A')}")
            print(f"  股票代碼: {report.get('stock_symbol', 'N/A')}")
            print(f"  分析日期: {report.get('analysis_date', 'N/A')}")
            print(f"  狀態: {report.get('status', 'N/A')}")
            print(f"  分析師: {report.get('analysts', [])}")
            print(f"  研究深度: {report.get('research_depth', 'N/A')}")
            
            # 檢查報告內容
            reports = report.get('reports', {})
            print(f"  報告模塊數量: {len(reports)}")
            
            if reports:
                print(f"  報告模塊:")
                for module_name, content in reports.items():
                    content_length = len(content) if isinstance(content, str) else 0
                    print(f"    - {module_name}: {content_length} 字符")
                    
                    # 檢查內容是否為空或只是占位符
                    if content_length == 0:
                        print(f"      ⚠️ 內容為空")
                    elif isinstance(content, str) and ("暫無詳細分析" in content or "演示數據" in content):
                        print(f"      ⚠️ 內容為演示數據或占位符")
                    else:
                        print(f"      ✅ 內容正常")
            else:
                print(f"  ⚠️ 沒有報告內容")
                
    except Exception as e:
        print(f"❌ 檢查分析記錄失敗: {e}")
        import traceback
        print(f"詳細錯誤: {traceback.format_exc()}")

def check_specific_stock(stock_symbol="000001"):
    """檢查特定股票的記錄"""
    print(f"\n🔍 檢查股票 {stock_symbol} 的記錄...")
    
    try:
        reports = mongodb_report_manager.get_analysis_reports(
            limit=10, 
            stock_symbol=stock_symbol
        )
        
        print(f"股票 {stock_symbol} 的記錄數: {len(reports)}")
        
        if reports:
            latest_report = reports[0]
            print(f"\n最新記錄詳情:")
            print(f"  分析ID: {latest_report.get('analysis_id')}")
            print(f"  時間戳: {latest_report.get('timestamp')}")
            print(f"  狀態: {latest_report.get('status')}")
            
            reports_content = latest_report.get('reports', {})
            if reports_content:
                print(f"\n報告內容詳情:")
                for module_name, content in reports_content.items():
                    if isinstance(content, str):
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"\n{module_name}:")
                        print(f"  長度: {len(content)} 字符")
                        print(f"  預覽: {preview}")
        else:
            print(f"⚠️ 沒有找到股票 {stock_symbol} 的記錄")
            
    except Exception as e:
        print(f"❌ 檢查特定股票記錄失敗: {e}")

def main():
    print(f"🔍 MongoDB分析記錄檢查工具")
    print(f"=" * 50)
    
    # 檢查連接
    if not check_mongodb_connection():
        return
    
    # 檢查所有記錄
    check_analysis_records()
    
    # 檢查特定股票
    check_specific_stock("000001")
    
    print(f"\n🎉 檢查完成")

if __name__ == "__main__":
    main()