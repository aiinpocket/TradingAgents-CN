#!/usr/bin/env python3
"""
測試圖路由修複
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

def test_graph_routing():
    """測試圖路由是否正常工作"""
    print("🔬 測試圖路由修複")
    print("=" * 60)
    
    # 檢查API密鑰
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 未找到DEEPSEEK_API_KEY，無法測試")
        return False
    
    try:
        from tradingagents.graph.setup import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        print("🔧 創建交易分析圖...")
        
        # 配置DeepSeek
        config = DEFAULT_CONFIG.copy()
        config.update({
            "llm_provider": "deepseek",
            "deep_think_llm": "deepseek-chat",
            "quick_think_llm": "deepseek-chat",
            "max_debate_rounds": 1,  # 减少轮次，快速測試
            "max_risk_discuss_rounds": 1,
            "online_tools": False,  # 關闭在線工具，减少複雜度
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
            "company_of_interest": "AAPL",  # 使用美股，减少複雜度
            "trade_date": "2025-07-08"
        }
        
        print(f"\n📊 開始測試分析: {input_data['company_of_interest']}")
        print(f"📅 交易日期: {input_data['trade_date']}")
        print("\n" + "="*60)
        print("開始圖路由測試，觀察是否有KeyError...")
        print("="*60)
        
        # 運行分析
        result = graph.run(input_data)
        
        print("="*60)
        print("圖路由測試完成！")
        print("="*60)
        
        # 輸出結果摘要
        if result and "decision" in result:
            decision = result["decision"]
            print(f"\n📋 分析結果摘要:")
            print(f"   投資建议: {decision.get('action', 'N/A')}")
            print(f"   置信度: {decision.get('confidence', 'N/A')}")
            print(f"   目標價格: {decision.get('target_price', 'N/A')}")
            
            return True
        else:
            print("❌ 未獲得有效的分析結果")
            return False
        
    except KeyError as e:
        print(f"❌ 圖路由KeyError: {e}")
        print("   這表明節點名稱映射仍有問題")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 圖路由修複測試")
    print("=" * 80)
    print("📝 這個測試将驗證圖路由是否正常工作")
    print("📝 主要檢查是否还有KeyError: 'Bull Researcher'錯誤")
    print("=" * 80)
    
    success = test_graph_routing()
    
    if success:
        print("\n🎉 圖路由測試成功！")
        print("   KeyError問題已修複")
    else:
        print("\n❌ 圖路由測試失败")
        print("   需要進一步調試")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
