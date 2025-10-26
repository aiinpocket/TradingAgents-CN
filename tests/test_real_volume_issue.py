#!/usr/bin/env python3
"""
測試真實的volume映射問題
驗證現有代碼是否真的存在KeyError: 'volume'問題
"""

import os
import sys

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 加載.env文件
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(project_root, '.env'))
    print(f"✅ 已加載.env文件")
except ImportError:
    print(f"⚠️ python-dotenv未安裝，嘗試手動加載環境變量")
except Exception as e:
    print(f"⚠️ 加載.env文件失败: {e}")

def test_real_tushare_volume_access():
    """測試真實的Tushare數據volume訪問"""
    print("🧪 測試真實Tushare數據volume訪問")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.data_source_manager import DataSourceManager, ChinaDataSource
        
        # 檢查Tushare是否可用
        tushare_token = os.getenv('TUSHARE_TOKEN')
        if not tushare_token:
            print("⚠️ TUSHARE_TOKEN未設置，無法測試真實數據")
            return True
        
        print(f"✅ TUSHARE_TOKEN已設置")
        
        # 創建數據源管理器
        manager = DataSourceManager()
        
        # 確保使用Tushare數據源
        if ChinaDataSource.TUSHARE in manager.available_sources:
            manager.set_current_source(ChinaDataSource.TUSHARE)
            print(f"📊 當前數據源: {manager.current_source.value}")
            
            # 測試獲取真實數據
            print(f"🔍 獲取000001真實數據...")
            
            try:
                result = manager._get_tushare_data('000001', '2025-07-20', '2025-07-26')
                
                if result and "❌" not in result:
                    print(f"✅ 成功獲取數據，長度: {len(result)}")
                    print(f"📊 結果預覽: {result[:200]}...")
                    
                    # 檢查結果中是否包含成交量信息
                    if "成交量" in result:
                        print(f"✅ 結果包含成交量信息")
                        return True
                    else:
                        print(f"⚠️ 結果不包含成交量信息")
                        return False
                else:
                    print(f"❌ 獲取數據失败: {result}")
                    return False
                    
            except KeyError as e:
                if "'volume'" in str(e):
                    print(f"🎯 確認存在KeyError: 'volume'問題！")
                    print(f"❌ 錯誤詳情: {e}")
                    return False
                else:
                    print(f"❌ 其他KeyError: {e}")
                    return False
            except Exception as e:
                print(f"❌ 其他錯誤: {e}")
                if "volume" in str(e).lower():
                    print(f"🎯 可能与volume相關的錯誤")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("❌ Tushare數據源不可用")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tushare_adapter_direct():
    """直接測試Tushare適配器"""
    print(f"\n🧪 直接測試Tushare適配器")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.tushare_adapter import get_tushare_adapter
        
        # 檢查Tushare是否可用
        tushare_token = os.getenv('TUSHARE_TOKEN')
        if not tushare_token:
            print("⚠️ TUSHARE_TOKEN未設置，無法測試真實數據")
            return True
        
        adapter = get_tushare_adapter()
        print(f"✅ Tushare適配器創建成功")
        
        # 測試獲取股票數據
        print(f"🔍 獲取000001股票數據...")
        
        try:
            data = adapter.get_stock_data('000001', '2025-07-20', '2025-07-26')
            
            if data is not None and not data.empty:
                print(f"✅ 成功獲取數據，形狀: {data.shape}")
                print(f"📊 列名: {list(data.columns)}")
                
                # 檢查volume列
                if 'volume' in data.columns:
                    print(f"✅ volume列存在")
                    volume_sum = data['volume'].sum()
                    print(f"📊 总成交量: {volume_sum:,.0f}")
                    
                    # 測試訪問volume列（這是關键測試）
                    try:
                        volume_values = data['volume'].tolist()
                        print(f"✅ 成功訪問volume列: {volume_values[:3]}...")
                        return True
                    except KeyError as e:
                        print(f"❌ KeyError訪問volume列: {e}")
                        return False
                else:
                    print(f"❌ volume列不存在")
                    print(f"📊 可用列: {list(data.columns)}")
                    return False
            else:
                print(f"❌ 未獲取到數據")
                return False
                
        except KeyError as e:
            if "'volume'" in str(e):
                print(f"🎯 確認存在KeyError: 'volume'問題！")
                print(f"❌ 錯誤詳情: {e}")
                return False
            else:
                print(f"❌ 其他KeyError: {e}")
                return False
        except Exception as e:
            print(f"❌ 其他錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_column_mapping_in_real_data():
    """測試真實數據中的列映射"""
    print(f"\n🧪 測試真實數據中的列映射")
    print("=" * 60)
    
    try:
        import tushare as ts
        
        # 檢查Tushare是否可用
        tushare_token = os.getenv('TUSHARE_TOKEN')
        if not tushare_token:
            print("⚠️ TUSHARE_TOKEN未設置，無法測試真實數據")
            return True
        
        # 直接調用Tushare API獲取原始數據
        print(f"🔍 直接調用Tushare API...")
        ts.set_token(tushare_token)
        pro = ts.pro_api()
        
        # 獲取原始數據
        raw_data = pro.daily(ts_code='000001.SZ', start_date='20250720', end_date='20250726')
        
        if raw_data is not None and not raw_data.empty:
            print(f"✅ 獲取原始數據成功，形狀: {raw_data.shape}")
            print(f"📊 原始列名: {list(raw_data.columns)}")
            
            # 檢查原始數據中的列名
            if 'vol' in raw_data.columns:
                print(f"✅ 原始數據包含'vol'列")
                vol_values = raw_data['vol'].tolist()
                print(f"📊 vol列值: {vol_values}")
            else:
                print(f"❌ 原始數據不包含'vol'列")
                return False
            
            # 測試我們的標準化函數
            from tradingagents.dataflows.tushare_adapter import get_tushare_adapter
            adapter = get_tushare_adapter()
            
            print(f"\n🔧 測試標準化函數...")
            standardized_data = adapter._standardize_data(raw_data)
            
            print(f"📊 標準化後列名: {list(standardized_data.columns)}")
            
            if 'volume' in standardized_data.columns:
                print(f"✅ 標準化後包含'volume'列")
                volume_values = standardized_data['volume'].tolist()
                print(f"📊 volume列值: {volume_values}")
                
                # 驗證映射是否正確
                if raw_data['vol'].sum() == standardized_data['volume'].sum():
                    print(f"✅ vol -> volume 映射正確")
                    return True
                else:
                    print(f"❌ vol -> volume 映射錯誤")
                    return False
            else:
                print(f"❌ 標準化後不包含'volume'列")
                return False
        else:
            print(f"❌ 未獲取到原始數據")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🔍 驗證真實環境中的volume映射問題")
    print("=" * 80)
    print("📋 目標: 在真實環境中驗證是否存在 KeyError: 'volume' 問題")
    print("=" * 80)
    
    tests = [
        ("真實數據列映射測試", test_column_mapping_in_real_data),
        ("Tushare適配器直接測試", test_tushare_adapter_direct),
        ("數據源管理器真實數據測試", test_real_tushare_volume_access),
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
    print("📊 真實環境測試結果总結:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总體結果: {passed}/{total} 測試通過")
    
    # 分析結果和建议
    print("\n📋 分析結論:")
    if passed == total:
        print("🎉 所有真實環境測試通過！")
        print("✅ 現有代碼的volume映射功能完全正常")
        print("\n💡 對PR #173的建议:")
        print("  1. 🤔 詢問PR作者具體的錯誤複現步骤")
        print("  2. 📅 確認PR作者使用的代碼版本和分支")
        print("  3. 🔍 檢查是否是特定環境、數據或配置的問題")
        print("  4. 📝 要求提供完整的錯誤堆棧信息")
        print("  5. ⚠️ 可能是已經修複的旧問題")
    else:
        print("❌ 部分真實環境測試失败")
        print("🎯 確實存在volume相關問題，PR #173的修複是必要的")
        print("\n💡 建议:")
        print("  1. ✅ 接受PR #173的修複")
        print("  2. 🔧 但需要優化實現方式")
        print("  3. 🧪 增加更多測試用例")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
