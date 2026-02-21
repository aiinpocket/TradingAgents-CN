#!/usr/bin/env python3
"""
驗證Docker環境下的日誌功能
"""

import os
import subprocess
import time
from pathlib import Path

def run_command(cmd):
    """運行命令並返回結果（不使用 shell=True，避免命令注入風險）"""
    import shlex
    try:
        args = shlex.split(cmd) if isinstance(cmd, str) else cmd
        result = subprocess.run(args, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_container_status():
    """檢查容器狀態"""
    print(" 檢查容器狀態...")
    
    success, output, error = run_command("docker-compose ps")
    if success:
        print(" 容器狀態:")
        print(output)
        
        # 檢查web容器是否運行
        if "TradingAgents-web" in output and "Up" in output:
            return True
        else:
            print(" TradingAgents-web容器未正常運行")
            return False
    else:
        print(f" 無法獲取容器狀態: {error}")
        return False

def trigger_logs_in_container():
    """在容器內觸發日誌生成"""
    print("\n 在容器內觸發日誌生成...")
    
    # 測試命令
    test_cmd = '''python -c "
import os
import sys
sys.path.insert(0, '/app')

# 設置環境變量
os.environ['DOCKER_CONTAINER'] = 'true'
os.environ['TRADINGAGENTS_LOG_DIR'] = '/app/logs'

try:
    from tradingagents.utils.logging_init import init_logging, get_logger
    
    print(' 初始化日誌系統...')
    init_logging()
    
    print(' 獲取日誌器...')
    logger = get_logger('docker_test')
    
    print(' 寫入測試日誌...')
    logger.info(' Docker環境日誌測試 - INFO級別')
    logger.warning(' Docker環境日誌測試 - WARNING級別')
    logger.error(' Docker環境日誌測試 - ERROR級別')
    
    print(' 日誌寫入完成')
    
    # 檢查日誌檔案
    import glob
    log_files = glob.glob('/app/logs/*.log*')
    print(f' 找到日誌檔案: {len(log_files)} 個')
    for log_file in log_files:
        size = os.path.getsize(log_file)
        print(f'    {log_file}: {size} 字節')
        
except Exception as e:
    print(f' 日誌測試失敗: {e}')
    import traceback
    traceback.print_exc()
"'''
    
    success, output, error = run_command([
        "docker", "exec", "TradingAgents-web", "python", "-c", test_cmd
    ])

    if success:
        print(" 容器內日誌測試:")
        print(output)
        return True
    else:
        print(f" 容器內日誌測試失敗:")
        print(f"錯誤: {error}")
        return False

def check_local_logs():
    """檢查本地日誌檔案"""
    print("\n 檢查本地日誌檔案...")
    
    logs_dir = Path("logs")
    if not logs_dir.exists():
        print(" logs目錄不存在")
        return False
    
    log_files = list(logs_dir.glob("*.log*"))
    
    if not log_files:
        print(" 未找到日誌檔案")
        return False
    
    print(f" 找到 {len(log_files)} 個日誌檔案:")
    
    for log_file in log_files:
        stat = log_file.stat()
        size = stat.st_size
        mtime = stat.st_mtime
        
        print(f"    {log_file.name}")
        print(f"      大小: {size:,} 字節")
        print(f"      修改時間: {time.ctime(mtime)}")
        
        # 顯示最後幾行內容
        if size > 0:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"      最後3行:")
                        for line in lines[-3:]:
                            print(f"        {line.rstrip()}")
            except Exception as e:
                print(f"       無法讀取文件: {e}")
        print()
    
    return True

def check_container_logs():
    """檢查容器內日誌檔案"""
    print("\n 檢查容器內日誌檔案...")
    
    success, output, error = run_command("docker exec TradingAgents-web ls -la /app/logs/")
    
    if success:
        print(" 容器內日誌目錄:")
        print(output)
        
        # 檢查具體的日誌檔案
        success2, output2, error2 = run_command([
            "docker", "exec", "TradingAgents-web",
            "find", "/app/logs", "-name", "*.log*", "-type", "f"
        ])
        if success2 and output2.strip():
            print(" 容器內日誌檔案:")
            for log_file in output2.strip().split('\n'):
                if log_file.strip():
                    print(f"   {log_file}")
                    
                    # 獲取檔案大小
                    success3, output3, error3 = run_command(f"docker exec TradingAgents-web wc -c {log_file}")
                    if success3:
                        size = output3.strip().split()[0]
                        print(f"      大小: {size} 字節")
        else:
            print(" 容器內未找到日誌檔案")
        
        return True
    else:
        print(f" 無法訪問容器內日誌目錄: {error}")
        return False

def check_docker_stdout_logs():
    """檢查Docker標準輸出日誌"""
    print("\n 檢查Docker標準輸出日誌...")
    
    success, output, error = run_command("docker logs --tail 20 TradingAgents-web")
    
    if success:
        print(" Docker標準輸出日誌 (最後20行):")
        print("-" * 60)
        print(output)
        print("-" * 60)
        return True
    else:
        print(f" 無法獲取Docker日誌: {error}")
        return False

def main():
    """主函數"""
    print(" Docker日誌功能驗證")
    print("=" * 60)
    
    results = []
    
    # 1. 檢查容器狀態
    results.append(("容器狀態", check_container_status()))
    
    # 2. 觸發日誌生成
    results.append(("日誌生成", trigger_logs_in_container()))
    
    # 等待一下讓日誌寫入
    print("\n 等待日誌寫入...")
    time.sleep(3)
    
    # 3. 檢查本地日誌
    results.append(("本地日誌", check_local_logs()))
    
    # 4. 檢查容器內日誌
    results.append(("容器內日誌", check_container_logs()))
    
    # 5. 檢查Docker標準日誌
    results.append(("Docker標準日誌", check_docker_stdout_logs()))
    
    # 總結結果
    print("\n" + "=" * 60)
    print(" 驗證結果總結")
    print("=" * 60)
    
    passed = 0
    for check_name, result in results:
        status = " 通過" if result else " 失敗"
        print(f"{check_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n 總體結果: {passed}/{len(results)} 項檢查通過")
    
    if passed == len(results):
        print("\n 所有檢查都通過！日誌功能正常")
        print("\n 現在可以:")
        print("   - 查看實時日誌: tail -f logs/tradingagents.log")
        print("   - 查看Docker日誌: docker-compose logs -f web")
        print("   - 使用日誌工具: python view_logs.py")
    elif passed >= len(results) * 0.6:
        print("\n 大部分功能正常")
        print(" 部分功能需要進一步檢查")
    else:
        print("\n 多項檢查失敗，需要進一步排查")
        print("\n 建議:")
        print("   1. 重新構建鏡像: docker-compose build")
        print("   2. 重啟容器: docker-compose down && docker-compose up -d")
        print("   3. 檢查配置: cat config/logging_docker.toml")
    
    return passed >= len(results) * 0.8

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
