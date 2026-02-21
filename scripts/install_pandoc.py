#!/usr/bin/env python3
"""
Pandoc安裝腳本
自動安裝pandoc工具，用於報告導出功能
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def check_pandoc():
    """檢查pandoc是否已安裝"""
    try:
        result = subprocess.run(['pandoc', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            logger.info(f"✅ Pandoc已安裝: {version}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    logger.error(f"❌ Pandoc未安裝")
    return False

def install_pandoc_python():
    """使用pypandoc下載pandoc"""
    try:
        import pypandoc

        logger.info(f"🔄 正在使用pypandoc下載pandoc...")
        pypandoc.download_pandoc()
        logger.info(f"✅ Pandoc下載成功！")
        return True
    except ImportError:
        logger.error(f"❌ pypandoc未安裝，請先運行: pip install pypandoc")
        return False
    except Exception as e:
        logger.error(f"❌ Pandoc下載失敗: {e}")
        return False

def install_pandoc_system():
    """使用系統包管理器安裝pandoc"""
    system = platform.system().lower()
    
    if system == "windows":
        return install_pandoc_windows()
    elif system == "darwin":  # macOS
        return install_pandoc_macos()
    elif system == "linux":
        return install_pandoc_linux()
    else:
        logger.error(f"❌ 不支持的操作系統: {system}")
        return False

def install_pandoc_windows():
    """在Windows上安裝pandoc"""
    logger.info(f"🔄 嘗試在Windows上安裝pandoc...")
    
    # 嘗試使用Chocolatey
    try:
        result = subprocess.run(['choco', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用Chocolatey安裝pandoc...")
            result = subprocess.run(['choco', 'install', 'pandoc', '-y'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ Pandoc安裝成功！")
                return True
            else:
                logger.error(f"❌ Chocolatey安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning(f"⚠️ Chocolatey未安裝")
    
    # 嘗試使用winget
    try:
        result = subprocess.run(['winget', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用winget安裝pandoc...")
            result = subprocess.run(['winget', 'install', 'JohnMacFarlane.Pandoc'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ Pandoc安裝成功！")
                return True
            else:
                logger.error(f"❌ winget安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning(f"⚠️ winget未安裝")
    
    logger.error(f"❌ 系統包管理器安裝失敗")
    return False

def install_pandoc_macos():
    """在macOS上安裝pandoc"""
    logger.info(f"🔄 嘗試在macOS上安裝pandoc...")
    
    # 嘗試使用Homebrew
    try:
        result = subprocess.run(['brew', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用Homebrew安裝pandoc...")
            result = subprocess.run(['brew', 'install', 'pandoc'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ Pandoc安裝成功！")
                return True
            else:
                logger.error(f"❌ Homebrew安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning(f"⚠️ Homebrew未安裝")
    
    logger.error(f"❌ 系統包管理器安裝失敗")
    return False

def install_pandoc_linux():
    """在Linux上安裝pandoc"""
    logger.info(f"🔄 嘗試在Linux上安裝pandoc...")
    
    # 嘗試使用apt (Ubuntu/Debian)
    try:
        result = subprocess.run(['apt', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用apt安裝pandoc...")
            result = subprocess.run(['sudo', 'apt-get', 'update'], 
                                  capture_output=True, text=True, timeout=120)
            result = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'pandoc'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ Pandoc安裝成功！")
                return True
            else:
                logger.error(f"❌ apt安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # 嘗試使用yum (CentOS/RHEL)
    try:
        result = subprocess.run(['yum', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用yum安裝pandoc...")
            result = subprocess.run(['sudo', 'yum', 'install', '-y', 'pandoc'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ Pandoc安裝成功！")
                return True
            else:
                logger.error(f"❌ yum安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    logger.error(f"❌ 系統包管理器安裝失敗")
    return False

def main():
    """主函數"""
    logger.info(f"🔧 Pandoc安裝腳本")
    logger.info(f"=")
    
    # 檢查是否已安裝
    if check_pandoc():
        logger.info(f"✅ Pandoc已可用，無需安裝")
        return True
    
    logger.info(f"\n🔄 開始安裝pandoc...")
    
    # 方法1: 使用pypandoc下載
    logger.info(f"\n📦 方法1: 使用pypandoc下載")
    if install_pandoc_python():
        if check_pandoc():
            return True
    
    # 方法2: 使用系統包管理器
    logger.info(f"\n🖥️ 方法2: 使用系統包管理器")
    if install_pandoc_system():
        if check_pandoc():
            return True
    
    # 安裝失敗
    logger.error(f"\n❌ 所有安裝方法都失敗了")
    logger.info(f"\n📖 手動安裝指南:")
    logger.info(f"1. 訪問 https://github.com/jgm/pandoc/releases")
    logger.info(f"2. 下載適合您系統的安裝包")
    logger.info(f"3. 按照官方文件安裝")
    logger.info(f"4. 確保pandoc在系統PATH中")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
