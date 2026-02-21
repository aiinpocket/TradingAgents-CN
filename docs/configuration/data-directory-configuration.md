# | Data Directory Configuration Guide

TradingAgents

This guide explains how to configure data directory paths in TradingAgents, resolve path-related issues, and provides multiple configuration methods.

## | Overview

TradingAgents
- 
- 
- CLI
- 

TradingAgents supports flexible data directory configuration, allowing users to:
- Customize data storage locations
- Configure via environment variables
- Manage through CLI commands
- Automatically create necessary directory structures

## | Configuration Methods

### 1. CLI | CLI Command Configuration

#### | View Current Configuration
```bash
# 
python -m cli.main data-config
python -m cli.main data-config --show
```

#### | Set Custom Data Directory
```bash
# Windows
python -m cli.main data-config --set "C:\MyTradingData"

# Linux/macOS
python -m cli.main data-config --set "/home/user/trading-data"
```

#### | Reset to Default Configuration
```bash
python -m cli.main data-config --reset
```

### 2. | Environment Variable Configuration

#### Windows
```cmd
# 
set TRADINGAGENTS_DATA_DIR=C:\MyTradingData

# 
set TRADINGAGENTS_CACHE_DIR=C:\MyTradingData\cache

# 
set TRADINGAGENTS_RESULTS_DIR=C:\MyTradingData\results
```

#### Linux/macOS
```bash
# 
export TRADINGAGENTS_DATA_DIR="/home/user/trading-data"

# 
export TRADINGAGENTS_CACHE_DIR="/home/user/trading-data/cache"

# 
export TRADINGAGENTS_RESULTS_DIR="/home/user/trading-data/results"
```

#### .env | .env File Configuration
```env
# .env
TRADINGAGENTS_DATA_DIR=/path/to/your/data
TRADINGAGENTS_CACHE_DIR=/path/to/your/cache
TRADINGAGENTS_RESULTS_DIR=/path/to/your/results
```

### 3. | Programmatic Configuration

```python
from tradingagents.dataflows.config import set_data_dir, get_data_dir
from tradingagents.config.config_manager import config_manager

# 
set_data_dir("/path/to/custom/data")

# 
current_dir = get_data_dir()
print(f": {current_dir}")

# 
config_manager.ensure_directories_exist()
```

## | Directory Structure



After configuring the data directory, the system automatically creates the following directory structure:

```
data/
 cache/ # | Cache directory
 finnhub_data/ # Finnhub | Finnhub data directory
 news_data/ # | News data
 insider_sentiment/ # | Insider sentiment data
 insider_transactions/ # | Insider transaction data
 results/ # | Analysis results
```

## | Configuration Priority



Configuration priority from high to low:

1. **** | Environment Variables
2. **CLI** | CLI Settings
3. **** | Default Configuration

## | Default Configuration



If no custom configuration is provided, the system uses the following default paths:

- **Windows**: `C:\Users\{username}\Documents\TradingAgents\data`
- **Linux/macOS**: `~/Documents/TradingAgents/data`

## | Troubleshooting

### 1 | Issue 1: Path Not Found Error

**** | Error Message:
```
No such file or directory: '/data/finnhub_data/news_data'
```

**** | Solution:
```bash
# CLI
python -m cli.main data-config --set "C:\YourDataPath"

# 
python -m cli.main data-config --reset
```

### 2 | Issue 2: Permission Denied

**** | Solution:
1. 
2. 
3. Windows

### 3 | Issue 3: Cross-Platform Path Issues

**** | Solution:
- `/` `\\` Windows
- 
- 

## | Verify Configuration

### 1. CLI | Verify Using CLI
```bash
python -m cli.main data-config --show
```

### 2. | Verify Using Test Script
```bash
python test_data_config_cli.py
```

### 3. | Verify Using Demo Script
```bash
python examples/data_dir_config_demo.py
```

## | Best Practices

1. **** | Use Absolute Paths
 - 
 - Avoid issues that relative paths might cause

2. **** | Regular Data Backup
 - 
 - Important analysis results should be backed up regularly

3. **** | Environment Isolation
 - 
 - Use different data directories for different projects

4. **** | Permission Management
 - 
 - Ensure the application has appropriate permissions to the data directory

## | Advanced Configuration

### | Custom Subdirectory Structure

```python
from tradingagents.config.config_manager import config_manager

# 
custom_dirs = {
 'custom_data': 'my_custom_data',
 'reports': 'analysis_reports',
 'logs': 'application_logs'
}

# 
for dir_name, dir_path in custom_dirs.items():
 full_path = os.path.join(config_manager.get_data_dir(), dir_path)
 os.makedirs(full_path, exist_ok=True)
```

### | Dynamic Configuration Updates

```python
# 
config_manager.set_data_dir('/new/data/path')
config_manager.ensure_directories_exist()

# 
print(f": {config_manager.get_data_dir()}")
```

## | Related Files

- `tradingagents/config/config_manager.py` - 
- `tradingagents/dataflows/config.py` - 
- `cli/main.py` - CLI
- `examples/data_dir_config_demo.py` - 
- `test_data_config_cli.py` - 

## | Technical Support


1. 
2. 
3. 
4. 

If you encounter configuration issues, please:
1. Check error logs
2. Run diagnostic scripts
3. Check permission settings
4. Refer to the troubleshooting guide