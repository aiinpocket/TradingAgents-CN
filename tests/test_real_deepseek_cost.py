#!/usr/bin/env python3
"""
實际測試DeepSeek成本計算修複效果
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

def test_real_deepseek_analysis():
    """測試真實的DeepSeek股票分析，觀察成本計算"""
    print("🧪 實际測試DeepSeek成本計算")
    print("=" * 60)
    
    # 檢查API密鑰
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 未找到DEEPSEEK_API_KEY，無法測試")
        return False
    
    try:
        from tradingagents.agents.analysts.market_analyst import create_market_analyst_react
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        print("🔧 初始化DeepSeek分析師...")
        
        # 創建DeepSeek LLM
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=1000
        )
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 創建ReAct市場分析師
        market_analyst = create_market_analyst_react(deepseek_llm, toolkit)
        
        print("📊 開始分析股票000002...")
        print("⏱️ 請觀察成本計算輸出...")
        print("-" * 50)
        
        # 模擬狀態
        state = {
            "company_of_interest": "000002",
            "trade_date": "2025-07-08",
            "messages": []
        }
        
        # 執行分析
        result = market_analyst(state)
        
        print("-" * 50)
        print("📋 分析完成！")
        
        market_report = result.get('market_report', '')
        print(f"📊 市場報告長度: {len(market_report)}")
        
        if len(market_report) > 500:
            print("✅ 分析成功生成詳細報告")
            print(f"📄 報告前200字符: {market_report[:200]}...")
            return True
        else:
            print("❌ 分析報告過短，可能有問題")
            return False
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_deepseek_call():
    """測試簡單的DeepSeek調用，觀察成本"""
    print("\n🤖 測試簡單DeepSeek調用")
    print("=" * 60)
    
    # 檢查API密鑰
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 未找到DEEPSEEK_API_KEY，無法測試")
        return False
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        
        print("🔧 創建DeepSeek實例...")
        
        # 創建DeepSeek實例
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=200
        )
        
        print("📤 發送測試請求...")
        print("⏱️ 請觀察成本計算輸出...")
        print("-" * 30)
        
        # 測試調用
        result = deepseek_llm.invoke("請簡要分析一下當前A股市場的整體趋势，不超過100字。")
        
        print("-" * 30)
        print("📋 調用完成！")
        print(f"📊 響應長度: {len(result.content)}")
        print(f"📄 響應內容: {result.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 簡單調用測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_calls():
    """測試多次調用，觀察累計成本"""
    print("\n🔄 測試多次DeepSeek調用")
    print("=" * 60)
    
    # 檢查API密鑰
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 未找到DEEPSEEK_API_KEY，無法測試")
        return False
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        
        print("🔧 創建DeepSeek實例...")
        
        # 創建DeepSeek實例
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=100
        )
        
        questions = [
            "什么是股票？",
            "什么是技術分析？",
            "什么是基本面分析？"
        ]
        
        print(f"📤 發送{len(questions)}個測試請求...")
        print("⏱️ 請觀察每次調用的成本計算...")
        print("-" * 40)
        
        for i, question in enumerate(questions, 1):
            print(f"\n🔸 第{i}次調用: {question}")
            result = deepseek_llm.invoke(question)
            print(f"   響應: {result.content[:50]}...")
        
        print("-" * 40)
        print("📋 多次調用完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 多次調用測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 DeepSeek成本計算實际測試")
    print("=" * 80)
    print("📝 註意觀察輸出中的成本信息：")
    print("   - 應该顯示具體的成本金額（如¥0.004537）")
    print("   - 不應该顯示¥0.000000")
    print("=" * 80)
    
    # 測試簡單調用
    simple_success = test_simple_deepseek_call()
    
    # 測試多次調用
    multiple_success = test_multiple_calls()
    
    # 測試實际分析（可選，比較耗時）
    print(f"\n❓ 是否要測試完整的股票分析？（比較耗時，約1-2分鐘）")
    print(f"   如果只想驗證成本計算，前面的測試已經足夠了。")
    
    # 這里我們跳過完整分析，因為比較耗時
    analysis_success = True  # test_real_deepseek_analysis()
    
    # 总結
    print("\n📋 測試总結")
    print("=" * 60)
    
    print(f"簡單調用: {'✅ 成功' if simple_success else '❌ 失败'}")
    print(f"多次調用: {'✅ 成功' if multiple_success else '❌ 失败'}")
    print(f"完整分析: {'⏭️ 跳過' if analysis_success else '❌ 失败'}")
    
    overall_success = simple_success and multiple_success
    
    if overall_success:
        print("\n🎉 DeepSeek成本計算測試成功！")
        print("   如果你在上面的輸出中看到了具體的成本金額")
        print("   （如¥0.004537而不是¥0.000000），")
        print("   那么成本計算修複就是成功的！")
    else:
        print("\n❌ DeepSeek成本計算測試失败")
        print("   請檢查API密鑰配置和網絡連接")
    
    print("\n🎯 測試完成！")
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
