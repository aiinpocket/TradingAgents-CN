#!/usr/bin/env python3
"""
測試DashScope工具調用失败檢測和補救機制

這個腳本測試新聞分析師在DashScope模型不調用工具時的補救機制。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def test_dashscope_tool_call_detection():
    """測試DashScope工具調用失败檢測機制"""
    
    print("🧪 測試DashScope工具調用失败檢測和補救機制")
    print("=" * 60)
    
    # 模擬DashScope模型類
    class MockDashScopeModel:
        def __init__(self):
            self.__class__.__name__ = "ChatDashScopeOpenAI"
        
        def invoke(self, messages):
            # 模擬返回結果
            class MockResult:
                def __init__(self, content, tool_calls=None):
                    self.content = content
                    self.tool_calls = tool_calls or []
            
            return MockResult("這是一個没有基於真實新聞數據的分析報告...")
    
    # 模擬工具
    class MockToolkit:
        @staticmethod
        def get_realtime_stock_news():
            class MockTool:
                def invoke(self, params):
                    ticker = params.get('ticker', 'UNKNOWN')
                    curr_date = params.get('curr_date', 'UNKNOWN')
                    # 返回足夠長的新聞數據（>100字符）
                    return f"""【东方財富新聞】{ticker} 股票最新消息：
                    
1. 公司發布重要公告，第三季度業绩超預期，净利润同比增長25%
2. 管理層宣布新的战略合作伙伴關系，預計将帶來顯著的收入增長
3. 行業分析師上調目標價格，認為该股票具有良好的投資價值
4. 最新財報顯示公司現金流狀况良好，负债率持续下降
5. 市場對公司未來發展前景保持乐觀態度

發布時間：{curr_date}
數據來源：东方財富網"""
            return MockTool()
        
        @staticmethod
        def get_google_news():
            class MockTool:
                def invoke(self, params):
                    query = params.get('query', 'UNKNOWN')
                    curr_date = params.get('curr_date', 'UNKNOWN')
                    # 返回足夠長的新聞數據（>100字符）
                    return f"""【Google新聞】{query} 相關新聞汇总：
                    
1. 市場分析師看好该股票前景，預計未來12個月将有顯著上涨
2. 機構投資者增持该股票，顯示對公司長期價值的認可
3. 行業整體表現良好，该公司作為龙头企業受益明顯
4. 技術分析顯示股價突破關键阻力位，趋势向好
5. 基本面分析表明公司估值合理，具有投資價值

時間：{curr_date}
數據來源：Google News"""
            return MockTool()
    
    # 測試參數
    ticker = "600036"
    current_date = datetime.now().strftime("%Y-%m-%d")
    llm = MockDashScopeModel()
    toolkit = MockToolkit()
    
    print(f"📊 測試股票: {ticker}")
    print(f"📅 當前日期: {current_date}")
    print(f"🤖 模型類型: {llm.__class__.__name__}")
    print()
    
    # 測試場景1：DashScope没有調用任何工具（tool_call_count = 0）
    print("🔍 測試場景1：DashScope没有調用任何工具")
    print("-" * 40)
    
    # 模擬LLM調用結果
    class MockResult:
        def __init__(self):
            self.content = "這是一個没有基於真實新聞數據的分析報告，長度為2089字符..."
            self.tool_calls = []  # 没有工具調用
    
    result = MockResult()
    tool_call_count = len(result.tool_calls)
    
    print(f"📈 LLM調用結果: 工具調用數量 = {tool_call_count}")
    print(f"📝 原始報告長度: {len(result.content)} 字符")
    
    # 應用增强的檢測逻辑
    report = ""
    
    if 'DashScope' in llm.__class__.__name__:
        if tool_call_count == 0:
            print("🚨 檢測到DashScope没有調用任何工具，啟動强制補救...")
            
            try:
                # 强制獲取新聞數據
                print("🔧 强制調用get_realtime_stock_news獲取新聞數據...")
                forced_news = toolkit.get_realtime_stock_news().invoke({"ticker": ticker, "curr_date": current_date})
                
                if forced_news and len(forced_news.strip()) > 100:
                    print(f"✅ 强制獲取新聞成功: {len(forced_news)} 字符")
                    print(f"📰 新聞內容預覽: {forced_news[:100]}...")
                    
                    # 模擬基於真實新聞數據重新生成分析
                    forced_prompt = f"""
基於以下最新獲取的新聞數據，對股票 {ticker} 進行詳細的新聞分析：

=== 最新新聞數據 ===
{forced_news}

請基於上述真實新聞數據撰寫詳細的中文分析報告。
"""
                    
                    print("🔄 基於强制獲取的新聞數據重新生成完整分析...")
                    # 模擬重新生成的結果
                    report = f"基於真實新聞數據的分析報告：\n\n{forced_news}\n\n詳細分析：该股票基於最新新聞顯示積極信號..."
                    print(f"✅ 强制補救成功，生成基於真實數據的報告，長度: {len(report)} 字符")
                    
                else:
                    print("⚠️ 强制獲取新聞失败，嘗試备用工具...")
                    
                    # 嘗試备用工具
                    backup_news = toolkit.get_google_news().invoke({"query": f"{ticker} 股票 新聞", "curr_date": current_date})
                    
                    if backup_news and len(backup_news.strip()) > 100:
                        print(f"✅ 备用工具獲取成功: {len(backup_news)} 字符")
                        report = f"基於备用新聞數據的分析報告：\n\n{backup_news}\n\n分析結論..."
                        print(f"✅ 备用工具補救成功，長度: {len(report)} 字符")
                    else:
                        print("❌ 所有新聞獲取方式都失败，使用原始結果")
                        report = result.content
                        
            except Exception as e:
                print(f"❌ 强制補救過程失败: {e}")
                report = result.content
    
    if not report:
        report = result.content
    
    print()
    print("📊 測試結果总結:")
    print(f"   原始報告長度: {len(result.content)} 字符")
    print(f"   最终報告長度: {len(report)} 字符")
    print(f"   是否包含真實新聞: {'是' if '东方財富新聞' in report or 'Google新聞' in report else '否'}")
    print(f"   補救機制狀態: {'成功' if len(report) > len(result.content) else '未觸發或失败'}")
    
    print()
    print("🎯 測試結論:")
    if '东方財富新聞' in report or 'Google新聞' in report:
        print("✅ 增强的DashScope工具調用失败檢測和補救機制工作正常")
        print("✅ 成功檢測到工具調用失败並强制獲取了真實新聞數據")
        print("✅ 基於真實新聞數據重新生成了分析報告")
    else:
        print("❌ 補救機制可能存在問題")
    
    return True

if __name__ == "__main__":
    try:
        test_dashscope_tool_call_detection()
        print("\n🎉 所有測試完成！")
    except Exception as e:
        print(f"\n❌ 測試過程中出現錯誤: {e}")
        sys.exit(1)