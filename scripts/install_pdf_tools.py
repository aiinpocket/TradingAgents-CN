#!/usr/bin/env python3
"""
PDF工具安裝腳本
自動安裝PDF生成所需的工具
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

def check_tool(command, name):
    """檢查工具是否已安裝"""
    try:
        result = subprocess.run([command, '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            logger.info(f"✅ {name}已安裝: {version_line}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        pass
    
    logger.error(f"❌ {name}未安裝")
    return False

def install_wkhtmltopdf():
    """安裝wkhtmltopdf"""
    system = platform.system().lower()
    
    logger.info(f"🔄 正在為{system}安裝wkhtmltopdf...")
    
    if system == "windows":
        return install_wkhtmltopdf_windows()
    elif system == "darwin":  # macOS
        return install_wkhtmltopdf_macos()
    elif system == "linux":
        return install_wkhtmltopdf_linux()
    else:
        logger.error(f"❌ 不支持的操作系統: {system}")
        return False

def install_wkhtmltopdf_windows():
    """在Windows上安裝wkhtmltopdf"""
    # 嘗試使用Chocolatey
    try:
        result = subprocess.run(['choco', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用Chocolatey安裝wkhtmltopdf...")
            result = subprocess.run(['choco', 'install', 'wkhtmltopdf', '-y'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ wkhtmltopdf安裝成功！")
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
            logger.info(f"🔄 使用winget安裝wkhtmltopdf...")
            result = subprocess.run(['winget', 'install', 'wkhtmltopdf.wkhtmltopdf'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ wkhtmltopdf安裝成功！")
                return True
            else:
                logger.error(f"❌ winget安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning(f"⚠️ winget未安裝")
    
    logger.error(f"❌ 自動安裝失敗，請手動下載安裝")
    logger.info(f"📥 下載地址: https://wkhtmltopdf.org/downloads.html")
    return False

def install_wkhtmltopdf_macos():
    """在macOS上安裝wkhtmltopdf"""
    try:
        result = subprocess.run(['brew', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用Homebrew安裝wkhtmltopdf...")
            result = subprocess.run(['brew', 'install', 'wkhtmltopdf'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ wkhtmltopdf安裝成功！")
                return True
            else:
                logger.error(f"❌ Homebrew安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning(f"⚠️ Homebrew未安裝")
    
    logger.error(f"❌ 自動安裝失敗，請手動安裝Homebrew或下載wkhtmltopdf")
    return False

def install_wkhtmltopdf_linux():
    """在Linux上安裝wkhtmltopdf"""
    # 嘗試使用apt
    try:
        result = subprocess.run(['apt', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用apt安裝wkhtmltopdf...")
            subprocess.run(['sudo', 'apt-get', 'update'], 
                          capture_output=True, text=True, timeout=120)
            result = subprocess.run(['sudo', 'apt-get', 'install', '-y', 'wkhtmltopdf'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ wkhtmltopdf安裝成功！")
                return True
            else:
                logger.error(f"❌ apt安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # 嘗試使用yum
    try:
        result = subprocess.run(['yum', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info(f"🔄 使用yum安裝wkhtmltopdf...")
            result = subprocess.run(['sudo', 'yum', 'install', '-y', 'wkhtmltopdf'], 
                                  capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"✅ wkhtmltopdf安裝成功！")
                return True
            else:
                logger.error(f"❌ yum安裝失敗: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    logger.error(f"❌ 自動安裝失敗，請手動安裝")
    return False

def test_pdf_generation():
    """測試PDF生成功能"""
    logger.info(f"\n🧪 測試PDF生成功能...")
    
    try:
        import pypandoc
        
        test_markdown = """# PDF測試報告

## 基本信息
- **測試時間**: 2025-01-12
- **測試目的**: 驗證PDF生成功能

## 測試內容
這是一個測試文件，用於驗證PDF生成是否正常工作。

### 中文支持測試
- 中文字符顯示測試
- **粗體中文**
- *斜體中文*

### 表格測試
| 項目 | 數值 | 狀態 |
|------|------|------|
| 測試1 | 100% | ✅ |
| 測試2 | 95% | ✅ |

---
*測試完成*
"""
        
        import tempfile

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        # 嘗試生成PDF
        pypandoc.convert_text(
            test_markdown,
            'pdf',
            format='markdown',
            outputfile=output_file,
            extra_args=[
                '--pdf-engine=wkhtmltopdf',
                '-V', 'geometry:margin=2cm'
            ]
        )
        
        if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
            file_size = os.path.getsize(output_file)
            logger.info(f"✅ PDF生成測試成功！文件大小: {file_size} 字節")
            
            # 清理測試文件
            os.unlink(output_file)
            return True
        else:
            logger.error(f"❌ PDF文件生成失敗")
            return False
            
    except Exception as e:
        logger.error(f"❌ PDF生成測試失敗: {e}")
        return False

def main():
    """主函數"""
    logger.info(f"🔧 PDF工具安裝腳本")
    logger.info(f"=")
    
    # 檢查當前狀態
    logger.info(f"📋 檢查當前工具狀態...")
    wkhtmltopdf_installed = check_tool('wkhtmltopdf', 'wkhtmltopdf')
    
    if wkhtmltopdf_installed:
        logger.info(f"\n✅ wkhtmltopdf已安裝，測試PDF生成功能...")
        if test_pdf_generation():
            logger.info(f"🎉 PDF功能完全正常！")
            return True
        else:
            logger.error(f"⚠️ wkhtmltopdf已安裝但PDF生成失敗，可能需要重新安裝")
    
    # 安裝wkhtmltopdf
    logger.info(f"\n🔄 開始安裝wkhtmltopdf...")
    if install_wkhtmltopdf():
        logger.info(f"\n🧪 測試安裝結果...")
        if check_tool('wkhtmltopdf', 'wkhtmltopdf'):
            if test_pdf_generation():
                logger.info(f"🎉 安裝成功，PDF功能正常！")
                return True
            else:
                logger.warning(f"⚠️ 安裝成功但PDF生成仍有問題")
        else:
            logger.error(f"❌ 安裝後仍無法找到wkhtmltopdf")
    
    # 提供手動安裝指導
    logger.info(f"\n📖 手動安裝指導:")
    logger.info(f"1. 訪問 https://wkhtmltopdf.org/downloads.html")
    logger.info(f"2. 下載適合您系統的安裝包")
    logger.info(f"3. 按照說明安裝")
    logger.info(f"4. 確保wkhtmltopdf在系統PATH中")
    logger.info(f"5. 重新運行此腳本測試")
    
    return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
