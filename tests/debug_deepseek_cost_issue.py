#!/usr/bin/env python3
"""
調試DeepSeek成本計算問題
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

def debug_config_manager():
    """調試配置管理器"""
    print("🔧 調試配置管理器")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import ConfigManager
        
        # 創建配置管理器
        config_manager = ConfigManager()
        
        print(f"📁 配置目錄: {config_manager.config_dir}")
        print(f"📄 定價文件: {config_manager.pricing_file}")
        print(f"📄 定價文件存在: {config_manager.pricing_file.exists()}")
        
        # 加載定價配置
        pricing_configs = config_manager.load_pricing()
        print(f"📊 加載的定價配置數量: {len(pricing_configs)}")
        
        # 查找DeepSeek配置
        deepseek_configs = [p for p in pricing_configs if p.provider == "deepseek"]
        print(f"📊 DeepSeek定價配置數量: {len(deepseek_configs)}")
        
        for config in deepseek_configs:
            print(f"   - 提供商: {config.provider}")
            print(f"   - 模型: {config.model_name}")
            print(f"   - 輸入價格: {config.input_price_per_1k}")
            print(f"   - 輸出價格: {config.output_price_per_1k}")
            print(f"   - 貨币: {config.currency}")
        
        # 測試成本計算
        print(f"\n💰 測試成本計算:")
        cost = config_manager.calculate_cost(
            provider="deepseek",
            model_name="deepseek-chat",
            input_tokens=2272,
            output_tokens=1215
        )
        print(f"   計算結果: ¥{cost:.6f}")
        
        if cost == 0.0:
            print(f"❌ 成本計算返回0，檢查匹配逻辑...")
            
            # 詳細檢查匹配逻辑
            for pricing in pricing_configs:
                print(f"   檢查配置: provider='{pricing.provider}', model='{pricing.model_name}'")
                if pricing.provider == "deepseek" and pricing.model_name == "deepseek-chat":
                    print(f"   ✅ 找到匹配配置!")
                    input_cost = (2272 / 1000) * pricing.input_price_per_1k
                    output_cost = (1215 / 1000) * pricing.output_price_per_1k
                    total_cost = input_cost + output_cost
                    print(f"   輸入成本: {input_cost:.6f}")
                    print(f"   輸出成本: {output_cost:.6f}")
                    print(f"   总成本: {total_cost:.6f}")
                    break
            else:
                print(f"   ❌ 未找到匹配的配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置管理器調試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_token_tracker():
    """調試Token跟蹤器"""
    print("\n📊 調試Token跟蹤器")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import ConfigManager, TokenTracker
        
        # 創建配置管理器和Token跟蹤器
        config_manager = ConfigManager()
        token_tracker = TokenTracker(config_manager)
        
        print(f"🔧 Token跟蹤器創建成功")
        
        # 檢查設置
        settings = config_manager.load_settings()
        cost_tracking_enabled = settings.get("enable_cost_tracking", True)
        print(f"📊 成本跟蹤啟用: {cost_tracking_enabled}")
        
        # 測試跟蹤使用
        print(f"💰 測試Token跟蹤...")
        usage_record = token_tracker.track_usage(
            provider="deepseek",
            model_name="deepseek-chat",
            input_tokens=2272,
            output_tokens=1215,
            session_id="debug_session",
            analysis_type="debug_analysis"
        )
        
        if usage_record:
            print(f"✅ Token跟蹤成功")
            print(f"   提供商: {usage_record.provider}")
            print(f"   模型: {usage_record.model_name}")
            print(f"   輸入tokens: {usage_record.input_tokens}")
            print(f"   輸出tokens: {usage_record.output_tokens}")
            print(f"   成本: ¥{usage_record.cost:.6f}")
            
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
        print(f"❌ Token跟蹤器調試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_deepseek_adapter():
    """調試DeepSeek適配器"""
    print("\n🤖 調試DeepSeek適配器")
    print("=" * 50)
    
    # 檢查API密鑰
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️ 未找到DEEPSEEK_API_KEY，跳過適配器調試")
        return True
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        
        print(f"🔧 創建DeepSeek適配器...")
        
        # 創建DeepSeek實例
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=100
        )
        
        print(f"📊 模型名稱: {deepseek_llm.model_name}")
        
        # 檢查TOKEN_TRACKING_ENABLED
        from tradingagents.llm_adapters.deepseek_adapter import TOKEN_TRACKING_ENABLED
        print(f"📊 Token跟蹤啟用: {TOKEN_TRACKING_ENABLED}")
        
        # 測試調用
        print(f"📤 發送測試請求...")
        result = deepseek_llm.invoke("測試")
        
        print(f"📊 調用完成")
        print(f"   響應長度: {len(result.content)}")
        
        return True
        
    except Exception as e:
        print(f"❌ DeepSeek適配器調試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def debug_model_name_issue():
    """調試模型名稱匹配問題"""
    print("\n🔍 調試模型名稱匹配問題")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import ConfigManager
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        
        # 創建配置管理器
        config_manager = ConfigManager()
        
        # 創建DeepSeek實例
        deepseek_llm = ChatDeepSeek(model="deepseek-chat")
        
        print(f"📊 適配器中的模型名稱: '{deepseek_llm.model_name}'")
        
        # 加載定價配置
        pricing_configs = config_manager.load_pricing()
        
        print(f"📊 定價配置中的DeepSeek模型:")
        for config in pricing_configs:
            if config.provider == "deepseek":
                print(f"   - 模型名稱: '{config.model_name}'")
                print(f"   - 匹配檢查: {config.model_name == deepseek_llm.model_name}")
        
        # 手動測試匹配
        print(f"\n💰 手動測試成本計算:")
        cost = config_manager.calculate_cost(
            provider="deepseek",
            model_name=deepseek_llm.model_name,
            input_tokens=100,
            output_tokens=50
        )
        print(f"   使用適配器模型名稱: ¥{cost:.6f}")
        
        cost2 = config_manager.calculate_cost(
            provider="deepseek",
            model_name="deepseek-chat",
            input_tokens=100,
            output_tokens=50
        )
        print(f"   使用硬編碼模型名稱: ¥{cost2:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型名稱調試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 DeepSeek成本計算問題深度調試")
    print("=" * 80)
    
    # 調試配置管理器
    config_success = debug_config_manager()
    
    # 調試Token跟蹤器
    tracker_success = debug_token_tracker()
    
    # 調試模型名稱匹配
    model_success = debug_model_name_issue()
    
    # 調試適配器
    adapter_success = debug_deepseek_adapter()
    
    # 总結
    print("\n📋 調試总結")
    print("=" * 60)
    
    print(f"配置管理器: {'✅ 正常' if config_success else '❌ 有問題'}")
    print(f"Token跟蹤器: {'✅ 正常' if tracker_success else '❌ 有問題'}")
    print(f"模型名稱匹配: {'✅ 正常' if model_success else '❌ 有問題'}")
    print(f"適配器調試: {'✅ 正常' if adapter_success else '❌ 有問題'}")
    
    overall_success = config_success and tracker_success and model_success and adapter_success
    
    if overall_success:
        print("\n🤔 所有組件都正常，但實际使用時成本為0...")
        print("   可能的原因:")
        print("   1. 在實际分析流程中使用了不同的配置目錄")
        print("   2. 某個地方覆蓋了配置")
        print("   3. 有緩存問題")
        print("   4. 模型名稱在某個地方被修改了")
    else:
        print("\n❌ 發現問題，請檢查上述失败的組件")
    
    print("\n🎯 調試完成！")
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
