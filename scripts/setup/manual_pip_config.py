#!/usr/bin/env python3
"""
手動創建pip配置文件
適用於老版本pip不支持config命令的情况
"""

import os
import sys
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def create_pip_config():
    """手動創建pip配置文件"""
    logger.info(f"🔧 手動創建pip配置文件")
    logger.info(f"=")
    
    # 檢查pip版本
    try:
        import subprocess
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"📦 當前pip版本: {result.stdout.strip()}")
        else:
            logger.warning(f"⚠️ 無法獲取pip版本")
    except Exception as e:
        logger.error(f"⚠️ 檢查pip版本失败: {e}")
    
    # 確定配置文件路徑
    if sys.platform == "win32":
        # Windows: %APPDATA%\pip\pip.ini
        config_dir = Path(os.environ.get('APPDATA', '')) / "pip"
        config_file = config_dir / "pip.ini"
    else:
        # Linux/macOS: ~/.pip/pip.conf
        config_dir = Path.home() / ".pip"
        config_file = config_dir / "pip.conf"
    
    logger.info(f"📁 配置目錄: {config_dir}")
    logger.info(f"📄 配置文件: {config_file}")
    
    # 創建配置目錄
    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ 配置目錄已創建")
    except Exception as e:
        logger.error(f"❌ 創建配置目錄失败: {e}")
        return False
    
    # 配置內容
    config_content = """[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple/
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 120

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
"""
    
    # 寫入配置文件
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config_content)
        logger.info(f"✅ pip配置文件已創建")
        logger.info(f"📄 配置文件位置: {config_file}")
    except Exception as e:
        logger.error(f"❌ 創建配置文件失败: {e}")
        return False
    
    # 顯示配置內容
    logger.info(f"\n📊 配置內容:")
    print(config_content)
    
    # 測試配置
    logger.info(f"🧪 測試pip配置...")
    try:
        # 嘗試使用新配置安裝一個小包進行測試
        import subprocess
        
        # 先檢查是否已安裝
        result = subprocess.run([sys.executable, "-m", "pip", "show", "six"], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            # 如果没安裝，嘗試安裝six包測試
            logger.info(f"📦 測試安裝six包...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "six"], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"✅ 配置測試成功，可以正常安裝包")
            else:
                logger.error(f"❌ 配置測試失败")
                logger.error(f"錯誤信息: {result.stderr}")
        else:
            logger.info(f"✅ pip配置正常（six包已安裝）")
    
    except subprocess.TimeoutExpired:
        logger.info(f"⏰ 測試超時，但配置文件已創建")
    except Exception as e:
        logger.warning(f"⚠️ 無法測試配置: {e}")
    
    return True

def install_packages():
    """安裝必要的包"""
    logger.info(f"\n📦 安裝必要的包...")
    
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
                
                # 如果失败，嘗試使用臨時鏡像
                logger.info(f"🔄 嘗試使用臨時鏡像安裝 {package}...")
                result2 = subprocess.run([
                    sys.executable, "-m", "pip", "install", 
                    "-i", "https://pypi.tuna.tsinghua.edu.cn/simple/",
                    "--trusted-host", "pypi.tuna.tsinghua.edu.cn",
                    package
                ], capture_output=True, text=True, timeout=120)
                
                if result2.returncode == 0:
                    logger.info(f"✅ {package} 使用臨時鏡像安裝成功")
                else:
                    logger.error(f"❌ {package} 仍然安裝失败")
        
        except subprocess.TimeoutExpired:
            logger.info(f"⏰ {package} 安裝超時")
        except Exception as e:
            logger.error(f"❌ {package} 安裝異常: {e}")

def upgrade_pip():
    """升級pip到最新版本"""
    logger.info(f"\n🔄 升級pip (重要！避免安裝錯誤)...")
    
    try:
        import subprocess
        
        # 使用清華鏡像升級pip
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "pip",
            "-i", "https://pypi.tuna.tsinghua.edu.cn/simple/",
            "--trusted-host", "pypi.tuna.tsinghua.edu.cn"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            logger.info(f"✅ pip升級成功")
            
            # 顯示新版本
            version_result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                                          capture_output=True, text=True)
            if version_result.returncode == 0:
                logger.info(f"📦 新版本: {version_result.stdout.strip()}")
        else:
            logger.error(f"❌ pip升級失败:")
            logger.error(f"錯誤信息: {result.stderr}")
            
            # 嘗試不使用鏡像升級
            logger.info(f"🔄 嘗試使用官方源升級...")
            result2 = subprocess.run([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], capture_output=True, text=True, timeout=120)
            
            if result2.returncode == 0:
                logger.info(f"✅ pip使用官方源升級成功")
            else:
                logger.error(f"❌ pip升級仍然失败")
    
    except subprocess.TimeoutExpired:
        logger.warning(f"⏰ pip升級超時")
    except Exception as e:
        logger.error(f"❌ pip升級異常: {e}")

def check_pip_version():
    """檢查並建议升級pip"""
    logger.debug(f"\n🔍 檢查pip版本...")
    
    try:
        import subprocess
        
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            version_info = result.stdout.strip()
            logger.info(f"📦 當前版本: {version_info}")
            
            # 提取版本號
            import re
            version_match = re.search(r'pip (\d+)\.(\d+)', version_info)
            if version_match:
                major, minor = int(version_match.group(1)), int(version_match.group(2))
                
                if major < 10:
                    logger.warning(f"⚠️ pip版本較老，建议升級")
                    logger.info(f"💡 升級命令:")
                    logger.info(f"   python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple/ --trusted-host pypi.tuna.tsinghua.edu.cn")
                else:
                    logger.info(f"✅ pip版本較新，支持config命令")
                    logger.info(f"💡 可以使用以下命令配置:")
                    logger.info(f"   pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/")
                    logger.info(f"   pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn")
    
    except Exception as e:
        logger.error(f"❌ 檢查pip版本失败: {e}")

def main():
    """主函數"""
    try:
        # 檢查pip版本
        check_pip_version()
        
        # 升級pip
        upgrade_pip()
        
        # 創建配置文件
        success = create_pip_config()
        
        if success:
            # 安裝包
            install_packages()
            
            logger.info(f"\n🎉 pip源配置完成!")
            logger.info(f"\n💡 使用說明:")
            logger.info(f"1. 配置文件已創建，以後安裝包會自動使用清華鏡像")
            logger.info(f"2. 如果仍然很慢，可以臨時使用:")
            logger.info(f"   pip install -i https://pypi.douban.com/simple/ --trusted-host pypi.douban.com package_name")
            logger.info(f"3. 其他可用鏡像:")
            logger.info(f"   - 豆瓣: https://pypi.douban.com/simple/")
            logger.info(f"   - 中科大: https://pypi.mirrors.ustc.edu.cn/simple/")
            logger.info(f"   - 華為云: https://mirrors.huaweicloud.com/repository/pypi/simple/")
            
            logger.info(f"\n🎯 下一步:")
            logger.info(f"1. 運行系統初始化: python scripts/setup/initialize_system.py")
            logger.info(f"2. 檢查系統狀態: python scripts/validation/check_system_status.py")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 配置失败: {e}")
        import traceback

        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
