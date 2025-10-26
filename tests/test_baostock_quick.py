#!/usr/bin/env python3
"""
快速測試BaoStock數據源
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_baostock_import():
    """測試BaoStock導入"""
    print("🔍 測試BaoStock導入...")
    try:
        import baostock as bs
        print(f"✅ BaoStock導入成功")
        print(f"   版本: {bs.__version__}")
        return True
    except ImportError as e:
        print(f"❌ BaoStock導入失败: {e}")
        return False

def test_baostock_connection():
    """測試BaoStock連接"""
    print("\n🔍 測試BaoStock連接...")
    try:
        import baostock as bs
        
        # 登錄系統
        lg = bs.login()
        if lg.error_code != '0':
            print(f"❌ BaoStock登錄失败: {lg.error_msg}")
            return False
        
        print(f"✅ BaoStock登錄成功")
        
        # 測試獲取數據
        rs = bs.query_history_k_data_plus(
            "sz.000001",  # 平安銀行
            "date,code,open,high,low,close,volume",
            start_date='2025-07-01',
            end_date='2025-07-12',
            frequency="d"
        )
        
        if rs.error_code != '0':
            print(f"❌ BaoStock數據獲取失败: {rs.error_msg}")
            bs.logout()
            return False
        
        # 獲取數據
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        
        print(f"✅ BaoStock數據獲取成功")
        print(f"   數據條數: {len(data_list)}")
        if data_list:
            print(f"   最新數據: {data_list[-1]}")
        
        # 登出系統
        bs.logout()
        return True
        
    except Exception as e:
        print(f"❌ BaoStock連接異常: {e}")
        try:
            import baostock as bs
            bs.logout()
        except:
            pass
        return False

def test_data_source_manager():
    """測試數據源管理器中的BaoStock"""
    print("\n🔍 測試數據源管理器中的BaoStock...")
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager
        
        manager = DataSourceManager()
        print(f"✅ 數據源管理器初始化成功")
        print(f"   當前數據源: {manager.current_source.value}")
        print(f"   可用數據源: {[s.value for s in manager.available_sources]}")
        
        # 檢查BaoStock是否在可用數據源中
        available_sources = [s.value for s in manager.available_sources]
        if 'baostock' in available_sources:
            print(f"✅ BaoStock已被识別為可用數據源")
            return True
        else:
            print(f"❌ BaoStock未被识別為可用數據源")
            return False
            
    except Exception as e:
        print(f"❌ 數據源管理器測試異常: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 BaoStock快速測試")
    print("=" * 40)
    
    results = []
    
    # 1. 測試導入
    import_result = test_baostock_import()
    results.append(('BaoStock導入', import_result))
    
    # 2. 測試連接（只有導入成功才測試）
    if import_result:
        connection_result = test_baostock_connection()
        results.append(('BaoStock連接', connection_result))
        
        # 3. 測試數據源管理器
        manager_result = test_data_source_manager()
        results.append(('數據源管理器', manager_result))
    
    # 統計結果
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 測試結果:")
    print("=" * 40)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n📈 总體結果: {passed}/{total}")
    
    if passed == total:
        print(f"🎉 BaoStock配置完成！")
        print(f"✅ 現在中國股票數據源包括:")
        print(f"   1. Tushare (主要)")
        print(f"   2. AKShare (备用)")
        print(f"   3. BaoStock (歷史數據备用)")
        print(f"   4. TDX (将被淘汰)")
    else:
        print(f"⚠️ BaoStock配置存在問題")
        print(f"❌ 請檢查網絡連接和庫安裝")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🎯 下一步:")
        print("1. 重新運行完整數據源測試")
        print("2. python tests/test_data_sources_comprehensive.py")
    else:
        print(f"\n🔧 故障排除:")
        print("1. 檢查網絡連接")
        print("2. 重新安裝: pip install baostock")
        print("3. 查看BaoStock官方文档")
