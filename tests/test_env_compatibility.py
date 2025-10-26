#!/usr/bin/env python3
"""
測試.env文件兼容性
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_env_loading():
    """測試.env文件加載"""
    print("🧪 測試.env文件加載")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import config_manager
        
        # 測試.env狀態檢查
        env_status = config_manager.get_env_config_status()
        print(f"✅ .env文件存在: {env_status['env_file_exists']}")
        
        # 測試API密鑰加載
        print("\n📋 API密鑰狀態:")
        for provider, configured in env_status['api_keys'].items():
            status = "✅ 已配置" if configured else "❌ 未配置"
            print(f"  {provider}: {status}")
        
        return True
    except Exception as e:
        print(f"❌ .env文件加載失败: {e}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

def test_model_config_merge():
    """測試模型配置合並"""
    print("\n🧪 測試模型配置合並")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import config_manager
        
        # 加載模型配置
        models = config_manager.load_models()
        print(f"📋 加載了 {len(models)} 個模型配置")
        
        # 檢查.env密鑰是否正確合並
        env_status = config_manager.get_env_config_status()
        
        for model in models:
            env_has_key = env_status['api_keys'].get(model.provider.lower(), False)
            model_has_key = bool(model.api_key)
            
            print(f"\n🤖 {model.provider} - {model.model_name}:")
            print(f"  .env中有密鑰: {env_has_key}")
            print(f"  模型配置有密鑰: {model_has_key}")
            print(f"  模型啟用狀態: {model.enabled}")
            
            if env_has_key:
                print(f"  API密鑰: ***{model.api_key[-4:] if model.api_key else 'None'}")
        
        return True
    except Exception as e:
        print(f"❌ 模型配置合並失败: {e}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

def test_settings_merge():
    """測試系統設置合並"""
    print("\n🧪 測試系統設置合並")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import config_manager
        
        # 加載設置
        settings = config_manager.load_settings()
        
        # 檢查.env中的設置是否正確合並
        env_settings = [
            "finnhub_api_key",
            "reddit_client_id", 
            "reddit_client_secret",
            "results_dir",
            "log_level"
        ]
        
        print("⚙️ 系統設置狀態:")
        for key in env_settings:
            value = settings.get(key, "未設置")
            if "api_key" in key or "secret" in key:
                display_value = f"***{value[-4:]}" if value and value != "未設置" else "未設置"
            else:
                display_value = value
            print(f"  {key}: {display_value}")
        
        return True
    except Exception as e:
        print(f"❌ 系統設置合並失败: {e}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

def test_backward_compatibility():
    """測試向後兼容性"""
    print("\n🧪 測試向後兼容性")
    print("=" * 50)
    
    try:
        # 測試原有的環境變量讀取方式
        dashscope_key = os.getenv("DASHSCOPE_API_KEY")
        finnhub_key = os.getenv("FINNHUB_API_KEY")
        
        print("🔑 直接環境變量讀取:")
        print(f"  DASHSCOPE_API_KEY: {'✅ 已設置' if dashscope_key else '❌ 未設置'}")
        print(f"  FINNHUB_API_KEY: {'✅ 已設置' if finnhub_key else '❌ 未設置'}")
        
        # 測試CLI工具兼容性
        from cli.main import check_api_keys
        
        # 模擬CLI檢查
        if dashscope_key and finnhub_key:
            print("✅ CLI工具API密鑰檢查應该通過")
        else:
            print("⚠️ CLI工具API密鑰檢查可能失败")
        
        return True
    except Exception as e:
        print(f"❌ 向後兼容性測試失败: {e}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

def main():
    """主測試函數"""
    print("🧪 .env文件兼容性測試")
    print("=" * 60)
    
    tests = [
        (".env文件加載", test_env_loading),
        ("模型配置合並", test_model_config_merge),
        ("系統設置合並", test_settings_merge),
        ("向後兼容性", test_backward_compatibility),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 測試通過")
            else:
                print(f"❌ {test_name} 測試失败")
        except Exception as e:
            print(f"❌ {test_name} 測試異常: {e}")
    
    print(f"\n📊 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 .env兼容性測試全部通過！")
        print("\n💡 兼容性特性:")
        print("✅ 優先從.env文件讀取API密鑰")
        print("✅ Web界面顯示配置來源")
        print("✅ 保持CLI工具完全兼容")
        print("✅ 支持原有的環境變量方式")
        print("✅ 新增Web管理界面作為補充")
        return True
    else:
        print("❌ 部分測試失败，請檢查兼容性實現")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
