#!/usr/bin/env python3
"""
測試信號處理器的調試腳本
"""

import sys
import os
sys.path.append('..')

def test_signal_processor():
    """測試信號處理器功能"""
    print("🔍 測試信號處理器...")
    
    try:
        from tradingagents.graph.signal_processing import SignalProcessor
        from tradingagents.llm_adapters import ChatDashScope
        
        # 創建LLM實例
        llm = ChatDashScope(
            model="qwen-plus-latest",
            temperature=0.1,
            max_tokens=1000
        )
        
        # 創建信號處理器
        processor = SignalProcessor(llm)
        print("✅ 信號處理器創建成功")
        
        # 測試信號
        test_signal = """
        基於全面分析，我建议對该股票採取持有策略。
        
        投資建议：持有
        置信度：75%
        目標價位：¥45.50
        風險評分：40%
        
        主要理由：
        1. 技術面顯示上升趋势
        2. 基本面穩健
        3. 市場情绪積極
        """
        
        print(f"\n📊 測試信號內容:")
        print(test_signal)
        
        # 處理信號
        print(f"\n🔄 開始處理信號...")
        result = processor.process_signal(test_signal, "000001")
        
        print(f"\n✅ 處理結果:")
        print(f"類型: {type(result)}")
        print(f"內容: {result}")
        
        # 檢查結果結構
        if isinstance(result, dict):
            print(f"\n📋 結果詳情:")
            for key, value in result.items():
                print(f"  {key}: {value}")
        
        return result
        
    except Exception as e:
        print(f"❌ 測試失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def test_trading_graph():
    """測試完整的交易圖"""
    print("\n" + "="*50)
    print("🔍 測試完整交易圖...")
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        config['llm_provider'] = '阿里百炼'
        config['quick_think_llm'] = 'qwen-plus-latest'
        config['deep_think_llm'] = 'qwen-plus-latest'
        
        print(f"📊 配置信息:")
        print(f"  LLM提供商: {config['llm_provider']}")
        print(f"  快速模型: {config['quick_think_llm']}")
        print(f"  深度模型: {config['deep_think_llm']}")
        
        # 創建交易圖
        print(f"\n🔄 創建交易圖...")
        graph = TradingAgentsGraph(analysts=['market'], config=config, debug=False)
        print("✅ 交易圖創建成功")
        
        # 測試信號處理器
        print(f"\n🔄 測試信號處理器...")
        test_signal = "推薦：买入\n目標價位：¥50.00\n置信度：80%\n風險評分：30%"
        result = graph.process_signal(test_signal, "000001")
        
        print(f"✅ 信號處理結果:")
        print(f"類型: {type(result)}")
        print(f"內容: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ 測試失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 開始信號處理器調試測試")
    print("="*50)
    
    # 檢查API密鑰
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 請設置 DASHSCOPE_API_KEY 環境變量")
        sys.exit(1)
    
    print(f"✅ API密鑰已配置: {api_key[:10]}...")
    
    # 測試信號處理器
    result1 = test_signal_processor()
    
    # 測試交易圖
    result2 = test_trading_graph()
    
    print("\n" + "="*50)
    print("🎯 測試总結:")
    print(f"信號處理器測試: {'✅ 成功' if result1 else '❌ 失败'}")
    print(f"交易圖測試: {'✅ 成功' if result2 else '❌ 失败'}")
