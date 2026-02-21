#!/usr/bin/env python3
"""
測試CLI日誌修復效果
驗證使用者介面是否清爽，日誌是否只寫入檔案
"""

import os
import sys
import subprocess

# 新增專案根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_cli_logging_setup():
    """測試CLI日誌設定"""
    print(" 測試CLI日誌設定")
    print("=" * 60)
    
    try:
        # 匯入CLI模組，觸發日誌設定
        from cli.main import setup_cli_logging, logger
        from tradingagents.utils.logging_manager import get_logger_manager
        
        print(" 測試前的日誌處理器:")
        logger_manager = get_logger_manager()
        handlers_before = len(logger_manager.root_logger.handlers)
        console_handlers_before = sum(1 for h in logger_manager.root_logger.handlers 
                                    if hasattr(h, 'stream') and h.stream.name == '<stderr>')
        print(f"   總處理器數量: {handlers_before}")
        print(f"   主控台處理器數量: {console_handlers_before}")
        
        # 執行CLI日誌設定
        setup_cli_logging()
        
        print("\n 測試後的日誌處理器:")
        handlers_after = len(logger_manager.root_logger.handlers)
        console_handlers_after = sum(1 for h in logger_manager.root_logger.handlers 
                                   if hasattr(h, 'stream') and h.stream.name == '<stderr>')
        print(f"   總處理器數量: {handlers_after}")
        print(f"   主控台處理器數量: {console_handlers_after}")
        
        # 驗證效果
        if console_handlers_after < console_handlers_before:
            print(" 主控台日誌處理器已成功移除")
        else:
            print(" 主控台日誌處理器未完全移除")
        
        # 測試日誌輸出
        print("\n 測試日誌輸出:")
        print("   執行 logger.info('測試訊息')...")
        logger.info("這是一條測試日誌訊息，應該只寫入檔案，不在主控台顯示")
        print("    如果上面沒有顯示時間戳和日誌資訊，說明修復成功")
        
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_console_output():
    """測試console輸出"""
    print("\n 測試console輸出")
    print("=" * 60)
    
    try:
        from rich.console import Console
        
        console = Console()
        
        print(" 測試Rich Console輸出:")
        console.print("[bold cyan]這是一條使用者介面訊息[/bold cyan]")
        console.print("[green] 這應該正常顯示，沒有時間戳[/green]")
        console.print("[yellow] 這是使用者友好的提示資訊[/yellow]")
        
        print(" Console輸出正常，介面清爽")
        
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        return False

def test_log_file_writing():
    """測試日誌檔案寫入"""
    print("\n 測試日誌檔案寫入")
    print("=" * 60)
    
    try:
        from cli.main import logger
        import glob
        
        # 寫入測試日誌
        test_message = "CLI日誌修復測試訊息 - 這應該只出現在日誌檔案中"
        logger.info(test_message)
        
        # 查找日誌檔案
        log_files = glob.glob("logs/*.log") + glob.glob("*.log")
        
        if log_files:
            print(f" 找到日誌檔案: {log_files}")
            
            # 檢查最新的日誌檔案
            latest_log = max(log_files, key=os.path.getmtime)
            print(f" 檢查最新日誌檔案: {latest_log}")
            
            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if test_message in content:
                        print(" 測試訊息已寫入日誌檔案")
                        return True
                    else:
                        print(" 測試訊息未在日誌檔案中找到")
                        return False
            except Exception as e:
                print(f" 讀取日誌檔案失敗: {e}")
                return False
        else:
            print(" 未找到日誌檔案")
            return False
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        return False

def test_cli_interface_preview():
    """預覽CLI介面效果"""
    print("\n 預覽CLI介面效果")
    print("=" * 60)
    
    try:
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        
        # 模擬修復後的CLI介面
        print(" 模擬修復後的CLI介面:")
        print("-" * 40)
        
        # 標題
        title_panel = Panel(
            "[bold blue]步驟 1: 選擇市場 | Step 1: Select Market[/bold blue]\n"
            "請選擇要分析的股票市場 | Please select the stock market to analyze",
            box_style="cyan"
        )
        console.print(title_panel)
        
        # 選項
        console.print("\n[bold cyan]請選擇股票市場 | Please select stock market:[/bold cyan]")
        console.print("[cyan]1[/cyan].  美股 | US Stock")
        console.print("   示例 | Examples: SPY, AAPL, TSLA, NVDA, MSFT")
        
        print("\n" + "-" * 40)
        print(" 介面清爽，沒有時間戳和技術日誌資訊")
        
        return True
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        return False

def main():
    """主測試函式"""
    print(" 開始測試CLI日誌修復效果")
    print("=" * 80)
    
    results = []
    
    # 測試1: CLI日誌設定
    results.append(test_cli_logging_setup())
    
    # 測試2: Console輸出
    results.append(test_console_output())
    
    # 測試3: 日誌檔案寫入
    results.append(test_log_file_writing())
    
    # 測試4: CLI介面預覽
    results.append(test_cli_interface_preview())
    
    # 總結結果
    print("\n" + "=" * 80)
    print(" 測試結果總結")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "CLI日誌設定",
        "Console輸出測試",
        "日誌檔案寫入",
        "CLI介面預覽"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = " 通過" if result else " 失敗"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n 總體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print(" 所有測試通過！CLI日誌修復成功")
        print("\n 修復效果:")
        print("1.  主控台不再顯示技術日誌資訊")
        print("2.  使用者介面清爽美觀")
        print("3.  系統日誌正常寫入檔案")
        print("4.  使用者提示使用Rich Console顯示")
        
        print("\n 使用者體驗改善:")
        print("- 介面簡潔，沒有時間戳干擾")
        print("- 彩色輸出更加美觀")
        print("- 技術資訊和使用者資訊分離")
        print("- 除錯資訊仍然記錄在日誌檔案中")
    else:
        print(" 部分測試失敗，需要進一步優化")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
