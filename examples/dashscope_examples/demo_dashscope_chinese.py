#!/usr/bin/env python3
"""
TradingAgents 中文演示腳本 - 使用阿里百炼大模型
專門针對中文用戶優化的股票分析演示
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
from tradingagents.llm_adapters import ChatDashScope
from langchain_core.messages import HumanMessage, SystemMessage

# 加載 .env 文件
load_dotenv()

def analyze_stock_with_chinese_output(stock_symbol="AAPL", analysis_date="2024-05-10"):
    """使用阿里百炼進行中文股票分析"""
    
    logger.info(f"🚀 TradingAgents 中文股票分析 - 阿里百炼版本")
    logger.info(f"=")
    
    # 檢查API密鑰
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    finnhub_key = os.getenv('FINNHUB_API_KEY')
    
    if not dashscope_key:
        logger.error(f"❌ 錯誤: 未找到 DASHSCOPE_API_KEY 環境變量")
        return
    
    if not finnhub_key:
        logger.error(f"❌ 錯誤: 未找到 FINNHUB_API_KEY 環境變量")
        return
    
    logger.info(f"✅ 阿里百炼 API 密鑰: {dashscope_key[:10]}...")
    logger.info(f"✅ FinnHub API 密鑰: {finnhub_key[:10]}...")
    print()
    
    try:
        logger.info(f"🤖 正在初始化阿里百炼大模型...")
        
        # 創建阿里百炼模型實例
        llm = ChatDashScope(
            model="qwen-plus-latest",
            temperature=0.1,
            max_tokens=3000
        )
        
        logger.info(f"✅ 模型初始化成功!")
        print()
        
        logger.info(f"📈 開始分析股票: {stock_symbol}")
        logger.info(f"📅 分析日期: {analysis_date}")
        logger.info(f"⏳ 正在進行智能分析，請稍候...")
        print()
        
        # 構建中文分析提示
        system_prompt = """你是一位專業的股票分析師，具有丰富的金融市場經驗。請用中文進行分析，確保內容專業、客觀、易懂。

你的任務是對指定股票進行全面分析，包括：
1. 技術面分析
2. 基本面分析  
3. 市場情绪分析
4. 風險評估
5. 投資建议

請確保分析結果：
- 使用中文表達
- 內容專業準確
- 結構清晰
- 包含具體的數據和指標
- 提供明確的投資建议"""

        user_prompt = f"""請對苹果公司(AAPL)進行全面的股票分析。

分析要求：
1. **技術面分析**：
   - 價格趋势分析
   - 關键技術指標（MA、MACD、RSI、布林帶等）
   - 支撑位和阻力位
   - 成交量分析

2. **基本面分析**：
   - 公司財務狀况
   - 營收和利润趋势
   - 市場地位和競爭優势
   - 未來增長前景

3. **市場情绪分析**：
   - 投資者情绪
   - 分析師評級
   - 機構持仓情况
   - 市場熱點關註度

4. **風險評估**：
   - 主要風險因素
   - 宏觀經濟影響
   - 行業競爭風險
   - 監管風險

5. **投資建议**：
   - 明確的买入/持有/卖出建议
   - 目標價位
   - 投資時間框架
   - 風險控制建议

請用中文撰寫詳細的分析報告，確保內容專業且易於理解。"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        # 生成分析報告
        response = llm.invoke(messages)
        
        logger.info(f"🎯 中文分析報告:")
        logger.info(f"=")
        print(response.content)
        logger.info(f"=")
        
        print()
        logger.info(f"✅ 分析完成!")
        print()
        logger.info(f"🌟 阿里百炼大模型優势:")
        logger.info(f"  - 中文理解和表達能力强")
        logger.info(f"  - 金融專業知识丰富")
        logger.info(f"  - 分析逻辑清晰嚴谨")
        logger.info(f"  - 適合中國投資者使用习惯")
        
        return response.content
        
    except Exception as e:
        logger.error(f"❌ 分析過程中出現錯誤: {str(e)}")
        import traceback

        logger.error(f"🔍 詳細錯誤信息:")
        traceback.print_exc()
        return None

def compare_models_chinese():
    """比較不同通義千問模型的中文表達能力"""
    logger.info(f"\n🔄 比較不同通義千問模型的中文分析能力")
    logger.info(f"=")
    
    models = [
        ("qwen-turbo", "通義千問 Turbo"),
        ("qwen-plus", "通義千問 Plus"),
        ("qwen-max", "通義千問 Max")
    ]
    
    question = "請用一段話总結苹果公司當前的投資價值，包括優势和風險。"
    
    for model_id, model_name in models:
        try:
            logger.info(f"\n🧠 {model_name} 分析:")
            logger.info(f"-")
            
            llm = ChatDashScope(model=model_id, temperature=0.1, max_tokens=500)
            response = llm.invoke([HumanMessage(content=question)])
            
            print(response.content)
            
        except Exception as e:
            logger.error(f"❌ {model_name} 分析失败: {str(e)}")

def main():
    """主函數"""
    # 進行完整的股票分析
    result = analyze_stock_with_chinese_output("AAPL", "2024-05-10")
    
    # 比較不同模型
    compare_models_chinese()
    
    logger.info(f"\n💡 使用建议:")
    logger.info(f"  1. 通義千問Plus適合日常分析，平衡性能和成本")
    logger.info(f"  2. 通義千問Max適合深度分析，质量最高")
    logger.info(f"  3. 通義千問Turbo適合快速查詢，響應最快")
    logger.info(f"  4. 所有模型都针對中文進行了優化")

if __name__ == "__main__":
    main()
