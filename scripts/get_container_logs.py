#!/usr/bin/env python3
"""
獲取Docker容器內部日誌文件的腳本
用於從運行中的TradingAgents容器獲取實際的日誌文件
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, capture_output=True):
    """執行命令"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def find_container():
    """查找TradingAgents容器"""
    print("🔍 查找TradingAgents容器...")
    
    # 可能的容器名稱
    possible_names = [
        "tradingagents-data-service",
        "tradingagents_data-service_1",
        "data-service",
        "tradingagents-cn-data-service-1"
    ]
    
    for name in possible_names:
        success, output, error = run_command(f"docker ps --filter name={name} --format '{{{{.Names}}}}'")
        if success and output.strip():
            print(f"✅ 找到容器: {output.strip()}")
            return output.strip()
    
    # 如果沒找到，列出所有容器讓用戶選擇
    print("⚠️ 未找到預期的容器名稱，列出所有運行中的容器:")
    success, output, error = run_command("docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'")
    if success:
        print(output)
        container_name = input("\n請輸入容器名稱: ").strip()
        if container_name:
            return container_name
    
    return None

def explore_container_filesystem(container_name):
    """探索容器文件系統，查找日誌文件"""
    print(f"🔍 探索容器 {container_name} 的文件系統...")
    
    # 檢查常見的日誌位置
    log_locations = [
        "/app",
        "/app/logs",
        "/var/log",
        "/tmp",
        "."
    ]
    
    found_logs = []
    
    for location in log_locations:
        print(f"\n📂 檢查目錄: {location}")
        
        # 列出目錄內容
        success, output, error = run_command(f"docker exec {container_name} ls -la {location}")
        if success:
            print(f"   目錄內容:")
            for line in output.split('\n'):
                if line.strip():
                    print(f"   {line}")
            
            # 查找.log文件
            success, output, error = run_command(f"docker exec {container_name} find {location} -maxdepth 2 -name '*.log' -type f 2>/dev/null")
            if success and output.strip():
                log_files = output.strip().split('\n')
                for log_file in log_files:
                    if log_file.strip():
                        found_logs.append(log_file.strip())
                        print(f"   📄 找到日誌文件: {log_file.strip()}")
    
    return found_logs

def get_log_file_info(container_name, log_file):
    """獲取日誌文件信息"""
    print(f"\n📊 日誌文件信息: {log_file}")
    
    # 文件大小和修改時間
    success, output, error = run_command(f"docker exec {container_name} ls -lh {log_file}")
    if success:
        print(f"   文件詳情: {output.strip()}")
    
    # 文件行數
    success, output, error = run_command(f"docker exec {container_name} wc -l {log_file}")
    if success:
        lines = output.strip().split()[0]
        print(f"   總行數: {lines}")
    
    # 最後修改時間
    success, output, error = run_command(f"docker exec {container_name} stat -c '%y' {log_file}")
    if success:
        print(f"   最後修改: {output.strip()}")

def preview_log_file(container_name, log_file, lines=20):
    """預覽日誌文件內容"""
    print(f"\n👀 預覽日誌文件 {log_file} (最後{lines}行):")
    print("=" * 80)
    
    success, output, error = run_command(f"docker exec {container_name} tail -{lines} {log_file}")
    if success:
        print(output)
    else:
        print(f"❌ 無法讀取日誌文件: {error}")
    
    print("=" * 80)

def copy_log_file(container_name, log_file, local_path=None):
    """複制日誌文件到本地"""
    if not local_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(log_file)
        local_path = f"{filename}_{timestamp}"
    
    print(f"\n📤 複制日誌文件到本地: {local_path}")
    
    success, output, error = run_command(f"docker cp {container_name}:{log_file} {local_path}")
    if success:
        print(f"✅ 日誌文件已複制到: {local_path}")
        
        # 檢查本地文件大小
        if os.path.exists(local_path):
            size = os.path.getsize(local_path)
            print(f"   文件大小: {size:,} 字節")
            
            # 顯示文件的最後幾行
            print(f"\n📋 文件內容預覽 (最後10行):")
            try:
                with open(local_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines[-10:]:
                        print(f"   {line.rstrip()}")
            except Exception as e:
                print(f"   ⚠️ 無法預覽文件內容: {e}")
        
        return local_path
    else:
        print(f"❌ 複制失敗: {error}")
        return None

def get_docker_logs(container_name):
    """獲取Docker標準日誌"""
    print(f"\n📋 獲取Docker標準日誌...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    docker_log_file = f"docker_logs_{timestamp}.log"
    
    success, output, error = run_command(f"docker logs {container_name}")
    if success:
        with open(docker_log_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ Docker日誌已保存到: {docker_log_file}")
        print(f"   日誌行數: {len(output.split(chr(10)))}")
        return docker_log_file
    else:
        print(f"❌ 獲取Docker日誌失敗: {error}")
        return None

def main():
    """主函數"""
    print("🚀 TradingAgents Docker容器日誌獲取工具")
    print("=" * 60)
    
    # 1. 查找容器
    container_name = find_container()
    if not container_name:
        print("❌ 未找到容器，請確保TradingAgents容器正在運行")
        return
    
    # 2. 探索文件系統
    log_files = explore_container_filesystem(container_name)
    
    # 3. 獲取Docker標準日誌
    docker_log_file = get_docker_logs(container_name)
    
    if not log_files:
        print("\n⚠️ 未在容器中找到.log文件")
        print("💡 可能的原因:")
        print("   - 日誌配置為輸出到stdout/stderr (被Docker捕獲)")
        print("   - 日誌文件在其他位置")
        print("   - 應用尚未生成日誌文件")
        
        if docker_log_file:
            print(f"\n✅ 但已獲取到Docker標準日誌: {docker_log_file}")
        return
    
    # 4. 處理找到的日誌文件
    print(f"\n📋 找到 {len(log_files)} 個日誌文件:")
    for i, log_file in enumerate(log_files, 1):
        print(f"   {i}. {log_file}")
    
    # 5. 讓用戶選擇要處理的日誌文件
    if len(log_files) == 1:
        selected_log = log_files[0]
        print(f"\n🎯 自動選擇唯一的日誌文件: {selected_log}")
    else:
        try:
            choice = input(f"\n請選擇要獲取的日誌文件 (1-{len(log_files)}, 或按Enter獲取所有): ").strip()
            if not choice:
                selected_logs = log_files
            else:
                index = int(choice) - 1
                if 0 <= index < len(log_files):
                    selected_logs = [log_files[index]]
                else:
                    print("❌ 無效選擇")
                    return
        except ValueError:
            print("❌ 無效輸入")
            return
        
        if len(selected_logs) == 1:
            selected_log = selected_logs[0]
        else:
            selected_log = None
    
    # 6. 處理選中的日誌文件
    if selected_log:
        # 單個文件處理
        get_log_file_info(container_name, selected_log)
        preview_log_file(container_name, selected_log)
        
        copy_choice = input("\n是否複制此日誌文件到本地? (y/N): ").strip().lower()
        if copy_choice in ['y', 'yes']:
            local_file = copy_log_file(container_name, selected_log)
            if local_file:
                print(f"\n🎉 日誌文件獲取完成!")
                print(f"📁 本地文件: {local_file}")
    else:
        # 多個文件處理
        print(f"\n📤 複制所有 {len(selected_logs)} 個日誌文件...")
        copied_files = []
        for log_file in selected_logs:
            local_file = copy_log_file(container_name, log_file)
            if local_file:
                copied_files.append(local_file)
        
        if copied_files:
            print(f"\n🎉 成功複制 {len(copied_files)} 個日誌文件:")
            for file in copied_files:
                print(f"   📁 {file}")
    
    print(f"\n📋 總結:")
    print(f"   容器名稱: {container_name}")
    print(f"   找到日誌文件: {len(log_files)} 個")
    if docker_log_file:
        print(f"   Docker日誌: {docker_log_file}")
    print(f"   完成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 操作被用戶中斷")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
