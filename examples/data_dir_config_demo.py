#!/usr/bin/env python3
"""


"""

import os
import sys
from pathlib import Path

# 
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')

# Python
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.config.config_manager import config_manager
from tradingagents.dataflows.config import get_config, set_data_dir, get_data_dir
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def show_current_config():
    """"""
    logger.info(f"\n[bold blue] [/bold blue]")
    
    # 
    settings = config_manager.load_settings()
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("", style="cyan")
    table.add_column("", style="green")
    table.add_column("", style="yellow")
    
    # 
    directories = {
        "": settings.get("data_dir", ""),
        "": settings.get("cache_dir", ""),
        "": settings.get("results_dir", "")
    }
    
    for name, path in directories.items():
        if path and path != "":
            status = " " if os.path.exists(path) else " "
        else:
            status = " "
        table.add_row(name, str(path), status)
    
    console.print(table)
    
    # 
    logger.info(f"\n[bold blue] [/bold blue]")
    env_table = Table(show_header=True, header_style="bold magenta")
    env_table.add_column("", style="cyan")
    env_table.add_column("", style="green")
    
    env_vars = {
        "TRADINGAGENTS_DATA_DIR": os.getenv("TRADINGAGENTS_DATA_DIR", ""),
        "TRADINGAGENTS_CACHE_DIR": os.getenv("TRADINGAGENTS_CACHE_DIR", ""),
        "TRADINGAGENTS_RESULTS_DIR": os.getenv("TRADINGAGENTS_RESULTS_DIR", "")
    }
    
    for var, value in env_vars.items():
        env_table.add_row(var, value)
    
    console.print(env_table)

def demo_set_custom_data_dir():
    """"""
    logger.info(f"\n[bold green] [/bold green]")
    
    # 
    custom_data_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents_Custom", "data")
    
    logger.info(f": {custom_data_dir}")
    set_data_dir(custom_data_dir)
    
    # 
    current_dir = get_data_dir()
    logger.info(f": {current_dir}")
    
    if current_dir == custom_data_dir:
        logger.info(f" ")
    else:
        logger.error(f" ")
    
    # 
    logger.info(f"\n[bold blue] [/bold blue]")
    if os.path.exists(custom_data_dir):
        for root, dirs, files in os.walk(custom_data_dir):
            level = root.replace(custom_data_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            logger.info(f"{indent} {os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                logger.info(f"{subindent} {file}")

def demo_config_integration():
    """"""
    logger.info(f"\n[bold green] [/bold green]")
    
    # dataflows.config
    config = get_config()
    logger.info(f" get_config() : {config.get('data_dir')}")
    
    # config_manager
    manager_data_dir = config_manager.get_data_dir()
    logger.info(f" config_manager : {manager_data_dir}")
    
    # 
    if config.get('data_dir') == manager_data_dir:
        logger.info(f" ")
    else:
        logger.error(f" ")

def demo_environment_variable_override():
    """"""
    logger.info(f"\n[bold green] [/bold green]")
    
    # 
    test_env_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents_ENV", "data")
    os.environ["TRADINGAGENTS_DATA_DIR"] = test_env_dir
    
    logger.info(f" TRADINGAGENTS_DATA_DIR = {test_env_dir}")
    
    # 
    settings = config_manager.load_settings()
    logger.info(f": {settings.get('data_dir')}")
    
    # 
    del os.environ["TRADINGAGENTS_DATA_DIR"]
    logger.info(f"")

def demo_directory_auto_creation():
    """"""
    logger.info(f"\n[bold green] [/bold green]")
    
    # 
    test_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents_AutoCreate", "data")
    
    # 
    import shutil
    if os.path.exists(test_dir):
        shutil.rmtree(os.path.dirname(test_dir))
    
    logger.info(f": {test_dir}")
    set_data_dir(test_dir)
    
    # 
    expected_dirs = [
        test_dir,
        os.path.join(test_dir, "cache"),
        os.path.join(test_dir, "finnhub_data"),
        os.path.join(test_dir, "finnhub_data", "news_data"),
        os.path.join(test_dir, "finnhub_data", "insider_sentiment"),
        os.path.join(test_dir, "finnhub_data", "insider_transactions")
    ]
    
    logger.info(f"\n:")
    for directory in expected_dirs:
        if os.path.exists(directory):
            logger.info(f" {directory}")
        else:
            logger.error(f" {directory}")

def show_configuration_guide():
    """"""
    guide_text = """
[bold blue] [/bold blue]

[bold green]1. :[/bold green]
```python
from tradingagents.dataflows.config import set_data_dir
set_data_dir("/path/to/your/data/directory")
```

[bold green]2. :[/bold green]
```bash
# Windows
set TRADINGAGENTS_DATA_DIR=C:\\path\\to\\data

# Linux/Mac
export TRADINGAGENTS_DATA_DIR=/path/to/data
```

[bold green]3. :[/bold green]
```python
from tradingagents.config.config_manager import config_manager
config_manager.set_data_dir("/path/to/your/data/directory")
```

[bold green]4. :[/bold green]
- : config/settings.json
- :
  - data_dir: 
  - cache_dir: 
  - results_dir: 
  - auto_create_dirs: 

[bold green]5. :[/bold green]
1.  ()
2. 
3. 
4.  ()
"""
    
    console.print(Panel(guide_text, title="", border_style="blue"))

def main():
    """"""
    logger.info(f"[bold blue] TradingAgents-CN [/bold blue]")
    logger.info(f"=")
    
    try:
        # 1. 
        show_current_config()
        
        # 2. 
        demo_set_custom_data_dir()
        
        # 3. 
        demo_config_integration()
        
        # 4. 
        demo_environment_variable_override()
        
        # 5. 
        demo_directory_auto_creation()
        
        # 6. 
        show_configuration_guide()
        
        logger.info(f"\n[bold green] ![/bold green]")
        
    except Exception as e:
        logger.error(f"\n[bold red] : {e}[/bold red]")
        import traceback

        console.print(traceback.format_exc())

if __name__ == "__main__":
    main()