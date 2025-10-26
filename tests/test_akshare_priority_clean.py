#!/usr/bin/env python3
"""
清理測試AKShare數據源優先級修複
强制重新加載模塊以避免緩存問題
"""

import os
import sys
import importlib

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def clean_import_test():
    """清理導入測試"""
    print("🧹 清理導入測試")
    print("=" * 60)
    
    try:
        # 清理可能的模塊緩存
        modules_to_clean = [
            'tradingagents.dataflows.data_source_manager',
            'tradingagents.dataflows',
            'tradingagents'
        ]
        
        for module_name in modules_to_clean:
            if module_name in sys.modules:
                print(f"🗑️ 清理模塊緩存: {module_name}")
                del sys.modules[module_name]
        
        # 重新導入
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        # 創建數據源管理器
        manager = DataSourceManager()
        
        print(f"📊 默認數據源: {manager.default_source.value}")
        print(f"📊 當前數據源: {manager.current_source.value}")
        print(f"📊 可用數據源: {[s.value for s in manager.available_sources]}")
        
        # 驗證默認數據源是AKShare
        if manager.default_source == ChinaDataSource.AKSHARE:
            print("✅ 默認數據源正確設置為AKShare")
            return True
        else:
            print(f"❌ 默認數據源錯誤: 期望akshare，實际{manager.default_source.value}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_env_variable_directly():
    """直接測試環境變量"""
    print("\n🔧 直接測試環境變量")
    print("=" * 60)
    
    try:
        # 檢查環境變量
        env_value = os.getenv('DEFAULT_CHINA_DATA_SOURCE')
        print(f"📊 環境變量 DEFAULT_CHINA_DATA_SOURCE: {env_value}")
        
        # 檢查.env文件
        env_file_path = os.path.join(project_root, '.env')
        if os.path.exists(env_file_path):
            print(f"📄 .env文件存在: {env_file_path}")
            with open(env_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'DEFAULT_CHINA_DATA_SOURCE' in content:
                    for line in content.split('\n'):
                        if 'DEFAULT_CHINA_DATA_SOURCE' in line and not line.strip().startswith('#'):
                            print(f"📊 .env文件中的設置: {line.strip()}")
                            break
        else:
            print("📄 .env文件不存在")
        
        # 手動加載.env文件
        try:
            from dotenv import load_dotenv
            load_dotenv()
            env_value_after_load = os.getenv('DEFAULT_CHINA_DATA_SOURCE')
            print(f"📊 加載.env後的環境變量: {env_value_after_load}")
        except ImportError:
            print("⚠️ python-dotenv未安裝，無法自動加載.env文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_manual_env_setting():
    """手動設置環境變量測試"""
    print("\n🔧 手動設置環境變量測試")
    print("=" * 60)
    
    try:
        # 手動設置環境變量
        os.environ['DEFAULT_CHINA_DATA_SOURCE'] = 'akshare'
        print(f"📊 手動設置環境變量: DEFAULT_CHINA_DATA_SOURCE=akshare")
        
        # 清理模塊緩存
        modules_to_clean = [
            'tradingagents.dataflows.data_source_manager',
        ]
        
        for module_name in modules_to_clean:
            if module_name in sys.modules:
                del sys.modules[module_name]
        
        # 重新導入
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        manager = DataSourceManager()
        
        print(f"📊 默認數據源: {manager.default_source.value}")
        print(f"📊 當前數據源: {manager.current_source.value}")
        
        if manager.default_source == ChinaDataSource.AKSHARE:
            print("✅ 手動設置環境變量後，默認數據源正確為AKShare")
            return True
        else:
            print(f"❌ 手動設置環境變量後，默認數據源仍然錯誤: {manager.default_source.value}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_order():
    """測試备用數據源顺序"""
    print("\n🔧 測試备用數據源顺序")
    print("=" * 60)
    
    try:
        # 確保環境變量設置
        os.environ['DEFAULT_CHINA_DATA_SOURCE'] = 'akshare'
        
        # 清理並重新導入
        if 'tradingagents.dataflows.data_source_manager' in sys.modules:
            del sys.modules['tradingagents.dataflows.data_source_manager']
        
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        
        manager = DataSourceManager()
        
        # 檢查源代碼中的fallback_order
        import inspect
        source_code = inspect.getsource(manager._try_fallback_sources)
        
        print("📊 檢查备用數據源顺序...")
        
        # 查找fallback_order定義
        lines = source_code.split('\n')
        in_fallback_order = False
        fallback_sources = []
        
        for line in lines:
            if 'fallback_order = [' in line:
                in_fallback_order = True
                continue
            elif in_fallback_order:
                if ']' in line:
                    break
                if 'ChinaDataSource.' in line:
                    source_name = line.strip().replace('ChinaDataSource.', '').replace(',', '')
                    fallback_sources.append(source_name)
        
        print(f"📊 备用數據源顺序: {fallback_sources}")
        
        if fallback_sources and fallback_sources[0] == 'AKSHARE':
            print("✅ 备用數據源顺序正確: AKShare排在第一位")
            return True
        else:
            print(f"❌ 备用數據源顺序錯誤: 期望AKSHARE在第一位，實际顺序: {fallback_sources}")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🧪 AKShare數據源優先級修複驗證 (清理版)")
    print("=" * 80)
    
    tests = [
        ("環境變量檢查", test_env_variable_directly),
        ("手動環境變量設置", test_manual_env_setting),
        ("清理導入測試", clean_import_test),
        ("备用數據源顺序", test_fallback_order),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 執行測試: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試{test_name}異常: {e}")
            results.append((test_name, False))
    
    # 总結結果
    print("\n" + "=" * 80)
    print("📊 測試結果总結:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！AKShare數據源優先級修複成功！")
        return True
    else:
        print("⚠️ 部分測試失败，需要進一步檢查。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
