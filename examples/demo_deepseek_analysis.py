#!/usr/bin/env python3
"""
DeepSeek V3股票分析演示
展示如何使用DeepSeek V3進行股票投資分析
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 導入日誌模塊
import logging
logger = logging.getLogger(__name__)

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

def check_deepseek_config():
    """檢查DeepSeek配置"""
    logger.debug(f"🔍 檢查DeepSeek V3配置...")
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    if not api_key:
        logger.error(f"❌ 錯誤：未找到DeepSeek API密鑰")
        logger.info(f"\n📝 配置步骤:")
        logger.info(f"1. 訪問 https://platform.deepseek.com/")
        logger.info(f"2. 註冊DeepSeek账號並登錄")
        logger.info(f"3. 進入API Keys页面")
        logger.info(f"4. 創建新的API Key")
        logger.info(f"5. 在.env文件中設置:")
        logger.info(f"   DEEPSEEK_API_KEY=your_api_key")
        logger.info(f"   DEEPSEEK_ENABLED=true")
        return False
    
    logger.info(f"✅ API Key: {api_key[:12]}...")
    logger.info(f"✅ Base URL: {base_url}")
    return True

def demo_simple_chat():
    """演示簡單對話功能"""
    logger.info(f"\n🤖 演示DeepSeek V3簡單對話...")
    
    try:
        from tradingagents.llm_adapters.deepseek_direct_adapter import create_deepseek_direct_adapter
        
        # 創建DeepSeek模型
        llm = create_deepseek_direct_adapter(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=500
        )
        
        # 測試對話
        message = """
        請簡要介紹股票投資的基本概念，包括：
        1. 什么是股票
        2. 股票投資的風險
        3. 基本的投資策略
        請用中文回答，控制在200字以內。
        """
        
        logger.info(f"💭 正在生成回答...")
        response = llm.invoke(message)
        logger.info(f"🎯 DeepSeek V3回答:\n{response}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 簡單對話演示失败: {e}")
        return False

def demo_reasoning_analysis():
    """演示推理分析功能"""
    logger.info(f"\n🧠 演示DeepSeek V3推理分析...")
    
    try:
        from tradingagents.llm_adapters.deepseek_direct_adapter import create_deepseek_direct_adapter
        
        # 創建DeepSeek適配器
        adapter = create_deepseek_direct_adapter(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=1000
        )
        
        # 複雜推理任務
        complex_query = """
        假設你是一個專業的股票分析師，請分析以下情况：
        
        公司A：
        - 市盈率：15倍
        - 營收增長率：20%
        - 负债率：30%
        - 行業：科技
        
        公司B：
        - 市盈率：25倍
        - 營收增長率：10%
        - 负债率：50%
        - 行業：傳統制造
        
        請從投資價值角度分析這两家公司，並給出投資建议。
        """
        
        logger.info(f"💭 正在進行深度分析...")
        response = adapter.invoke(complex_query)
        logger.info(f"🎯 DeepSeek V3分析:\n{response}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 推理分析演示失败: {e}")
        return False

def demo_stock_analysis_with_tools():
    """演示帶工具的股票分析"""
    logger.info(f"\n📊 演示DeepSeek V3工具調用股票分析...")
    
    try:
        from tradingagents.llm_adapters.deepseek_direct_adapter import create_deepseek_direct_adapter
        # 移除langchain工具導入以避免兼容性問題
        
        # 定義股票分析工具（簡化版本，不使用langchain裝饰器）
        def get_stock_info(symbol: str) -> str:
            """獲取股票基本信息"""
            stock_data = {
                "AAPL": "苹果公司 - 科技股，主營iPhone、Mac等產品，市值約3万億美元，P/E: 28.5",
                "TSLA": "特斯拉 - 电動汽車制造商，由馬斯克領導，專註新能源汽車，P/E: 65.2",
                "MSFT": "微软 - 软件巨头，主營Windows、Office、Azure云服務，P/E: 32.1",
                "000001": "平安銀行 - 中國股份制銀行，总部深圳，金融服務業，P/E: 5.8",
                "600036": "招商銀行 - 中國領先銀行，零售銀行業務突出，P/E: 6.2"
            }
            return stock_data.get(symbol, f"股票{symbol}的基本信息")
        
        def get_financial_metrics(symbol: str) -> str:
            """獲取財務指標"""
            return f"股票{symbol}的財務指標：ROE 15%，毛利率 35%，净利润增長率 12%"
        
        def get_market_sentiment(symbol: str) -> str:
            """獲取市場情绪"""
            return f"股票{symbol}當前市場情绪：中性偏乐觀，機構持仓比例65%"
        
        # 創建DeepSeek適配器
        adapter = create_deepseek_direct_adapter(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=1000
        )
        
        # 測試股票分析
        test_queries = [
            "請全面分析苹果公司(AAPL)的投資價值，包括基本面、財務狀况和市場情绪",
            "對比分析招商銀行(600036)和平安銀行(000001)，哪個更值得投資？"
        ]
        
        for query in test_queries:
            logger.info(f"\n❓ 用戶問題: {query}")
            logger.info(f"💭 正在分析...")
            
            # 獲取相關股票信息
            if "AAPL" in query:
                stock_info = get_stock_info("AAPL")
                financial_info = get_financial_metrics("AAPL")
                sentiment_info = get_market_sentiment("AAPL")
                context = f"股票信息: {stock_info}\n財務指標: {financial_info}\n市場情绪: {sentiment_info}"
            elif "600036" in query and "000001" in query:
                stock_info_1 = get_stock_info("600036")
                stock_info_2 = get_stock_info("000001")
                context = f"招商銀行信息: {stock_info_1}\n平安銀行信息: {stock_info_2}"
            else:
                context = "基於一般股票分析原則"
            
            # 構建分析提示
            analysis_prompt = f"""
            你是一個專業的股票分析師，請根據以下信息回答用戶問題：
            
            背景信息：
            {context}
            
            用戶問題：{query}
            
            請提供專業的分析建议，分析要深入、逻辑清晰，並給出具體的投資建议。
            """
            
            response = adapter.invoke(analysis_prompt)
            logger.info(f"🎯 分析結果:\n{response}")
            logger.info(f"-")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 工具調用演示失败: {e}")
        return False

def demo_trading_system():
    """演示完整的交易分析系統（簡化版本）"""
    logger.info(f"\n🎯 演示DeepSeek V3完整交易分析系統...")
    
    try:
        from tradingagents.llm_adapters.deepseek_direct_adapter import create_deepseek_direct_adapter
        
        # 創建DeepSeek適配器
        adapter = create_deepseek_direct_adapter()
        
        # 模擬交易分析查詢
        trading_query = "請分析苹果公司(AAPL)的投資價值，包括技術面、基本面和風險評估"
        
        logger.info(f"🏗️ 使用DeepSeek進行交易分析...")
        result = adapter.invoke(trading_query)
        
        logger.info(f"✅ DeepSeek V3交易分析完成！")
        logger.info(f"\n📊 分析結果: {result[:200]}...")
        
        logger.info(f"\n📝 系統特點:")
        logger.info(f"- 🧠 使用DeepSeek V3大模型，推理能力强")
        logger.info(f"- 🛠️ 支持工具調用和智能體協作")
        logger.info(f"- 📊 可進行多維度股票分析")
        logger.info(f"- 💰 成本極低，性價比極高")
        logger.info(f"- 🇨🇳 中文理解能力優秀")
        
        logger.info(f"\n💡 使用建议:")
        logger.info(f"1. 通過Web界面選擇DeepSeek模型")
        logger.info(f"2. 輸入股票代碼進行分析")
        logger.info(f"3. 系統将自動調用多個智能體協作分析")
        logger.info(f"4. 享受高质量、低成本的AI分析服務")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 交易系統演示失败: {e}")
        return False

def main():
    """主演示函數"""
    logger.info(f"🎯 DeepSeek V3股票分析演示")
    logger.info(f"=")
    
    # 檢查配置
    if not check_deepseek_config():
        return False
    
    # 運行演示
    demos = [
        ("簡單對話", demo_simple_chat),
        ("推理分析", demo_reasoning_analysis),
        ("工具調用分析", demo_stock_analysis_with_tools),
        ("完整交易系統", demo_trading_system),
    ]
    
    success_count = 0
    for demo_name, demo_func in demos:
        logger.info(f"\n{'='*20} {demo_name} {'='*20}")
        try:
            if demo_func():
                success_count += 1
                logger.info(f"✅ {demo_name}演示成功")
            else:
                logger.error(f"❌ {demo_name}演示失败")
        except Exception as e:
            logger.error(f"❌ {demo_name}演示異常: {e}")
    
    # 总結
    logger.info(f"\n")
    logger.info(f"📋 演示总結")
    logger.info(f"=")
    logger.info(f"成功演示: {success_count}/{len(demos)}")
    
    if success_count == len(demos):
        logger.info(f"\n🎉 所有演示成功！")
        logger.info(f"\n🚀 DeepSeek V3已成功集成到TradingAgents！")
        logger.info(f"\n📝 特色功能:")
        logger.info(f"- 🧠 强大的推理和分析能力")
        logger.info(f"- 🛠️ 完整的工具調用支持")
        logger.info(f"- 🤖 多智能體協作分析")
        logger.info(f"- 💰 極高的性價比")
        logger.info(f"- 🇨🇳 優秀的中文理解能力")
        logger.info(f"- 📊 專業的金融分析能力")
        
        logger.info(f"\n🎯 下一步:")
        logger.info(f"1. 在Web界面中選擇DeepSeek模型")
        logger.info(f"2. 開始您的股票投資分析之旅")
        logger.info(f"3. 體驗高性價比的AI投資助手")
    else:
        logger.error(f"\n⚠️ {len(demos) - success_count} 個演示失败")
        logger.info(f"請檢查API密鑰配置和網絡連接")
    
    return success_count == len(demos)

if __name__ == "__main__":
    success = main()
    logger.error(f"\n{'🎉 演示完成' if success else '❌ 演示失败'}")
    sys.exit(0 if success else 1)
