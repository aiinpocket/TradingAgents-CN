#!/usr/bin/env python3
"""
配置pip源為國內鏡像
提高包安裝速度
"""

import os
import sys
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def configure_pip_source():
    """配置pip源"""
    logger.info(f"🔧 配置pip源為國內鏡像")
    logger.info(f"=")
    
    # 獲取pip配置目錄
    if sys.platform == "win32":
        # Windows
        pip_config_dir = Path.home() / "pip"
        config_file = pip_config_dir / "pip.ini"
    else:
        # Linux/macOS
        pip_config_dir = Path.home() / ".pip"
        config_file = pip_config_dir / "pip.conf"
    
    logger.info(f"📁 pip配置目錄: {pip_config_dir}")
    logger.info(f"📄 配置文件: {config_file}")
    
    # 創建配置目錄
    pip_config_dir.mkdir(exist_ok=True)
    logger.info(f"✅ 配置目錄已創建")
    
    # 可選的鏡像源
    mirrors = {
        "清華大學": {
            "url": "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "trusted_host": "pypi.tuna.tsinghua.edu.cn"
        },
        "阿里云": {
            "url": "https://mirrors.aliyun.com/pypi/simple/",
            "trusted_host": "mirrors.aliyun.com"
        },
        "中科大": {
            "url": "https://pypi.mirrors.ustc.edu.cn/simple/",
            "trusted_host": "pypi.mirrors.ustc.edu.cn"
        },
        "豆瓣": {
            "url": "https://pypi.douban.com/simple/",
            "trusted_host": "pypi.douban.com"
        },
        "華為云": {
            "url": "https://mirrors.huaweicloud.com/repository/pypi/simple/",
            "trusted_host": "mirrors.huaweicloud.com"
        }
    }
    
    logger.info(f"\n📋 可用的鏡像源:")
    for i, (name, info) in enumerate(mirrors.items(), 1):
        logger.info(f"  {i}. {name}: {info['url']}")
    
    # 默認選擇清華大學鏡像（通常最快最穩定）
    selected_mirror = mirrors["清華大學"]
    logger.info(f"\n✅ 自動選擇: 清華大學鏡像")
    logger.info(f"   URL: {selected_mirror['url']}")
    
    # 生成配置內容
    if sys.platform == "win32":
        # Windows pip.ini格式
        config_content = f"""[global]
index-url = {selected_mirror['url']}
trusted-host = {selected_mirror['trusted_host']}
timeout = 120

[install]
trusted-host = {selected_mirror['trusted_host']}
"""
    else:
        # Linux/macOS pip.conf格式
        config_content = f"""[global]
index-url = {selected_mirror['url']}
trusted-host = {selected_mirror['trusted_host']}
timeout = 120

[install]
trusted-host = {selected_mirror['trusted_host']}
"""
    
    # 寫入配置文件
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        logger.info(f"✅ pip配置已保存到: {config_file}")
    except Exception as e:
        logger.error(f"❌ 配置保存失败: {e}")
        return False
    
    # 測試配置
    logger.info(f"\n🧪 測試pip配置...")
    try:
        import subprocess
        
        # 測試pip源
        result = subprocess.run([
            sys.executable, "-m", "pip", "config", "list"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logger.info(f"✅ pip配置測試成功")
            logger.info(f"📊 當前配置:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
        else:
            logger.error(f"⚠️ pip配置測試失败: {result.stderr}")
    
    except Exception as e:
        logger.warning(f"⚠️ 無法測試pip配置: {e}")
    
    # 生成使用說明
    logger.info(f"\n📋 使用說明:")
    logger.info(f"1. 配置已永久生效，以後安裝包會自動使用國內鏡像")
    logger.info(f"2. 如需臨時使用其他源，可以使用:")
    logger.info(f"   pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ package_name")
    logger.info(f"3. 如需恢複默認源，刪除配置文件:")
    logger.info(f"   del {config_file}")
    
    return True

def install_database_packages():
    """安裝數據庫相關包"""
    logger.info(f"\n📦 安裝數據庫相關包...")
    
    packages = ["pymongo", "redis"]
    
    for package in packages:
        logger.info(f"\n📥 安裝 {package}...")
        try:
            import subprocess
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", package
            ], capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                logger.info(f"✅ {package} 安裝成功")
            else:
                logger.error(f"❌ {package} 安裝失败:")
                print(result.stderr)
        
        except subprocess.TimeoutExpired:
            logger.info(f"⏰ {package} 安裝超時")
        except Exception as e:
            logger.error(f"❌ {package} 安裝異常: {e}")

def create_pip_upgrade_script():
    """創建pip升級腳本"""
    logger.info(f"\n📝 創建pip管理腳本...")
    
    project_root = Path(__file__).parent.parent.parent
    script_content = """@echo off
REM pip管理腳本 - 使用國內鏡像

echo 🔧 pip管理工具
echo ================

echo.
echo 1. 升級pip
python -m pip install --upgrade pip

echo.
echo 2. 安裝常用包
python -m pip install pymongo redis pandas requests

echo.
echo 3. 顯示已安裝包
python -m pip list

echo.
echo 4. 檢查pip配置
python -m pip config list

echo.
echo ✅ 完成!
pause
"""
    
    script_file = project_root / "scripts" / "setup" / "pip_manager.bat"
    try:
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        logger.info(f"✅ pip管理腳本已創建: {script_file}")
    except Exception as e:
        logger.error(f"⚠️ 腳本創建失败: {e}")

def main():
    """主函數"""
    try:
        # 配置pip源
        success = configure_pip_source()
        
        if success:
            # 安裝數據庫包
            install_database_packages()
            
            # 創建管理腳本
            create_pip_upgrade_script()
            
            logger.info(f"\n🎉 pip源配置完成!")
            logger.info(f"\n💡 建议:")
            logger.info(f"1. 重新運行系統初始化: python scripts/setup/initialize_system.py")
            logger.info(f"2. 檢查系統狀態: python scripts/validation/check_system_status.py")
            logger.info(f"3. 使用pip管理腳本: scripts/setup/pip_manager.bat")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 配置失败: {e}")
        import traceback

        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
