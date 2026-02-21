# 🔧 Web應用啟動問題排除指南

## 🚨 常見問題

### 1. ModuleNotFoundError: No module named 'tradingagents'

**問題描述**:
```bash
ModuleNotFoundError: No module named 'tradingagents'
```

**原因**: 項目沒有安裝到Python環境中，導致無法導入模塊。

**解決方案**:

#### 方案A: 開發模式安裝（推薦）
```bash
# 1. 激活虛擬環境
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS

# 2. 安裝項目到虛擬環境
pip install -e .

# 3. 啟動Web應用
python start_web.py
```

#### 方案B: 使用一鍵安裝腳本
```bash
# 1. 激活虛擬環境
.\env\Scripts\activate  # Windows

# 2. 運行一鍵安裝腳本
python scripts/install_and_run.py
```

#### 方案C: 手動設置Python路徑
```bash
# Windows
set PYTHONPATH=%CD%;%PYTHONPATH%
streamlit run web/app.py

# Linux/macOS
export PYTHONPATH=$PWD:$PYTHONPATH
streamlit run web/app.py
```

### 2. ModuleNotFoundError: No module named 'streamlit'

**問題描述**:
```bash
ModuleNotFoundError: No module named 'streamlit'
```

**解決方案**:
```bash
# 安裝Streamlit和相關依賴
pip install streamlit plotly altair

# 或者安裝完整的Web依賴
pip install -r requirements_web.txt
```

### 3. 虛擬環境問題

**問題描述**: 不確定是否在虛擬環境中

**檢查方法**:
```bash
# 檢查Python路徑
python -c "import sys; print(sys.prefix)"

# 檢查是否在虛擬環境
python -c "import sys; print(hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))"
```

**解決方案**:
```bash
# 創建虛擬環境（如果不存在）
python -m venv env

# 激活虛擬環境
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS
```

### 4. 端口占用問題

**問題描述**:
```bash
OSError: [Errno 48] Address already in use
```

**解決方案**:
```bash
# 方法1: 使用不同端口
streamlit run web/app.py --server.port 8502

# 方法2: 杀死占用端口的進程
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/macOS
lsof -ti:8501 | xargs kill -9
```

### 5. 權限問題

**問題描述**: 在某些系統上可能遇到權限問題

**解決方案**:
```bash
# 確保有執行權限
chmod +x start_web.py
chmod +x web/run_web.py

# 或者使用python命令運行
python start_web.py
```

## 🛠️ 啟動方式對比

| 啟動方式 | 優點 | 缺點 | 推薦度 |
|---------|------|------|--------|
| `python start_web.py` | 簡單，自動處理路徑 | 需要在項目根目錄 | ⭐⭐⭐⭐⭐ |
| `pip install -e . && streamlit run web/app.py` | 標準方式，穩定 | 需要安裝步驟 | ⭐⭐⭐⭐ |
| `python web/run_web.py` | 功能完整，有檢查 | 可能有導入問題 | ⭐⭐⭐ |
| `PYTHONPATH=. streamlit run web/app.py` | 不需要安裝 | 環境變量設置複雜 | ⭐⭐ |

## 🔍 診斷工具

### 環境檢查腳本
```bash
# 運行環境檢查
python scripts/check_api_config.py
```

### 手動檢查步驟
```python
# 檢查Python環境
import sys
print("Python版本:", sys.version)
print("Python路徑:", sys.executable)
print("虛擬環境:", hasattr(sys, 'real_prefix'))

# 檢查模塊導入
try:
    import tradingagents
    print("✅ tradingagents模塊可用")
except ImportError as e:
    print("❌ tradingagents模塊不可用:", e)

try:
    import streamlit
    print("✅ streamlit模塊可用")
except ImportError as e:
    print("❌ streamlit模塊不可用:", e)
```

## 📋 完整啟動檢查清單

### 啟動前檢查
- [ ] 虛擬環境已激活
- [ ] Python版本 >= 3.10
- [ ] 項目已安裝 (`pip install -e .`)
- [ ] Streamlit已安裝
- [ ] .env文件已配置
- [ ] 端口8501未被占用

### 啟動命令
```bash
# 推薦啟動方式
python start_web.py
```

### 啟動後驗證
- [ ] 瀏覽器自動打開 http://localhost:8501
- [ ] 頁面正常加載，無錯誤信息
- [ ] 側邊欄配置正常顯示
- [ ] 可以選擇分析師和股票代碼

## 🆘 獲取幫助

如果以上方法都無法解決問題：

1. **查看詳細錯誤日誌**:
   ```bash
   python start_web.py 2>&1 | tee startup.log
   ```

2. **檢查系統環境**:
   ```bash
   python --version
   pip list | grep -E "(streamlit|tradingagents)"
   ```

3. **重新安裝**:
   ```bash
   pip uninstall tradingagents
   pip install -e .
   ```

4. **提交Issue**: 
   - 訪問 [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)
   - 提供錯誤日誌和系統信息

## 💡 最佳實踐

1. **始終使用虛擬環境**
2. **定期更新依賴**: `pip install -U -r requirements.txt`
3. **保持項目結構完整**
4. **定期清理緩存**: `python web/run_web.py --force-clean`
5. **備份配置文件**: 定期備份.env文件
