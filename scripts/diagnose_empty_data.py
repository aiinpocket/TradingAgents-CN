#!/usr/bin/env python3
"""
診斷Tushare返回空數據的原因
分析時間參數、股票代碼、API限制等可能的問題
"""

import sys
import os
from datetime import datetime, timedelta

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_time_parameters():
    """測試不同的時間參數"""
    print("🕐 測試時間參數...")
    print("=" * 60)
    
    # 測試不同的時間範围
    test_cases = [
        {
            "name": "原始問題時間",
            "start": "2025-01-10", 
            "end": "2025-01-17"
        },
        {
            "name": "最近7天",
            "start": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            "end": datetime.now().strftime('%Y-%m-%d')
        },
        {
            "name": "最近30天", 
            "start": (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
            "end": datetime.now().strftime('%Y-%m-%d')
        },
        {
            "name": "2024年最後一周",
            "start": "2024-12-25",
            "end": "2024-12-31"
        },
        {
            "name": "2025年第一周",
            "start": "2025-01-01", 
            "end": "2025-01-07"
        }
    ]
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        provider = get_tushare_provider()
        
        if not provider.connected:
            print("❌ Tushare未連接")
            return
        
        symbol = "300033"  # 同花顺
        
        for case in test_cases:
            print(f"\n📅 {case['name']}: {case['start']} 到 {case['end']}")
            
            try:
                data = provider.get_stock_daily(symbol, case['start'], case['end'])
                
                if data is not None and not data.empty:
                    print(f"   ✅ 獲取成功: {len(data)}條數據")
                    print(f"   📊 數據範围: {data['trade_date'].min()} 到 {data['trade_date'].max()}")
                else:
                    print(f"   ❌ 返回空數據")
                    
            except Exception as e:
                print(f"   ❌ 異常: {e}")
                
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

def test_stock_codes():
    """測試不同的股票代碼"""
    print("\n📊 測試不同股票代碼...")
    print("=" * 60)
    
    # 測試不同類型的股票
    test_symbols = [
        {"code": "300033", "name": "同花顺", "market": "創業板"},
        {"code": "000001", "name": "平安銀行", "market": "深圳主板"},
        {"code": "600036", "name": "招商銀行", "market": "上海主板"},
        {"code": "688001", "name": "華兴源創", "market": "科創板"},
        {"code": "002415", "name": "海康威視", "market": "深圳中小板"},
    ]
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        provider = get_tushare_provider()
        
        if not provider.connected:
            print("❌ Tushare未連接")
            return
        
        # 使用最近7天的數據
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"📅 測試時間範围: {start_date} 到 {end_date}")
        
        for symbol_info in test_symbols:
            symbol = symbol_info["code"]
            print(f"\n📈 {symbol} ({symbol_info['name']} - {symbol_info['market']})")
            
            try:
                data = provider.get_stock_daily(symbol, start_date, end_date)
                
                if data is not None and not data.empty:
                    print(f"   ✅ 獲取成功: {len(data)}條數據")
                    # 顯示最新一條數據
                    latest = data.iloc[-1]
                    print(f"   💰 最新價格: {latest['close']:.2f}")
                else:
                    print(f"   ❌ 返回空數據")
                    
            except Exception as e:
                print(f"   ❌ 異常: {e}")
                
    except Exception as e:
        print(f"❌ 初始化失败: {e}")

def test_api_limits():
    """測試API限制和權限"""
    print("\n🔐 測試API限制和權限...")
    print("=" * 60)
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        import time
        
        provider = get_tushare_provider()
        
        if not provider.connected:
            print("❌ Tushare未連接")
            return
        
        # 測試基本信息獲取（通常權限要求較低）
        print("📋 測試股票基本信息獲取...")
        try:
            stock_list = provider.get_stock_list()
            if stock_list is not None and not stock_list.empty:
                print(f"   ✅ 股票列表獲取成功: {len(stock_list)}只股票")
            else:
                print(f"   ❌ 股票列表為空")
        except Exception as e:
            print(f"   ❌ 股票列表獲取失败: {e}")
        
        # 測試連续調用（檢查頻率限制）
        print("\n⏱️ 測試API調用頻率...")
        symbol = "000001"
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        
        for i in range(3):
            print(f"   第{i+1}次調用...")
            start_time = time.time()
            
            try:
                data = provider.get_stock_daily(symbol, start_date, end_date)
                duration = time.time() - start_time
                
                if data is not None and not data.empty:
                    print(f"   ✅ 成功: {len(data)}條數據，耗時: {duration:.2f}秒")
                else:
                    print(f"   ❌ 空數據，耗時: {duration:.2f}秒")
                    
            except Exception as e:
                duration = time.time() - start_time
                print(f"   ❌ 異常: {e}，耗時: {duration:.2f}秒")
            
            # 短暂延迟避免頻率限制
            if i < 2:
                time.sleep(1)
                
    except Exception as e:
        print(f"❌ 測試失败: {e}")

def test_date_formats():
    """測試日期格式處理"""
    print("\n📅 測試日期格式處理...")
    print("=" * 60)
    
    # 測試不同的日期格式
    date_formats = [
        {"format": "YYYY-MM-DD", "start": "2025-01-10", "end": "2025-01-17"},
        {"format": "YYYYMMDD", "start": "20250110", "end": "20250117"},
    ]
    
    try:
        from tradingagents.dataflows.tushare_utils import get_tushare_provider
        provider = get_tushare_provider()
        
        if not provider.connected:
            print("❌ Tushare未連接")
            return
        
        symbol = "000001"
        
        for fmt in date_formats:
            print(f"\n📝 測試格式 {fmt['format']}: {fmt['start']} 到 {fmt['end']}")
            
            try:
                data = provider.get_stock_daily(symbol, fmt['start'], fmt['end'])
                
                if data is not None and not data.empty:
                    print(f"   ✅ 獲取成功: {len(data)}條數據")
                else:
                    print(f"   ❌ 返回空數據")
                    
            except Exception as e:
                print(f"   ❌ 異常: {e}")
                
    except Exception as e:
        print(f"❌ 測試失败: {e}")

def main():
    """主函數"""
    print("🔍 Tushare空數據問題診斷")
    print("=" * 80)
    
    # 1. 測試時間參數
    test_time_parameters()
    
    # 2. 測試股票代碼
    test_stock_codes()
    
    # 3. 測試API限制
    test_api_limits()
    
    # 4. 測試日期格式
    test_date_formats()
    
    # 5. 总結
    print("\n📋 診斷总結")
    print("=" * 60)
    print("💡 可能的原因:")
    print("   1. 時間範围問題 - 查詢的日期範围內没有交易數據")
    print("   2. 股票代碼問題 - 股票代碼格式不正確或股票已退市")
    print("   3. API權限問題 - Tushare账號權限不足")
    print("   4. 網絡問題 - 網絡連接不穩定")
    print("   5. 緩存問題 - 緩存了錯誤的空數據")
    print("   6. 交易日歷 - 查詢日期不是交易日")

if __name__ == "__main__":
    main()
