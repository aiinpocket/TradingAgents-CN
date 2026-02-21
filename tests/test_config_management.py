#!/usr/bin/env python3
"""
配置管理功能測試
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.config.config_manager import ConfigManager, ModelConfig, PricingConfig, TokenTracker

def test_config_manager():
    """測試配置管理器基本功能"""
    print(" 測試配置管理器")
    print("=" * 50)
    
    # 創建臨時目錄用於測試
    with tempfile.TemporaryDirectory() as temp_dir:
        config_manager = ConfigManager(temp_dir)
        
        # 測試模型配置
        print(" 測試模型配置...")
        models = config_manager.load_models()
        assert len(models) > 0, "應該有預設模型配置"
        
        # 添加新模型
        new_model = ModelConfig(
            provider="test_provider",
            model_name="test_model",
            api_key="test_key_123",
            max_tokens=2000,
            temperature=0.5
        )
        
        models.append(new_model)
        config_manager.save_models(models)
        
        # 重新載入驗證
        reloaded_models = config_manager.load_models()
        assert len(reloaded_models) == len(models), "模型數量應該匹配"
        
        test_model = next((m for m in reloaded_models if m.provider == "test_provider"), None)
        assert test_model is not None, "應該找到測試模型"
        assert test_model.api_key == "test_key_123", "API密鑰應該匹配"
        
        print(" 模型配置測試通過")
        
        # 測試定價配置
        print(" 測試定價配置...")
        pricing_configs = config_manager.load_pricing()
        assert len(pricing_configs) > 0, "應該有預設定價配置"
        
        # 添加新定價
        new_pricing = PricingConfig(
            provider="test_provider",
            model_name="test_model",
            input_price_per_1k=0.001,
            output_price_per_1k=0.002,
            currency="CNY"
        )
        
        pricing_configs.append(new_pricing)
        config_manager.save_pricing(pricing_configs)
        
        # 測試成本計算
        cost = config_manager.calculate_cost("test_provider", "test_model", 1000, 500)
        expected_cost = (1000 / 1000) * 0.001 + (500 / 1000) * 0.002
        assert abs(cost - expected_cost) < 0.000001, f"成本計算錯誤: {cost} != {expected_cost}"
        
        print(" 定價配置測試通過")
        
        # 測試使用記錄
        print(" 測試使用記錄...")
        record = config_manager.add_usage_record(
            provider="test_provider",
            model_name="test_model",
            input_tokens=1000,
            output_tokens=500,
            session_id="test_session",
            analysis_type="test_analysis"
        )
        
        assert record.cost == expected_cost, "使用記錄成本應該匹配"
        
        # 測試統計
        stats = config_manager.get_usage_statistics(30)
        assert stats["total_requests"] >= 1, "應該有至少一條使用記錄"
        assert stats["total_cost"] >= expected_cost, "總成本應該包含測試記錄"
        
        print(" 使用記錄測試通過")
        
        # 測試設置
        print(" 測試系統設置...")
        settings = config_manager.load_settings()
        assert "default_provider" in settings, "應該有預設設置"
        
        settings["test_setting"] = "test_value"
        config_manager.save_settings(settings)
        
        reloaded_settings = config_manager.load_settings()
        assert reloaded_settings["test_setting"] == "test_value", "設置應該被保存"
        
        print(" 系統設置測試通過")

def test_token_tracker():
    """測試Token跟蹤器"""
    print("\n 測試Token跟蹤器")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_manager = ConfigManager(temp_dir)
        token_tracker = TokenTracker(config_manager)
        
        # 測試使用跟蹤
        print(" 測試使用跟蹤...")
        record = token_tracker.track_usage(
            model_name="gpt-4o-mini",
            input_tokens=2000,
            output_tokens=1000,
            session_id="test_session_123",
            analysis_type="stock_analysis"
        )
        
        assert record is not None, "應該返回使用記錄"
        assert record.input_tokens == 2000, "輸入token數應該匹配"
        assert record.output_tokens == 1000, "輸出token數應該匹配"
        assert record.cost > 0, "成本應該大於0"
        
        print(" 使用跟蹤測試通過")
        
        # 測試成本估算
        print(" 測試成本估算...")
        estimated_cost = token_tracker.estimate_cost(
            model_name="gpt-4o-mini",
            estimated_input_tokens=1000,
            estimated_output_tokens=500
        )
        
        assert estimated_cost > 0, "估算成本應該大於0"
        
        print(" 成本估算測試通過")
        
        # 測試會話成本
        print(" 測試會話成本...")
        session_cost = token_tracker.get_session_cost("test_session_123")
        assert session_cost == record.cost, "會話成本應該匹配記錄成本"
        
        print(" 會話成本測試通過")

def test_pricing_accuracy():
    """測試定價準確性"""
    print("\n 測試定價準確性")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_manager = ConfigManager(temp_dir)
        
        # 測試不同供應商的定價
        test_cases = [
            ("openai", "gpt-3.5-turbo", 1000, 500),
            ("anthropic", "claude-haiku-4-5", 1000, 500),
        ]
        
        for provider, model, input_tokens, output_tokens in test_cases:
            cost = config_manager.calculate_cost(provider, model, input_tokens, output_tokens)
            print(f" {provider} {model}: {input_tokens}+{output_tokens} tokens = ¥{cost:.6f}")
            
            # 驗證成本計算邏輯
            pricing_configs = config_manager.load_pricing()
            pricing = next((p for p in pricing_configs if p.provider == provider and p.model_name == model), None)
            
            if pricing:
                expected_cost = (input_tokens / 1000) * pricing.input_price_per_1k + (output_tokens / 1000) * pricing.output_price_per_1k
                assert abs(cost - expected_cost) < 0.000001, f"成本計算錯誤: {cost} != {expected_cost}"
            else:
                assert cost == 0.0, f"未知模型應該返回0成本，但得到 {cost}"
        
        print(" 定價準確性測試通過")

def test_usage_statistics():
    """測試使用統計功能"""
    print("\n 測試使用統計功能")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        config_manager = ConfigManager(temp_dir)
        
        # 添加多條使用記錄
        test_records = [
            ("openai", "gpt-3.5-turbo", 1500, 750, "session3", "news_analysis"),
            ("anthropic", "claude-haiku-4-5", 1200, 600, "session4", "social_analysis"),
        ]
        
        total_expected_cost = 0
        for provider, model, input_tokens, output_tokens, session_id, analysis_type in test_records:
            record = config_manager.add_usage_record(
                provider=provider,
                model_name=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                session_id=session_id,
                analysis_type=analysis_type
            )
            total_expected_cost += record.cost
        
        # 測試統計資料
        stats = config_manager.get_usage_statistics(30)
        
        assert stats["total_requests"] == len(test_records), f"請求數應該是 {len(test_records)}"
        print(f" 統計總成本: {stats['total_cost']:.6f}, 預期總成本: {total_expected_cost:.6f}")
        assert abs(stats["total_cost"] - total_expected_cost) < 0.001, "總成本應該匹配"
        
        # 測試按供應商統計
        provider_stats = stats["provider_stats"]
        assert "openai" in provider_stats, "應該有openai統計"
        assert "anthropic" in provider_stats, "應該有anthropic統計"
        
        print(" 使用統計測試通過")

def main():
    """主測試函數"""
    print(" 配置管理功能測試")
    print("=" * 60)
    
    try:
        test_config_manager()
        test_token_tracker()
        test_pricing_accuracy()
        test_usage_statistics()
        
        print("\n 所有測試通過！")
        print("=" * 60)
        print(" 配置管理功能正常")
        print(" Token跟蹤功能正常")
        print(" 成本計算準確")
        print(" 使用統計正確")
        
        return True
        
    except Exception as e:
        print(f"\n 測試失敗: {e}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
