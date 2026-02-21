# Web

## 

### 1. ModuleNotFoundError: No module named 'tradingagents'

****:
```bash
ModuleNotFoundError: No module named 'tradingagents'
```

****: Python

****:

#### A: 
```bash
# 1. 
.\env\Scripts\activate # Windows
source env/bin/activate # Linux/macOS

# 2. 
pip install -e .

# 3. Web
python start_web.py
```

#### B: 
```bash
# 1. 
.\env\Scripts\activate # Windows

# 2. 
python scripts/install_and_run.py
```

#### C: Python
```bash
# Windows
set PYTHONPATH=%CD%;%PYTHONPATH%
streamlit run web/app.py

# Linux/macOS
export PYTHONPATH=$PWD:$PYTHONPATH
streamlit run web/app.py
```

### 2. ModuleNotFoundError: No module named 'streamlit'

****:
```bash
ModuleNotFoundError: No module named 'streamlit'
```

****:
```bash
# Streamlit
pip install streamlit plotly altair

# Web
pip install -r requirements_web.txt
```

### 3. 

****: 

****:
```bash
# Python
python -c "import sys; print(sys.prefix)"

# 
python -c "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"
```

****:
```bash
# 
python -m venv env

# 
.\env\Scripts\activate # Windows
source env/bin/activate # Linux/macOS
```

### 4. 

****:
```bash
OSError: [Errno 48] Address already in use
```

****:
```bash
# 1: 
streamlit run web/app.py --server.port 8502

# 2: 
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8501 | xargs kill -9
```

### 5. 

****: 

****:
```bash
# 
chmod +x start_web.py
chmod +x web/run_web.py

# python
python start_web.py
```

## 

| | | | |
|---------|------|------|--------|
| `python start_web.py` | | | |
| `pip install -e . && streamlit run web/app.py` | | | |
| `python web/run_web.py` | | | |
| `PYTHONPATH=. streamlit run web/app.py` | | | |

## 

### 
```bash
# 
python scripts/check_api_config.py
```

### 
```python
# Python
import sys
print("Python:", sys.version)
print("Python:", sys.executable)
print(":", hasattr(sys, 'real_prefix'))

# 
try:
 import tradingagents
 print(" tradingagents")
except ImportError as e:
 print(" tradingagents:", e)

try:
 import streamlit
 print(" streamlit")
except ImportError as e:
 print(" streamlit:", e)
```

## 

### 
- [ ] 
- [ ] Python >= 3.10
- [ ] (`pip install -e .`)
- [ ] Streamlit
- [ ] .env
- [ ] 8501

### 
```bash
# 
python start_web.py
```

### 
- [ ] http://localhost:8501
- [ ] 
- [ ] 
- [ ] 

## 



1. ****:
 ```bash
 python start_web.py 2>&1 | tee startup.log
 ```

2. ****:
 ```bash
 python --version
 pip list | grep -E "(streamlit|tradingagents)"
 ```

3. ****:
 ```bash
 pip uninstall tradingagents
 pip install -e .
 ```

4. **Issue**: 
 - [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)
 - 

## 

1. ****
2. ****: `pip install -U -r requirements.txt`
3. ****
4. ****: `python web/run_web.py --force-clean`
5. ****: .env
