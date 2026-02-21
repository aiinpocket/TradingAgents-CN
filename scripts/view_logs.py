#!/usr/bin/env python3
"""
TradingAgents 日誌查看工具
方便查看和分析應用日誌
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

def get_log_files():
    """取得所有日誌檔案"""
    logs_dir = Path("logs")
    if not logs_dir.exists():
        return []
    
    log_files = []
    for pattern in ["*.log", "*.log.*"]:
        log_files.extend(logs_dir.glob(pattern))
    
    return sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)

def show_log_files():
    """顯示所有日誌檔案"""
    log_files = get_log_files()
    
    if not log_files:
        print(" 未找到日誌檔案")
        return []
    
    print(f" 找到 {len(log_files)} 個日誌檔案:")
    print("-" * 60)
    
    for i, log_file in enumerate(log_files, 1):
        stat = log_file.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        # 格式化檔案大小
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size/1024:.1f} KB"
        else:
            size_str = f"{size/(1024*1024):.1f} MB"
        
        print(f"{i:2d}.  {log_file.name}")
        print(f"      大小: {size_str}")
        print(f"      修改時間: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    return log_files

def view_log_file(log_file, lines=50):
    """查看日誌檔案內容"""
    print(f" 查看日誌檔案: {log_file.name}")
    print("=" * 80)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        if not content:
            print(" 日誌檔案為空")
            return
        
        total_lines = len(content)
        print(f" 總行數: {total_lines:,}")
        
        if lines > 0:
            if lines >= total_lines:
                print(f" 顯示全部內容:")
                start_line = 0
            else:
                print(f" 顯示最後 {lines} 行:")
                start_line = total_lines - lines
            
            print("-" * 80)
            for i, line in enumerate(content[start_line:], start_line + 1):
                print(f"{i:6d} | {line.rstrip()}")
        else:
            print(" 顯示全部內容:")
            print("-" * 80)
            for i, line in enumerate(content, 1):
                print(f"{i:6d} | {line.rstrip()}")
        
        print("-" * 80)
        
    except Exception as e:
        print(f" 讀取檔案失敗: {e}")

def tail_log_file(log_file):
    """實時跟蹤日誌檔案"""
    print(f" 實時跟蹤日誌檔案: {log_file.name}")
    print(" 按 Ctrl+C 停止跟蹤")
    print("=" * 80)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            # 移動到檔案末尾
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] {line.rstrip()}")
                else:
                    time.sleep(0.1)
                    
    except KeyboardInterrupt:
        print("\n[STOP]停止跟蹤")
    except Exception as e:
        print(f" 跟蹤失敗: {e}")

def search_logs(keyword, log_files=None):
    """搜索日誌內容"""
    if log_files is None:
        log_files = get_log_files()
    
    if not log_files:
        print(" 未找到日誌檔案")
        return
    
    print(f" 搜索關鍵詞: '{keyword}'")
    print("=" * 80)
    
    total_matches = 0
    
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            matches = []
            for i, line in enumerate(lines, 1):
                if keyword.lower() in line.lower():
                    matches.append((i, line.rstrip()))
            
            if matches:
                print(f" {log_file.name} ({len(matches)} 個匹配)")
                print("-" * 60)
                
                for line_num, line in matches[-10:]:  # 顯示最後10個匹配
                    print(f"{line_num:6d} | {line}")
                
                if len(matches) > 10:
                    print(f"     ... 還有 {len(matches) - 10} 個匹配")
                
                print()
                total_matches += len(matches)
                
        except Exception as e:
            print(f" 搜索 {log_file.name} 失敗: {e}")
    
    print(f" 總共找到 {total_matches} 個匹配")

def main():
    """主函式"""
    print(" TradingAgents 日誌查看工具")
    print("=" * 50)
    
    while True:
        print("\n 選擇操作:")
        print("1.  顯示所有日誌檔案")
        print("2.  查看日誌檔案內容")
        print("3.  實時跟蹤日誌")
        print("4.  搜索日誌內容")
        print("5.  查看Docker日誌")
        print("0.  退出")
        
        try:
            choice = input("\n請選擇 (0-5): ").strip()
            
            if choice == "0":
                print(" 再見！")
                break
            elif choice == "1":
                show_log_files()
            elif choice == "2":
                log_files = show_log_files()
                if log_files:
                    try:
                        file_num = int(input(f"\n選擇檔案 (1-{len(log_files)}): ")) - 1
                        if 0 <= file_num < len(log_files):
                            lines = input("顯示行數 (預設50，0=全部): ").strip()
                            lines = int(lines) if lines else 50
                            view_log_file(log_files[file_num], lines)
                        else:
                            print(" 無效選擇")
                    except ValueError:
                        print(" 請輸入有效數字")
            elif choice == "3":
                log_files = show_log_files()
                if log_files:
                    try:
                        file_num = int(input(f"\n選擇檔案 (1-{len(log_files)}): ")) - 1
                        if 0 <= file_num < len(log_files):
                            tail_log_file(log_files[file_num])
                        else:
                            print(" 無效選擇")
                    except ValueError:
                        print(" 請輸入有效數字")
            elif choice == "4":
                keyword = input("輸入搜索關鍵詞: ").strip()
                if keyword:
                    search_logs(keyword)
                else:
                    print(" 請輸入關鍵詞")
            elif choice == "5":
                print(" 查看Docker容器日誌...")
                print(" 執行以下命令查看Docker日誌:")
                print("   docker-compose logs -f web")
                print("   docker logs TradingAgents-web")
            else:
                print(" 無效選擇，請重新輸入")
                
        except KeyboardInterrupt:
            print("\n 再見！")
            break
        except Exception as e:
            print(f" 發生錯誤: {e}")

if __name__ == "__main__":
    main()
