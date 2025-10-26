#!/usr/bin/env python3
"""
個人股票分析腳本
根據您的需求自定義分析參數
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

# 加載環境變量
load_dotenv()

def analyze_my_stock():
    """分析您感兴趣的股票"""
    
    # 🎯 在這里修改您要分析的股票
    STOCK_SYMBOL = "NVDA"  # 修改為您想分析的股票代碼
    ANALYSIS_FOCUS = "AI芯片和數據中心業務前景"  # 修改分析重點
    
    logger.info(f"🚀 開始分析股票: {STOCK_SYMBOL}")
    logger.info(f"🎯 分析重點: {ANALYSIS_FOCUS}")
    logger.info(f"=")
    
    # 檢查API密鑰
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error(f"❌ 請設置 DASHSCOPE_API_KEY 環境變量")
        return
    
    try:
        # 初始化模型
        llm = ChatDashScope(
            model="qwen-plus-latest",  # 可選: qwen-turbo, qwen-plus-latest, qwen-max
            temperature=0.1,
            max_tokens=4000
        )
        
        # 構建分析提示
        system_prompt = """
你是一位專業的股票分析師，具有丰富的投資經驗。
請提供客觀、詳細、實用的股票分析報告。
分析應该包含具體數據、清晰逻辑和可操作建议。
"""
        
        analysis_prompt = f"""
請對股票 {STOCK_SYMBOL} 進行全面的投資分析，特別關註{ANALYSIS_FOCUS}。

請從以下角度進行分析：

1. **公司基本面分析**
   - 最新財務數據（營收、利润、現金流）
   - 核心業務表現和增長趋势
   - 競爭優势和護城河

2. **技術面分析**
   - 當前股價走势和趋势判斷
   - 關键技術指標（MA、RSI、MACD等）
   - 重要支撑位和阻力位

3. **行業和市場分析**
   - 行業發展趋势和市場機會
   - 主要競爭對手比較
   - 市場地位和份額變化

4. **風險評估**
   - 主要風險因素识別
   - 宏觀經濟影響
   - 行業特定風險

5. **投資建议**
   - 投資評級（买入/持有/卖出）
   - 目標價位和時間框架
   - 適合的投資者類型
   - 仓位管理建议

請用中文撰寫，提供具體的數據和分析依據。
"""
        
        # 生成分析
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=analysis_prompt)
        ]
        
        logger.info(f"⏳ 正在生成分析報告...")
        response = llm.invoke(messages)
        
        logger.info(f"\n📊 {STOCK_SYMBOL} 投資分析報告:")
        logger.info(f"=")
        print(response.content)
        logger.info(f"=")
        
        # 保存報告
        filename = f"{STOCK_SYMBOL}_analysis_report.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"股票代碼: {STOCK_SYMBOL}\n")
            f.write(f"分析重點: {ANALYSIS_FOCUS}\n")
            f.write(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n")
            f.write(response.content)
        
        logger.info(f"✅ 分析報告已保存到: {filename}")
        
    except Exception as e:
        logger.error(f"❌ 分析失败: {e}")

if __name__ == "__main__":
    import datetime

    analyze_my_stock()
