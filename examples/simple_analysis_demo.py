#!/usr/bin/env python3
"""
簡單股票分析演示
展示如何快速使用 TradingAgents 進行投資分析
"""

import os
import sys
from pathlib import Path

from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def quick_analysis_demo():
    """快速分析演示"""

    logger.info("TradingAgents 快速投資分析演示")
    logger.info("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("請先設定 OPENAI_API_KEY 或 ANTHROPIC_API_KEY 環境變數")
        logger.info("在 .env 檔案中添加:")
        logger.info("  OPENAI_API_KEY=your_api_key")
        logger.info("  或")
        logger.info("  ANTHROPIC_API_KEY=your_api_key")
        return

    logger.info("環境檢查通過")

    analysis_examples = {
        "技術面分析": {
            "description": "分析價格趨勢、技術指標、支撐阻力位",
            "suitable_for": "短期交易者、技術分析愛好者",
            "example_stocks": ["AAPL", "TSLA", "NVDA"]
        },
        "基本面分析": {
            "description": "分析財務狀況、業務模式、競爭優勢",
            "suitable_for": "長期投資者、價值投資者",
            "example_stocks": ["MSFT", "GOOGL", "BRK.B"]
        },
        "風險評估": {
            "description": "識別各類風險因素，制定風險控制策略",
            "suitable_for": "風險管理、投資組合管理",
            "example_stocks": ["SPY", "QQQ", "VTI"]
        },
        "行業比較": {
            "description": "對比同行業公司的相對優勢",
            "suitable_for": "行業研究、選股決策",
            "example_stocks": ["AAPL vs MSFT", "TSLA vs F", "AMZN vs WMT"]
        }
    }

    logger.info("\n支援的分析類型:")
    for i, (analysis_type, info) in enumerate(analysis_examples.items(), 1):
        logger.info(f"\n{i}. {analysis_type}")
        logger.info(f"   描述: {info['description']}")
        logger.info(f"   適合: {info['suitable_for']}")
        logger.info(f"   範例: {', '.join(info['example_stocks'])}")

    logger.info("\n" + "=" * 60)
    logger.info("使用方法:")
    logger.info("\n1. 啟動 Web 介面進行分析:")
    logger.info("   python start_web.py")

    logger.info("\n2. 交互式 CLI 工具:")
    logger.info("   python -m cli.main analyze")

    logger.info("\n3. 自訂分析腳本:")
    logger.info("   修改範例程式中的股票代碼和分析參數")

    logger.info("\n" + "=" * 60)
    logger.info("實用技巧:")

    tips = [
        "選擇合適的模型平衡性能和成本",
        "分析前先查看最新的財報和新聞",
        "結合多個時間框架進行分析",
        "設定合理的止損和目標價位",
        "定期回顧和調整投資策略"
    ]

    for i, tip in enumerate(tips, 1):
        logger.info(f"{i}. {tip}")

    logger.info("\n" + "=" * 60)
    logger.info("重要提醒:")
    logger.info("• 分析結果僅供參考，不構成投資建議")
    logger.info("• 投資有風險，決策需謹慎")
    logger.info("• 建議結合多方信息進行驗證")
    logger.info("• 重大投資決策請諮詢專業財務顧問")

def show_analysis_workflow():
    """展示分析工作流程"""

    logger.info("\n投資分析工作流程:")
    logger.info("=" * 60)

    workflow_steps = [
        {
            "step": "1. 選擇分析目標",
            "details": [
                "確定要分析的股票代碼",
                "明確分析目的（短期交易 vs 長期投資）",
                "選擇分析重點（技術面 vs 基本面）"
            ]
        },
        {
            "step": "2. 收集基礎資訊",
            "details": [
                "查看最新股價和成交量",
                "了解最近的重要新聞和公告",
                "檢查財報發布時間和業績預期"
            ]
        },
        {
            "step": "3. 執行 AI 分析",
            "details": [
                "選擇合適的分析程式",
                "設定分析參數",
                "等待 AI 生成分析報告"
            ]
        },
        {
            "step": "4. 驗證和補充",
            "details": [
                "對比其他分析師觀點",
                "查證關鍵數據和事實",
                "補充最新市場資訊"
            ]
        },
        {
            "step": "5. 制定投資策略",
            "details": [
                "確定買入/賣出時機",
                "設定目標價位和止損點",
                "規劃倉位管理策略"
            ]
        },
        {
            "step": "6. 執行和監控",
            "details": [
                "按計劃執行交易",
                "定期監控投資表現",
                "根據市場變化調整策略"
            ]
        }
    ]

    for workflow in workflow_steps:
        logger.info(f"\n{workflow['step']}")
        for detail in workflow['details']:
            logger.info(f"   • {detail}")

def main():
    """主函數"""

    from dotenv import load_dotenv
    load_dotenv()

    quick_analysis_demo()
    show_analysis_workflow()

    logger.info("\n" + "=" * 60)
    logger.info("開始您的投資分析之旅!")
    logger.info("建議從 Web 介面開始: python start_web.py")

if __name__ == "__main__":
    main()
