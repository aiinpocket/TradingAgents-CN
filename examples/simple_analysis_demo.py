#!/usr/bin/env python3
"""
簡單股票分析演示
展示如何快速使用TradingAgents-CN進行投資分析
"""

import os
import sys
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def quick_analysis_demo():
    """快速分析演示"""
    
    logger.info(f"🚀 TradingAgents-CN 快速投資分析演示")
    logger.info(f"=")
    
    # 檢查環境
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error(f"❌ 請先設置 DASHSCOPE_API_KEY 環境變量")
        logger.info(f"💡 在 .env 文件中添加: DASHSCOPE_API_KEY=your_api_key")
        return
    
    logger.info(f"✅ 環境檢查通過")
    
    # 演示不同類型的分析
    analysis_examples = {
        "技術面分析": {
            "description": "分析價格趋势、技術指標、支撑阻力位",
            "suitable_for": "短期交易者、技術分析爱好者",
            "example_stocks": ["AAPL", "TSLA", "NVDA"]
        },
        "基本面分析": {
            "description": "分析財務狀况、業務模式、競爭優势",
            "suitable_for": "長期投資者、價值投資者",
            "example_stocks": ["MSFT", "GOOGL", "BRK.B"]
        },
        "風險評估": {
            "description": "识別各類風險因素，制定風險控制策略",
            "suitable_for": "風險管理、投資組合管理",
            "example_stocks": ["SPY", "QQQ", "VTI"]
        },
        "行業比較": {
            "description": "對比同行業公司的相對優势",
            "suitable_for": "行業研究、選股決策",
            "example_stocks": ["AAPL vs MSFT", "TSLA vs F", "AMZN vs WMT"]
        }
    }
    
    logger.info(f"\n📊 支持的分析類型:")
    for i, (analysis_type, info) in enumerate(analysis_examples.items(), 1):
        logger.info(f"\n{i}. {analysis_type}")
        logger.info(f"   📝 描述: {info['description']}")
        logger.info(f"   👥 適合: {info['suitable_for']}")
        logger.info(f"   📈 示例: {', '.join(info['example_stocks'])}")
    
    logger.info(f"\n")
    logger.info(f"🎯 使用方法:")
    logger.info(f"\n1. 預設示例分析:")
    logger.info(f"   python examples/dashscope/demo_dashscope_chinese.py")
    logger.info(f"   python examples/dashscope/demo_dashscope_simple.py")
    
    logger.info(f"\n2. 交互式CLI工具:")
    logger.info(f"   python -m cli.main analyze")
    
    logger.info(f"\n3. 自定義分析腳本:")
    logger.info(f"   修改示例程序中的股票代碼和分析參數")
    
    logger.info(f"\n")
    logger.info(f"💡 實用技巧:")
    
    tips = [
        "選擇qwen-plus模型平衡性能和成本",
        "使用qwen-max獲得最高质量的分析",
        "分析前先查看最新的財報和新聞",
        "結合多個時間框架進行分析",
        "設置合理的止損和目標價位",
        "定期回顧和調整投資策略"
    ]
    
    for i, tip in enumerate(tips, 1):
        logger.info(f"{i}. {tip}")
    
    logger.info(f"\n")
    logger.warning(f"⚠️ 重要提醒:")
    logger.info(f"• 分析結果仅供參考，不構成投資建议")
    logger.info(f"• 投資有風險，決策需谨慎")
    logger.info(f"• 建议結合多方信息進行驗證")
    logger.info(f"• 重大投資決策請咨詢專業財務顧問")

def show_analysis_workflow():
    """展示分析工作流程"""
    
    logger.info(f"\n🔄 投資分析工作流程:")
    logger.info(f"=")
    
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
            "step": "2. 收集基础信息", 
            "details": [
                "查看最新股價和成交量",
                "了解最近的重要新聞和公告",
                "檢查財報發布時間和業绩預期"
            ]
        },
        {
            "step": "3. 運行AI分析",
            "details": [
                "選擇合適的分析程序",
                "配置分析參數",
                "等待AI生成分析報告"
            ]
        },
        {
            "step": "4. 驗證和補充",
            "details": [
                "對比其他分析師觀點",
                "查證關键數據和事實",
                "補充最新市場信息"
            ]
        },
        {
            "step": "5. 制定投資策略",
            "details": [
                "確定买入/卖出時機",
                "設置目標價位和止損點",
                "規劃仓位管理策略"
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
        logger.info(f"\n📋 {workflow['step']}")
        for detail in workflow['details']:
            logger.info(f"   • {detail}")

def show_model_comparison():
    """展示不同模型的特點"""
    
    logger.info(f"\n🧠 阿里百炼模型對比:")
    logger.info(f"=")
    
    models = {
        "qwen-turbo": {
            "特點": "響應速度快，成本低",
            "適用場景": "快速查詢，批量分析",
            "分析质量": "⭐⭐⭐",
            "響應速度": "⭐⭐⭐⭐⭐",
            "成本效益": "⭐⭐⭐⭐⭐"
        },
        "qwen-plus": {
            "特點": "平衡性能和成本，推薦日常使用",
            "適用場景": "日常分析，投資決策",
            "分析质量": "⭐⭐⭐⭐",
            "響應速度": "⭐⭐⭐⭐",
            "成本效益": "⭐⭐⭐⭐"
        },
        "qwen-max": {
            "特點": "最高质量，深度分析",
            "適用場景": "重要決策，深度研究",
            "分析质量": "⭐⭐⭐⭐⭐",
            "響應速度": "⭐⭐⭐",
            "成本效益": "⭐⭐⭐"
        }
    }
    
    for model, info in models.items():
        logger.info(f"\n🤖 {model}")
        for key, value in info.items():
            logger.info(f"   {key}: {value}")

def main():
    """主函數"""
    
    # 加載環境變量
    from dotenv import load_dotenv

    load_dotenv()
    
    quick_analysis_demo()
    show_analysis_workflow()
    show_model_comparison()
    
    logger.info(f"\n")
    logger.info(f"🚀 開始您的投資分析之旅!")
    logger.info(f"💡 建议從簡單示例開始: python examples/dashscope/demo_dashscope_simple.py")

if __name__ == "__main__":
    main()
