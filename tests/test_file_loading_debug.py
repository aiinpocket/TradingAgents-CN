#!/usr/bin/env python3
"""
調試文件加載問題
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

def test_file_loading():
    """測試文件加載"""
    print("🔬 文件加載調試")
    print("=" * 80)
    
    try:
        from tradingagents.config.config_manager import ConfigManager
        
        print("🔧 創建ConfigManager...")
        config_manager = ConfigManager()
        
        print("\n📊 加載定價配置...")
        print("=" * 60)
        
        # 這會觸發詳細的文件加載日誌
        pricing_configs = config_manager.load_pricing()
        
        print("=" * 60)
        print(f"📊 最终加載的配置數量: {len(pricing_configs)}")
        
        # 查找DeepSeek配置
        deepseek_configs = [p for p in pricing_configs if p.provider == "deepseek"]
        print(f"📊 DeepSeek配置數量: {len(deepseek_configs)}")
        
        if deepseek_configs:
            print("✅ 找到DeepSeek配置:")
            for config in deepseek_configs:
                print(f"   - {config.model_name}: 輸入¥{config.input_price_per_1k}/1K, 輸出¥{config.output_price_per_1k}/1K")
        else:
            print("❌ 未找到DeepSeek配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件加載測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 文件加載調試測試")
    print("=" * 80)
    print("📝 這個測試将顯示實际加載的配置文件內容")
    print("=" * 80)
    
    success = test_file_loading()
    
    if success:
        print("\n🎉 文件加載測試完成！")
        print("請查看上面的詳細日誌，確認加載的文件內容。")
    else:
        print("\n❌ 文件加載測試失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
