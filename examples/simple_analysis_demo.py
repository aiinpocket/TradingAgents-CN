#!/usr/bin/env python3
"""

 TradingAgents 
"""

import os
import sys
from pathlib import Path

from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def quick_analysis_demo():
    """"""

    logger.info("TradingAgents ")
    logger.info("=" * 60)

    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error(" OPENAI_API_KEY  ANTHROPIC_API_KEY ")
        logger.info(" .env :")
        logger.info("  OPENAI_API_KEY=your_api_key")
        logger.info("  ")
        logger.info("  ANTHROPIC_API_KEY=your_api_key")
        return

    logger.info("")

    analysis_examples = {
        "": {
            "description": "",
            "suitable_for": "",
            "example_stocks": ["AAPL", "TSLA", "NVDA"]
        },
        "": {
            "description": "",
            "suitable_for": "",
            "example_stocks": ["MSFT", "GOOGL", "BRK.B"]
        },
        "": {
            "description": "",
            "suitable_for": "",
            "example_stocks": ["SPY", "QQQ", "VTI"]
        },
        "": {
            "description": "",
            "suitable_for": "",
            "example_stocks": ["AAPL vs MSFT", "TSLA vs F", "AMZN vs WMT"]
        }
    }

    logger.info("\n:")
    for i, (analysis_type, info) in enumerate(analysis_examples.items(), 1):
        logger.info(f"\n{i}. {analysis_type}")
        logger.info(f"   : {info['description']}")
        logger.info(f"   : {info['suitable_for']}")
        logger.info(f"   : {', '.join(info['example_stocks'])}")

    logger.info("\n" + "=" * 60)
    logger.info(":")
    logger.info("\n1.  Web :")
    logger.info("   python start_web.py")

    logger.info("\n2.  CLI :")
    logger.info("   python -m cli.main analyze")

    logger.info("\n3. :")
    logger.info("   ")

    logger.info("\n" + "=" * 60)
    logger.info(":")

    tips = [
        "",
        "",
        "",
        "",
        ""
    ]

    for i, tip in enumerate(tips, 1):
        logger.info(f"{i}. {tip}")

    logger.info("\n" + "=" * 60)
    logger.info(":")
    logger.info("• ")
    logger.info("• ")
    logger.info("• ")
    logger.info("• ")

def show_analysis_workflow():
    """"""

    logger.info("\n:")
    logger.info("=" * 60)

    workflow_steps = [
        {
            "step": "1. ",
            "details": [
                "",
                " vs ",
                " vs "
            ]
        },
        {
            "step": "2. ",
            "details": [
                "",
                "",
                ""
            ]
        },
        {
            "step": "3.  AI ",
            "details": [
                "",
                "",
                " AI "
            ]
        },
        {
            "step": "4. ",
            "details": [
                "",
                "",
                ""
            ]
        },
        {
            "step": "5. ",
            "details": [
                "/",
                "",
                ""
            ]
        },
        {
            "step": "6. ",
            "details": [
                "",
                "",
                ""
            ]
        }
    ]

    for workflow in workflow_steps:
        logger.info(f"\n{workflow['step']}")
        for detail in workflow['details']:
            logger.info(f"   • {detail}")

def main():
    """"""

    from dotenv import load_dotenv
    load_dotenv()

    quick_analysis_demo()
    show_analysis_workflow()

    logger.info("\n" + "=" * 60)
    logger.info("!")
    logger.info(" Web : python start_web.py")

if __name__ == "__main__":
    main()
