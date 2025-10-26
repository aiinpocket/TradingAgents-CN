#!/usr/bin/env python3
"""
測試配置加載問題
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

def test_pricing_config_loading():
    """測試定價配置加載"""
    print("🔧 測試定價配置加載")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import ConfigManager
        
        # 創建配置管理器
        config_manager = ConfigManager()
        
        print(f"📁 配置目錄: {config_manager.config_dir}")
        print(f"📄 定價文件: {config_manager.pricing_file}")
        print(f"📄 定價文件存在: {config_manager.pricing_file.exists()}")
        
        # 直接讀取文件內容
        if config_manager.pricing_file.exists():
            with open(config_manager.pricing_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"📄 文件內容長度: {len(content)}")
            
            import json
            data = json.loads(content)
            print(f"📊 JSON中的配置數量: {len(data)}")
            
            for i, config in enumerate(data, 1):
                print(f"   {i}. {config['provider']}/{config['model_name']}")
        
        # 使用ConfigManager加載
        print(f"\n📊 使用ConfigManager加載:")
        pricing_configs = config_manager.load_pricing()
        print(f"📊 加載的配置數量: {len(pricing_configs)}")
        
        for i, config in enumerate(pricing_configs, 1):
            print(f"   {i}. {config.provider}/{config.model_name}")
        
        # 查找DeepSeek配置
        deepseek_configs = [p for p in pricing_configs if p.provider == "deepseek"]
        print(f"\n📊 DeepSeek配置數量: {len(deepseek_configs)}")
        
        # 查找百炼配置
        dashscope_configs = [p for p in pricing_configs if p.provider == "dashscope"]
        print(f"📊 百炼配置數量: {len(dashscope_configs)}")
        for config in dashscope_configs:
            print(f"   - {config.model_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置加載測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cost_calculation():
    """測試成本計算"""
    print("\n💰 測試成本計算")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import ConfigManager
        
        config_manager = ConfigManager()
        
        # 測試DeepSeek成本計算
        print("🤖 測試DeepSeek成本計算:")
        deepseek_cost = config_manager.calculate_cost(
            provider="deepseek",
            model_name="deepseek-chat",
            input_tokens=1000,
            output_tokens=500
        )
        print(f"   DeepSeek成本: ¥{deepseek_cost:.6f}")
        
        # 測試百炼成本計算
        print("🌟 測試百炼成本計算:")
        dashscope_cost1 = config_manager.calculate_cost(
            provider="dashscope",
            model_name="qwen-plus",
            input_tokens=1000,
            output_tokens=500
        )
        print(f"   qwen-plus成本: ¥{dashscope_cost1:.6f}")
        
        dashscope_cost2 = config_manager.calculate_cost(
            provider="dashscope",
            model_name="qwen-plus-latest",
            input_tokens=1000,
            output_tokens=500
        )
        print(f"   qwen-plus-latest成本: ¥{dashscope_cost2:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 成本計算測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 配置加載問題調試")
    print("=" * 80)
    
    # 測試配置加載
    loading_success = test_pricing_config_loading()
    
    # 測試成本計算
    calc_success = test_cost_calculation()
    
    # 总結
    print("\n📋 測試总結")
    print("=" * 60)
    
    print(f"配置加載: {'✅ 正常' if loading_success else '❌ 有問題'}")
    print(f"成本計算: {'✅ 正常' if calc_success else '❌ 有問題'}")
    
    overall_success = loading_success and calc_success
    
    if overall_success:
        print("\n🎉 配置系統正常工作！")
        print("   如果實际使用時仍有問題，可能是:")
        print("   1. 使用了不同的配置目錄")
        print("   2. 配置被緩存了")
        print("   3. 模型名稱在某個地方被修改了")
    else:
        print("\n❌ 配置系統有問題，需要修複")
    
    print("\n🎯 測試完成！")
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
