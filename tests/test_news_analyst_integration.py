#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新聞分析師與統一新聞工具的集成
"""

import os
import sys
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_news_analyst_integration():
    """測試新聞分析師與統一新聞工具的集成"""
    
    print(" 開始測試新聞分析師集成...")
    
    try:
        # 匯入必要的模組
        from tradingagents.agents.analysts.news_analyst import create_news_analyst
        from tradingagents.tools.unified_news_tool import create_unified_news_tool
        print(" 成功匯入必要模組")
        
        # 建立模擬工具包
        class MockToolkit:
            def __init__(self):
                # 建立統一新聞工具
                self.unified_news_tool = create_unified_news_tool(self)
                
            def get_realtime_stock_news(self, params):
                stock_code = params.get("stock_code", "unknown")
                return f"""
【發布時間】2025-07-28 18:00:00
【新聞標題】{stock_code}公司發布重要公告，業績超預期增長
【文章來源】東方財富網

【新聞內容】
1. 公司Q2季度營收同比增長25%，淨利潤增長30%
2. 新產品線獲得重大突破，市場前景廣闊
3. 管理層對下半年業績表示樂觀
4. 分析師上調目標價至50元

【市場影響】
- 短期利好：業績超預期，市場情緒積極
- 中期利好：新產品線帶來增長動力
- 長期利好：行業地位進一步鞏固
"""
            
            def get_google_news(self, params):
                query = params.get("query", "unknown")
                return f"Google新聞搜索結果 - {query}: 相關財經新聞內容"
            
            def get_global_news_openai(self, params):
                query = params.get("query", "unknown")
                return f"OpenAI全球新聞 - {query}: 國際財經新聞內容"
        
        toolkit = MockToolkit()
        print(" 建立模擬工具包成功")
        
        # 建立模擬LLM
        class MockLLM:
            def __init__(self):
                self.__class__.__name__ = "MockLLM"
            
            def bind_tools(self, tools):
                return self
            
            def invoke(self, messages):
                # 模擬LLM回應，包含工具呼叫
                class MockResult:
                    def __init__(self):
                        self.content = """
# 股票新聞分析報告

##  核心要點
基於最新取得的新聞資料，該股票展現出強勁的業績增長態勢：

###  業績亮點
- Q2營收同比增長25%，超出市場預期
- 淨利潤增長30%，盈利能力顯著提升
- 新產品線獲得重大突破

###  市場影響分析
**短期影響（1-3個月）**：
- 預期股價上漲5-10%
- 市場情緒轉向積極

**中期影響（3-12個月）**：
- 新產品線貢獻增量收入
- 估值有望修複至合理水平

###  投資建議
- **評級**：買入
- **目標價**：50元
- **風險等級**：中等

基於真實新聞資料的專業分析報告。
"""
                        # 模擬工具呼叫
                        self.tool_calls = [{
                            "name": "get_stock_news_unified",
                            "args": {"stock_code": "AAPL", "max_news": 10}
                        }]
                
                return MockResult()
        
        llm = MockLLM()
        print(" 建立模擬LLM成功")
        
        # 建立新聞分析師
        news_analyst = create_news_analyst(llm, toolkit)
        print(" 建立新聞分析師成功")
        
        # 測試不同股票
        test_stocks = [
            ("AAPL", "蘋果公司 - 美股"),
            ("MSFT", "微軟 - 美股"),
            ("GOOGL", "Alphabet - 美股")
        ]
        
        for stock_code, description in test_stocks:
            print(f"\n{'='*60}")
            print(f" 測試股票: {stock_code} ({description})")
            print(f"{'='*60}")
            
            try:
                # 呼叫新聞分析師
                start_time = datetime.now()
                result = news_analyst({
                    "messages": [],
                    "company_of_interest": stock_code,
                    "trade_date": "2025-07-28",
                    "session_id": f"test_{stock_code}"
                })
                end_time = datetime.now()
                
                print(f" 分析耗時: {(end_time - start_time).total_seconds():.2f}秒")
                
                # 檢查結果
                if result and "messages" in result and len(result["messages"]) > 0:
                    final_message = result["messages"][-1]
                    if hasattr(final_message, 'content'):
                        report = final_message.content
                        print(f" 成功取得新聞分析報告")
                        print(f" 報告長度: {len(report)} 字元")
                        
                        # 顯示報告摘要
                        if len(report) > 300:
                            print(f" 報告摘要: {report[:300]}...")
                        else:
                            print(f" 完整報告: {report}")
                        
                        # 檢查是否包含真實新聞特征
                        news_indicators = ['發布時間', '新聞標題', '文章來源', '東方財富', '業績', '營收']
                        has_real_news = any(indicator in report for indicator in news_indicators)
                        print(f" 包含真實新聞特征: {'是' if has_real_news else '否'}")
                        
                        if has_real_news:
                            print(" 集成測試成功！")
                        else:
                            print(" 可能需要進一步優化")
                    else:
                        print(" 訊息內容為空")
                else:
                    print(" 未取得到分析結果")
                    
            except Exception as e:
                print(f" 測試股票 {stock_code} 時出錯: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(" 新聞分析師集成測試完成!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f" 測試過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_analyst_integration()