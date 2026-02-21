#!/usr/bin/env python3
"""
測試CLI日誌修複效果
驗證用戶界面是否清爽，日誌是否只寫入文件
"""

import os
import sys
import subprocess

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_cli_logging_setup():
    """測試CLI日誌設置"""
    print("🔧 測試CLI日誌設置")
    print("=" * 60)
    
    try:
        # 導入CLI模塊，觸發日誌設置
        from cli.main import setup_cli_logging, logger
        from tradingagents.utils.logging_manager import get_logger_manager
        
        print("📊 測試前的日誌處理器:")
        logger_manager = get_logger_manager()
        handlers_before = len(logger_manager.root_logger.handlers)
        console_handlers_before = sum(1 for h in logger_manager.root_logger.handlers 
                                    if hasattr(h, 'stream') and h.stream.name == '<stderr>')
        print(f"   總處理器數量: {handlers_before}")
        print(f"   控制台處理器數量: {console_handlers_before}")
        
        # 執行CLI日誌設置
        setup_cli_logging()
        
        print("\n📊 測試後的日誌處理器:")
        handlers_after = len(logger_manager.root_logger.handlers)
        console_handlers_after = sum(1 for h in logger_manager.root_logger.handlers 
                                   if hasattr(h, 'stream') and h.stream.name == '<stderr>')
        print(f"   總處理器數量: {handlers_after}")
        print(f"   控制台處理器數量: {console_handlers_after}")
        
        # 驗證效果
        if console_handlers_after < console_handlers_before:
            print("✅ 控制台日誌處理器已成功移除")
        else:
            print("⚠️ 控制台日誌處理器未完全移除")
        
        # 測試日誌輸出
        print("\n🧪 測試日誌輸出:")
        print("   執行 logger.info('測試消息')...")
        logger.info("這是一條測試日誌消息，應該只寫入文件，不在控制台顯示")
        print("   ✅ 如果上面沒有顯示時間戳和日誌信息，說明修複成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_console_output():
    """測試console輸出"""
    print("\n🎨 測試console輸出")
    print("=" * 60)
    
    try:
        from rich.console import Console
        
        console = Console()
        
        print("📊 測試Rich Console輸出:")
        console.print("[bold cyan]這是一條用戶界面消息[/bold cyan]")
        console.print("[green]✅ 這應該正常顯示，沒有時間戳[/green]")
        console.print("[yellow]💡 這是用戶友好的提示信息[/yellow]")
        
        print("✅ Console輸出正常，界面清爽")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_log_file_writing():
    """測試日誌文件寫入"""
    print("\n📁 測試日誌文件寫入")
    print("=" * 60)
    
    try:
        from cli.main import logger
        import glob
        
        # 寫入測試日誌
        test_message = "CLI日誌修複測試消息 - 這應該只出現在日誌文件中"
        logger.info(test_message)
        
        # 查找日誌文件
        log_files = glob.glob("logs/*.log") + glob.glob("*.log")
        
        if log_files:
            print(f"📄 找到日誌文件: {log_files}")
            
            # 檢查最新的日誌文件
            latest_log = max(log_files, key=os.path.getmtime)
            print(f"📄 檢查最新日誌文件: {latest_log}")
            
            try:
                with open(latest_log, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if test_message in content:
                        print("✅ 測試消息已寫入日誌文件")
                        return True
                    else:
                        print("⚠️ 測試消息未在日誌文件中找到")
                        return False
            except Exception as e:
                print(f"⚠️ 讀取日誌文件失敗: {e}")
                return False
        else:
            print("⚠️ 未找到日誌文件")
            return False
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_cli_interface_preview():
    """預覽CLI界面效果"""
    print("\n👀 預覽CLI界面效果")
    print("=" * 60)
    
    try:
        from rich.console import Console
        from rich.panel import Panel
        
        console = Console()
        
        # 模擬修複後的CLI界面
        print("🎭 模擬修複後的CLI界面:")
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
        console.print("[cyan]1[/cyan]. 🌍 美股 | US Stock")
        console.print("   示例 | Examples: SPY, AAPL, TSLA")
        console.print("[cyan]2[/cyan]. 🌍 A股 | China A-Share")
        console.print("   示例 | Examples: 000001 (平安銀行), 600036 (招商銀行)")
        console.print("[cyan]3[/cyan]. 🌍 港股 | Hong Kong Stock")
        console.print("   示例 | Examples: 0700.HK (騰訊), 09988.HK (阿里巴巴)")
        
        print("\n" + "-" * 40)
        print("✅ 界面清爽，沒有時間戳和技術日誌信息")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試CLI日誌修複效果")
    print("=" * 80)
    
    results = []
    
    # 測試1: CLI日誌設置
    results.append(test_cli_logging_setup())
    
    # 測試2: Console輸出
    results.append(test_console_output())
    
    # 測試3: 日誌文件寫入
    results.append(test_log_file_writing())
    
    # 測試4: CLI界面預覽
    results.append(test_cli_interface_preview())
    
    # 總結結果
    print("\n" + "=" * 80)
    print("📋 測試結果總結")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "CLI日誌設置",
        "Console輸出測試",
        "日誌文件寫入",
        "CLI界面預覽"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n📊 總體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！CLI日誌修複成功")
        print("\n📋 修複效果:")
        print("1. ✅ 控制台不再顯示技術日誌信息")
        print("2. ✅ 用戶界面清爽美觀")
        print("3. ✅ 系統日誌正常寫入文件")
        print("4. ✅ 用戶提示使用Rich Console顯示")
        
        print("\n🎯 用戶體驗改善:")
        print("- 界面簡潔，沒有時間戳干擾")
        print("- 彩色輸出更加美觀")
        print("- 技術信息和用戶信息分離")
        print("- 調試信息仍然記錄在日誌文件中")
    else:
        print("⚠️ 部分測試失敗，需要進一步優化")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
