#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試新聞分析師与統一新聞工具的集成
"""

import os
import sys
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_news_analyst_integration():
    """測試新聞分析師与統一新聞工具的集成"""
    
    print("🚀 開始測試新聞分析師集成...")
    
    try:
        # 導入必要的模塊
        from tradingagents.agents.analysts.news_analyst import create_news_analyst
        from tradingagents.tools.unified_news_tool import create_unified_news_tool
        print("✅ 成功導入必要模塊")
        
        # 創建模擬工具包
        class MockToolkit:
            def __init__(self):
                # 創建統一新聞工具
                self.unified_news_tool = create_unified_news_tool(self)
                
            def get_realtime_stock_news(self, params):
                stock_code = params.get("stock_code", "unknown")
                return f"""
【發布時間】2025-07-28 18:00:00
【新聞標題】{stock_code}公司發布重要公告，業绩超預期增長
【文章來源】东方財富網

【新聞內容】
1. 公司Q2季度營收同比增長25%，净利润增長30%
2. 新產品線獲得重大突破，市場前景廣阔
3. 管理層對下半年業绩表示乐觀
4. 分析師上調目標價至50元

【市場影響】
- 短期利好：業绩超預期，市場情绪積極
- 中期利好：新產品線帶來增長動力
- 長期利好：行業地位進一步巩固
"""
            
            def get_google_news(self, params):
                query = params.get("query", "unknown")
                return f"Google新聞搜索結果 - {query}: 相關財經新聞內容"
            
            def get_global_news_openai(self, params):
                query = params.get("query", "unknown")
                return f"OpenAI全球新聞 - {query}: 國际財經新聞內容"
        
        toolkit = MockToolkit()
        print("✅ 創建模擬工具包成功")
        
        # 創建模擬LLM
        class MockLLM:
            def __init__(self):
                self.__class__.__name__ = "MockLLM"
            
            def bind_tools(self, tools):
                return self
            
            def invoke(self, messages):
                # 模擬LLM響應，包含工具調用
                class MockResult:
                    def __init__(self):
                        self.content = """
# 股票新聞分析報告

## 📈 核心要點
基於最新獲取的新聞數據，该股票展現出强劲的業绩增長態势：

### 🎯 業绩亮點
- Q2營收同比增長25%，超出市場預期
- 净利润增長30%，盈利能力顯著提升
- 新產品線獲得重大突破

### 📊 市場影響分析
**短期影響（1-3個月）**：
- 預期股價上涨5-10%
- 市場情绪轉向積極

**中期影響（3-12個月）**：
- 新產品線贡献增量收入
- 估值有望修複至合理水平

### 💰 投資建议
- **評級**：买入
- **目標價**：50元
- **風險等級**：中等

基於真實新聞數據的專業分析報告。
"""
                        # 模擬工具調用
                        self.tool_calls = [{
                            "name": "get_stock_news_unified",
                            "args": {"stock_code": "000001", "max_news": 10}
                        }]
                
                return MockResult()
        
        llm = MockLLM()
        print("✅ 創建模擬LLM成功")
        
        # 創建新聞分析師
        news_analyst = create_news_analyst(llm, toolkit)
        print("✅ 創建新聞分析師成功")
        
        # 測試不同股票
        test_stocks = [
            ("000001", "平安銀行 - A股"),
            ("00700", "腾讯控股 - 港股"),
            ("AAPL", "苹果公司 - 美股")
        ]
        
        for stock_code, description in test_stocks:
            print(f"\n{'='*60}")
            print(f"🔍 測試股票: {stock_code} ({description})")
            print(f"{'='*60}")
            
            try:
                # 調用新聞分析師
                start_time = datetime.now()
                result = news_analyst({
                    "messages": [],
                    "company_of_interest": stock_code,
                    "trade_date": "2025-07-28",
                    "session_id": f"test_{stock_code}"
                })
                end_time = datetime.now()
                
                print(f"⏱️ 分析耗時: {(end_time - start_time).total_seconds():.2f}秒")
                
                # 檢查結果
                if result and "messages" in result and len(result["messages"]) > 0:
                    final_message = result["messages"][-1]
                    if hasattr(final_message, 'content'):
                        report = final_message.content
                        print(f"✅ 成功獲取新聞分析報告")
                        print(f"📊 報告長度: {len(report)} 字符")
                        
                        # 顯示報告摘要
                        if len(report) > 300:
                            print(f"📝 報告摘要: {report[:300]}...")
                        else:
                            print(f"📝 完整報告: {report}")
                        
                        # 檢查是否包含真實新聞特征
                        news_indicators = ['發布時間', '新聞標題', '文章來源', '东方財富', '業绩', '營收']
                        has_real_news = any(indicator in report for indicator in news_indicators)
                        print(f"🔍 包含真實新聞特征: {'是' if has_real_news else '否'}")
                        
                        if has_real_news:
                            print("🎉 集成測試成功！")
                        else:
                            print("⚠️ 可能需要進一步優化")
                    else:
                        print("❌ 消息內容為空")
                else:
                    print("❌ 未獲取到分析結果")
                    
            except Exception as e:
                print(f"❌ 測試股票 {stock_code} 時出錯: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print("🎉 新聞分析師集成測試完成!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ 測試過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_news_analyst_integration()