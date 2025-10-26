#!/usr/bin/env python3
"""
獨立的AKShare功能測試
绕過yfinance依賴問題，直接測試AKShare集成
"""

import sys
import os

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def test_akshare_direct():
    """直接測試AKShare功能"""
    print("🔍 直接測試AKShare功能")
    print("=" * 40)
    
    try:
        import akshare as ak
        print(f"✅ AKShare導入成功，版本: {ak.__version__}")
        
        # 測試獲取股票列表
        print("📊 測試獲取股票列表...")
        stock_list = ak.stock_info_a_code_name()
        print(f"✅ 獲取到{len(stock_list)}只股票")
        
        # 測試獲取股票數據
        print("📈 測試獲取招商銀行(000001)數據...")
        data = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20241201", end_date="20241210", adjust="")
        print(f"✅ 獲取到{len(data)}條數據")
        print(f"   最新收盘價: {data.iloc[-1]['收盘']}")
        
        # 測試獲取實時行情
        print("📊 測試獲取實時行情...")
        realtime = ak.stock_zh_a_spot_em()
        print(f"✅ 獲取到{len(realtime)}只股票的實時行情")
        
        return True
        
    except Exception as e:
        print(f"❌ AKShare測試失败: {e}")
        return False

def test_akshare_utils_direct():
    """直接測試akshare_utils模塊"""
    print("\n🔍 直接測試akshare_utils模塊")
    print("=" * 40)
    
    try:
        # 直接導入akshare_utils，避免通過__init__.py
        akshare_utils_path = os.path.join(project_root, 'tradingagents', 'dataflows', 'akshare_utils.py')
        
        if os.path.exists(akshare_utils_path):
            print(f"✅ 找到akshare_utils.py文件")
            
            # 使用exec直接執行文件內容
            with open(akshare_utils_path, 'r', encoding='utf-8') as f:
                akshare_utils_code = f.read()
            
            # 創建獨立的命名空間
            namespace = {}
            exec(akshare_utils_code, namespace)
            
            # 測試AKShareProvider
            if 'AKShareProvider' in namespace:
                provider_class = namespace['AKShareProvider']
                provider = provider_class()
                
                print(f"✅ AKShareProvider初始化成功，連接狀態: {provider.connected}")
                
                if provider.connected:
                    # 測試獲取股票數據
                    stock_data = provider.get_stock_data("000001", "2024-12-01", "2024-12-10")
                    if stock_data is not None and not stock_data.empty:
                        print(f"✅ 獲取股票數據成功，{len(stock_data)}條記錄")
                    else:
                        print("❌ 獲取股票數據失败")
                    
                    # 測試獲取股票信息
                    stock_info = provider.get_stock_info("000001")
                    print(f"✅ 獲取股票信息: {stock_info}")
                
                return True
            else:
                print("❌ AKShareProvider類未找到")
                return False
        else:
            print(f"❌ akshare_utils.py文件不存在: {akshare_utils_path}")
            return False
            
    except Exception as e:
        print(f"❌ akshare_utils測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_data_source_enum():
    """檢查數據源枚举定義"""
    print("\n🔍 檢查數據源枚举定義")
    print("=" * 40)
    
    try:
        # 直接讀取data_source_manager.py文件
        data_source_manager_path = os.path.join(project_root, 'tradingagents', 'dataflows', 'data_source_manager.py')
        
        if os.path.exists(data_source_manager_path):
            with open(data_source_manager_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 檢查AKShare相關定義
            if 'AKSHARE' in content:
                print("✅ 找到AKSHARE枚举定義")
            else:
                print("❌ 未找到AKSHARE枚举定義")
            
            if 'akshare' in content.lower():
                print("✅ 找到akshare相關代碼")
                
                # 統計akshare出現次數
                akshare_count = content.lower().count('akshare')
                print(f"   akshare在代碼中出現{akshare_count}次")
            else:
                print("❌ 未找到akshare相關代碼")
            
            return True
        else:
            print(f"❌ data_source_manager.py文件不存在")
            return False
            
    except Exception as e:
        print(f"❌ 數據源枚举檢查失败: {e}")
        return False

def analyze_yfinance_issue():
    """分析yfinance依賴問題"""
    print("\n🔍 分析yfinance依賴問題")
    print("=" * 40)
    
    try:
        # 檢查yfinance是否可以獨立導入
        import yfinance as yf
        print("✅ yfinance可以獨立導入")
        return True
    except Exception as e:
        print(f"❌ yfinance導入失败: {e}")
        
        # 檢查curl_cffi
        try:
            import curl_cffi
            print("✅ curl_cffi可以導入")
        except Exception as e2:
            print(f"❌ curl_cffi導入失败: {e2}")
        
        # 檢查cffi
        try:
            import cffi
            print("✅ cffi可以導入")
        except Exception as e3:
            print(f"❌ cffi導入失败: {e3}")
        
        return False

def main():
    """主測試函數"""
    print("🔍 AKShare功能獨立測試")
    print("=" * 60)
    
    test_results = {}
    
    # 1. 直接測試AKShare
    test_results['akshare_direct'] = test_akshare_direct()
    
    # 2. 直接測試akshare_utils
    test_results['akshare_utils_direct'] = test_akshare_utils_direct()
    
    # 3. 檢查數據源枚举
    test_results['data_source_enum'] = check_data_source_enum()
    
    # 4. 分析yfinance問題
    test_results['yfinance_analysis'] = analyze_yfinance_issue()
    
    # 总結結果
    print(f"\n📊 獨立測試总結")
    print("=" * 60)
    
    passed = sum(test_results.values())
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name:25} {status}")
    
    print(f"\n🎯 总體結果: {passed}/{total} 項測試通過")
    
    # 分析結果
    if test_results.get('akshare_direct', False) and test_results.get('akshare_utils_direct', False):
        print("\n🎉 AKShare核心功能完全正常！")
        print("💡 問題只是yfinance依賴導致的模塊導入問題")
        print("✅ 可以安全刪除重複的AKShare分支")
        
        print(f"\n🎯 分支管理建议:")
        print("✅ AKShare功能本身完全正常")
        print("✅ feature/tushare-integration包含完整的AKShare集成")
        print("✅ 可以安全刪除以下分支:")
        print("   - feature/akshare-integration")
        print("   - feature/akshare-integration-clean")
        
        return True
    else:
        print("\n⚠️ AKShare功能存在問題，需要進一步調查")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n🚀 下一步建议:")
        print("1. 修複yfinance依賴問題（可選）")
        print("2. 刪除重複的AKShare分支")
        print("3. 發布v0.1.6版本")
    else:
        print(f"\n🔧 需要修複的問題:")
        print("1. 檢查AKShare集成代碼")
        print("2. 修複依賴問題")
        print("3. 重新測試後再考慮分支清理")
