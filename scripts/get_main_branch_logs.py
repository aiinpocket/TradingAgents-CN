#!/usr/bin/env python3
"""
獲取TradingAgents主分支Docker容器日誌
適用於當前main分支的單體應用架構
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(cmd, capture_output=True):
    """執行命令（不使用 shell=True，避免命令注入風險）"""
    import shlex
    try:
        args = shlex.split(cmd) if isinstance(cmd, str) else cmd
        if capture_output:
            result = subprocess.run(args, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(args)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def find_tradingagents_container():
    """查找TradingAgents Web容器"""
    print(" 查找TradingAgents Web容器...")
    
    # 根據docker-compose.yml，容器名應該是 TradingAgents-web
    container_names = [
        "TradingAgents-web",
        "tradingagents-web", 
        "tradingagents_web_1",
        "tradingagents-cn_web_1"
    ]
    
    for name in container_names:
        success, output, error = run_command(f"docker ps --filter name={name} --format '{{{{.Names}}}}'")
        if success and output.strip():
            print(f" 找到容器: {output.strip()}")
            return output.strip()
    
    # 如果沒找到，列出所有容器
    print(" 未找到預期的容器，列出所有運行中的容器:")
    success, output, error = run_command("docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'")
    if success:
        print(output)
        container_name = input("\n請輸入TradingAgents Web容器名稱: ").strip()
        if container_name:
            return container_name
    
    return None

def get_container_info(container_name):
    """獲取容器基本信息"""
    print(f"\n 容器信息: {container_name}")
    print("-" * 50)
    
    # 容器狀態
    success, output, error = run_command(f"docker inspect {container_name} --format '{{{{.State.Status}}}}'")
    if success:
        print(f"   狀態: {output.strip()}")
    
    # 容器啟動時間
    success, output, error = run_command(f"docker inspect {container_name} --format '{{{{.State.StartedAt}}}}'")
    if success:
        print(f"   啟動時間: {output.strip()}")
    
    # 容器鏡像
    success, output, error = run_command(f"docker inspect {container_name} --format '{{{{.Config.Image}}}}'")
    if success:
        print(f"   鏡像: {output.strip()}")

def explore_log_locations(container_name):
    """探索容器內的日誌位置"""
    print(f"\n 探索容器 {container_name} 的日誌位置...")
    print("-" * 50)
    
    # 檢查預期的日誌目錄
    log_locations = [
        "/app/logs",
        "/app", 
        "/app/tradingagents",
        "/tmp",
        "/var/log"
    ]
    
    found_logs = []
    
    for location in log_locations:
        print(f"\n 檢查目錄: {location}")
        
        # 檢查目錄是否存在
        success, output, error = run_command(f"docker exec {container_name} test -d {location}")
        if not success:
            print(f"    目錄不存在")
            continue
        
        # 列出目錄內容
        success, output, error = run_command(f"docker exec {container_name} ls -la {location}")
        if success:
            print(f"    目錄內容:")
            for line in output.split('\n'):
                if line.strip():
                    print(f"      {line}")
        
        # 查找日誌文件
        success, output, error = run_command([
            "docker", "exec", container_name,
            "find", location, "-maxdepth", "2", "-name", "*.log", "-type", "f"
        ])
        if success and output.strip():
            log_files = [f.strip() for f in output.strip().split('\n') if f.strip()]
            for log_file in log_files:
                found_logs.append(log_file)
                print(f"    找到日誌文件: {log_file}")
                
                # 獲取文件信息
                success2, output2, error2 = run_command(f"docker exec {container_name} ls -lh {log_file}")
                if success2:
                    print(f"      詳情: {output2.strip()}")
    
    return found_logs

def get_docker_logs(container_name):
    """獲取Docker標準日誌"""
    print(f"\n 獲取Docker標準日誌...")
    print("-" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    docker_log_file = f"tradingagents_docker_logs_{timestamp}.log"
    
    success, output, error = run_command(f"docker logs {container_name}")
    if success:
        with open(docker_log_file, 'w', encoding='utf-8') as f:
            f.write(output)
        
        # 統計信息
        lines = len(output.split('\n'))
        size = len(output.encode('utf-8'))
        
        print(f" Docker日誌已保存到: {docker_log_file}")
        print(f"    日誌行數: {lines:,}")
        print(f"    文件大小: {size:,} 字節")
        
        # 顯示最後幾行
        print(f"\n 最後10行日誌預覽:")
        print("=" * 60)
        last_lines = output.split('\n')[-11:-1]  # 最後10行
        for line in last_lines:
            if line.strip():
                print(line)
        print("=" * 60)
        
        return docker_log_file
    else:
        print(f" 獲取Docker日誌失敗: {error}")
        return None

def copy_log_files(container_name, log_files):
    """複制容器內的日誌文件"""
    if not log_files:
        print("\n 未找到容器內的日誌文件")
        return []
    
    print(f"\n 複制容器內的日誌文件...")
    print("-" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    copied_files = []
    
    for log_file in log_files:
        filename = os.path.basename(log_file)
        local_file = f"{filename}_{timestamp}"
        
        print(f" 複制: {log_file} -> {local_file}")
        
        success, output, error = run_command(f"docker cp {container_name}:{log_file} {local_file}")
        if success:
            print(f"    複制成功")
            
            # 檢查本地文件
            if os.path.exists(local_file):
                size = os.path.getsize(local_file)
                print(f"    文件大小: {size:,} 字節")
                
                # 預覽文件內容
                try:
                    with open(local_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        print(f"    文件行數: {len(lines):,}")
                        
                        if lines:
                            print(f"    最後3行預覽:")
                            for line in lines[-3:]:
                                print(f"      {line.rstrip()}")
                except Exception as e:
                    print(f"    無法預覽文件: {e}")
                
                copied_files.append(local_file)
        else:
            print(f"    複制失敗: {error}")
    
    return copied_files

def check_log_configuration(container_name):
    """檢查日誌配置"""
    print(f"\n 檢查日誌配置...")
    print("-" * 50)
    
    # 檢查環境變量
    print(" 日誌相關環境變量:")
    success, output, error = run_command([
        "docker", "exec", container_name, "sh", "-c", "env | grep -i log"
    ])
    if success and output.strip():
        for line in output.split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print("    未找到日誌相關環境變量")
    
    # 檢查Python日誌配置
    print("\n 檢查Python日誌配置:")
    python_check = '''
import os
import logging
print("Python日誌配置:")
print(f"  日誌級別: {os.getenv('TRADINGAGENTS_LOG_LEVEL', 'NOT_SET')}")
print(f"  日誌目錄: {os.getenv('TRADINGAGENTS_LOG_DIR', 'NOT_SET')}")
print(f"  當前工作目錄: {os.getcwd()}")
print(f"  日誌目錄是否存在: {os.path.exists('/app/logs')}")
if os.path.exists('/app/logs'):
    print(f"  日誌目錄內容: {os.listdir('/app/logs')}")
'''
    
    success, output, error = run_command([
        "docker", "exec", container_name, "python", "-c", python_check
    ])
    if success:
        print(output)
    else:
        print(f"    檢查失敗: {error}")

def get_recent_activity(container_name):
    """獲取最近的活動日誌"""
    print(f"\n獲取最近的活動日誌...")
    print("-" * 50)
    
    # 最近1小時的Docker日誌
    print(" 最近1小時的Docker日誌:")
    success, output, error = run_command(f"docker logs --since 1h {container_name}")
    if success:
        lines = output.split('\n')
        recent_lines = [line for line in lines if line.strip()][-20:]  # 最後20行
        
        if recent_lines:
            print("   最近20行:")
            for line in recent_lines:
                print(f"   {line}")
        else:
            print("    最近1小時無日誌輸出")
    else:
        print(f"    獲取失敗: {error}")

def main():
    """主函數"""
    print(" TradingAgents 主分支日誌獲取工具")
    print("=" * 60)
    print(f"執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 查找容器
    container_name = find_tradingagents_container()
    if not container_name:
        print(" 未找到TradingAgents容器，請確保容器正在運行")
        print("\n 啟動容器的命令:")
        print("   docker-compose up -d")
        return False
    
    # 2. 獲取容器信息
    get_container_info(container_name)
    
    # 3. 檢查日誌配置
    check_log_configuration(container_name)
    
    # 4. 探索日誌位置
    log_files = explore_log_locations(container_name)
    
    # 5. 獲取Docker標準日誌
    docker_log_file = get_docker_logs(container_name)
    
    # 6. 複制容器內日誌文件
    copied_files = copy_log_files(container_name, log_files)
    
    # 7. 獲取最近活動
    get_recent_activity(container_name)
    
    # 8. 生成總結報告
    print("\n" + "=" * 60)
    print(" 日誌獲取總結報告")
    print("=" * 60)
    
    print(f" 容器名稱: {container_name}")
    print(f" 找到容器內日誌文件: {len(log_files)} 個")
    print(f" 成功複制文件: {len(copied_files)} 個")
    
    if docker_log_file:
        print(f" Docker標準日誌: {docker_log_file}")
    
    if copied_files:
        print(f" 複制的日誌文件:")
        for file in copied_files:
            print(f"   - {file}")
    
    print(f"\n 建議:")
    if not log_files:
        print("   - 應用可能將日誌輸出到stdout，已通過Docker日誌捕獲")
        print("   - 檢查應用的日誌配置，確保寫入到文件")
        print("   - 考慮在docker-compose.yml中添加日誌目錄掛載")
    
    print("   - 將獲取到的日誌文件發送給開發者進行問題診斷")
    
    if docker_log_file:
        print(f"\n 主要發送文件: {docker_log_file}")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n 操作被用戶中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
