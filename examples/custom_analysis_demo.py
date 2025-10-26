#!/usr/bin/env python3
"""
自定義股票分析演示
展示如何使用TradingAgents-CN進行個性化投資分析
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

from dotenv import load_dotenv
from tradingagents.llm_adapters import ChatDashScope
from langchain_core.messages import HumanMessage, SystemMessage

# 加載 .env 文件
load_dotenv()

def analyze_stock_custom(symbol, analysis_focus="comprehensive"):
    """
    自定義股票分析函數
    
    Args:
        symbol: 股票代碼 (如 "AAPL", "TSLA", "MSFT")
        analysis_focus: 分析重點
            - "comprehensive": 全面分析
            - "technical": 技術面分析
            - "fundamental": 基本面分析
            - "risk": 風險評估
            - "comparison": 行業比較
    """
    
    logger.info(f"\n🚀 開始分析股票: {symbol}")
    logger.info(f"📊 分析重點: {analysis_focus}")
    logger.info(f"=")
    
    # 檢查API密鑰
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error(f"❌ 錯誤: 請設置 DASHSCOPE_API_KEY 環境變量")
        return
    
    logger.info(f"✅ 阿里百炼 API 密鑰: {api_key[:12]}...")
    
    try:
        # 初始化阿里百炼模型
        logger.info(f"\n🤖 正在初始化阿里百炼模型...")
        llm = ChatDashScope(
            model="qwen-plus-latest",  # 使用平衡性能的模型
            temperature=0.1,    # 降低隨機性，提高分析的一致性
            max_tokens=4000     # 允許更長的分析報告
        )
        logger.info(f"✅ 模型初始化成功!")
        
        # 根據分析重點定制提示詞
        analysis_prompts = {
            "comprehensive": f"""
請對股票 {symbol} 進行全面的投資分析，包括：
1. 技術面分析（價格趋势、技術指標、支撑阻力位）
2. 基本面分析（財務狀况、業務表現、競爭優势）
3. 市場情绪分析（投資者情绪、分析師觀點）
4. 風險評估（各類風險因素）
5. 投資建议（評級、目標價、時間框架）

請用中文撰寫詳細的分析報告，格式清晰，逻辑嚴谨。
""",
            "technical": f"""
請專註於股票 {symbol} 的技術面分析，詳細分析：
1. 價格走势和趋势判斷
2. 主要技術指標（MA、MACD、RSI、KDJ等）
3. 支撑位和阻力位
4. 成交量分析
5. 圖表形態识別
6. 短期交易建议

請提供具體的买卖點位建议。
""",
            "fundamental": f"""
請專註於股票 {symbol} 的基本面分析，詳細分析：
1. 公司財務狀况（營收、利润、現金流）
2. 業務模式和競爭優势
3. 行業地位和市場份額
4. 管理層质量
5. 未來增長前景
6. 估值水平分析

請評估公司的內在價值和長期投資價值。
""",
            "risk": f"""
請專註於股票 {symbol} 的風險評估，詳細分析：
1. 宏觀經濟風險
2. 行業周期性風險
3. 公司特定風險
4. 監管政策風險
5. 市場流動性風險
6. 技術和競爭風險

請提供風險控制建议和應對策略。
""",
            "comparison": f"""
請将股票 {symbol} 与同行業主要競爭對手進行比較分析：
1. 財務指標對比
2. 業務模式比較
3. 市場地位對比
4. 估值水平比較
5. 增長前景對比
6. 投資價值排序

請說明该股票相對於競爭對手的優劣势。
"""
        }
        
        # 構建消息
        system_message = SystemMessage(content="""
你是一位專業的股票分析師，具有丰富的金融市場經驗。請基於你的專業知识，
為用戶提供客觀、詳細、實用的股票分析報告。分析應该：

1. 基於事實和數據
2. 逻辑清晰，結構完整
3. 包含具體的數字和指標
4. 提供可操作的建议
5. 明確風險提示

請用專業但易懂的中文進行分析。
""")
        
        human_message = HumanMessage(content=analysis_prompts[analysis_focus])
        
        # 生成分析
        logger.info(f"\n⏳ 正在生成{analysis_focus}分析，請稍候...")
        response = llm.invoke([system_message, human_message])
        
        logger.info(f"\n🎯 {symbol} 分析報告:")
        logger.info(f"=")
        print(response.content)
        logger.info(f"=")
        
        return response.content
        
    except Exception as e:
        logger.error(f"❌ 分析失败: {str(e)}")
        return None

def interactive_analysis():
    """交互式分析界面"""
    
    logger.info(f"🚀 TradingAgents-CN 自定義股票分析工具")
    logger.info(f"=")
    
    while True:
        logger.info(f"\n📊 請選擇分析選項:")
        logger.info(f"1. 全面分析 (comprehensive)")
        logger.info(f"2. 技術面分析 (technical)")
        logger.info(f"3. 基本面分析 (fundamental)")
        logger.info(f"4. 風險評估 (risk)")
        logger.info(f"5. 行業比較 (comparison)")
        logger.info(f"6. 退出")
        
        choice = input("\n請輸入選項 (1-6): ").strip()
        
        if choice == "6":
            logger.info(f"👋 感谢使用，再见！")
            break
            
        if choice not in ["1", "2", "3", "4", "5"]:
            logger.error(f"❌ 無效選項，請重新選擇")
            continue
            
        # 獲取股票代碼
        symbol = input("\n請輸入股票代碼 (如 AAPL, TSLA, MSFT): ").strip().upper()
        if not symbol:
            logger.error(f"❌ 股票代碼不能為空")
            continue
            
        # 映射選項到分析類型
        analysis_types = {
            "1": "comprehensive",
            "2": "technical", 
            "3": "fundamental",
            "4": "risk",
            "5": "comparison"
        }
        
        analysis_type = analysis_types[choice]
        
        # 執行分析
        result = analyze_stock_custom(symbol, analysis_type)
        
        if result:
            # 詢問是否保存報告
            save_choice = input("\n💾 是否保存分析報告到文件? (y/n): ").strip().lower()
            if save_choice == 'y':
                filename = f"{symbol}_{analysis_type}_analysis.txt"
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"股票代碼: {symbol}\n")
                        f.write(f"分析類型: {analysis_type}\n")
                        f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("=" * 60 + "\n")
                        f.write(result)
                    logger.info(f"✅ 報告已保存到: {filename}")
                except Exception as e:
                    logger.error(f"❌ 保存失败: {e}")
        
        # 詢問是否繼续
        continue_choice = input("\n🔄 是否繼续分析其他股票? (y/n): ").strip().lower()
        if continue_choice != 'y':
            logger.info(f"👋 感谢使用，再见！")
            break

def batch_analysis_demo():
    """批量分析演示"""
    
    logger.info(f"\n🔄 批量分析演示")
    logger.info(f"=")
    
    # 預定義的股票列表
    stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
    
    logger.info(f"📊 将分析以下股票: {', '.join(stocks)}")
    
    for i, stock in enumerate(stocks, 1):
        logger.info(f"\n[{i}/{len(stocks)}] 正在分析 {stock}...")
        
        # 進行簡化的技術面分析
        result = analyze_stock_custom(stock, "technical")
        
        if result:
            # 保存到文件
            filename = f"batch_analysis_{stock}.txt"
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result)
                logger.info(f"✅ {stock} 分析完成，已保存到 {filename}")
            except Exception as e:
                logger.error(f"❌ 保存 {stock} 分析失败: {e}")
        
        # 添加延迟避免API限制
        import time
        time.sleep(2)
    
    logger.info(f"\n🎉 批量分析完成！共分析了 {len(stocks)} 只股票")

def main():
    """主函數"""
    
    logger.info(f"🚀 TradingAgents-CN 自定義分析演示")
    logger.info(f"=")
    logger.info(f"選擇運行模式:")
    logger.info(f"1. 交互式分析")
    logger.info(f"2. 批量分析演示")
    logger.info(f"3. 單股票快速分析")
    
    mode = input("\n請選擇模式 (1-3): ").strip()
    
    if mode == "1":
        interactive_analysis()
    elif mode == "2":
        batch_analysis_demo()
    elif mode == "3":
        symbol = input("請輸入股票代碼: ").strip().upper()
        if symbol:
            analyze_stock_custom(symbol, "comprehensive")
    else:
        logger.error(f"❌ 無效選項")

if __name__ == "__main__":
    import datetime

    main()
