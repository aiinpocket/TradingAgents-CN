#!/usr/bin/env python3
"""
測試配置統一
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

def test_config_unification():
    """測試配置統一是否正常工作"""
    print("🔬 測試配置統一")
    print("=" * 60)
    
    try:
        from tradingagents.config.config_manager import config_manager
        
        print("🔧 測試全局配置管理器...")
        
        # 檢查配置目錄
        print(f"📁 配置目錄: {config_manager.config_dir}")
        print(f"📁 配置目錄絕對路徑: {config_manager.config_dir.absolute()}")
        print(f"📄 定價文件: {config_manager.pricing_file}")
        print(f"📄 定價文件存在: {config_manager.pricing_file.exists()}")
        
        # 加載定價配置
        pricing_configs = config_manager.load_pricing()
        print(f"📊 加載的定價配置數量: {len(pricing_configs)}")
        
        # 查找DeepSeek配置
        deepseek_configs = [p for p in pricing_configs if p.provider == "deepseek"]
        print(f"📊 DeepSeek配置數量: {len(deepseek_configs)}")
        
        if deepseek_configs:
            print("✅ 找到DeepSeek配置:")
            for config in deepseek_configs:
                print(f"   - {config.model_name}: 輸入¥{config.input_price_per_1k}/1K, 輸出¥{config.output_price_per_1k}/1K")
        else:
            print("❌ 未找到DeepSeek配置")
        
        # 測試成本計算
        print(f"\n💰 測試成本計算:")
        deepseek_cost = config_manager.calculate_cost(
            provider="deepseek",
            model_name="deepseek-chat",
            input_tokens=1000,
            output_tokens=500
        )
        print(f"   DeepSeek成本: ¥{deepseek_cost:.6f}")
        
        if deepseek_cost > 0:
            print("✅ DeepSeek成本計算正常")
            return True
        else:
            print("❌ DeepSeek成本計算仍為0")
            return False
        
    except Exception as e:
        print(f"❌ 配置統一測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_web_config_access():
    """測試Web界面配置訪問"""
    print("\n🌐 測試Web界面配置訪問")
    print("=" * 60)
    
    try:
        # 模擬Web界面的導入方式
        sys.path.insert(0, str(project_root / "web"))
        
        # 導入Web配置管理页面
        from pages.config_management import config_manager as web_config_manager
        
        print("🔧 測試Web配置管理器...")
        
        # 檢查配置目錄
        print(f"📁 Web配置目錄: {web_config_manager.config_dir}")
        print(f"📁 Web配置目錄絕對路徑: {web_config_manager.config_dir.absolute()}")
        
        # 加載定價配置
        web_pricing_configs = web_config_manager.load_pricing()
        print(f"📊 Web加載的定價配置數量: {len(web_pricing_configs)}")
        
        # 查找DeepSeek配置
        web_deepseek_configs = [p for p in web_pricing_configs if p.provider == "deepseek"]
        print(f"📊 Web DeepSeek配置數量: {len(web_deepseek_configs)}")
        
        if web_deepseek_configs:
            print("✅ Web界面找到DeepSeek配置")
            return True
        else:
            print("❌ Web界面未找到DeepSeek配置")
            return False
        
    except Exception as e:
        print(f"❌ Web配置訪問測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_consistency():
    """測試配置一致性"""
    print("\n🔄 測試配置一致性")
    print("=" * 60)
    
    try:
        from tradingagents.config.config_manager import config_manager
        
        # 從不同路徑導入，應该使用相同的配置
        sys.path.insert(0, str(project_root / "web"))
        from pages.config_management import config_manager as web_config_manager
        
        # 比較配置目錄
        main_config_dir = config_manager.config_dir.absolute()
        web_config_dir = web_config_manager.config_dir.absolute()
        
        print(f"📁 主配置目錄: {main_config_dir}")
        print(f"📁 Web配置目錄: {web_config_dir}")
        
        if main_config_dir == web_config_dir:
            print("✅ 配置目錄一致")
            
            # 比較配置數量
            main_configs = config_manager.load_pricing()
            web_configs = web_config_manager.load_pricing()
            
            print(f"📊 主配置數量: {len(main_configs)}")
            print(f"📊 Web配置數量: {len(web_configs)}")
            
            if len(main_configs) == len(web_configs):
                print("✅ 配置數量一致")
                return True
            else:
                print("❌ 配置數量不一致")
                return False
        else:
            print("❌ 配置目錄不一致")
            return False
        
    except Exception as e:
        print(f"❌ 配置一致性測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 配置統一測試")
    print("=" * 80)
    print("📝 這個測試将驗證配置統一是否成功")
    print("📝 檢查所有組件是否使用相同的配置文件")
    print("=" * 80)
    
    # 測試配置統一
    unification_success = test_config_unification()
    
    # 測試Web配置訪問
    web_access_success = test_web_config_access()
    
    # 測試配置一致性
    consistency_success = test_config_consistency()
    
    # 总結
    print("\n📋 測試总結")
    print("=" * 60)
    
    print(f"配置統一: {'✅ 成功' if unification_success else '❌ 失败'}")
    print(f"Web配置訪問: {'✅ 成功' if web_access_success else '❌ 失败'}")
    print(f"配置一致性: {'✅ 成功' if consistency_success else '❌ 失败'}")
    
    overall_success = unification_success and web_access_success and consistency_success
    
    if overall_success:
        print("\n🎉 配置統一成功！")
        print("   現在所有組件都使用項目根目錄的統一配置")
        print("   不再需要維護多套配置文件")
    else:
        print("\n❌ 配置統一失败")
        print("   需要進一步調試")
    
    print("\n🎯 測試完成！")
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
