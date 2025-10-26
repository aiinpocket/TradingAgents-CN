#!/usr/bin/env python3
"""
CLI工具中文化演示腳本
展示TradingAgents CLI工具的中文支持功能
"""

import subprocess
import sys
import time

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('cli')


def run_command(command, description):
    """運行命令並顯示結果"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🎯 {description}")
    logger.info(f"命令: {command}")
    logger.info(f"=")
    
    try:
        result = subprocess.run(
            command.split(), 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        print(result.stdout)
        if result.stderr:
            logger.error(f"錯誤輸出:", result.stderr)
    except subprocess.TimeoutExpired:
        logger.info(f"⏰ 命令執行超時")
    except Exception as e:
        logger.error(f"❌ 執行錯誤: {e}")
    
    time.sleep(1)

def main():
    """主演示函數"""
    logger.info(f"🚀 TradingAgents CLI 中文化功能演示")
    logger.info(f"=")
    logger.info(f"本演示将展示CLI工具的各種中文化功能")
    print()
    
    # 演示各種命令
    commands = [
        ("python -m cli.main --help", "主幫助信息 - 顯示所有可用命令"),
        ("python -m cli.main help", "中文幫助 - 詳細的中文使用指南"),
        ("python -m cli.main config", "配置信息 - 顯示LLM提供商和設置"),
        ("python -m cli.main version", "版本信息 - 顯示软件版本和特性"),
        ("python -m cli.main examples", "示例程序 - 列出可用的演示程序"),
        ("python -m cli.main test", "測試功能 - 運行系統集成測試"),
    ]
    
    for command, description in commands:
        run_command(command, description)
    
    logger.info(f"\n")
    logger.info(f"🎉 CLI中文化演示完成！")
    logger.info(f"=")
    print()
    logger.info(f"💡 主要特色:")
    logger.info(f"• ✅ 完整的中文用戶界面")
    logger.info(f"• ✅ 雙語命令說明")
    logger.error(f"• ✅ 中文錯誤提示")
    logger.info(f"• ✅ 阿里百炼大模型支持")
    logger.info(f"• ✅ 詳細的使用指導")
    print()
    logger.info(f"🚀 下一步:")
    logger.info(f"1. 配置API密鑰: 編辑 .env 文件")
    logger.info(f"2. 運行測試: python -m cli.main test")
    logger.info(f"3. 開始分析: python -m cli.main analyze")
    print()
    logger.info(f"📖 獲取更多幫助:")
    logger.info(f"• python -m cli.main help")
    logger.info(f"• 查看 examples/ 目錄的演示程序")
    logger.info(f"• 查看 docs/ 目錄的詳細文档")

if __name__ == "__main__":
    main()
