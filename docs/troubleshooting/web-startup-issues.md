# Web 啟動疑難排解

## 常見問題

### 1. ModuleNotFoundError: No module named 'tradingagents'

**錯誤訊息**:
```bash
ModuleNotFoundError: No module named 'tradingagents'
```

**原因**: Python 路徑未正確設定

**解決方式**:

#### A: 安裝套件（推薦）
```bash
# 1. 啟用虛擬環境
.\env\Scripts\activate # Windows
source env/bin/activate # Linux/macOS

# 2. 安裝套件
pip install -e .

# 3. 啟動 Web 應用
python start_app.py
```

#### B: 使用安裝指令碼
```bash
# 1. 啟用虛擬環境
.\env\Scripts\activate # Windows

# 2. 一鍵安裝並啟動
python scripts/install_and_run.py
```

#### C: 手動設定 Python 路徑
```bash
# Windows
set PYTHONPATH=%CD%;%PYTHONPATH%
python start_app.py

# Linux/macOS
export PYTHONPATH=$PWD:$PYTHONPATH
python start_app.py
```

### 2. 虛擬環境問題

**狀況**: 未啟用虛擬環境

**檢測方式**:
```bash
# 確認 Python 路徑
python -c "import sys; print(sys.prefix)"

# 確認是否在虛擬環境中
python -c "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"
```

**解決方式**:
```bash
# 建立虛擬環境
python -m venv env

# 啟用
.\env\Scripts\activate # Windows
source env/bin/activate # Linux/macOS
```

### 3. 連接埠被佔用

**錯誤訊息**:
```bash
OSError: [Errno 48] Address already in use
```

**解決方式**:
```bash
# 方法 1: 使用不同連接埠
python start_app.py --port 8502

# 方法 2: 關閉佔用連接埠的程序
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8501 | xargs kill -9
```

## 快速啟動指南

| 命令 | 適用場景 |
|---------|------|
| `python start_app.py` | 標準啟動 |
| `python start_app.py --reload` | 開發模式（自動重載）|
| `python start_app.py --port 8502` | 指定連接埠 |
| `python scripts/install_and_run.py` | 首次安裝並啟動 |

## 診斷工具

### API 配置檢查
```bash
python scripts/check_api_config.py
```

### 環境驗證
```python
# Python 環境檢查
import sys
print("Python:", sys.version)
print("Python 路徑:", sys.executable)
print("虛擬環境:", hasattr(sys, 'real_prefix'))

try:
    import tradingagents
    print("tradingagents 匯入成功")
except ImportError as e:
    print("tradingagents 匯入失敗:", e)

try:
    import fastapi
    print("fastapi 匯入成功")
except ImportError as e:
    print("fastapi 匯入失敗:", e)
```

## 啟動前檢查清單

### 環境準備
- [ ] 虛擬環境已啟用
- [ ] Python >= 3.10
- [ ] 套件已安裝（`pip install -e .`）
- [ ] .env 檔案已配置 API 密鑰
- [ ] 連接埠 8501 未被佔用

### 啟動確認
- [ ] http://localhost:8501 可正常存取
- [ ] 頁面右上角顯示「已連線」
- [ ] 配置頁面顯示 API 密鑰狀態正確

## 求助管道

如果以上方式都無法解決問題：

1. **收集錯誤資訊**:
   ```bash
   python start_app.py 2>&1 | tee startup.log
   ```

2. **確認套件版本**:
   ```bash
   python --version
   pip list | grep -E "(fastapi|uvicorn|tradingagents)"
   ```

3. **重新安裝套件**:
   ```bash
   pip uninstall tradingagents
   pip install -e .
   ```

4. **提交 Issue**: 附上錯誤日誌到
   - [GitHub Issues](https://github.com/aiinpocket/TradingAgents-CN/issues)
