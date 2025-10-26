#!/usr/bin/env python3
"""
TradingAgents 簡化演示腳本 - 使用阿里百炼大模型
這個腳本展示了如何使用阿里百炼大模型進行簡單的LLM測試
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

# 加載 .env 文件
load_dotenv()

def test_simple_llm():
    """測試簡單的LLM調用"""
    logger.info(f"🚀 阿里百炼大模型簡單測試")
    logger.info(f"=")
    
    # 檢查API密鑰
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    
    if not dashscope_key:
        logger.error(f"❌ 錯誤: 未找到 DASHSCOPE_API_KEY 環境變量")
        return
    
    logger.info(f"✅ 阿里百炼 API 密鑰: {dashscope_key[:10]}...")
    print()
    
    try:
        from tradingagents.llm_adapters import ChatDashScope
        from langchain_core.messages import HumanMessage
        
        logger.info(f"🤖 正在初始化阿里百炼模型...")
        
        # 創建模型實例
        llm = ChatDashScope(
            model="qwen-plus",
            temperature=0.1,
            max_tokens=1000
        )
        
        logger.info(f"✅ 模型初始化成功!")
        print()
        
        # 測試金融分析能力
        logger.info(f"📈 測試金融分析能力...")
        
        messages = [HumanMessage(content="""
請分析特斯拉公司(TSLA)的投資價值，從以下几個角度：
1. 公司基本面 - 財務狀况、盈利能力、現金流
2. 技術面分析 - 股價趋势、技術指標、支撑阻力位
3. 市場前景 - 电動車市場、自動驾驶、能源業務
4. 風險因素 - 競爭風險、監管風險、執行風險
5. 投資建议 - 評級、目標價、投資時間框架

請用中文回答，提供具體的數據和分析，保持專業和客觀。
""")]
        
        logger.info(f"⏳ 正在生成分析報告...")
        response = llm.invoke(messages)
        
        logger.info(f"🎯 分析結果:")
        logger.info(f"=")
        print(response.content)
        logger.info(f"=")
        
        logger.info(f"✅ 測試完成!")
        print()
        logger.info(f"🌟 阿里百炼大模型特色:")
        logger.info(f"  - 中文理解能力强")
        logger.info(f"  - 金融領域知识丰富")
        logger.info(f"  - 推理能力出色")
        logger.info(f"  - 響應速度快")
        
    except Exception as e:
        logger.error(f"❌ 測試失败: {str(e)}")
        import traceback
        logger.error(f"🔍 詳細錯誤信息:")
        traceback.print_exc()

def test_multiple_models():
    """測試多個模型"""
    logger.info(f"\n🔄 測試不同的通義千問模型")
    logger.info(f"=")
    
    models = [
        ("qwen-turbo", "通義千問 Turbo - 快速響應"),
        ("qwen-plus-latest", "通義千問 Plus - 平衡性能"),
        ("qwen-max", "通義千問 Max - 最强性能")
    ]
    
    question = "請用一句話总結苹果公司的核心競爭優势。"
    
    for model_id, model_name in models:
        try:
            logger.info(f"\n🧠 測試 {model_name}...")
            
            from tradingagents.llm_adapters import ChatDashScope
            from langchain_core.messages import HumanMessage

            
            llm = ChatDashScope(model=model_id, temperature=0.1, max_tokens=200)
            response = llm.invoke([HumanMessage(content=question)])
            
            logger.info(f"✅ {model_name}: {response.content}")
            
        except Exception as e:
            logger.error(f"❌ {model_name} 測試失败: {str(e)}")

def main():
    """主函數"""
    test_simple_llm()
    test_multiple_models()
    
    logger.info(f"\n💡 下一步:")
    logger.info(f"  1. 如果測試成功，說明阿里百炼集成正常")
    logger.info(f"  2. 完整的TradingAgents需要解決記忆系統的兼容性")
    logger.info(f"  3. 可以考慮為阿里百炼添加嵌入模型支持")

if __name__ == "__main__":
    main()
