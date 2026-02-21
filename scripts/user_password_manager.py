#!/usr/bin/env python3
"""
用戶密碼管理工具
支持通過命令行修改用戶密碼、創建用戶、刪除用戶等操作
"""

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, Optional

def get_users_file_path() -> Path:
    """獲取用戶配置文件路徑"""
    # 從腳本目錄向上查找web目錄
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    users_file = project_root / "web" / "config" / "users.json"
    return users_file

def hash_password(password: str) -> str:
    """密碼哈希"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_users() -> Dict:
    """加載用戶配置"""
    users_file = get_users_file_path()
    
    if not users_file.exists():
        print(f" 用戶配置文件不存在: {users_file}")
        return {}
    
    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f" 加載用戶配置失敗: {e}")
        return {}

def save_users(users: Dict) -> bool:
    """保存用戶配置"""
    users_file = get_users_file_path()
    
    try:
        # 確保目錄存在
        users_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        
        print(f" 用戶配置已保存到: {users_file}")
        return True
    except Exception as e:
        print(f" 保存用戶配置失敗: {e}")
        return False

def list_users():
    """列出所有用戶"""
    users = load_users()
    
    if not users:
        print(" 沒有找到用戶")
        return
    
    print(" 用戶列表:")
    print("-" * 60)
    print(f"{'用戶名':<15} {'角色':<10} {'權限':<30} {'創建時間'}")
    print("-" * 60)
    
    for username, user_info in users.items():
        role = user_info.get('role', 'unknown')
        permissions = ', '.join(user_info.get('permissions', []))
        created_at = user_info.get('created_at', 0)
        created_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(created_at))
        
        print(f"{username:<15} {role:<10} {permissions:<30} {created_time}")

def change_password(username: str, new_password: str) -> bool:
    """修改用戶密碼"""
    users = load_users()
    
    if username not in users:
        print(f" 用戶不存在: {username}")
        return False
    
    # 更新密碼哈希
    users[username]['password_hash'] = hash_password(new_password)
    
    if save_users(users):
        print(f" 用戶 {username} 的密碼已成功修改")
        return True
    else:
        return False

def create_user(username: str, password: str, role: str = "user", permissions: list = None) -> bool:
    """創建新用戶"""
    users = load_users()
    
    if username in users:
        print(f" 用戶已存在: {username}")
        return False
    
    if permissions is None:
        permissions = ["analysis"] if role == "user" else ["analysis", "config", "admin"]
    
    # 創建新用戶
    users[username] = {
        "password_hash": hash_password(password),
        "role": role,
        "permissions": permissions,
        "created_at": time.time()
    }
    
    if save_users(users):
        print(f" 用戶 {username} 創建成功")
        print(f"   角色: {role}")
        print(f"   權限: {', '.join(permissions)}")
        return True
    else:
        return False

def delete_user(username: str) -> bool:
    """刪除用戶"""
    users = load_users()
    
    if username not in users:
        print(f" 用戶不存在: {username}")
        return False
    
    # 防止刪除最後一個管理員
    admin_count = sum(1 for user in users.values() if user.get('role') == 'admin')
    if users[username].get('role') == 'admin' and admin_count <= 1:
        print(f" 不能刪除最後一個管理員用戶")
        return False
    
    del users[username]
    
    if save_users(users):
        print(f" 用戶 {username} 已刪除")
        return True
    else:
        return False

def reset_to_default():
    """重置為默認用戶配置"""
    default_users = {
        "admin": {
            "password_hash": hash_password("admin123"),
            "role": "admin",
            "permissions": ["analysis", "config", "admin"],
            "created_at": time.time()
        },
        "user": {
            "password_hash": hash_password("user123"),
            "role": "user", 
            "permissions": ["analysis"],
            "created_at": time.time()
        }
    }
    
    if save_users(default_users):
        print(" 用戶配置已重置為默認設置")
        print("   默認用戶:")
        print("   - admin / admin123 (管理員)")
        print("   - user / user123 (普通用戶)")
        return True
    else:
        return False

def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="TradingAgents-CN 用戶密碼管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 列出所有用戶
  python user_password_manager.py list

  # 修改用戶密碼
  python user_password_manager.py change-password admin newpassword123

  # 創建新用戶
  python user_password_manager.py create-user newuser password123 --role user

  # 刪除用戶
  python user_password_manager.py delete-user olduser

  # 重置為默認配置
  python user_password_manager.py reset
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 列出用戶命令
    subparsers.add_parser('list', help='列出所有用戶')
    
    # 修改密碼命令
    change_parser = subparsers.add_parser('change-password', help='修改用戶密碼')
    change_parser.add_argument('username', help='用戶名')
    change_parser.add_argument('password', help='新密碼')
    
    # 創建用戶命令
    create_parser = subparsers.add_parser('create-user', help='創建新用戶')
    create_parser.add_argument('username', help='用戶名')
    create_parser.add_argument('password', help='密碼')
    create_parser.add_argument('--role', choices=['user', 'admin'], default='user', help='用戶角色')
    create_parser.add_argument('--permissions', nargs='+', help='用戶權限列表')
    
    # 刪除用戶命令
    delete_parser = subparsers.add_parser('delete-user', help='刪除用戶')
    delete_parser.add_argument('username', help='用戶名')
    
    # 重置命令
    subparsers.add_parser('reset', help='重置為默認用戶配置')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print(" TradingAgents-CN 用戶密碼管理工具")
    print("=" * 50)
    
    try:
        if args.command == 'list':
            list_users()
        
        elif args.command == 'change-password':
            change_password(args.username, args.password)
        
        elif args.command == 'create-user':
            create_user(args.username, args.password, args.role, args.permissions)
        
        elif args.command == 'delete-user':
            delete_parser = input(f"確認刪除用戶 '{args.username}'? (y/N): ")
            if delete_parser.lower() == 'y':
                delete_user(args.username)
            else:
                print(" 操作已取消")
        
        elif args.command == 'reset':
            confirm = input("確認重置為默認用戶配置? 這將刪除所有現有用戶! (y/N): ")
            if confirm.lower() == 'y':
                reset_to_default()
            else:
                print(" 操作已取消")
    
    except KeyboardInterrupt:
        print("\n 操作被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f" 發生錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()