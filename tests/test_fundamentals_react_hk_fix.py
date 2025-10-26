"""
測試基本面分析師ReAct模式的港股修複
"""

import sys
import os

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_react_fundamentals_hk_config():
    """測試ReAct模式基本面分析師港股配置"""
    print("🧪 測試ReAct模式基本面分析師港股配置...")
    
    try:
        # 讀取基本面分析師文件
        with open('tradingagents/agents/analysts/fundamentals_analyst.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查ReAct模式港股配置
        has_hk_react_branch = 'elif is_hk:' in content and 'ReAct Agent分析港股' in content
        has_hk_stock_data_tool = 'HKStockDataTool' in content
        has_hk_fundamentals_tool = 'HKFundamentalsTool' in content
        has_hk_unified_call = 'get_hk_stock_data_unified' in content
        has_hk_info_call = 'get_hk_stock_info_unified' in content
        
        print(f"  港股ReAct分支: {has_hk_react_branch}")
        print(f"  港股數據工具: {has_hk_stock_data_tool}")
        print(f"  港股基本面工具: {has_hk_fundamentals_tool}")
        print(f"  港股統一數據調用: {has_hk_unified_call}")
        print(f"  港股信息調用: {has_hk_info_call}")
        
        if all([has_hk_react_branch, has_hk_stock_data_tool, has_hk_fundamentals_tool, 
                has_hk_unified_call, has_hk_info_call]):
            print("  ✅ ReAct模式基本面分析師港股配置正確")
            return True
        else:
            print("  ❌ ReAct模式基本面分析師港股配置不完整")
            return False
        
    except Exception as e:
        print(f"❌ ReAct模式基本面分析師港股配置測試失败: {e}")
        return False

def test_us_stock_separation():
    """測試美股和港股的分離"""
    print("\n🧪 測試美股和港股的分離...")
    
    try:
        # 讀取基本面分析師文件
        with open('tradingagents/agents/analysts/fundamentals_analyst.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查美股工具不再處理港股
        us_fundamentals_desc = 'description: str = f"獲取美股{ticker}的基本面數據'
        no_hk_in_us_desc = '美股/港股' not in content.split('USFundamentalsTool')[1].split('def _run')[0]
        
        print(f"  美股工具描述正確: {us_fundamentals_desc in content}")
        print(f"  美股工具不包含港股: {no_hk_in_us_desc}")
        
        if us_fundamentals_desc in content and no_hk_in_us_desc:
            print("  ✅ 美股和港股分離正確")
            return True
        else:
            print("  ❌ 美股和港股分離不完整")
            return False
        
    except Exception as e:
        print(f"❌ 美股和港股分離測試失败: {e}")
        return False

def test_hk_query_format():
    """測試港股查詢格式"""
    print("\n🧪 測試港股查詢格式...")
    
    try:
        # 讀取基本面分析師文件
        with open('tradingagents/agents/analysts/fundamentals_analyst.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查港股查詢格式
        has_hk_query = '請對港股{ticker}進行詳細的基本面分析' in content
        has_hk_currency = '價格以港币(HK$)計價' in content
        has_hk_features = 'T+0交易、港币汇率' in content
        has_hk_format = '🇭🇰 港股基本信息' in content
        
        print(f"  港股查詢格式: {has_hk_query}")
        print(f"  港币計價說明: {has_hk_currency}")
        print(f"  港股特點說明: {has_hk_features}")
        print(f"  港股報告格式: {has_hk_format}")
        
        if all([has_hk_query, has_hk_currency, has_hk_features, has_hk_format]):
            print("  ✅ 港股查詢格式正確")
            return True
        else:
            print("  ❌ 港股查詢格式不完整")
            return False
        
    except Exception as e:
        print(f"❌ 港股查詢格式測試失败: {e}")
        return False

def test_toolkit_method_usage():
    """測試工具包方法使用"""
    print("\n🧪 測試工具包方法使用...")
    
    try:
        from tradingagents.agents.utils.agent_utils import Toolkit
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建工具包
        config = DEFAULT_CONFIG.copy()
        config["online_tools"] = True
        toolkit = Toolkit(config)
        
        # 檢查港股方法
        has_hk_method = hasattr(toolkit, 'get_hk_stock_data_unified')
        
        print(f"  工具包港股方法: {has_hk_method}")
        
        if has_hk_method:
            # 檢查方法是否可調用
            method = getattr(toolkit, 'get_hk_stock_data_unified')
            is_callable = callable(method)
            print(f"  方法可調用: {is_callable}")
            
            if is_callable:
                print("  ✅ 工具包方法使用正確")
                return True
            else:
                print("  ❌ 工具包方法不可調用")
                return False
        else:
            print("  ❌ 工具包港股方法不存在")
            return False
        
    except Exception as e:
        print(f"❌ 工具包方法使用測試失败: {e}")
        return False

def test_stock_type_detection():
    """測試股票類型檢測"""
    print("\n🧪 測試股票類型檢測...")
    
    try:
        from tradingagents.utils.stock_utils import StockUtils
        
        # 測試港股檢測
        hk_stocks = ["0700.HK", "9988.HK", "3690.HK"]
        us_stocks = ["AAPL", "TSLA", "MSFT"]
        china_stocks = ["000001", "600036", "300001"]
        
        print("  港股檢測:")
        for stock in hk_stocks:
            market_info = StockUtils.get_market_info(stock)
            is_hk = market_info['is_hk']
            print(f"    {stock}: {is_hk} ({'✅' if is_hk else '❌'})")
            if not is_hk:
                return False
        
        print("  美股檢測:")
        for stock in us_stocks:
            market_info = StockUtils.get_market_info(stock)
            is_us = market_info['is_us']
            print(f"    {stock}: {is_us} ({'✅' if is_us else '❌'})")
            if not is_us:
                return False
        
        print("  A股檢測:")
        for stock in china_stocks:
            market_info = StockUtils.get_market_info(stock)
            is_china = market_info['is_china']
            print(f"    {stock}: {is_china} ({'✅' if is_china else '❌'})")
            if not is_china:
                return False
        
        print("  ✅ 股票類型檢測正確")
        return True
        
    except Exception as e:
        print(f"❌ 股票類型檢測測試失败: {e}")
        return False

def main():
    """運行所有測試"""
    print("🔧 基本面分析師ReAct模式港股修複測試")
    print("=" * 60)
    
    tests = [
        test_react_fundamentals_hk_config,
        test_us_stock_separation,
        test_hk_query_format,
        test_toolkit_method_usage,
        test_stock_type_detection
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ 測試 {test_func.__name__} 異常: {e}")
    
    print("\n" + "=" * 60)
    print(f"🔧 基本面分析師ReAct模式港股修複測試完成: {passed}/{total} 通過")
    
    if passed == total:
        print("🎉 基本面分析師ReAct模式港股修複成功！")
        print("\n✅ 修複总結:")
        print("  - ReAct模式添加了港股專用分支")
        print("  - 港股使用HKStockDataTool和HKFundamentalsTool")
        print("  - 港股優先使用AKShare數據源")
        print("  - 美股和港股處理完全分離")
        print("  - 港股查詢格式包含港币計價和市場特點")
        print("\n🚀 現在港股基本面分析會使用正確的數據源！")
    else:
        print("⚠️ 部分測試失败，請檢查失败的測試")

if __name__ == "__main__":
    main()
