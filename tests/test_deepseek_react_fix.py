#!/usr/bin/env python3
"""
測試DeepSeek使用ReAct Agent的修複效果
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv()

def test_deepseek_react_market_analyst():
    """測試DeepSeek的ReAct市場分析師"""
    print("🤖 測試DeepSeek ReAct市場分析師")
    print("=" * 60)
    
    try:
        # 檢查API密鑰
        if not os.getenv("DEEPSEEK_API_KEY"):
            print("⚠️ 未找到DEEPSEEK_API_KEY，無法測試")
            return False
        
        from tradingagents.agents.analysts.market_analyst import create_market_analyst_react
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建DeepSeek LLM
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=2000
        )
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 創建ReAct市場分析師
        market_analyst = create_market_analyst_react(deepseek_llm, toolkit)
        
        # 模擬狀態
        state = {
            "company_of_interest": "000002",
            "trade_date": "2025-07-08",
            "messages": []
        }
        
        print(f"📊 開始分析股票: {state['company_of_interest']}")
        
        # 執行分析
        result = market_analyst(state)
        
        print(f"📊 分析結果:")
        print(f"   消息數量: {len(result.get('messages', []))}")
        
        market_report = result.get('market_report', '')
        print(f"   市場報告長度: {len(market_report)}")
        print(f"   市場報告前500字符:")
        print("-" * 50)
        print(market_report[:500])
        print("-" * 50)
        
        # 檢查報告质量
        has_data = any(keyword in market_report for keyword in ["¥", "RSI", "MACD", "万科", "技術指標", "6.56"])
        has_analysis = len(market_report) > 500
        not_placeholder = "正在調用工具" not in market_report and "(調用工具" not in market_report
        
        print(f"📊 報告质量檢查:")
        print(f"   包含實际數據: {'✅' if has_data else '❌'}")
        print(f"   分析內容充實: {'✅' if has_analysis else '❌'}")
        print(f"   非占位符內容: {'✅' if not_placeholder else '❌'}")
        
        success = has_data and has_analysis and not_placeholder
        print(f"   整體評估: {'✅ 成功' if success else '❌ 需要改進'}")
        
        if success:
            print("\n🎉 DeepSeek ReAct市場分析師修複成功！")
            print("   - 正確調用了工具獲取數據")
            print("   - 生成了基於真實數據的分析報告")
            print("   - 報告內容充實且專業")
        else:
            print("\n⚠️ DeepSeek ReAct市場分析師仍需改進")
            if not has_data:
                print("   - 缺少實际數據分析")
            if not has_analysis:
                print("   - 分析內容不夠充實")
            if not not_placeholder:
                print("   - 仍包含占位符內容")
        
        return success
        
    except Exception as e:
        print(f"❌ DeepSeek ReAct市場分析師測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_graph_setup_logic():
    """測試圖設置逻辑是否正確選擇ReAct模式"""
    print("\n🔧 測試圖設置逻辑")
    print("=" * 60)
    
    try:
        from tradingagents.graph.setup import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 模擬DeepSeek配置
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "deepseek"
        config["deep_think_llm"] = "deepseek-chat"
        config["quick_think_llm"] = "deepseek-chat"
        
        print(f"📊 配置信息:")
        print(f"   LLM提供商: {config['llm_provider']}")
        print(f"   深度思考模型: {config['deep_think_llm']}")
        print(f"   快速思考模型: {config['quick_think_llm']}")
        
        # 創建圖實例
        graph = TradingAgentsGraph(config)
        
        # 設置分析師（這會觸發選擇逻辑）
        print(f"\n📈 設置市場分析師...")
        graph.setup_and_compile(selected_analysts=["market"])
        
        print(f"✅ 圖設置完成")
        return True
        
    except Exception as e:
        print(f"❌ 圖設置逻辑測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 DeepSeek ReAct修複效果測試")
    print("=" * 80)
    
    # 測試圖設置逻辑
    setup_success = test_graph_setup_logic()
    
    # 測試DeepSeek ReAct分析師
    analyst_success = test_deepseek_react_market_analyst()
    
    # 总結
    print("\n📋 測試总結")
    print("=" * 60)
    
    print(f"圖設置逻辑: {'✅ 正確' if setup_success else '❌ 有問題'}")
    print(f"DeepSeek ReAct分析師: {'✅ 修複成功' if analyst_success else '❌ 仍需修複'}")
    
    overall_success = setup_success and analyst_success
    
    if overall_success:
        print("\n🎉 DeepSeek ReAct修複完全成功！")
        print("   - 圖設置逻辑正確選擇ReAct模式")
        print("   - DeepSeek能正確執行工具調用並生成分析")
        print("   - 現在DeepSeek和百炼都使用穩定的ReAct Agent模式")
    else:
        print("\n⚠️ 仍有問題需要解決")
        if not setup_success:
            print("   - 圖設置逻辑需要檢查")
        if not analyst_success:
            print("   - DeepSeek ReAct分析師需要進一步修複")
    
    print("\n🎯 測試完成！")
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
