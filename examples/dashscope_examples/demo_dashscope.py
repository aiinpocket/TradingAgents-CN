#!/usr/bin/env python3
"""
TradingAgents 演示腳本 - 使用阿里百炼大模型
這個腳本展示了如何使用阿里百炼大模型運行 TradingAgents 框架
"""

import os
import sys
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 加載 .env 文件
load_dotenv()

def main():
    """主函數"""
    logger.info(f"🚀 TradingAgents 演示 - 阿里百炼版本")
    logger.info(f"=")
    
    # 檢查API密鑰
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    
    if not dashscope_key:
        logger.error(f"❌ 錯誤: 未找到 DASHSCOPE_API_KEY 環境變量")
        logger.info(f"請設置您的阿里百炼 API 密鑰:")
        logger.info(f"  Windows: set DASHSCOPE_API_KEY=your_api_key")
        logger.info(f"  Linux/Mac: export DASHSCOPE_API_KEY=your_api_key")
        logger.info(f"  或創建 .env 文件")
        print()
        logger.info(f"🔗 獲取API密鑰:")
        logger.info(f"  1. 訪問 https://dashscope.aliyun.com/")
        logger.info(f"  2. 註冊/登錄阿里云账號")
        logger.info(f"  3. 開通百炼服務")
        logger.info(f"  4. 在控制台獲取API密鑰")
        return
    
    if not finnhub_key:
        logger.error(f"❌ 錯誤: 未找到 FINNHUB_API_KEY 環境變量")
        logger.info(f"請設置您的 FinnHub API 密鑰:")
        logger.info(f"  Windows: set FINNHUB_API_KEY=your_api_key")
        logger.info(f"  Linux/Mac: export FINNHUB_API_KEY=your_api_key")
        logger.info(f"  或創建 .env 文件")
        print()
        logger.info(f"🔗 獲取API密鑰:")
        logger.info(f"  訪問 https://finnhub.io/ 註冊免費账戶")
        return
    
    logger.info(f"✅ 阿里百炼 API 密鑰: {dashscope_key[:10]}...")
    logger.info(f"✅ FinnHub API 密鑰: {finnhub_key[:10]}...")
    print()
    
    # 創建阿里百炼配置
    config = DEFAULT_CONFIG.copy()
    config["llm_provider"] = "dashscope"
    config["backend_url"] = "https://dashscope.aliyuncs.com/api/v1"
    config["deep_think_llm"] = "qwen-plus-latest"  # 使用通義千問Plus進行深度思考
    config["quick_think_llm"] = "qwen-turbo"  # 使用通義千問Turbo進行快速任務
    config["max_debate_rounds"] = 1  # 减少辩論轮次以降低成本
    config["online_tools"] = True
    
    logger.info(f"📊 配置信息:")
    logger.info(f"  LLM 提供商: {config['llm_provider']}")
    logger.info(f"  深度思考模型: {config['deep_think_llm']} (通義千問Plus)")
    logger.info(f"  快速思考模型: {config['quick_think_llm']} (通義千問Turbo)")
    logger.info(f"  最大辩論轮次: {config['max_debate_rounds']}")
    logger.info(f"  在線工具: {config['online_tools']}")
    print()
    
    try:
        logger.info(f"🤖 正在初始化 TradingAgents...")
        ta = TradingAgentsGraph(debug=True, config=config)
        logger.info(f"✅ TradingAgents 初始化成功!")
        print()
        
        # 分析股票
        stock_symbol = "AAPL"  # 苹果公司
        analysis_date = "2024-05-10"

        # 設置中文輸出提示
        import os
        os.environ['TRADINGAGENTS_LANGUAGE'] = 'zh-CN'
        
        logger.info(f"📈 開始分析股票: {stock_symbol}")
        logger.info(f"📅 分析日期: {analysis_date}")
        logger.info(f"⏳ 正在進行多智能體分析，請稍候...")
        logger.info(f"🧠 使用阿里百炼大模型進行智能分析...")
        print()
        
        # 執行分析
        state, decision = ta.propagate(stock_symbol, analysis_date)
        
        logger.info(f"🎯 分析結果:")
        logger.info(f"=")
        print(decision)
        print()
        
        logger.info(f"✅ 分析完成!")
        logger.info(f"💡 提示: 您可以修改 stock_symbol 和 analysis_date 來分析其他股票")
        print()
        logger.info(f"🌟 阿里百炼大模型特色:")
        logger.info(f"  - 中文理解能力强")
        logger.info(f"  - 金融領域知识丰富")
        logger.info(f"  - 推理能力出色")
        logger.info(f"  - 成本相對較低")
        
    except Exception as e:
        logger.error(f"❌ 運行時錯誤: {str(e)}")
        print()
        # 顯示詳細的錯誤信息
        import traceback

        logger.error(f"🔍 詳細錯誤信息:")
        traceback.print_exc()
        print()
        logger.info(f"🔧 可能的解決方案:")
        logger.info(f"1. 檢查阿里百炼API密鑰是否正確")
        logger.info(f"2. 確認已開通百炼服務並有足夠額度")
        logger.info(f"3. 檢查網絡連接")
        logger.error(f"4. 查看詳細錯誤信息進行調試")
        print()
        logger.info(f"📞 如需幫助:")
        logger.info(f"  - 阿里百炼官方文档: https://help.aliyun.com/zh/dashscope/")
        logger.info(f"  - 控制台: https://dashscope.console.aliyun.com/")

if __name__ == "__main__":
    main()
