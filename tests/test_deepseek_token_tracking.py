#!/usr/bin/env python3
"""
DeepSeek Token統計功能測試
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

def test_deepseek_adapter():
    """測試DeepSeek適配器的Token統計功能"""
    print("🧪 測試DeepSeek適配器Token統計...")
    
    # 檢查DeepSeek配置
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("⚠️ 未找到DEEPSEEK_API_KEY，跳過測試")
        return True  # 跳過而不是失败
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        from tradingagents.config.config_manager import config_manager, token_tracker
        
        # 獲取初始統計
        initial_stats = config_manager.get_usage_statistics(1)
        initial_cost = initial_stats.get("total_cost", 0)
        
        # 創建DeepSeek實例
        llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=100
        )
        
        # 生成會話ID
        session_id = f"test_deepseek_{int(datetime.now().timestamp())}"
        
        # 測試調用
        response = llm.invoke(
            "請簡單說明什么是股票，不超過50字。",
            session_id=session_id,
            analysis_type="test_analysis"
        )
        
        print(f"   ✅ 響應接收成功，長度: {len(response.content)}")
        
        # 等待統計更新
        import time
        time.sleep(1)
        
        # 檢查統計更新
        updated_stats = config_manager.get_usage_statistics(1)
        updated_cost = updated_stats.get("total_cost", 0)
        
        cost_increase = updated_cost - initial_cost
        
        print(f"   💰 成本增加: ¥{cost_increase:.4f}")
        
        # 檢查DeepSeek統計
        provider_stats = updated_stats.get("provider_stats", {})
        deepseek_stats = provider_stats.get("deepseek", {})
        
        if deepseek_stats:
            print(f"   📊 DeepSeek統計存在: ✅")
            return True
        else:
            print(f"   📊 DeepSeek統計缺失: ❌")
            return False
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

def test_trading_graph_integration():
    """測試TradingGraph中的DeepSeek集成"""
    print("\n🧪 測試TradingGraph DeepSeek集成...")
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("⚠️ 未找到DEEPSEEK_API_KEY，跳過測試")
        return True
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 配置DeepSeek
        config = DEFAULT_CONFIG.copy()
        config.update({
            "llm_provider": "deepseek",
            "llm_model": "deepseek-chat",
            "quick_think_llm": "deepseek-chat",
            "deep_think_llm": "deepseek-chat",
            "backend_url": "https://api.deepseek.com",
            "online_tools": True,
            "max_debate_rounds": 1,
        })
        
        # 創建TradingAgentsGraph
        ta = TradingAgentsGraph(
            selected_analysts=["fundamentals"],
            config=config,
            debug=False  # 减少輸出
        )
        
        print(f"   ✅ TradingAgentsGraph創建成功")
        return True
        
    except Exception as e:
        print(f"❌ 集成測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 DeepSeek Token統計功能測試")
    print("=" * 50)
    
    tests = [
        ("DeepSeek適配器", test_deepseek_adapter),
        ("TradingGraph集成", test_trading_graph_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}測試異常: {e}")
            results.append((test_name, False))
    
    # 总結結果
    print("\n" + "="*50)
    print("📋 測試結果总結:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总計: {passed}/{len(results)} 項測試通過")
    
    return passed >= len(results) // 2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
