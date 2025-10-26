#!/usr/bin/env python3
"""
測試AKShare數據源優先級修複
驗證AKShare已被設置為第一優先級數據源
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_default_data_source():
    """測試默認數據源設置"""
    print("🔧 測試默認數據源設置")
    print("=" * 60)
    
    try:
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

def test_fallback_priority():
    """測試备用數據源優先級"""
    print("\n🔧 測試备用數據源優先級")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        manager = DataSourceManager()
        
        # 模擬當前數據源失败，測試备用數據源顺序
        print("📊 模擬數據源失败，檢查备用數據源優先級...")
        
        # 檢查_try_fallback_sources方法中的fallback_order
        # 這里我們通過檢查源代碼來驗證
        import inspect
        source_code = inspect.getsource(manager._try_fallback_sources)
        
        if "ChinaDataSource.AKSHARE" in source_code:
            # 檢查AKShare是否在Tushare之前
            akshare_pos = source_code.find("ChinaDataSource.AKSHARE")
            tushare_pos = source_code.find("ChinaDataSource.TUSHARE")
            
            if akshare_pos < tushare_pos and akshare_pos != -1:
                print("✅ 备用數據源優先級正確: AKShare > Tushare")
                return True
            else:
                print("❌ 备用數據源優先級錯誤: AKShare應该在Tushare之前")
                return False
        else:
            print("❌ 备用數據源配置中未找到AKShare")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variable_override():
    """測試環境變量覆蓋"""
    print("\n🔧 測試環境變量覆蓋")
    print("=" * 60)
    
    try:
        # 保存原始環境變量
        original_env = os.getenv('DEFAULT_CHINA_DATA_SOURCE')
        
        # 測試設置為tushare
        os.environ['DEFAULT_CHINA_DATA_SOURCE'] = 'tushare'
        
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        # 重新導入以獲取新的環境變量
        import importlib
        import tradingagents.dataflows.data_source_manager as dsm
        importlib.reload(dsm)
        
        manager = dsm.DataSourceManager()
        
        if manager.default_source == ChinaDataSource.TUSHARE:
            print("✅ 環境變量覆蓋功能正常")
            result = True
        else:
            print(f"❌ 環境變量覆蓋失败: 期望tushare，實际{manager.default_source.value}")
            result = False
        
        # 恢複原始環境變量
        if original_env:
            os.environ['DEFAULT_CHINA_DATA_SOURCE'] = original_env
        else:
            os.environ.pop('DEFAULT_CHINA_DATA_SOURCE', None)
        
        return result
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_akshare_availability():
    """測試AKShare可用性"""
    print("\n🔧 測試AKShare可用性")
    print("=" * 60)
    
    try:
        import akshare as ak
        print(f"✅ AKShare庫已安裝: v{ak.__version__}")
        
        # 簡單測試AKShare功能
        print("📊 測試AKShare基本功能...")
        
        # 這里不實际調用API，只測試導入
        from tradingagents.dataflows.akshare_utils import get_china_stock_data_akshare
        print("✅ AKShare工具函數導入成功")
        
        return True
        
    except ImportError:
        print("❌ AKShare庫未安裝")
        return False
    except Exception as e:
        print(f"❌ AKShare測試失败: {e}")
        return False

def test_data_source_switching():
    """測試數據源切換功能"""
    print("\n🔧 測試數據源切換功能")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        manager = DataSourceManager()
        original_source = manager.current_source
        
        print(f"📊 原始數據源: {original_source.value}")
        
        # 測試切換到不同數據源
        test_sources = [ChinaDataSource.TUSHARE, ChinaDataSource.BAOSTOCK]
        
        for source in test_sources:
            if source in manager.available_sources:
                success = manager.set_current_source(source)
                if success:
                    print(f"✅ 成功切換到: {source.value}")
                    current = manager.get_current_source()
                    if current == source:
                        print(f"✅ 當前數據源確認: {current.value}")
                    else:
                        print(f"❌ 數據源切換驗證失败")
                        return False
                else:
                    print(f"❌ 切換到{source.value}失败")
                    return False
            else:
                print(f"⚠️ 數據源{source.value}不可用，跳過測試")
        
        # 恢複原始數據源
        manager.set_current_source(original_source)
        print(f"📊 恢複原始數據源: {original_source.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🧪 AKShare數據源優先級修複驗證")
    print("=" * 80)
    
    tests = [
        ("默認數據源設置", test_default_data_source),
        ("备用數據源優先級", test_fallback_priority),
        ("環境變量覆蓋", test_environment_variable_override),
        ("AKShare可用性", test_akshare_availability),
        ("數據源切換功能", test_data_source_switching),
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
