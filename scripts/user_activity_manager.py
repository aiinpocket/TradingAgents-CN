#!/usr/bin/env python3
"""
用戶活動記錄管理工具
用於查看、分析和管理用戶操作行為記錄
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import pandas as pd

# 添加項目根目錄到路徑
sys.path.append(str(Path(__file__).parent.parent))

def get_activity_dir():
    """獲取活動記錄目錄"""
    return Path(__file__).parent.parent / "web" / "data" / "user_activities"

def load_activities(start_date: datetime = None, end_date: datetime = None) -> List[Dict[str, Any]]:
    """加載活動記錄"""
    activity_dir = get_activity_dir()
    activities = []
    
    if not activity_dir.exists():
        print("❌ 活動記錄目錄不存在")
        return activities
    
    # 確定日期範围
    if start_date is None:
        start_date = datetime.now() - timedelta(days=7)
    if end_date is None:
        end_date = datetime.now()
    
    # 遍歷日期範围內的文件
    current_date = start_date.date()
    end_date_only = end_date.date()
    
    while current_date <= end_date_only:
        date_str = current_date.strftime("%Y-%m-%d")
        activity_file = activity_dir / f"user_activities_{date_str}.jsonl"
        
        if activity_file.exists():
            try:
                with open(activity_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            activity = json.loads(line.strip())
                            activity_time = datetime.fromtimestamp(activity['timestamp'])
                            if start_date <= activity_time <= end_date:
                                activities.append(activity)
            except Exception as e:
                print(f"❌ 讀取文件失败 {activity_file}: {e}")
        
        current_date += timedelta(days=1)
    
    return sorted(activities, key=lambda x: x['timestamp'], reverse=True)

def list_activities(args):
    """列出用戶活動"""
    print("📋 用戶活動記錄")
    print("=" * 80)
    
    # 解析日期參數
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    
    activities = load_activities(start_date, end_date)
    
    if not activities:
        print("📭 未找到活動記錄")
        return
    
    # 應用過濾條件
    if args.username:
        activities = [a for a in activities if a.get('username') == args.username]
    
    if args.action_type:
        activities = [a for a in activities if a.get('action_type') == args.action_type]
    
    # 應用限制
    if args.limit:
        activities = activities[:args.limit]
    
    print(f"📊 找到 {len(activities)} 條記錄")
    print()
    
    # 顯示活動記錄
    for i, activity in enumerate(activities, 1):
        timestamp = datetime.fromtimestamp(activity['timestamp'])
        success_icon = "✅" if activity.get('success', True) else "❌"
        
        print(f"{i:3d}. {success_icon} {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"     👤 用戶: {activity.get('username', 'unknown')} ({activity.get('user_role', 'unknown')})")
        print(f"     🔧 操作: {activity.get('action_type', 'unknown')} - {activity.get('action_name', 'unknown')}")
        
        if activity.get('details'):
            details_str = ", ".join([f"{k}={v}" for k, v in activity['details'].items()])
            print(f"     📝 詳情: {details_str}")
        
        if activity.get('duration_ms'):
            print(f"     ⏱️ 耗時: {activity['duration_ms']}ms")
        
        if not activity.get('success', True) and activity.get('error_message'):
            print(f"     ❌ 錯誤: {activity['error_message']}")
        
        print()

def show_statistics(args):
    """顯示統計信息"""
    print("📊 用戶活動統計")
    print("=" * 80)
    
    # 解析日期參數
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    
    activities = load_activities(start_date, end_date)
    
    if not activities:
        print("📭 未找到活動記錄")
        return
    
    # 基本統計
    total_activities = len(activities)
    unique_users = len(set(a['username'] for a in activities))
    successful_activities = sum(1 for a in activities if a.get('success', True))
    success_rate = (successful_activities / total_activities * 100) if total_activities > 0 else 0
    
    print(f"📈 总體統計:")
    print(f"   📊 总活動數: {total_activities}")
    print(f"   👥 活躍用戶: {unique_users}")
    print(f"   ✅ 成功率: {success_rate:.1f}%")
    print()
    
    # 按活動類型統計
    activity_types = {}
    for activity in activities:
        action_type = activity.get('action_type', 'unknown')
        activity_types[action_type] = activity_types.get(action_type, 0) + 1
    
    print(f"📋 按活動類型統計:")
    for action_type, count in sorted(activity_types.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_activities * 100) if total_activities > 0 else 0
        print(f"   {action_type:15s}: {count:4d} ({percentage:5.1f}%)")
    print()
    
    # 按用戶統計
    user_activities = {}
    for activity in activities:
        username = activity.get('username', 'unknown')
        user_activities[username] = user_activities.get(username, 0) + 1
    
    print(f"👥 按用戶統計:")
    for username, count in sorted(user_activities.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_activities * 100) if total_activities > 0 else 0
        print(f"   {username:15s}: {count:4d} ({percentage:5.1f}%)")
    print()
    
    # 按日期統計
    daily_activities = {}
    for activity in activities:
        date_str = datetime.fromtimestamp(activity['timestamp']).strftime('%Y-%m-%d')
        daily_activities[date_str] = daily_activities.get(date_str, 0) + 1
    
    print(f"📅 按日期統計:")
    for date_str in sorted(daily_activities.keys()):
        count = daily_activities[date_str]
        print(f"   {date_str}: {count:4d}")
    print()
    
    # 耗時統計
    durations = [a.get('duration_ms', 0) for a in activities if a.get('duration_ms')]
    if durations:
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        print(f"⏱️ 耗時統計:")
        print(f"   平均耗時: {avg_duration:.1f}ms")
        print(f"   最大耗時: {max_duration}ms")
        print(f"   最小耗時: {min_duration}ms")
        print()

def export_activities(args):
    """導出活動記錄"""
    print("📤 導出用戶活動記錄")
    print("=" * 80)
    
    # 解析日期參數
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
    if args.end_date:
        end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
    
    activities = load_activities(start_date, end_date)
    
    if not activities:
        print("📭 未找到活動記錄")
        return
    
    # 應用過濾條件
    if args.username:
        activities = [a for a in activities if a.get('username') == args.username]
    
    if args.action_type:
        activities = [a for a in activities if a.get('action_type') == args.action_type]
    
    # 確定輸出文件
    if args.output:
        output_file = Path(args.output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"user_activities_export_{timestamp}.csv")
    
    try:
        # 轉換為DataFrame並導出
        df_data = []
        for activity in activities:
            row = {
                'timestamp': activity['timestamp'],
                'datetime': datetime.fromtimestamp(activity['timestamp']).isoformat(),
                'username': activity.get('username', ''),
                'user_role': activity.get('user_role', ''),
                'action_type': activity.get('action_type', ''),
                'action_name': activity.get('action_name', ''),
                'session_id': activity.get('session_id', ''),
                'ip_address': activity.get('ip_address', ''),
                'page_url': activity.get('page_url', ''),
                'duration_ms': activity.get('duration_ms', ''),
                'success': activity.get('success', True),
                'error_message': activity.get('error_message', ''),
                'details': json.dumps(activity.get('details', {}), ensure_ascii=False)
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"✅ 成功導出 {len(activities)} 條記錄到: {output_file}")
        
    except Exception as e:
        print(f"❌ 導出失败: {e}")

def cleanup_activities(args):
    """清理旧的活動記錄"""
    print("🗑️ 清理旧的活動記錄")
    print("=" * 80)
    
    activity_dir = get_activity_dir()
    if not activity_dir.exists():
        print("❌ 活動記錄目錄不存在")
        return
    
    days_to_keep = args.days or 90
    cutoff_date = datetime.now() - timedelta(days=days_to_keep)
    deleted_count = 0
    
    print(f"🗓️ 将刪除 {cutoff_date.strftime('%Y-%m-%d')} 之前的記錄")
    
    if not args.force:
        confirm = input("⚠️ 確認刪除吗? (y/N): ")
        if confirm.lower() != 'y':
            print("❌ 操作已取消")
            return
    
    try:
        for activity_file in activity_dir.glob("user_activities_*.jsonl"):
            try:
                # 從文件名提取日期
                date_str = activity_file.stem.replace("user_activities_", "")
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    activity_file.unlink()
                    deleted_count += 1
                    print(f"🗑️ 刪除: {activity_file.name}")
                    
            except ValueError:
                # 文件名格式不正確，跳過
                continue
                
        print(f"✅ 成功刪除 {deleted_count} 個文件")
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="用戶活動記錄管理工具")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # list 命令
    list_parser = subparsers.add_parser('list', help='列出用戶活動')
    list_parser.add_argument('--username', help='按用戶名過濾')
    list_parser.add_argument('--action-type', help='按活動類型過濾')
    list_parser.add_argument('--start-date', help='開始日期 (YYYY-MM-DD)')
    list_parser.add_argument('--end-date', help='結束日期 (YYYY-MM-DD)')
    list_parser.add_argument('--limit', type=int, help='限制返回記錄數')
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='顯示統計信息')
    stats_parser.add_argument('--start-date', help='開始日期 (YYYY-MM-DD)')
    stats_parser.add_argument('--end-date', help='結束日期 (YYYY-MM-DD)')
    
    # export 命令
    export_parser = subparsers.add_parser('export', help='導出活動記錄')
    export_parser.add_argument('--username', help='按用戶名過濾')
    export_parser.add_argument('--action-type', help='按活動類型過濾')
    export_parser.add_argument('--start-date', help='開始日期 (YYYY-MM-DD)')
    export_parser.add_argument('--end-date', help='結束日期 (YYYY-MM-DD)')
    export_parser.add_argument('--output', help='輸出文件路徑')
    
    # cleanup 命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧記錄')
    cleanup_parser.add_argument('--days', type=int, default=90, help='保留天數 (默認90天)')
    cleanup_parser.add_argument('--force', action='store_true', help='强制刪除，不詢問確認')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_activities(args)
        elif args.command == 'stats':
            show_statistics(args)
        elif args.command == 'export':
            export_activities(args)
        elif args.command == 'cleanup':
            cleanup_activities(args)
        else:
            print(f"❌ 未知命令: {args.command}")
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n⚠️ 操作被用戶中斷")
    except Exception as e:
        print(f"❌ 執行失败: {e}")

if __name__ == "__main__":
    main()