#!/usr/bin/env python3
"""
構建包含PDF支持的Docker鏡像
"""

import subprocess
import sys
import time
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')


def run_command(command, description, timeout=300):
    """運行命令並顯示進度"""
    logger.info(f"\n🔄 {description}...")
    logger.info(f"命令: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description}成功")
            if result.stdout.strip():
                logger.info(f"輸出: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"❌ {description}失敗")
            logger.error(f"錯誤: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ {description}超時")
        return False
    except Exception as e:
        logger.error(f"❌ {description}異常: {e}")
        return False

def check_dockerfile():
    """檢查Dockerfile是否包含PDF依賴"""
    logger.debug(f"🔍 檢查Dockerfile配置...")
    
    dockerfile_path = Path("Dockerfile")
    if not dockerfile_path.exists():
        logger.error(f"❌ Dockerfile不存在")
        return False
    
    content = dockerfile_path.read_text()
    
    required_packages = [
        'wkhtmltopdf',
        'xvfb',
        'fonts-wqy-zenhei',
        'pandoc'
    ]
    
    missing_packages = []
    for package in required_packages:
        if package not in content:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"⚠️ Dockerfile缺少PDF依賴: {', '.join(missing_packages)}")
        logger.info(f"請確保Dockerfile包含以下包:")
        for package in required_packages:
            logger.info(f"  - {package}")
        return False
    
    logger.info(f"✅ Dockerfile包含所有PDF依賴")
    return True

def build_docker_image():
    """構建Docker鏡像"""
    return run_command(
        "docker build -t tradingagents-cn:latest .",
        "構建Docker鏡像",
        timeout=600  # 10分鐘超時
    )

def test_docker_container():
    """測試Docker容器"""
    logger.info(f"\n🧪 測試Docker容器...")
    
    # 啟動容器進行測試
    start_cmd = """docker run -d --name tradingagents-test \
        -e DOCKER_CONTAINER=true \
        -e DISPLAY=:99 \
        tradingagents-cn:latest \
        python scripts/test_docker_pdf.py"""
    
    if not run_command(start_cmd, "啟動測試容器", timeout=60):
        return False
    
    # 等待容器啟動
    time.sleep(5)
    
    # 獲取測試結果
    logs_cmd = "docker logs tradingagents-test"
    result = run_command(logs_cmd, "獲取測試日誌", timeout=30)
    
    # 清理測試容器
    cleanup_cmd = "docker rm -f tradingagents-test"
    run_command(cleanup_cmd, "清理測試容器", timeout=30)
    
    return result

def main():
    """主函數"""
    logger.info(f"🐳 構建包含PDF支持的Docker鏡像")
    logger.info(f"=")
    
    # 檢查當前目錄
    if not Path("Dockerfile").exists():
        logger.error(f"❌ 請在項目根目錄運行此腳本")
        return False
    
    steps = [
        ("檢查Dockerfile配置", check_dockerfile),
        ("構建Docker鏡像", build_docker_image),
        ("測試Docker容器", test_docker_container),
    ]
    
    for step_name, step_func in steps:
        logger.info(f"\n{'='*20} {step_name} {'='*20}")
        
        if not step_func():
            logger.error(f"\n❌ {step_name}失敗，構建中止")
            return False
    
    logger.info(f"\n")
    logger.info(f"🎉 Docker鏡像構建完成！")
    logger.info(f"=")
    
    logger.info(f"\n📋 使用說明:")
    logger.info(f"1. 啟動完整服務:")
    logger.info(f"   docker-compose up -d")
    logger.info(f"\n2. 僅啟動Web服務:")
    logger.info(f"   docker run -p 8501:8501 tradingagents-cn:latest")
    logger.info(f"\n3. 測試PDF功能:")
    logger.info(f"   docker run tradingagents-cn:latest python scripts/test_docker_pdf.py")
    
    logger.info(f"\n💡 提示:")
    logger.info(f"- PDF導出功能已在Docker環境中優化")
    logger.info(f"- 支持中文字體和虛擬顯示器")
    logger.info(f"- 如遇問題請查看容器日誌")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
