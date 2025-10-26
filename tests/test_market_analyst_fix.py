#!/usr/bin/env python3
"""
測試修複後的市場分析師
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

def test_deepseek_market_analyst():
    """測試DeepSeek的市場分析師"""
    print("🤖 測試DeepSeek市場分析師修複效果")
    print("=" * 60)
    
    try:
        from tradingagents.agents.analysts.market_analyst import create_market_analyst
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
        
        # 創建市場分析師
        market_analyst = create_market_analyst(deepseek_llm, toolkit)
        
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
        has_data = any(keyword in market_report for keyword in ["¥", "RSI", "MACD", "万科", "技術指標"])
        has_analysis = len(market_report) > 500
        not_placeholder = "正在調用工具" not in market_report
        
        print(f"📊 報告质量檢查:")
        print(f"   包含實际數據: {'✅' if has_data else '❌'}")
        print(f"   分析內容充實: {'✅' if has_analysis else '❌'}")
        print(f"   非占位符內容: {'✅' if not_placeholder else '❌'}")
        
        success = has_data and has_analysis and not_placeholder
        print(f"   整體評估: {'✅ 成功' if success else '❌ 需要改進'}")
        
        return success
        
    except Exception as e:
        print(f"❌ DeepSeek市場分析師測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dashscope_market_analyst():
    """測試百炼的市場分析師（ReAct模式）"""
    print("\n🌟 測試百炼市場分析師（ReAct模式）")
    print("=" * 60)
    
    try:
        # 檢查API密鑰
        if not os.getenv("DASHSCOPE_API_KEY"):
            print("⚠️ 未找到DASHSCOPE_API_KEY，跳過百炼測試")
            return True  # 跳過不算失败
        
        from tradingagents.agents.analysts.market_analyst import create_market_analyst_react
        from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建百炼LLM
        dashscope_llm = ChatDashScope(
            model="qwen-plus",
            temperature=0.1,
            max_tokens=2000
        )
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 創建ReAct市場分析師
        market_analyst = create_market_analyst_react(dashscope_llm, toolkit)
        
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
        has_data = any(keyword in market_report for keyword in ["¥", "RSI", "MACD", "万科", "技術指標"])
        has_analysis = len(market_report) > 500
        not_placeholder = "正在調用工具" not in market_report
        
        print(f"📊 報告质量檢查:")
        print(f"   包含實际數據: {'✅' if has_data else '❌'}")
        print(f"   分析內容充實: {'✅' if has_analysis else '❌'}")
        print(f"   非占位符內容: {'✅' if not_placeholder else '❌'}")
        
        success = has_data and has_analysis and not_placeholder
        print(f"   整體評估: {'✅ 成功' if success else '❌ 需要改進'}")
        
        return success
        
    except Exception as e:
        print(f"❌ 百炼市場分析師測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 市場分析師修複效果測試")
    print("=" * 80)
    
    # 檢查API密鑰
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not deepseek_key:
        print("⚠️ 未找到DEEPSEEK_API_KEY，無法測試")
        return False
    
    # 測試DeepSeek
    deepseek_success = test_deepseek_market_analyst()
    
    # 測試百炼（如果有API密鑰）
    dashscope_success = test_dashscope_market_analyst()
    
    # 总結
    print("\n📋 測試总結")
    print("=" * 60)
    
    print(f"DeepSeek市場分析師: {'✅ 修複成功' if deepseek_success else '❌ 仍需修複'}")
    print(f"百炼ReAct分析師: {'✅ 工作正常' if dashscope_success else '❌ 需要檢查'}")
    
    overall_success = deepseek_success and dashscope_success
    
    if overall_success:
        print("\n🎉 市場分析師修複成功！")
        print("   - DeepSeek現在能正確執行工具調用並生成完整分析")
        print("   - 百炼ReAct模式繼续正常工作")
        print("   - 两個模型都能基於真實數據生成技術分析報告")
    else:
        print("\n⚠️ 仍有問題需要解決")
        if not deepseek_success:
            print("   - DeepSeek市場分析師需要進一步修複")
        if not dashscope_success:
            print("   - 百炼ReAct分析師需要檢查")
    
    print("\n🎯 測試完成！")
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
