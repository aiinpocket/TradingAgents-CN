#!/usr/bin/env python3
"""
調試DeepSeek成本計算問題
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv()

def test_pricing_config():
    """測試定價配置"""
    print("🔍 測試定價配置...")
    
    from tradingagents.config.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    pricing_configs = config_manager.load_pricing()
    
    print(f"📊 加載了 {len(pricing_configs)} 個定價配置:")
    for pricing in pricing_configs:
        if pricing.provider == "deepseek":
            print(f"   ✅ {pricing.provider}/{pricing.model_name}: 輸入¥{pricing.input_price_per_1k}/1K, 輸出¥{pricing.output_price_per_1k}/1K")

def test_cost_calculation():
    """測試成本計算"""
    print("\n🧮 測試成本計算...")
    
    from tradingagents.config.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    
    # 測試DeepSeek成本計算
    test_cases = [
        ("deepseek", "deepseek-chat", 2000, 1000),
        ("deepseek", "deepseek-coder", 1500, 800),
        ("dashscope", "qwen-turbo", 2000, 1000),  # 對比測試
    ]
    
    for provider, model, input_tokens, output_tokens in test_cases:
        cost = config_manager.calculate_cost(provider, model, input_tokens, output_tokens)
        print(f"   {provider}/{model}: {input_tokens}+{output_tokens} tokens = ¥{cost:.6f}")

def test_token_tracking():
    """測試Token跟蹤"""
    print("\n📝 測試Token跟蹤...")
    
    from tradingagents.config.config_manager import token_tracker
    
    # 測試DeepSeek使用記錄
    record = token_tracker.track_usage(
        provider="deepseek",
        model_name="deepseek-chat",
        input_tokens=2000,
        output_tokens=1000,
        session_id="debug_test_001",
        analysis_type="debug_test"
    )
    
    if record:
        print(f"   ✅ 記錄創建成功:")
        print(f"      Provider: {record.provider}")
        print(f"      Model: {record.model_name}")
        print(f"      Tokens: {record.input_tokens}+{record.output_tokens}")
        print(f"      Cost: ¥{record.cost:.6f}")
    else:
        print(f"   ❌ 記錄創建失败")

def test_deepseek_adapter():
    """測試DeepSeek適配器"""
    print("\n🤖 測試DeepSeek適配器...")
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("   ⚠️ 未找到DEEPSEEK_API_KEY，跳過適配器測試")
        return
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        
        # 創建DeepSeek實例
        llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=100
        )
        
        print(f"   ✅ DeepSeek適配器創建成功")
        print(f"      Model: {llm.model_name}")
        print(f"      Base URL: {llm.openai_api_base}")
        
        # 測試簡單調用
        response = llm.invoke(
            "請簡單說明什么是股票，不超過30字。",
            session_id="debug_adapter_test",
            analysis_type="debug_test"
        )
        
        print(f"   ✅ API調用成功，響應長度: {len(response.content)}")
        
    except Exception as e:
        print(f"   ❌ DeepSeek適配器測試失败: {e}")

def check_usage_statistics():
    """檢查使用統計"""
    print("\n📊 檢查使用統計...")
    
    from tradingagents.config.config_manager import config_manager
    
    stats = config_manager.get_usage_statistics(1)
    
    print(f"   总成本: ¥{stats.get('total_cost', 0):.6f}")
    print(f"   总請求: {stats.get('total_requests', 0)}")
    print(f"   总Token: {stats.get('total_tokens', 0)}")
    
    provider_stats = stats.get('provider_stats', {})
    deepseek_stats = provider_stats.get('deepseek', {})
    
    if deepseek_stats:
        print(f"   DeepSeek統計:")
        print(f"      成本: ¥{deepseek_stats.get('cost', 0):.6f}")
        print(f"      請求: {deepseek_stats.get('requests', 0)}")
        print(f"      Token: {deepseek_stats.get('tokens', 0)}")
    else:
        print(f"   ❌ 未找到DeepSeek統計")

def main():
    """主函數"""
    print("🔧 DeepSeek成本計算調試")
    print("=" * 50)
    
    try:
        test_pricing_config()
        test_cost_calculation()
        test_token_tracking()
        test_deepseek_adapter()
        check_usage_statistics()
        
        print("\n" + "=" * 50)
        print("✅ 調試完成")
        
    except Exception as e:
        print(f"\n❌ 調試過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
