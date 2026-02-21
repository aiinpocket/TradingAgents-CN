# Streamlit

## 

Streamlit Web

```
Exception in thread Thread-9:
Traceback (most recent call last):
 File "C:\Users\PC\AppData\Local\Programs\Python\Python310\lib\threading.py", line 1016, in _bootstrap_inner
 self.run()
 File "C:\code\TradingAgentsCN\env\lib\site-packages\watchdog\observers\api.py", line 213, in run
 self.dispatch_events(self.event_queue)
 ...
FileNotFoundError: [WinError 2] : 'C:\\code\\TradingAgentsCN\\web\\pages\\__pycache__\\config_management.cpython-310.pyc.2375409084592'
```

## 

Streamlitwatchdog

1. **Python**Python`__pycache__``.pyc`
2. ****Python
3. ****Streamlitwatchdog
4. ****Pythonwatchdog
5. **FileNotFoundError**

## 

### 1Streamlit

`.streamlit/config.toml`

```toml
[server.fileWatcher]
# 
watcherType = "auto"
# __pycache__.pyc
excludePatterns = [
 "**/__pycache__/**",
 "**/*.pyc",
 "**/*.pyo",
 "**/*.pyd",
 "**/.git/**",
 "**/node_modules/**",
 "**/.env",
 "**/venv/**",
 "**/env/**"
]
```

### 2

Python

```bash
# Windows PowerShell
Get-ChildItem -Path . -Recurse -Name "__pycache__" | Remove-Item -Recurse -Force

# Linux/macOS
find . -type d -name "__pycache__" -exec rm -rf {} +
```

### 3

Python

```bash
# .env
PYTHONDONTWRITEBYTECODE=1
```



```python
import os
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
```

## 

1. **Streamlit**
 ```bash
 python web/run_web.py
 ```

2. ****
 - `.streamlit/config.toml`
 - 

3. ****
 - 
 - FileNotFoundError

## 

1. **.gitignore**`__pycache__/``*.pyc`.gitignore
2. ****
3. ****Streamlit
4. ****Python

## 

- [Streamlit](https://docs.streamlit.io/library/advanced-features/configuration)
- [Python](https://docs.python.org/3/tutorial/modules.html#compiled-python-files)
- [Watchdog](https://python-watchdog.readthedocs.io/)

## 

**Q: **
A: Python

**Q: **
A: 

**Q: **
A: 

## 

- **2025-07-03**: 
- **2025-07-03**: Streamlit
- **2025-07-03**: .gitignore