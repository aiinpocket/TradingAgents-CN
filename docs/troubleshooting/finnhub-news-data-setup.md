# Finnhub新聞數據配置指南

## 問題描述

如果您遇到以下錯誤信息：

```
[DEBUG] FinnhubNewsTool調用，股票代碼: AAPL 
獲取新聞數據失败: [Errno 2] No such file or directory: '/Users/yluo/Documents/Code/ScAI/FR1-data\\finnhub_data\\news_data\\AAPL_data_formatted.json'
```

這表明存在以下問題：
1. **路徑配置錯誤**：混合了Unix和Windows路徑分隔符
2. **數據文件不存在**：缺少Finnhub新聞數據文件
3. **數據目錄配置**：數據目錄路徑不正確

## 解決方案

### 1. 路徑修複（已自動修複）

我們已經修複了 `tradingagents/default_config.py` 中的路徑配置：

```python
# 修複前（硬編碼Unix路徑）
"data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",

# 修複後（跨平台兼容路徑）
"data_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data"),
```

### 2. 數據目錄結構

正確的數據目錄結構應该是：

```
~/Documents/TradingAgents/data/
├── finnhub_data/
│   ├── news_data/
│   │   ├── AAPL_data_formatted.json
│   │   ├── TSLA_data_formatted.json
│   │   └── ...
│   ├── insider_senti/
│   ├── insider_trans/
│   └── ...
└── other_data/
```

### 3. 獲取Finnhub數據

#### 方法一：使用API下載（推薦）

1. **配置Finnhub API密鑰**
   ```bash
   # 在.env文件中添加
   FINNHUB_API_KEY=your_finnhub_api_key_here
   ```

2. **運行數據下載腳本**
   ```bash
   # 下載新聞數據
   python scripts/download_finnhub_data.py --data-type news --symbols AAPL,TSLA,MSFT

   # 下載所有類型數據
   python scripts/download_finnhub_data.py --all

   # 强制刷新已存在的數據
   python scripts/download_finnhub_data.py --force-refresh

   # 下載指定天數的新聞數據
   python scripts/download_finnhub_data.py --data-type news --days 30 --symbols AAPL
   ```

3. **腳本參數說明**
   - `--data-type`: 數據類型 (news, sentiment, transactions, all)
   - `--symbols`: 股票代碼，用逗號分隔
   - `--days`: 新聞數據天數 (默認7天)
   - `--force-refresh`: 强制刷新已存在的數據
   - `--all`: 下載所有類型數據

#### 方法二：手動創建測試數據

如果您只是想測試功能，可以創建示例數據：

```bash
# 運行示例數據生成腳本
python scripts/development/download_finnhub_sample_data.py

# 或者運行測試腳本，會自動創建示例數據
python tests/test_finnhub_news_fix.py
```

### 4. 驗證配置

運行以下命令驗證配置是否正確：

```bash
# 驗證路徑修複
python tests/test_finnhub_news_fix.py

# 測試新聞數據獲取
python -c "
from tradingagents.dataflows.interface import get_finnhub_news
result = get_finnhub_news('AAPL', '2025-01-02', 7)
print(result[:200])
"
```

## 錯誤處理改進

我們已經改進了錯誤處理，現在當數據文件不存在時，會顯示詳細的錯誤信息：

```
⚠️ 無法獲取AAPL的新聞數據 (2024-12-26 到 2025-01-02)
可能的原因：
1. 數據文件不存在或路徑配置錯誤
2. 指定日期範围內没有新聞數據
3. 需要先下載或更新Finnhub新聞數據
建议：檢查數據目錄配置或重新獲取新聞數據
```

## 配置選項

### 自定義數據目錄

如果您想使用自定義數據目錄，可以在代碼中設置：

```python
from tradingagents.dataflows.config import set_config

# 設置自定義數據目錄
config = {
    "data_dir": "C:/your/custom/data/directory"
}
set_config(config)
```

### 環境變量配置

您也可以通過環境變量設置：

```bash
# Windows
set TRADINGAGENTS_DATA_DIR=C:\your\custom\data\directory

# Linux/Mac
export TRADINGAGENTS_DATA_DIR=/your/custom/data/directory
```

## 常见問題

### Q1: 數據目錄權限問題

**問題**：無法創建或寫入數據目錄

**解決方案**：
```bash
# Windows（以管理員身份運行）
mkdir "C:\Users\%USERNAME%\Documents\TradingAgents\data"

# Linux/Mac
mkdir -p ~/Documents/TradingAgents/data
chmod 755 ~/Documents/TradingAgents/data
```

### Q2: Finnhub API配額限制

**問題**：API調用次數超限

**解決方案**：
1. 升級Finnhub API計劃
2. 使用緩存减少API調用
3. 限制數據獲取頻率

### Q3: 數據格式錯誤

**問題**：JSON文件格式不正確

**解決方案**：
```bash
# 驗證JSON格式
python -c "import json; print(json.load(open('path/to/file.json')))"

# 重新下載數據
python scripts/download_finnhub_data.py --force-refresh
```

## 技術細節

### 修複的文件

1. **`tradingagents/default_config.py`**
   - 修複硬編碼的Unix路徑
   - 使用跨平台兼容的路徑構建

2. **`tradingagents/dataflows/finnhub_utils.py`**
   - 添加文件存在性檢查
   - 改進錯誤處理和調試信息
   - 使用UTF-8編碼讀取文件

3. **`tradingagents/dataflows/interface.py`**
   - 改進get_finnhub_news函數的錯誤提示
   - 提供詳細的故障排除建议

### 路徑處理逻辑

```python
# 跨平台路徑構建
data_path = os.path.join(
    data_dir, 
    "finnhub_data", 
    "news_data", 
    f"{ticker}_data_formatted.json"
)

# 文件存在性檢查
if not os.path.exists(data_path):
    print(f"⚠️ [DEBUG] 數據文件不存在: {data_path}")
    return {}
```

## 聯系支持

如果您仍然遇到問題，請：

1. 運行診斷腳本：`python tests/test_finnhub_news_fix.py`
2. 檢查日誌輸出中的詳細錯誤信息
3. 確認Finnhub API密鑰配置正確
4. 提供完整的錯誤堆棧信息

---

**更新日期**：2025-01-02  
**版本**：v1.0  
**適用範围**：TradingAgents-CN v0.1.3+