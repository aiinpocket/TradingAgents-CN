#!/usr/bin/env python3
"""
批量股票分析腳本
一次性分析多只股票，生成對比報告
"""

import os
import sys
import time
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from tradingagents.llm_adapters import ChatDashScope
from langchain_core.messages import HumanMessage, SystemMessage


# 加載環境變量
load_dotenv()

def batch_stock_analysis():
    """批量分析股票"""
    
    # 🎯 在這里定義您要分析的股票組合
    stock_portfolio = {
        "科技股": ["AAPL", "MSFT", "GOOGL", "AMZN"],
        "AI芯片": ["NVDA", "AMD", "INTC"],
        "电動車": ["TSLA", "BYD", "NIO"],
        "ETF": ["SPY", "QQQ", "VTI"]
    }
    
    logger.info(f"🚀 TradingAgents-CN 批量股票分析")
    logger.info(f"=")
    
    # 檢查API密鑰
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error(f"❌ 請設置 DASHSCOPE_API_KEY 環境變量")
        return
    
    try:
        # 初始化模型
        llm = ChatDashScope(
            model="qwen-turbo",  # 使用快速模型進行批量分析
            temperature=0.1,
            max_tokens=2000
        )
        
        all_results = {}
        
        for category, stocks in stock_portfolio.items():
            logger.info(f"\n📊 正在分析 {category} 板塊...")
            category_results = {}
            
            for i, stock in enumerate(stocks, 1):
                logger.info(f"  [{i}/{len(stocks)}] 分析 {stock}...")
                
                # 簡化的分析提示
                prompt = f"""
請對股票 {stock} 進行簡要投資分析，包括：

1. 當前基本面狀况（1-2句話）
2. 技術面趋势判斷（1-2句話）
3. 主要機會和風險（各1-2句話）
4. 投資建议（买入/持有/卖出，目標價）

請保持簡潔，用中文回答。
"""
                
                try:
                    response = llm.invoke([HumanMessage(content=prompt)])
                    category_results[stock] = response.content
                    logger.info(f"    ✅ {stock} 分析完成")
                    
                    # 添加延迟避免API限制
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"    ❌ {stock} 分析失败: {e}")
                    category_results[stock] = f"分析失败: {e}"
            
            all_results[category] = category_results
        
        # 生成汇总報告
        logger.info(f"\n📋 生成汇总報告...")
        generate_summary_report(all_results, llm)
        
    except Exception as e:
        logger.error(f"❌ 批量分析失败: {e}")

def generate_summary_report(results, llm):
    """生成汇总報告"""
    
    # 保存詳細結果
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    detail_filename = f"batch_analysis_detail_{timestamp}.txt"
    
    with open(detail_filename, 'w', encoding='utf-8') as f:
        f.write("TradingAgents-CN 批量股票分析報告\n")
        f.write("=" * 60 + "\n")
        f.write(f"生成時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        for category, stocks in results.items():
            f.write(f"\n{category} 板塊分析\n")
            f.write("-" * 30 + "\n")
            
            for stock, analysis in stocks.items():
                f.write(f"\n【{stock}】\n")
                f.write(analysis + "\n")
    
    logger.info(f"✅ 詳細報告已保存到: {detail_filename}")
    
    # 生成投資組合建议
    try:
        portfolio_prompt = f"""
基於以下股票分析結果，請提供投資組合建议：

{format_results_for_summary(results)}

請提供：
1. 推薦的投資組合配置（各板塊權重）
2. 重點推薦的3-5只股票及理由
3. 需要規避的風險股票
4. 整體市場觀點和策略建议

請用中文回答，保持專業和客觀。
"""
        
        logger.info(f"⏳ 正在生成投資組合建议...")
        portfolio_response = llm.invoke([HumanMessage(content=portfolio_prompt)])
        
        # 保存投資組合建议
        summary_filename = f"portfolio_recommendation_{timestamp}.txt"
        with open(summary_filename, 'w', encoding='utf-8') as f:
            f.write("投資組合建议報告\n")
            f.write("=" * 60 + "\n")
            f.write(f"生成時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(portfolio_response.content)
        
        logger.info(f"✅ 投資組合建议已保存到: {summary_filename}")
        
        # 顯示簡要建议
        logger.info(f"\n🎯 投資組合建议摘要:")
        logger.info(f"=")
        print(portfolio_response.content[:500] + "...")
        logger.info(f"=")
        
    except Exception as e:
        logger.error(f"❌ 生成投資組合建议失败: {e}")

def format_results_for_summary(results):
    """格式化結果用於汇总分析"""
    formatted = ""
    for category, stocks in results.items():
        formatted += f"\n{category}:\n"
        for stock, analysis in stocks.items():
            # 提取關键信息
            formatted += f"- {stock}: {analysis[:100]}...\n"
    return formatted

if __name__ == "__main__":
    batch_stock_analysis()
