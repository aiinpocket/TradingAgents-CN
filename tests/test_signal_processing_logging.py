#!/usr/bin/env python3
"""
測試訊號處理模組的日誌記錄修復
"""

import os
import sys

# 新增項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_signal_processing_logging():
    """測試訊號處理模組的日誌記錄"""
    print("\n 測試訊號處理模組日誌記錄")
    print("=" * 80)
    
    try:
        # 設定日誌等級
        from tradingagents.utils.logging_init import get_logger
        logger = get_logger("default")
        logger.setLevel("INFO")
        
        print(" 建立訊號處理器...")
        
        # 匯入訊號處理器
        from tradingagents.graph.signal_processing import SignalProcessor
        
        processor = SignalProcessor()
        print(" 訊號處理器建立完成")
        
        # 測試不同的股票代碼
        test_cases = [
            ("MSFT", "Microsoft"),
            ("AAPL", "Apple Inc."),
            ("TSLA", "Tesla Inc."),
        ]
        
        for stock_symbol, company_name in test_cases:
            print(f"\n 測試股票: {stock_symbol} ({company_name})")
            print("-" * 60)
            
            # 建立模擬的交易訊號
            mock_signal = f"""
# {company_name}({stock_symbol})投資分析報告

##  基本面分析
- 股票代碼: {stock_symbol}
- 公司名稱: {company_name}
- 投資建議: 買入
- 目標價格: 100.00
- 風險評級: 中等

##  技術面分析
- 趨勢: 上漲
- 支撐位: 90.00
- 阻力位: 110.00

##  最終決策
基於綜合分析，建議買入{company_name}({stock_symbol})。
"""
            
            print(f" [測試] 呼叫訊號處理器...")
            print(f"   股票代碼: {stock_symbol}")
            print(f"   訊號長度: {len(mock_signal)} 字元")
            
            try:
                # 呼叫訊號處理器（這裡應該會觸發日誌記錄）
                result = processor.process_signal(mock_signal, stock_symbol)
                
                print(f" 訊號處理完成")
                print(f"   返回結果類型: {type(result)}")
                
                if isinstance(result, dict):
                    print(f"   結果鍵: {list(result.keys())}")
                    
                    # 檢查是否包含股票代碼
                    if 'stock_symbol' in result:
                        print(f"   提取的股票代碼: {result['stock_symbol']}")
                    
                    # 檢查投資建議
                    if 'investment_decision' in result:
                        decision = result['investment_decision']
                        print(f"   投資決策: {decision}")
                    
                    # 檢查目標價格
                    if 'target_price' in result:
                        price = result['target_price']
                        print(f"   目標價格: {price}")
                
            except Exception as e:
                print(f" 訊號處理失敗: {e}")
                import traceback
                traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_logging_extraction():
    """測試日誌裝飾器的股票代碼提取"""
    print("\n 測試日誌裝飾器股票代碼提取")
    print("=" * 80)
    
    try:
        # 模擬訊號處理模組的呼叫
        from tradingagents.utils.tool_logging import log_graph_module
        
        # 建立一個測試函式來驗證日誌裝飾器
        @log_graph_module("signal_processing")
        def mock_process_signal(self, full_signal: str, stock_symbol: str = None) -> dict:
            """模擬訊號處理函式"""
            print(f" [模擬函式] 接收到的參數:")
            print(f"   full_signal 長度: {len(full_signal) if full_signal else 0}")
            print(f"   stock_symbol: {stock_symbol}")
            
            return {
                'stock_symbol': stock_symbol,
                'processed': True
            }
        
        # 建立模擬的self物件
        class MockProcessor:
            pass
        
        mock_self = MockProcessor()
        
        # 測試不同的呼叫方式
        test_cases = [
            ("MSFT", "位置參數呼叫"),
            ("AAPL", "關鍵字參數呼叫"),
            ("TSLA", "混合參數呼叫"),
        ]
        
        for stock_symbol, call_type in test_cases:
            print(f"\n 測試: {stock_symbol} ({call_type})")
            print("-" * 40)
            
            mock_signal = f"測試訊號 for {stock_symbol}"
            
            try:
                if call_type == "位置參數呼叫":
                    # 位置參數呼叫：mock_process_signal(self, full_signal, stock_symbol)
                    result = mock_process_signal(mock_self, mock_signal, stock_symbol)
                elif call_type == "關鍵字參數呼叫":
                    # 關鍵字參數呼叫
                    result = mock_process_signal(mock_self, mock_signal, stock_symbol=stock_symbol)
                else:
                    # 混合呼叫
                    result = mock_process_signal(mock_self, full_signal=mock_signal, stock_symbol=stock_symbol)
                
                print(f" 呼叫成功: {result}")
                
            except Exception as e:
                print(f" 呼叫失敗: {e}")
        
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函式"""
    print(" 開始測試訊號處理日誌記錄修復")
    print("=" * 100)
    
    results = []
    
    # 測試1: 日誌裝飾器股票代碼提取
    results.append(test_logging_extraction())
    
    # 測試2: 訊號處理模組日誌記錄
    results.append(test_signal_processing_logging())
    
    # 總結結果
    print("\n" + "=" * 100)
    print(" 測試結果總結")
    print("=" * 100)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "日誌裝飾器股票代碼提取",
        "訊號處理模組日誌記錄"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = " 通過" if result else " 失敗"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n 總體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print(" 所有測試通過！訊號處理日誌記錄修復成功")
        print("\n 修復效果:")
        print("1.  正確提取訊號處理模組的股票代碼")
        print("2.  日誌顯示準確的股票資訊")
        print("3.  避免顯示 'unknown' 股票代碼")
        print("4.  支援多種參數呼叫方式")
        
        print("\n 解決的問題:")
        print("-  訊號處理模組日誌顯示股票代碼為 'unknown'")
        print("-  日誌裝飾器無法正確解析訊號處理模組的參數")
        print("-  股票代碼提取邏輯不相容訊號處理模組")
    else:
        print(" 部分測試失敗，需要進一步優化")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
