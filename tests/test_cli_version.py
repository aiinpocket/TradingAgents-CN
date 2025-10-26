#!/usr/bin/env python3
"""
測試命令行版本
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

def test_cli_imports():
    """測試CLI模塊導入"""
    print("🔬 測試CLI模塊導入")
    print("=" * 60)
    
    try:
        # 測試導入CLI主模塊
        from cli.main import app, console
        print("✅ CLI主模塊導入成功")
        
        # 測試導入分析師類型
        from cli.models import AnalystType
        print("✅ 分析師類型導入成功")
        
        # 測試導入工具函數
        from cli.utils import get_user_selections
        print("✅ CLI工具函數導入成功")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI模塊導入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_config():
    """測試CLI配置"""
    print("\n🔧 測試CLI配置")
    print("=" * 60)
    
    try:
        from tradingagents.default_config import DEFAULT_CONFIG
        from tradingagents.config.config_manager import config_manager
        
        print("🔧 測試默認配置...")
        print(f"   LLM提供商: {DEFAULT_CONFIG.get('llm_provider', 'N/A')}")
        print(f"   深度思考模型: {DEFAULT_CONFIG.get('deep_think_llm', 'N/A')}")
        print(f"   快速思考模型: {DEFAULT_CONFIG.get('quick_think_llm', 'N/A')}")
        
        print("\n🔧 測試配置管理器...")
        print(f"   配置目錄: {config_manager.config_dir}")
        
        # 測試定價配置
        pricing_configs = config_manager.load_pricing()
        print(f"   定價配置數量: {len(pricing_configs)}")
        
        # 查找DeepSeek配置
        deepseek_configs = [p for p in pricing_configs if p.provider == "deepseek"]
        print(f"   DeepSeek配置數量: {len(deepseek_configs)}")
        
        if deepseek_configs:
            print("✅ CLI可以訪問DeepSeek配置")
            return True
        else:
            print("❌ CLI無法訪問DeepSeek配置")
            return False
        
    except Exception as e:
        print(f"❌ CLI配置測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_graph_creation():
    """測試CLI圖創建"""
    print("\n📊 測試CLI圖創建")
    print("=" * 60)
    
    # 檢查API密鑰
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️ 未找到DEEPSEEK_API_KEY，跳過圖創建測試")
        return True
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        print("🔧 創建測試配置...")
        config = DEFAULT_CONFIG.copy()
        config.update({
            "llm_provider": "deepseek",
            "deep_think_llm": "deepseek-chat",
            "quick_think_llm": "deepseek-chat",
            "max_debate_rounds": 1,
            "max_risk_discuss_rounds": 1,
            "online_tools": False,  # 關闭在線工具，减少複雜度
            "memory_enabled": False
        })
        
        print("📊 創建交易分析圖...")
        # 使用CLI的方式創建圖
        graph = TradingAgentsGraph(
            ["market"],  # 只使用市場分析師
            config=config,
            debug=True
        )
        
        print("✅ CLI圖創建成功")
        return True
        
    except Exception as e:
        print(f"❌ CLI圖創建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_cost_tracking():
    """測試CLI成本跟蹤"""
    print("\n💰 測試CLI成本跟蹤")
    print("=" * 60)
    
    try:
        from tradingagents.config.config_manager import config_manager, token_tracker
        
        print("🔧 測試成本計算...")
        cost = config_manager.calculate_cost(
            provider="deepseek",
            model_name="deepseek-chat",
            input_tokens=1000,
            output_tokens=500
        )
        print(f"   DeepSeek成本: ¥{cost:.6f}")
        
        if cost > 0:
            print("✅ CLI成本計算正常")
            
            print("\n🔧 測試Token跟蹤...")
            usage_record = token_tracker.track_usage(
                provider="deepseek",
                model_name="deepseek-chat",
                input_tokens=100,
                output_tokens=50,
                session_id="cli_test",
                analysis_type="cli_test"
            )
            
            if usage_record and usage_record.cost > 0:
                print(f"   跟蹤記錄成本: ¥{usage_record.cost:.6f}")
                print("✅ CLI Token跟蹤正常")
                return True
            else:
                print("❌ CLI Token跟蹤失败")
                return False
        else:
            print("❌ CLI成本計算為0")
            return False
        
    except Exception as e:
        print(f"❌ CLI成本跟蹤測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_help():
    """測試CLI幫助功能"""
    print("\n❓ 測試CLI幫助功能")
    print("=" * 60)
    
    try:
        from cli.main import app
        
        print("🔧 測試CLI應用創建...")
        print(f"   應用名稱: {app.info.name}")
        print(f"   應用幫助: {app.info.help[:50]}...")
        
        print("✅ CLI幫助功能正常")
        return True
        
    except Exception as e:
        print(f"❌ CLI幫助功能測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 命令行版本測試")
    print("=" * 80)
    print("📝 這個測試将驗證CLI版本是否正常工作")
    print("📝 檢查模塊導入、配置訪問、圖創建等功能")
    print("=" * 80)
    
    # 運行各項測試
    tests = [
        ("模塊導入", test_cli_imports),
        ("配置訪問", test_cli_config),
        ("圖創建", test_cli_graph_creation),
        ("成本跟蹤", test_cli_cost_tracking),
        ("幫助功能", test_cli_help),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name}測試異常: {e}")
            results[test_name] = False
    
    # 总結
    print("\n📋 測試总結")
    print("=" * 60)
    
    for test_name, success in results.items():
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{test_name}: {status}")
    
    overall_success = all(results.values())
    
    if overall_success:
        print("\n🎉 CLI版本測試全部通過！")
        print("   命令行版本可以正常使用")
        print("   建议運行: python -m cli.main analyze")
    else:
        print("\n❌ CLI版本測試有失败項")
        print("   請檢查失败的測試項")
    
    print("\n🎯 測試完成！")
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
