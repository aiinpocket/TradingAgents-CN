#!/usr/bin/env python3
"""
用戶活動記錄系統演示腳本
演示如何使用用戶活動記錄功能
"""

import sys
import time
from pathlib import Path
from datetime import datetime

# 添加項目路徑
sys.path.append(str(Path(__file__).parent.parent))

try:
    from web.utils.user_activity_logger import UserActivityLogger
    print("✅ 成功導入用戶活動記錄器")
except ImportError as e:
    print(f"❌ 導入失败: {e}")
    sys.exit(1)

def demo_user_activities():
    """演示用戶活動記錄功能"""
    print("🚀 用戶活動記錄系統演示")
    print("=" * 50)
    
    # 創建活動記錄器實例
    logger = UserActivityLogger()
    
    # 模擬用戶登錄
    print("\n1. 模擬用戶登錄...")
    logger.log_login(
        username="demo_user",
        success=True
    )
    time.sleep(1)
    
    # 模擬页面訪問
    print("2. 模擬页面訪問...")
    logger.log_page_visit(
        page_name="📊 股票分析",
        page_params={"access_method": "sidebar_navigation"}
    )
    time.sleep(1)
    
    # 模擬分析請求
    print("3. 模擬分析請求...")
    start_time = time.time()
    logger.log_analysis_request(
        stock_code="AAPL",
        analysis_type="美股_深度分析",
        success=True
    )
    time.sleep(2)  # 模擬分析耗時
    
    # 記錄分析完成
    duration_ms = int((time.time() - start_time) * 1000)
    logger.log_activity(
        action_type="analysis",
        action_name="analysis_completed",
        success=True,
        duration_ms=duration_ms,
        details={
            "stock_code": "AAPL",
            "result_sections": ["基本信息", "技術分析", "基本面分析", "風險評估"]
        }
    )
    
    # 模擬配置更改
    print("4. 模擬配置更改...")
    logger.log_config_change(
        config_type="model_settings",
        changes={
            "default_model": {"old": "qwen-turbo", "new": "qwen-plus"},
            "change_reason": "performance_optimization"
        }
    )
    time.sleep(1)
    
    # 模擬數據導出
    print("5. 模擬數據導出...")
    logger.log_data_export(
        export_type="analysis_results",
        data_info={
            "stock_code": "AAPL",
            "file_format": "pdf",
            "file_size_mb": 2.5,
            "export_sections": ["summary", "charts", "recommendations"]
        },
        success=True
    )
    time.sleep(1)
    
    # 模擬用戶登出
    print("6. 模擬用戶登出...")
    logger.log_logout(username="demo_user")
    
    print("\n✅ 演示完成！")
    
    # 顯示統計信息
    print("\n📊 活動統計:")
    stats = logger.get_activity_statistics(days=1)
    print(f"   总活動數: {stats['total_activities']}")
    print(f"   活躍用戶: {stats['unique_users']}")
    print(f"   成功率: {stats['success_rate']:.1f}%")
    
    print("\n📋 按類型統計:")
    for activity_type, count in stats['activity_types'].items():
        print(f"   {activity_type}: {count}")
    
    # 顯示最近的活動
    print("\n📝 最近的活動記錄:")
    recent_activities = logger.get_user_activities(limit=5)
    for i, activity in enumerate(recent_activities, 1):
        timestamp = datetime.fromtimestamp(activity['timestamp'])
        success_icon = "✅" if activity.get('success', True) else "❌"
        print(f"   {i}. {success_icon} {timestamp.strftime('%H:%M:%S')} - {activity['action_name']}")

def demo_activity_management():
    """演示活動管理功能"""
    print("\n🔧 活動管理功能演示")
    print("=" * 50)
    
    logger = UserActivityLogger()
    
    # 獲取活動統計
    print("\n📈 獲取活動統計...")
    stats = logger.get_activity_statistics(days=7)
    print(f"   過去7天总活動數: {stats['total_activities']}")
    print(f"   活躍用戶數: {stats['unique_users']}")
    print(f"   平均成功率: {stats['success_rate']:.1f}%")
    
    # 按用戶統計
    if stats['user_activities']:
        print("\n👥 用戶活動排行:")
        for username, count in list(stats['user_activities'].items())[:5]:
            print(f"   {username}: {count} 次活動")
    
    # 按日期統計
    if stats['daily_activities']:
        print("\n📅 每日活動統計:")
        for date_str, count in list(stats['daily_activities'].items())[-3:]:
            print(f"   {date_str}: {count} 次活動")
    
    print("\n✅ 管理功能演示完成！")

def main():
    """主函數"""
    print("🎯 用戶活動記錄系統完整演示")
    print("=" * 60)
    
    try:
        # 演示基本功能
        demo_user_activities()
        
        # 演示管理功能
        demo_activity_management()
        
        print("\n🎉 所有演示完成！")
        print("\n💡 提示:")
        print("   - 活動記錄已保存到 web/data/user_activities/ 目錄")
        print("   - 可以使用 scripts/user_activity_manager.py 查看和管理記錄")
        print("   - 在Web界面的'📈 歷史記錄'页面可以查看活動儀表板")
        
    except Exception as e:
        print(f"❌ 演示過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()