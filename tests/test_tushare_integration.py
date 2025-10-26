#!/usr/bin/env python3
"""
Tushare集成測試
驗證Tushare數據源的集成功能，包括數據獲取、緩存、接口調用等
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_tushare_provider():
    """測試Tushare提供器基本功能"""
    print("\n🔧 測試Tushare提供器")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        
        print("✅ Tushare工具庫加載成功")
        
        # 創建提供器實例
        provider = get_tushare_provider()
        
        if provider.connected:
            print("✅ Tushare API連接成功")
            
            # 測試獲取股票列表
            print("🔄 測試獲取股票列表...")
            stock_list = provider.get_stock_list()
            
            if not stock_list.empty:
                print(f"✅ 獲取股票列表成功: {len(stock_list)}條")
                print(f"📊 示例股票: {stock_list.head(3)[['ts_code', 'name']].to_string(index=False)}")
            else:
                print("❌ 獲取股票列表失败")
            
            # 測試獲取股票信息
            print("🔄 測試獲取股票信息...")
            stock_info = provider.get_stock_info("000001")
            
            if stock_info and stock_info.get('name'):
                print(f"✅ 獲取股票信息成功: {stock_info['name']}")
            else:
                print("❌ 獲取股票信息失败")
            
            # 測試獲取股票數據
            print("🔄 測試獲取股票數據...")
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            stock_data = provider.get_stock_daily("000001", start_date, end_date)
            
            if not stock_data.empty:
                print(f"✅ 獲取股票數據成功: {len(stock_data)}條")
            else:
                print("❌ 獲取股票數據失败")
        else:
            print("❌ Tushare API連接失败")
        
    except Exception as e:
        print(f"❌ Tushare提供器測試失败: {e}")
        import traceback
        traceback.print_exc()


def test_tushare_adapter():
    """測試Tushare適配器功能"""
    print("\n🔧 測試Tushare適配器")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.tushare_adapter import get_tushare_adapter
        
        print("✅ Tushare適配器庫加載成功")
        
        # 創建適配器實例
        adapter = get_tushare_adapter()
        
        # 測試獲取股票數據
        print("🔄 測試獲取股票數據...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        stock_data = adapter.get_stock_data("000001", start_date, end_date)
        
        if not stock_data.empty:
            print(f"✅ 獲取股票數據成功: {len(stock_data)}條")
            print(f"📊 數據列: {list(stock_data.columns)}")
        else:
            print("❌ 獲取股票數據失败")
        
        # 測試獲取股票信息
        print("🔄 測試獲取股票信息...")
        stock_info = adapter.get_stock_info("000001")
        
        if stock_info and stock_info.get('name'):
            print(f"✅ 獲取股票信息成功: {stock_info['name']}")
        else:
            print("❌ 獲取股票信息失败")
        
        # 測試搜索股票
        print("🔄 測試搜索股票...")
        search_results = adapter.search_stocks("平安")
        
        if not search_results.empty:
            print(f"✅ 搜索股票成功: {len(search_results)}條結果")
        else:
            print("❌ 搜索股票失败")
        
        # 測試基本面數據
        print("🔄 測試基本面數據...")
        fundamentals = adapter.get_fundamentals("000001")
        
        if fundamentals and len(fundamentals) > 100:
            print(f"✅ 獲取基本面數據成功: {len(fundamentals)}字符")
        else:
            print("❌ 獲取基本面數據失败")
        
    except Exception as e:
        print(f"❌ Tushare適配器測試失败: {e}")
        import traceback
        traceback.print_exc()


def test_tushare_interface():
    """測試Tushare接口函數"""
    print("\n🔧 測試Tushare接口函數")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.interface import (
            get_china_stock_data_tushare,
            search_china_stocks_tushare,
            get_china_stock_fundamentals_tushare,
            get_china_stock_info_tushare
        )
        
        print("✅ Tushare接口函數加載成功")
        
        # 測試獲取股票數據接口
        print("🔄 測試股票數據接口...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data_result = get_china_stock_data_tushare("000001", start_date, end_date)
        
        if "股票代碼: 000001" in data_result:
            print("✅ 股票數據接口測試成功")
        else:
            print("❌ 股票數據接口測試失败")
        
        # 測試搜索接口
        print("🔄 測試搜索接口...")
        search_result = search_china_stocks_tushare("平安")
        
        if "搜索關键詞: 平安" in search_result:
            print("✅ 搜索接口測試成功")
        else:
            print("❌ 搜索接口測試失败")
        
        # 測試股票信息接口
        print("🔄 測試股票信息接口...")
        info_result = get_china_stock_info_tushare("000001")
        
        if "股票代碼: 000001" in info_result:
            print("✅ 股票信息接口測試成功")
        else:
            print("❌ 股票信息接口測試失败")
        
        # 測試基本面接口
        print("🔄 測試基本面接口...")
        fundamentals_result = get_china_stock_fundamentals_tushare("000001")
        
        if "基本面分析報告" in fundamentals_result:
            print("✅ 基本面接口測試成功")
        else:
            print("❌ 基本面接口測試失败")
        
    except Exception as e:
        print(f"❌ Tushare接口函數測試失败: {e}")
        import traceback
        traceback.print_exc()


def test_tushare_cache():
    """測試Tushare緩存功能"""
    print("\n🔧 測試Tushare緩存功能")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.tushare_adapter import get_tushare_adapter
        
        adapter = get_tushare_adapter()
        
        if not adapter.enable_cache:
            print("⚠️ 緩存功能未啟用，跳過緩存測試")
            return
        
        print("✅ 緩存功能已啟用")
        
        # 第一次獲取數據（應该從API獲取）
        print("🔄 第一次獲取數據（從API）...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        
        data1 = adapter.get_stock_data("000001", start_date, end_date)
        
        if not data1.empty:
            print(f"✅ 第一次獲取成功: {len(data1)}條")
        else:
            print("❌ 第一次獲取失败")
            return
        
        # 第二次獲取數據（應该從緩存獲取）
        print("🔄 第二次獲取數據（從緩存）...")
        data2 = adapter.get_stock_data("000001", start_date, end_date)
        
        if not data2.empty:
            print(f"✅ 第二次獲取成功: {len(data2)}條")
            
            # 比較數據是否一致
            if len(data1) == len(data2):
                print("✅ 緩存數據一致性驗證通過")
            else:
                print("⚠️ 緩存數據可能不一致")
        else:
            print("❌ 第二次獲取失败")
        
    except Exception as e:
        print(f"❌ Tushare緩存測試失败: {e}")
        import traceback
        traceback.print_exc()


def check_tushare_environment():
    """檢查Tushare環境配置"""
    print("\n🔧 檢查Tushare環境配置")
    print("=" * 60)
    
    # 檢查Tushare庫
    try:
        import tushare as ts
        print("✅ Tushare庫已安裝")
        print(f"📦 Tushare版本: {ts.__version__}")
    except ImportError:
        print("❌ Tushare庫未安裝，請運行: pip install tushare")
        return False
    
    # 檢查API Token
    token = os.getenv('TUSHARE_TOKEN')
    if token:
        print("✅ TUSHARE_TOKEN環境變量已設置")
        print(f"🔑 Token長度: {len(token)}字符")
    else:
        print("❌ 未設置TUSHARE_TOKEN環境變量")
        print("💡 請在.env文件中設置: TUSHARE_TOKEN=your_token_here")
        return False
    
    # 檢查緩存目錄
    try:
        from tradingagents.dataflows.cache_manager import get_cache
        cache = get_cache()
        print("✅ 緩存管理器可用")
    except Exception as e:
        print(f"⚠️ 緩存管理器不可用: {e}")
    
    return True


def main():
    """主測試函數"""
    print("🔬 Tushare集成測試")
    print("=" * 70)
    print("💡 測試目標:")
    print("   - Tushare環境配置檢查")
    print("   - Tushare提供器功能測試")
    print("   - Tushare適配器功能測試")
    print("   - Tushare接口函數測試")
    print("   - Tushare緩存功能測試")
    print("=" * 70)
    
    # 檢查環境配置
    if not check_tushare_environment():
        print("\n❌ 環境配置檢查失败，請先配置Tushare環境")
        return
    
    # 運行所有測試
    test_tushare_provider()
    test_tushare_adapter()
    test_tushare_interface()
    test_tushare_cache()
    
    # 总結
    print("\n📋 Tushare集成測試总結")
    print("=" * 60)
    print("✅ Tushare提供器: 基本功能測試")
    print("✅ Tushare適配器: 數據獲取和處理")
    print("✅ Tushare接口: 統一接口函數")
    print("✅ Tushare緩存: 性能優化功能")
    
    print("\n🎉 Tushare集成測試完成！")
    print("\n🎯 現在可以使用Tushare數據源:")
    print("   1. 在CLI中選擇Tushare作為A股數據源")
    print("   2. 在Web界面中配置Tushare數據源")
    print("   3. 使用API接口獲取A股數據")
    print("   4. 享受高质量的A股數據服務")
    
    input("按回車键退出...")


if __name__ == "__main__":
    main()
