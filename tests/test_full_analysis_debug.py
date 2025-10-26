#!/usr/bin/env python3
"""
運行完整的股票分析，觀察DeepSeek成本計算的詳細日誌
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

def test_full_stock_analysis():
    """運行完整的股票分析"""
    print("🔬 完整股票分析 - DeepSeek成本計算調試")
    print("=" * 80)
    
    # 檢查API密鑰
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 未找到DEEPSEEK_API_KEY，無法測試")
        return False
    
    try:
        from tradingagents.graph.setup import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        print("🔧 初始化交易分析圖...")
        
        # 配置DeepSeek
        config = DEFAULT_CONFIG.copy()
        config.update({
            "llm_provider": "deepseek",
            "deep_think_llm": "deepseek-chat",
            "quick_think_llm": "deepseek-chat",
            "max_debate_rounds": 1,  # 减少轮次，節省時間
            "max_risk_discuss_rounds": 1,
            "online_tools": True,
            "memory_enabled": False
        })
        
        print(f"📊 配置信息:")
        print(f"   LLM提供商: {config['llm_provider']}")
        print(f"   深度思考模型: {config['deep_think_llm']}")
        print(f"   快速思考模型: {config['quick_think_llm']}")
        
        # 創建圖實例
        graph = TradingAgentsGraph(config)
        
        # 設置分析師（只選擇市場分析師，减少複雜度）
        print(f"📈 設置分析師...")
        graph.setup_and_compile(selected_analysts=["market"])
        
        print(f"✅ 圖設置完成")
        
        # 準备輸入
        input_data = {
            "company_of_interest": "300059",  # 东方財富
            "trade_date": "2025-07-08"
        }
        
        print(f"\n📊 開始分析股票: {input_data['company_of_interest']}")
        print(f"📅 交易日期: {input_data['trade_date']}")
        print("\n" + "="*100)
        print("開始完整分析流程，請觀察DeepSeek成本計算的詳細日誌：")
        print("="*100)
        
        # 運行分析
        result = graph.run(input_data)
        
        print("="*100)
        print("分析完成！")
        print("="*100)
        
        # 輸出結果摘要
        if result and "decision" in result:
            decision = result["decision"]
            print(f"\n📋 分析結果摘要:")
            print(f"   投資建议: {decision.get('action', 'N/A')}")
            print(f"   置信度: {decision.get('confidence', 'N/A')}")
            print(f"   目標價格: {decision.get('target_price', 'N/A')}")
            
            if "market_report" in result:
                market_report = result["market_report"]
                print(f"   市場報告長度: {len(market_report)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整分析測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 完整股票分析 - DeepSeek成本計算調試測試")
    print("=" * 80)
    print("📝 這個測試将運行完整的股票分析流程")
    print("📝 請仔細觀察所有的成本計算日誌")
    print("📝 特別註意是否有成本為¥0.000000的情况")
    print("=" * 80)
    
    success = test_full_stock_analysis()
    
    if success:
        print("\n🎉 完整分析測試完成！")
        print("請查看上面的詳細日誌，分析成本計算的完整流程。")
    else:
        print("\n❌ 完整分析測試失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
