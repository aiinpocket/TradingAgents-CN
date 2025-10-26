#!/usr/bin/env python3
"""
驗證DeepSeek成本計算修複
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

def test_deepseek_cost_calculation():
    """測試DeepSeek成本計算"""
    print("🧪 測試DeepSeek成本計算修複")
    print("=" * 50)
    
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("⚠️ 未找到DEEPSEEK_API_KEY，跳過測試")
        return False
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        from tradingagents.config.config_manager import config_manager
        
        # 獲取初始統計
        initial_stats = config_manager.get_usage_statistics(1)
        initial_cost = initial_stats.get("total_cost", 0)
        
        print(f"📊 初始成本: ¥{initial_cost:.6f}")
        
        # 創建DeepSeek實例
        llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=100
        )
        
        # 測試多次調用
        test_cases = [
            "什么是股票？",
            "請簡單解釋市盈率的含義。",
            "分析一下投資風險。"
        ]
        
        total_expected_cost = 0
        
        for i, prompt in enumerate(test_cases, 1):
            print(f"\n🔍 測試 {i}: {prompt}")
            
            response = llm.invoke(
                prompt,
                session_id=f"test_cost_{i}",
                analysis_type="cost_test"
            )
            
            print(f"   響應長度: {len(response.content)}")
        
        # 等待統計更新
        import time
        time.sleep(1)
        
        # 檢查最终統計
        final_stats = config_manager.get_usage_statistics(1)
        final_cost = final_stats.get("total_cost", 0)
        
        cost_increase = final_cost - initial_cost
        
        print(f"\n📊 最终統計:")
        print(f"   初始成本: ¥{initial_cost:.6f}")
        print(f"   最终成本: ¥{final_cost:.6f}")
        print(f"   成本增加: ¥{cost_increase:.6f}")
        
        # 檢查DeepSeek統計
        provider_stats = final_stats.get("provider_stats", {})
        deepseek_stats = provider_stats.get("deepseek", {})
        
        if deepseek_stats:
            print(f"   DeepSeek成本: ¥{deepseek_stats.get('cost', 0):.6f}")
            print(f"   DeepSeek請求: {deepseek_stats.get('requests', 0)}")
            print(f"   DeepSeek Token: {deepseek_stats.get('tokens', 0)}")
        
        # 驗證成本是否合理
        if cost_increase > 0:
            print(f"\n✅ 成本計算修複成功！")
            print(f"   每次調用平均成本: ¥{cost_increase/len(test_cases):.6f}")
            return True
        else:
            print(f"\n❌ 成本計算仍有問題")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cost_precision():
    """測試成本精度顯示"""
    print("\n🔍 測試成本精度顯示")
    print("-" * 30)
    
    from tradingagents.config.config_manager import ConfigManager
    
    config_manager = ConfigManager()
    
    # 測試小額成本計算
    test_cases = [
        (10, 5),    # 很小的token數
        (100, 50),  # 小的token數
        (1000, 500), # 中等token數
        (2000, 1000) # 較大token數
    ]
    
    for input_tokens, output_tokens in test_cases:
        cost = config_manager.calculate_cost("deepseek", "deepseek-chat", input_tokens, output_tokens)
        print(f"   {input_tokens:4d}+{output_tokens:4d} tokens = ¥{cost:.6f}")

def main():
    """主函數"""
    success1 = test_deepseek_cost_calculation()
    test_cost_precision()
    
    print("\n" + "=" * 50)
    if success1:
        print("🎉 DeepSeek成本計算修複驗證成功！")
    else:
        print("❌ DeepSeek成本計算仍需修複")
    
    return success1

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
