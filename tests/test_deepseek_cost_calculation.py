#!/usr/bin/env python3
"""
測試DeepSeek成本計算修複
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

def test_deepseek_pricing_config():
    """測試DeepSeek定價配置"""
    print("🔧 測試DeepSeek定價配置")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import ConfigManager
        
        # 創建配置管理器
        config_manager = ConfigManager()
        
        # 加載定價配置
        pricing_configs = config_manager.load_pricing()
        
        print(f"📊 加載的定價配置數量: {len(pricing_configs)}")
        
        # 查找DeepSeek配置
        deepseek_configs = [p for p in pricing_configs if p.provider == "deepseek"]
        
        print(f"📊 DeepSeek定價配置數量: {len(deepseek_configs)}")
        
        for config in deepseek_configs:
            print(f"   模型: {config.model_name}")
            print(f"   輸入價格: ¥{config.input_price_per_1k}/1K tokens")
            print(f"   輸出價格: ¥{config.output_price_per_1k}/1K tokens")
            print(f"   貨币: {config.currency}")
            print()
        
        return len(deepseek_configs) > 0
        
    except Exception as e:
        print(f"❌ 定價配置測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_deepseek_cost_calculation():
    """測試DeepSeek成本計算"""
    print("💰 測試DeepSeek成本計算")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import ConfigManager
        
        # 創建配置管理器
        config_manager = ConfigManager()
        
        # 測試成本計算
        test_cases = [
            {"input_tokens": 1000, "output_tokens": 500},
            {"input_tokens": 2617, "output_tokens": 312},  # 實际使用的token數
            {"input_tokens": 3240, "output_tokens": 320},
            {"input_tokens": 1539, "output_tokens": 103},
        ]
        
        for i, case in enumerate(test_cases, 1):
            input_tokens = case["input_tokens"]
            output_tokens = case["output_tokens"]
            
            cost = config_manager.calculate_cost(
                provider="deepseek",
                model_name="deepseek-chat",
                input_tokens=input_tokens,
                output_tokens=output_tokens
            )
            
            print(f"測試用例 {i}:")
            print(f"   輸入tokens: {input_tokens}")
            print(f"   輸出tokens: {output_tokens}")
            print(f"   計算成本: ¥{cost:.6f}")
            
            # 手動驗證計算
            expected_cost = (input_tokens / 1000) * 0.0014 + (output_tokens / 1000) * 0.0028
            print(f"   預期成本: ¥{expected_cost:.6f}")
            print(f"   計算正確: {'✅' if abs(cost - expected_cost) < 0.000001 else '❌'}")
            print()
            
            if cost == 0.0:
                print(f"❌ 成本計算返回0，說明配置有問題")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 成本計算測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_token_tracker():
    """測試Token跟蹤器"""
    print("📊 測試Token跟蹤器")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import ConfigManager, TokenTracker
        
        # 創建配置管理器和Token跟蹤器
        config_manager = ConfigManager()
        token_tracker = TokenTracker(config_manager)
        
        # 測試跟蹤使用
        usage_record = token_tracker.track_usage(
            provider="deepseek",
            model_name="deepseek-chat",
            input_tokens=1000,
            output_tokens=500,
            session_id="test_session",
            analysis_type="test_analysis"
        )
        
        if usage_record:
            print(f"✅ Token跟蹤成功")
            print(f"   提供商: {usage_record.provider}")
            print(f"   模型: {usage_record.model_name}")
            print(f"   輸入tokens: {usage_record.input_tokens}")
            print(f"   輸出tokens: {usage_record.output_tokens}")
            print(f"   成本: ¥{usage_record.cost:.6f}")
            print(f"   會話ID: {usage_record.session_id}")
            
            if usage_record.cost > 0:
                print(f"✅ 成本計算正確")
                return True
            else:
                print(f"❌ 成本計算仍為0")
                return False
        else:
            print(f"❌ Token跟蹤失败")
            return False
        
    except Exception as e:
        print(f"❌ Token跟蹤器測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_deepseek_adapter_integration():
    """測試DeepSeek適配器集成"""
    print("🤖 測試DeepSeek適配器集成")
    print("=" * 50)
    
    try:
        # 檢查API密鑰
        if not os.getenv("DEEPSEEK_API_KEY"):
            print("⚠️ 未找到DEEPSEEK_API_KEY，跳過適配器測試")
            return True
        
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        
        # 創建DeepSeek實例
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=100
        )
        
        # 測試簡單調用
        print("📤 發送測試請求...")
        result = deepseek_llm.invoke("請用一句話介紹DeepSeek")
        
        print(f"📊 響應類型: {type(result)}")
        print(f"📊 響應內容長度: {len(result.content)}")
        print(f"📊 響應內容: {result.content[:100]}...")
        
        # 檢查是否有成本信息輸出
        print(f"✅ DeepSeek適配器集成測試完成")
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek適配器集成測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 DeepSeek成本計算修複驗證")
    print("=" * 80)
    
    # 測試定價配置
    config_success = test_deepseek_pricing_config()
    
    # 測試成本計算
    calc_success = test_deepseek_cost_calculation()
    
    # 測試Token跟蹤器
    tracker_success = test_token_tracker()
    
    # 測試適配器集成
    adapter_success = test_deepseek_adapter_integration()
    
    # 总結
    print("\n📋 測試总結")
    print("=" * 60)
    
    print(f"定價配置: {'✅ 正確' if config_success else '❌ 有問題'}")
    print(f"成本計算: {'✅ 正確' if calc_success else '❌ 有問題'}")
    print(f"Token跟蹤: {'✅ 正確' if tracker_success else '❌ 有問題'}")
    print(f"適配器集成: {'✅ 正確' if adapter_success else '❌ 有問題'}")
    
    overall_success = config_success and calc_success and tracker_success and adapter_success
    
    if overall_success:
        print("\n🎉 DeepSeek成本計算修複成功！")
        print("   - 定價配置已正確設置")
        print("   - 成本計算逻辑正常工作")
        print("   - Token跟蹤器正確記錄成本")
        print("   - 適配器集成正常")
        print("\n現在DeepSeek的token使用成本應该正確顯示了！")
    else:
        print("\n⚠️ DeepSeek成本計算仍有問題")
        print("   請檢查上述失败的測試項目")
    
    print("\n🎯 測試完成！")
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
