#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票數據服務測試程序
測試MongoDB -> Tushare數據接口的完整降級機制
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from tradingagents.dataflows.stock_data_service import StockDataService, get_stock_data_service
    from tradingagents.api.stock_api import (
        get_stock_info, get_all_stocks, get_stock_data,
        search_stocks, get_market_summary, check_service_status
    )
    SERVICES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 服務不可用: {e}")
    SERVICES_AVAILABLE = False

class TestStockDataService(unittest.TestCase):
    """股票數據服務測試類"""
    
    def setUp(self):
        """測試前準备"""
        if not SERVICES_AVAILABLE:
            self.skipTest("股票數據服務不可用")
        
        self.service = StockDataService()
    
    def test_service_initialization(self):
        """測試服務初始化"""
        print("\n🧪 測試服務初始化...")
        
        # 檢查服務是否正確初始化
        self.assertIsNotNone(self.service)
        
        # 檢查各組件的初始化狀態
        print(f"  📊 數據庫管理器: {'✅' if self.service.db_manager else '❌'}")
        print(f"  📡 統一數據接口: {'✅' if hasattr(self.service, 'get_stock_data') else '❌'}")
        
        print("  ✅ 服務初始化測試通過")
    
    def test_get_stock_basic_info_single(self):
        """測試獲取單個股票基础信息"""
        print("\n🧪 測試獲取單個股票基础信息...")
        
        test_codes = ['000001', '600000', '300001']
        
        for code in test_codes:
            print(f"  🔍 測試股票代碼: {code}")
            
            result = self.service.get_stock_basic_info(code)
            
            # 結果不應该為None
            self.assertIsNotNone(result)
            
            if isinstance(result, dict):
                if 'error' in result:
                    print(f"    ⚠️ 獲取失败: {result['error']}")
                else:
                    print(f"    ✅ 獲取成功: {result.get('name', 'N/A')}")
                    # 檢查必要字段
                    self.assertIn('code', result)
                    self.assertIn('name', result)
                    self.assertIn('source', result)
            
        print("  ✅ 單個股票信息測試完成")
    
    def test_get_stock_basic_info_all(self):
        """測試獲取所有股票基础信息"""
        print("\n🧪 測試獲取所有股票基础信息...")
        
        result = self.service.get_stock_basic_info()
        
        # 結果不應该為None
        self.assertIsNotNone(result)
        
        if isinstance(result, list) and len(result) > 0:
            print(f"  ✅ 獲取成功: {len(result)} 只股票")
            
            # 檢查第一個股票的字段
            first_stock = result[0]
            if 'error' not in first_stock:
                self.assertIn('code', first_stock)
                self.assertIn('name', first_stock)
                print(f"  📊 示例股票: {first_stock.get('code')} - {first_stock.get('name')}")
        elif isinstance(result, dict) and 'error' in result:
            print(f"  ⚠️ 獲取失败: {result['error']}")
        else:
            print(f"  ⚠️ 未獲取到數據")
        
        print("  ✅ 所有股票信息測試完成")
    
    def test_market_classification(self):
        """測試市場分類功能"""
        print("\n🧪 測試市場分類功能...")
        
        test_cases = [
            ('000001', '深圳', '深市主板'),
            ('600000', '上海', '沪市主板'),
            ('300001', '深圳', '創業板'),
            ('688001', '上海', '科創板')
        ]
        
        for code, expected_market, expected_category in test_cases:
            market = self.service._get_market_name(code)
            category = self.service._get_stock_category(code)
            
            print(f"  📊 {code}: {market} - {category}")
            
            self.assertEqual(market, expected_market)
            self.assertEqual(category, expected_category)
        
        print("  ✅ 市場分類測試通過")
    
    def test_fallback_data(self):
        """測試降級數據功能"""
        print("\n🧪 測試降級數據功能...")
        
        # 測試單個股票的降級數據
        fallback_single = self.service._get_fallback_data('999999')
        self.assertIsInstance(fallback_single, dict)
        self.assertIn('code', fallback_single)
        self.assertIn('error', fallback_single)
        print(f"  📊 單個股票降級: {fallback_single['code']} - {fallback_single.get('name')}")
        
        # 測試所有股票的降級數據
        fallback_all = self.service._get_fallback_data()
        self.assertIsInstance(fallback_all, dict)
        self.assertIn('error', fallback_all)
        print(f"  📊 所有股票降級: {fallback_all['error']}")
        
        print("  ✅ 降級數據測試通過")

class TestStockAPI(unittest.TestCase):
    """股票API測試類"""
    
    def setUp(self):
        """測試前準备"""
        if not SERVICES_AVAILABLE:
            self.skipTest("股票API不可用")
    
    def test_service_status(self):
        """測試服務狀態檢查"""
        print("\n🧪 測試服務狀態檢查...")
        
        status = check_service_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn('service_available', status)
        
        print(f"  📊 服務狀態:")
        for key, value in status.items():
            print(f"    {key}: {value}")
        
        print("  ✅ 服務狀態測試通過")
    
    def test_get_stock_info_api(self):
        """測試股票信息API"""
        print("\n🧪 測試股票信息API...")
        
        test_codes = ['000001', '600000', '999999']  # 包含一個不存在的代碼
        
        for code in test_codes:
            print(f"  🔍 測試API獲取: {code}")
            
            result = get_stock_info(code)
            
            self.assertIsInstance(result, dict)
            
            if 'error' in result:
                print(f"    ⚠️ 預期錯誤: {result['error']}")
            else:
                print(f"    ✅ 獲取成功: {result.get('name')}")
                self.assertIn('code', result)
                self.assertIn('name', result)
        
        print("  ✅ 股票信息API測試完成")
    
    def test_search_stocks_api(self):
        """測試股票搜索API"""
        print("\n🧪 測試股票搜索API...")
        
        keywords = ['平安', '銀行', '000001', 'xyz123']  # 包含一個不存在的關键詞
        
        for keyword in keywords:
            print(f"  🔍 搜索關键詞: '{keyword}'")
            
            results = search_stocks(keyword)
            
            self.assertIsInstance(results, list)
            
            if not results or (len(results) == 1 and 'error' in results[0]):
                print(f"    ⚠️ 未找到匹配結果")
            else:
                print(f"    ✅ 找到 {len(results)} 個匹配結果")
                # 檢查第一個結果
                if results and 'error' not in results[0]:
                    first_result = results[0]
                    print(f"    📊 示例: {first_result.get('code')} - {first_result.get('name')}")
        
        print("  ✅ 股票搜索API測試完成")
    
    def test_market_summary_api(self):
        """測試市場概覽API"""
        print("\n🧪 測試市場概覽API...")
        
        summary = get_market_summary()
        
        self.assertIsInstance(summary, dict)
        
        if 'error' in summary:
            print(f"  ⚠️ 獲取失败: {summary['error']}")
        else:
            print(f"  ✅ 獲取成功:")
            print(f"    📊 总股票數: {summary.get('total_count', 0):,}")
            print(f"    🏢 沪市股票: {summary.get('shanghai_count', 0):,}")
            print(f"    🏢 深市股票: {summary.get('shenzhen_count', 0):,}")
            print(f"    🔗 數據源: {summary.get('data_source', 'unknown')}")
            
            # 檢查必要字段
            self.assertIn('total_count', summary)
            self.assertIn('data_source', summary)
        
        print("  ✅ 市場概覽API測試完成")
    
    def test_stock_data_api(self):
        """測試股票數據API"""
        print("\n🧪 測試股票數據API...")
        
        # 測試獲取股票歷史數據
        stock_code = '000001'
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"  📊 獲取 {stock_code} 從 {start_date} 到 {end_date} 的數據")
        
        result = get_stock_data(stock_code, start_date, end_date)
        
        self.assertIsInstance(result, str)
        
        # 檢查結果是否包含預期內容
        if "❌" in result:
            print(f"    ⚠️ 獲取失败（預期情况）")
        else:
            print(f"    ✅ 獲取成功（數據長度: {len(result)} 字符）")
        
        print("  ✅ 股票數據API測試完成")

class TestFallbackMechanism(unittest.TestCase):
    """降級機制測試類"""
    
    def setUp(self):
        """測試前準备"""
        if not SERVICES_AVAILABLE:
            self.skipTest("降級機制測試不可用")
    
    @patch('tradingagents.dataflows.stock_data_service.DATABASE_MANAGER_AVAILABLE', False)
    def test_mongodb_unavailable_fallback(self):
        """測試MongoDB不可用時的降級"""
        print("\n🧪 測試MongoDB不可用時的降級...")
        
        # 創建一個新的服務實例（模擬MongoDB不可用）
        service = StockDataService()
        
        # 數據庫管理器應该為None
        self.assertIsNone(service.db_manager)
        
        # 嘗試獲取股票信息（應该降級到Tushare數據接口）
        result = service.get_stock_basic_info('000001')
        
        self.assertIsNotNone(result)
        
        if isinstance(result, dict):
            if 'error' in result:
                print(f"    ⚠️ 降級失败: {result['error']}")
            else:
                print(f"    ✅ 降級成功: {result.get('name')}")
                self.assertEqual(result.get('source'), 'unified_api')
        
        print("  ✅ MongoDB降級測試完成")
    
    def test_invalid_stock_code_fallback(self):
        """測試無效股票代碼的降級"""
        print("\n🧪 測試無效股票代碼的降級...")
        
        service = StockDataService()
        
        # 測試明顯無效的股票代碼
        invalid_codes = ['999999', 'INVALID', '123456']
        
        for code in invalid_codes:
            print(f"  🔍 測試無效代碼: {code}")
            
            result = service.get_stock_basic_info(code)
            
            self.assertIsNotNone(result)
            
            if isinstance(result, dict):
                # 應该包含錯誤信息或降級數據
                if 'error' in result:
                    print(f"    ✅ 正確识別無效代碼")
                else:
                    print(f"    ⚠️ 返回了數據: {result.get('name')}")
        
        print("  ✅ 無效代碼降級測試完成")

def run_comprehensive_test():
    """運行综合測試"""
    print("🚀 股票數據服務综合測試")
    print("=" * 60)
    
    if not SERVICES_AVAILABLE:
        print("❌ 服務不可用，無法運行測試")
        return
    
    # 創建測試套件
    test_suite = unittest.TestSuite()
    
    # 添加測試用例
    test_suite.addTest(unittest.makeSuite(TestStockDataService))
    test_suite.addTest(unittest.makeSuite(TestStockAPI))
    test_suite.addTest(unittest.makeSuite(TestFallbackMechanism))
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 輸出測試結果摘要
    print("\n" + "=" * 60)
    print("📊 測試結果摘要:")
    print(f"  ✅ 成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  ❌ 失败: {len(result.failures)}")
    print(f"  💥 錯誤: {len(result.errors)}")
    print(f"  ⏭️ 跳過: {len(result.skipped)}")
    
    if result.failures:
        print("\n❌ 失败的測試:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 錯誤的測試:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    # 总體評估
    if result.wasSuccessful():
        print("\n🎉 所有測試通過！股票數據服務工作正常")
    else:
        print("\n⚠️ 部分測試失败，請檢查相關配置")
    
    return result.wasSuccessful()

def run_manual_test():
    """運行手動測試（用於調試）"""
    print("🔧 手動測試模式")
    print("=" * 40)
    
    if not SERVICES_AVAILABLE:
        print("❌ 服務不可用")
        return
    
    try:
        # 測試服務狀態
        print("\n1. 檢查服務狀態:")
        status = check_service_status()
        for key, value in status.items():
            print(f"   {key}: {value}")
        
        # 測試獲取股票信息
        print("\n2. 獲取股票信息:")
        stock_info = get_stock_info('000001')
        if 'error' in stock_info:
            print(f"   錯誤: {stock_info['error']}")
        else:
            print(f"   成功: {stock_info.get('code')} - {stock_info.get('name')}")
        
        # 測試搜索功能
        print("\n3. 搜索股票:")
        results = search_stocks('平安')
        if results and 'error' not in results[0]:
            print(f"   找到 {len(results)} 只股票")
            for i, stock in enumerate(results[:3], 1):
                print(f"   {i}. {stock.get('code')} - {stock.get('name')}")
        else:
            print("   未找到匹配的股票")
        
        # 測試市場概覽
        print("\n4. 市場概覽:")
        summary = get_market_summary()
        if 'error' in summary:
            print(f"   錯誤: {summary['error']}")
        else:
            print(f"   总股票數: {summary.get('total_count', 0):,}")
            print(f"   數據源: {summary.get('data_source')}")
        
        print("\n✅ 手動測試完成")
        
    except Exception as e:
        print(f"\n❌ 手動測試失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='股票數據服務測試程序')
    parser.add_argument('--manual', action='store_true', help='運行手動測試模式')
    parser.add_argument('--comprehensive', action='store_true', help='運行综合測試')
    
    args = parser.parse_args()
    
    if args.manual:
        run_manual_test()
    elif args.comprehensive:
        run_comprehensive_test()
    else:
        # 默認運行综合測試
        print("💡 提示: 使用 --manual 運行手動測試，--comprehensive 運行综合測試")
        print("默認運行综合測試...\n")
        run_comprehensive_test()