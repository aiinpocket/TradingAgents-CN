#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試統一新聞工具集成效果
"""

import os
import sys
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tradingagents.agents.analysts.news_analyst import create_news_analyst
from tradingagents.agents.utils.agent_utils import Toolkit
from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek

def test_unified_news_tool():
    """測試統一新聞工具的集成效果"""
    
    print("🚀 開始測試統一新聞工具集成...")
    
    # 測試股票列表 - 包含A股、港股、美股
    test_stocks = [
        ("000001", "平安銀行 - A股"),
        ("00700", "腾讯控股 - 港股"), 
        ("AAPL", "苹果公司 - 美股")
    ]
    
    try:
        # 初始化工具包
        print("📦 初始化工具包...")
        from tradingagents.default_config import DEFAULT_CONFIG
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config=config)
        
        # 創建LLM實例（使用DeepSeek）
        print("🤖 創建LLM實例...")
        llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1
        )
        
        # 創建新聞分析師
        print("📰 創建新聞分析師...")
        news_analyst = create_news_analyst(llm, toolkit)
        
        # 測試每個股票
        for stock_code, description in test_stocks:
            print(f"\n{'='*60}")
            print(f"🔍 測試股票: {stock_code} ({description})")
            print(f"{'='*60}")
            
            try:
                # 調用新聞分析師
                result = news_analyst({
                    "messages": [],
                    "company_of_interest": stock_code,
                    "trade_date": "2025-07-28",
                    "session_id": f"test_{stock_code}"
                })
                
                # 檢查結果
                if result and "messages" in result and len(result["messages"]) > 0:
                    final_message = result["messages"][-1]
                    if hasattr(final_message, 'content'):
                        report = final_message.content
                        print(f"✅ 成功獲取新聞分析報告")
                        print(f"📊 報告長度: {len(report)} 字符")
                        
                        # 顯示報告摘要
                        if len(report) > 200:
                            print(f"📝 報告摘要: {report[:200]}...")
                        else:
                            print(f"📝 完整報告: {report}")
                            
                        # 檢查是否包含真實新聞特征
                        news_indicators = ['發布時間', '新聞標題', '文章來源', '东方財富', '財聯社', '證券時報']
                        has_real_news = any(indicator in report for indicator in news_indicators)
                        print(f"🔍 包含真實新聞特征: {'是' if has_real_news else '否'}")
                    else:
                        print("❌ 消息內容為空")
                else:
                    print("❌ 未獲取到新聞分析報告")
                    
            except Exception as e:
                print(f"❌ 測試股票 {stock_code} 時出錯: {e}")
                import traceback
                traceback.print_exc()
                
        print(f"\n{'='*60}")
        print("🎉 統一新聞工具測試完成!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ 測試過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_unified_news_tool()