#!/usr/bin/env python3
"""
Streamlit文件監控錯誤修復腳本

這個腳本用於修復Streamlit應用中的文件監控錯誤：
FileNotFoundError: [WinError 2] 系統找不到指定的文件。: '__pycache__\\*.pyc.*'

使用方法:
python scripts/fix_streamlit_watcher.py
"""

import os
import sys
import shutil
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')


def clean_pycache_files():
    """清理所有__pycache__目錄和.pyc文件"""
    
    project_root = Path(__file__).parent.parent
    logger.debug(f"🔍 掃描項目目錄: {project_root}")
    
    # 查找所有__pycache__目錄
    cache_dirs = list(project_root.rglob("__pycache__"))
    pyc_files = list(project_root.rglob("*.pyc"))
    pyo_files = list(project_root.rglob("*.pyo"))
    
    total_cleaned = 0
    
    # 清理__pycache__目錄
    if cache_dirs:
        logger.info(f"\n🧹 發現 {len(cache_dirs)} 個__pycache__目錄")
        for cache_dir in cache_dirs:
            try:
                shutil.rmtree(cache_dir)
                logger.info(f"  ✅ 已刪除: {cache_dir.relative_to(project_root)}")
                total_cleaned += 1
            except Exception as e:
                logger.error(f"  ❌ 刪除失敗: {cache_dir.relative_to(project_root)} - {e}")
    
    # 清理單獨的.pyc文件
    if pyc_files:
        logger.info(f"\n🧹 發現 {len(pyc_files)} 個.pyc文件")
        for pyc_file in pyc_files:
            try:
                pyc_file.unlink()
                logger.info(f"  ✅ 已刪除: {pyc_file.relative_to(project_root)}")
                total_cleaned += 1
            except Exception as e:
                logger.error(f"  ❌ 刪除失敗: {pyc_file.relative_to(project_root)} - {e}")
    
    # 清理.pyo文件
    if pyo_files:
        logger.info(f"\n🧹 發現 {len(pyo_files)} 個.pyo文件")
        for pyo_file in pyo_files:
            try:
                pyo_file.unlink()
                logger.info(f"  ✅ 已刪除: {pyo_file.relative_to(project_root)}")
                total_cleaned += 1
            except Exception as e:
                logger.error(f"  ❌ 刪除失敗: {pyo_file.relative_to(project_root)} - {e}")
    
    if total_cleaned == 0:
        logger.info(f"\n✅ 沒有發現需要清理的緩存文件")
    else:
        logger.info(f"\n✅ 總共清理了 {total_cleaned} 個文件/目錄")

def check_streamlit_config():
    """檢查Streamlit配置文件"""
    
    project_root = Path(__file__).parent.parent
    config_file = project_root / ".streamlit" / "config.toml"
    
    logger.debug(f"\n🔍 檢查Streamlit配置文件: {config_file}")
    
    if config_file.exists():
        logger.info(f"  ✅ 配置文件存在")
        
        # 檢查配置內容
        try:
            content = config_file.read_text(encoding='utf-8')
            if "excludePatterns" in content and "__pycache__" in content:
                logger.info(f"  ✅ 配置文件包含__pycache__排除規則")
            else:
                logger.warning(f"  ⚠️ 配置文件可能缺少__pycache__排除規則")
        except Exception as e:
            logger.error(f"  ❌ 讀取配置文件失敗: {e}")
    else:
        logger.error(f"  ❌ 配置文件不存在")
        logger.info(f"  💡 建議運行: python web/run_web.py 來創建配置文件")

def set_environment_variables():
    """設置環境變量禁用字節碼生成"""
    
    logger.info(f"\n🔧 設置環境變量...")
    
    # 設置當前會話的環境變量
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    logger.info(f"  ✅ 已設置 PYTHONDONTWRITEBYTECODE=1")
    
    # 檢查.env文件
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        content = env_file.read_text(encoding='utf-8')
        if 'PYTHONDONTWRITEBYTECODE' not in content:
            logger.info(f"  💡 建議在.env文件中添加: PYTHONDONTWRITEBYTECODE=1")
        else:
            logger.info(f"  ✅ .env文件已包含PYTHONDONTWRITEBYTECODE設置")
    else:
        logger.info(f"  💡 建議創建.env文件並添加: PYTHONDONTWRITEBYTECODE=1")

def main():
    """主函數"""
    
    logger.error(f"🔧 Streamlit文件監控錯誤修復工具")
    logger.info(f"=")
    
    logger.info(f"\n📋 此工具將執行以下操作:")
    logger.info(f"  1. 清理所有Python緩存文件(__pycache__, *.pyc, *.pyo)")
    logger.info(f"  2. 檢查Streamlit配置文件")
    logger.info(f"  3. 設置環境變量禁用字節碼生成")
    
    response = input("\n是否繼續? (y/n): ").lower().strip()
    if response != 'y':
        logger.error(f"❌ 操作已取消")
        return
    
    try:
        # 步驟1: 清理緩存文件
        logger.info(f"\n")
        logger.info(f"步驟1: 清理Python緩存文件")
        logger.info(f"=")
        clean_pycache_files()
        
        # 步驟2: 檢查配置文件
        logger.info(f"\n")
        logger.info(f"步驟2: 檢查Streamlit配置")
        logger.info(f"=")
        check_streamlit_config()
        
        # 步驟3: 設置環境變量
        logger.info(f"\n")
        logger.info(f"步驟3: 設置環境變量")
        logger.info(f"=")
        set_environment_variables()
        
        logger.info(f"\n")
        logger.info(f"🎉 修復完成!")
        logger.info(f"\n📝 建議:")
        logger.info(f"  1. 重啟Streamlit應用")
        logger.info(f"  2. 如果問題仍然存在，請查看文件:")
        logger.info(f"     docs/troubleshooting/streamlit-file-watcher-fix.md")
        logger.info(f"  3. 考慮使用虛擬環境隔離Python包")
        
    except Exception as e:
        logger.error(f"\n❌ 修復過程中出現錯誤: {e}")
        logger.info(f"請手動執行以下操作:")
        logger.info(f"  1. 刪除所有__pycache__目錄")
        logger.info(f"  2. 檢查.streamlit/config.toml配置文件")
        logger.info(f"  3. 設置環境變量 PYTHONDONTWRITEBYTECODE=1")

if __name__ == "__main__":
    main()