#!/usr/bin/env python3
"""
測試中文輸出功能
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

def test_dashscope_chinese():
    """測試阿里百炼模型的中文輸出"""
    try:
        from tradingagents.llm_adapters import ChatDashScope
        
        print("🧪 測試阿里百炼模型中文輸出")
        print("=" * 50)
        
        # 創建模型實例
        llm = ChatDashScope(
            model="qwen-plus",
            temperature=0.1,
            max_tokens=500
        )
        
        # 測試中文提示詞
        test_prompt = """你是一位專業的股票分析師。請用中文分析苹果公司(AAPL)的投資前景。
        
請重點關註：
1. 公司的競爭優势
2. 市場前景
3. 投資建议

請確保回答使用中文。"""
        
        print("發送測試提示詞...")
        response = llm.invoke(test_prompt)
        
        print("✅ 模型響應成功")
        print(f"響應內容: {response.content[:200]}...")
        
        # 檢查是否包含中文
        chinese_chars = sum(1 for char in response.content if '\u4e00' <= char <= '\u9fff')
        total_chars = len(response.content)
        chinese_ratio = chinese_chars / total_chars if total_chars > 0 else 0
        
        print(f"中文字符比例: {chinese_ratio:.2%}")
        
        if chinese_ratio > 0.3:
            print("✅ 模型正確輸出中文內容")
            return True
        else:
            print("❌ 模型輸出中文比例較低")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_signal_processor_chinese():
    """測試信號處理器的中文輸出"""
    try:
        from tradingagents.graph.signal_processing import SignalProcessor
        from tradingagents.llm_adapters import ChatDashScope
        
        print("\n🧪 測試信號處理器中文輸出")
        print("=" * 50)
        
        # 創建模型實例
        llm = ChatDashScope(
            model="qwen-plus",
            temperature=0.1,
            max_tokens=100
        )
        
        # 創建信號處理器
        processor = SignalProcessor(llm)
        
        # 測試信號
        test_signal = """基於技術分析和基本面分析，苹果公司顯示出强劲的增長潜力。
        建议买入该股票，目標價位200美元。"""
        
        print("處理測試信號...")
        decision = processor.process_signal(test_signal, "AAPL")
        
        print(f"✅ 信號處理成功")
        print(f"決策結果: {decision}")
        
        # 檢查決策是否為中文
        if any(word in decision for word in ['买入', '卖出', '持有']):
            print("✅ 信號處理器輸出中文決策")
            return True
        elif any(word in decision.upper() for word in ['BUY', 'SELL', 'HOLD']):
            print("⚠️ 信號處理器輸出英文決策")
            return False
        else:
            print(f"❓ 未识別的決策格式: {decision}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主測試函數"""
    print("🧪 中文輸出功能測試")
    print("=" * 60)
    
    # 檢查環境變量
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("❌ DASHSCOPE_API_KEY 環境變量未設置")
        return
    
    # 測試基本中文輸出
    success1 = test_dashscope_chinese()
    
    # 測試信號處理器
    success2 = test_signal_processor_chinese()
    
    print(f"\n📊 測試結果:")
    print(f"  基本中文輸出: {'✅ 通過' if success1 else '❌ 失败'}")
    print(f"  信號處理器: {'✅ 通過' if success2 else '❌ 失败'}")
    
    if success1 and success2:
        print("\n🎉 所有測試通過！中文輸出功能正常")
    else:
        print("\n⚠️ 部分測試失败，可能需要進一步調整")

if __name__ == "__main__":
    main()
