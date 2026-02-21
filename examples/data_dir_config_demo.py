#!/usr/bin/env python3
"""
數據目錄配置演示
展示如何使用新的數據目錄配置功能
"""

import os
import sys
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.config.config_manager import config_manager
from tradingagents.dataflows.config import get_config, set_data_dir, get_data_dir
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def show_current_config():
    """顯示當前配置"""
    logger.info(f"\n[bold blue]📁 當前數據目錄配置[/bold blue]")
    
    # 從配置管理器獲取設置
    settings = config_manager.load_settings()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("配置項", style="cyan")
    table.add_column("路徑", style="green")
    table.add_column("狀態", style="yellow")
    
    # 檢查各個目錄
    directories = {
        "數據目錄": settings.get("data_dir", "未配置"),
        "緩存目錄": settings.get("cache_dir", "未配置"),
        "結果目錄": settings.get("results_dir", "未配置")
    }
    
    for name, path in directories.items():
        if path and path != "未配置":
            status = "✅ 存在" if os.path.exists(path) else "❌ 不存在"
        else:
            status = "⚠️ 未配置"
        table.add_row(name, str(path), status)
    
    console.print(table)
    
    # 顯示環境變量配置
    logger.info(f"\n[bold blue]🌍 環境變量配置[/bold blue]")
    env_table = Table(show_header=True, header_style="bold magenta")
    env_table.add_column("環境變量", style="cyan")
    env_table.add_column("值", style="green")
    
    env_vars = {
        "TRADINGAGENTS_DATA_DIR": os.getenv("TRADINGAGENTS_DATA_DIR", "未設置"),
        "TRADINGAGENTS_CACHE_DIR": os.getenv("TRADINGAGENTS_CACHE_DIR", "未設置"),
        "TRADINGAGENTS_RESULTS_DIR": os.getenv("TRADINGAGENTS_RESULTS_DIR", "未設置")
    }
    
    for var, value in env_vars.items():
        env_table.add_row(var, value)
    
    console.print(env_table)

def demo_set_custom_data_dir():
    """演示設置自定義數據目錄"""
    logger.info(f"\n[bold green]🔧 設置自定義數據目錄演示[/bold green]")
    
    # 設置自定義數據目錄
    custom_data_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents_Custom", "data")
    
    logger.info(f"設置數據目錄為: {custom_data_dir}")
    set_data_dir(custom_data_dir)
    
    # 驗證設置
    current_dir = get_data_dir()
    logger.info(f"當前數據目錄: {current_dir}")
    
    if current_dir == custom_data_dir:
        logger.info(f"✅ 數據目錄設置成功")
    else:
        logger.error(f"❌ 數據目錄設置失敗")
    
    # 顯示創建的目錄結構
    logger.info(f"\n[bold blue]📂 創建的目錄結構[/bold blue]")
    if os.path.exists(custom_data_dir):
        for root, dirs, files in os.walk(custom_data_dir):
            level = root.replace(custom_data_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            logger.info(f"{indent}📁 {os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                logger.info(f"{subindent}📄 {file}")

def demo_config_integration():
    """演示配置集成"""
    logger.info(f"\n[bold green]🔗 配置集成演示[/bold green]")
    
    # 通過dataflows.config獲取配置
    config = get_config()
    logger.info(f"通過 get_config() 獲取的數據目錄: {config.get('data_dir')}")
    
    # 通過config_manager獲取配置
    manager_data_dir = config_manager.get_data_dir()
    logger.info(f"通過 config_manager 獲取的數據目錄: {manager_data_dir}")
    
    # 驗證一致性
    if config.get('data_dir') == manager_data_dir:
        logger.info(f"✅ 配置一致性驗證通過")
    else:
        logger.error(f"❌ 配置一致性驗證失敗")

def demo_environment_variable_override():
    """演示環境變量覆蓋"""
    logger.info(f"\n[bold green]🌍 環境變量覆蓋演示[/bold green]")
    
    # 模擬設置環境變量
    test_env_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents_ENV", "data")
    os.environ["TRADINGAGENTS_DATA_DIR"] = test_env_dir
    
    logger.info(f"設置環境變量 TRADINGAGENTS_DATA_DIR = {test_env_dir}")
    
    # 重新加載配置
    settings = config_manager.load_settings()
    logger.info(f"重新加載後的數據目錄: {settings.get('data_dir')}")
    
    # 清理環境變量
    del os.environ["TRADINGAGENTS_DATA_DIR"]
    logger.info(f"清理環境變量")

def demo_directory_auto_creation():
    """演示目錄自動創建"""
    logger.info(f"\n[bold green]🏗️ 目錄自動創建演示[/bold green]")
    
    # 設置一個新的數據目錄
    test_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents_AutoCreate", "data")
    
    # 確保目錄不存在
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(os.path.dirname(test_dir))
    
    logger.info(f"設置新數據目錄: {test_dir}")
    set_data_dir(test_dir)
    
    # 檢查目錄是否被創建
    expected_dirs = [
        test_dir,
        os.path.join(test_dir, "cache"),
        os.path.join(test_dir, "finnhub_data"),
        os.path.join(test_dir, "finnhub_data", "news_data"),
        os.path.join(test_dir, "finnhub_data", "insider_sentiment"),
        os.path.join(test_dir, "finnhub_data", "insider_transactions")
    ]
    
    logger.info(f"\n檢查自動創建的目錄:")
    for directory in expected_dirs:
        if os.path.exists(directory):
            logger.info(f"✅ {directory}")
        else:
            logger.error(f"❌ {directory}")

def show_configuration_guide():
    """顯示配置指南"""
    guide_text = """
[bold blue]📖 數據目錄配置指南[/bold blue]

[bold green]1. 通過代碼配置:[/bold green]
```python
from tradingagents.dataflows.config import set_data_dir
set_data_dir("/path/to/your/data/directory")
```

[bold green]2. 通過環境變量配置:[/bold green]
```bash
# Windows
set TRADINGAGENTS_DATA_DIR=C:\\path\\to\\data

# Linux/Mac
export TRADINGAGENTS_DATA_DIR=/path/to/data
```

[bold green]3. 通過配置管理器:[/bold green]
```python
from tradingagents.config.config_manager import config_manager
config_manager.set_data_dir("/path/to/your/data/directory")
```

[bold green]4. 配置文件位置:[/bold green]
- 配置檔案儲存在: config/settings.json
- 支持的配置項:
  - data_dir: 數據目錄
  - cache_dir: 緩存目錄
  - results_dir: 結果目錄
  - auto_create_dirs: 自動創建目錄

[bold green]5. 優先級:[/bold green]
1. 環境變量 (最高優先級)
2. 代碼中的設置
3. 配置文件中的設置
4. 默認值 (最低優先級)
"""
    
    console.print(Panel(guide_text, title="配置指南", border_style="blue"))

def main():
    """主演示函數"""
    logger.info(f"[bold blue]🎯 TradingAgents-CN 數據目錄配置演示[/bold blue]")
    logger.info(f"=")
    
    try:
        # 1. 顯示當前配置
        show_current_config()
        
        # 2. 演示設置自定義數據目錄
        demo_set_custom_data_dir()
        
        # 3. 演示配置集成
        demo_config_integration()
        
        # 4. 演示環境變量覆蓋
        demo_environment_variable_override()
        
        # 5. 演示目錄自動創建
        demo_directory_auto_creation()
        
        # 6. 顯示配置指南
        show_configuration_guide()
        
        logger.info(f"\n[bold green]✅ 演示完成![/bold green]")
        
    except Exception as e:
        logger.error(f"\n[bold red]❌ 演示過程中出現錯誤: {e}[/bold red]")
        import traceback

        console.print(traceback.format_exc())

if __name__ == "__main__":
    main()