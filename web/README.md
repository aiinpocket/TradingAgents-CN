# TradingAgents-CN Web 管理介面

基於 Streamlit 建構的 TradingAgents Web 管理介面，提供直覺的股票分析體驗。支援多種 LLM 提供商和多種模型，讓您輕鬆進行專業的股票投資分析。

## 功能特性

### 現代化 Web 介面
- 直覺的股票分析介面
- 即時分析進度顯示
- 響應式設計，支援行動裝置
- 專業的 UI 設計和使用者體驗

### 多 LLM 提供商支援
- **OpenAI**: gpt-4o, gpt-4o-mini
- **Anthropic Claude**: claude-opus-4, claude-sonnet-4
- **智慧切換**: 一鍵切換不同的模型

### 專業分析功能
- **多分析師協作**: 市場技術、基本面、新聞、社交媒體分析師
- **視覺化結果**: 專業的分析報告和圖表展示
- **配置資訊**: 顯示使用的模型和分析師資訊
- **風險評估**: 多維度風險分析和提示

## 快速開始

### 1. 環境準備

```bash
# 啟用虛擬環境
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS

# 確保已安裝相依套件
pip install -r requirements.txt

# 安裝專案到虛擬環境（重要!）
pip install -e .

# 配置 API 金鑰
cp .env.example .env
# 編輯 .env 檔案，新增您的 API 金鑰
```

### 2. 啟動 Web 介面

```bash
# 方法 1: 使用簡化啟動指令碼（推薦）
python start_web.py

# 方法 2: 使用專案啟動指令碼
python web/run_web.py

# 方法 3: 使用快捷指令碼
# Windows
start_web.bat

# Linux/macOS
./start_web.sh

# 方法 4: 直接啟動（需要先安裝專案）
python -m streamlit run web/app.py
```

### 3. 存取介面

在瀏覽器中開啟 `http://localhost:8501`

## 使用指南

### 配置分析參數

#### 左側邊欄配置：

1. **API 金鑰狀態**
   - 查看已配置的 API 金鑰狀態
   - 綠色表示已配置，紅色表示未配置

2. **模型配置**
   - **選擇 LLM 提供商**: OpenAI 或 Anthropic Claude
   - **選擇具體模型**:
     - OpenAI: gpt-4o(推薦) / gpt-4o-mini(快速)
     - Anthropic: claude-opus-4(強大) / claude-sonnet-4(平衡)

3. **進階設定**
   - **啟用記憶功能**: 學習和記住分析歷史
   - **除錯模式**: 顯示詳細的分析過程資訊
   - **最大輸出長度**: 控制回覆的詳細程度

#### 主介面配置：

1. **股票分析配置**
   - **股票代碼**: 輸入要分析的股票代碼（如 AAPL、TSLA）
   - **分析日期**: 選擇分析的基準日期
   - **分析師選擇**: 選擇參與分析的分析師
     - 市場技術分析師 - 技術指標和圖表分析
     - 基本面分析師 - 財務資料和公司基本面
     - 新聞分析師 - 新聞事件影響分析
     - 社交媒體分析師 - 社交媒體情緒分析
   - **研究深度**: 設定分析的詳細程度（1-5 級）

### 開始分析

1. **點選「開始分析」按鈕**
2. **觀察即時進度**:
   - 配置分析參數
   - 檢查環境變數
   - 初始化分析引擎
   - 執行股票分析
   - 分析完成

3. **等待分析完成**（通常需要 2-5 分鐘）

### 查看分析結果

#### 投資決策摘要
- **投資建議**: BUY/SELL/HOLD
- **置信度**: 分析結果的信心程度
- **風險評分**: 投資風險等級
- **目標價格**: 預期價格目標

#### 分析配置資訊
- **LLM 提供商**: 使用的服務商
- **模型**: 具體使用的模型名稱
- **分析師數量**: 參與分析的分析師
- **分析師列表**: 具體的分析師類型

#### 詳細分析報告
- **市場技術分析**: 技術指標、圖表模式、趨勢分析
- **基本面分析**: 財務健康度、估值分析、行業對比
- **新聞分析**: 最新新聞事件對股價的影響
- **社交媒體分析**: 投資者情緒和討論熱度
- **風險評估**: 多維度風險分析和建議

## 技術架構

### 目錄結構

```
web/
├── app.py                 # 主應用入口
├── run_web.py            # 啟動指令碼
├── components/           # UI 元件
│   ├── __init__.py
│   ├── sidebar.py        # 左側配置欄
│   ├── analysis_form.py  # 分析表單
│   ├── results_display.py # 結果展示
│   └── header.py         # 頁面頭部
├── utils/                # 工具函式
│   ├── __init__.py
│   ├── analysis_runner.py # 分析執行器
│   ├── api_checker.py    # API 檢查
│   └── progress_tracker.py # 進度追蹤
├── static/               # 靜態資源
└── README.md            # 本文件
```

### 資料流程

```
使用者輸入 -> 參數驗證 -> API 檢查 -> 分析執行 -> 結果展示
    |           |           |           |           |
  表單元件   -> 配置驗證   -> 金鑰檢查   -> 進度追蹤   -> 結果元件
```

### 元件說明

- **sidebar.py**: 左側配置欄，包含 API 狀態、模型選擇、進階設定
- **analysis_form.py**: 主分析表單，股票代碼、分析師選擇等
- **results_display.py**: 結果展示元件，包含決策摘要、詳細報告等
- **analysis_runner.py**: 核心分析執行器，支援多 LLM 提供商
- **progress_tracker.py**: 即時進度追蹤，提供使用者回饋

## 配置說明

### 環境變數配置

在專案根目錄的 `.env` 檔案中配置：

```env
# OpenAI API (recommended)
OPENAI_API_KEY=your_openai_api_key

# Anthropic API (optional, Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key

# FinnHub API (optional, US stock data)
FINNHUB_API_KEY=your_finnhub_key

# FinnHub API (social media sentiment analysis)
FINNHUB_API_KEY=your_finnhub_key
```

### 模型配置說明

#### OpenAI 模型
- **gpt-4o**: 強大性能，推薦日常使用
- **gpt-4o-mini**: 快速回應，適合簡單分析

#### Anthropic Claude 模型
- **claude-opus-4**: 頂級性能，適合深度分析
- **claude-sonnet-4**: 平衡效能，推薦日常使用

## 故障排除

### 常見問題

#### 1. 頁面無法載入
```bash
# 檢查 Python 環境
python --version  # 需要 3.10+

# 檢查相依套件安裝
pip list | grep streamlit

# 檢查連接埠占用
netstat -an | grep 8501
```

#### 2. API 金鑰問題
- 檢查 `.env` 檔案是否存在
- 確認 API 金鑰格式正確
- 驗證 API 金鑰有效性和餘額

#### 3. 分析失敗
- 檢查網路連線
- 確認股票代碼有效
- 查看瀏覽器主控台錯誤訊息

#### 4. 結果顯示異常
- 重新整理頁面重試
- 清除瀏覽器快取
- 檢查模型配置是否正確

### 除錯模式

啟用詳細日誌查看問題：

```bash
# 啟用 Streamlit 除錯模式
streamlit run web/app.py --logger.level=debug

# 啟用應用除錯模式
# 在左側邊欄勾選「除錯模式」
```

### 取得協助

如果遇到問題：

1. 查看 [完整文件](../docs/)
2. 執行 [測試程式](../tests/test_web_fix.py)
3. 提交 [GitHub Issue](https://github.com/aiinpocket/TradingAgents-CN/issues)

## 開發指南

### 新增元件

1. 在 `components/` 目錄建立新檔案
2. 實作元件函式
3. 在 `app.py` 中匯入和使用

```python
# components/new_component.py
import streamlit as st

def render_new_component():
    """渲染新元件"""
    st.subheader("新元件")
    # 元件邏輯
    return component_data

# app.py
from components.new_component import render_new_component

# 在主應用中使用
data = render_new_component()
```

### 自訂樣式

在 `static/` 目錄中新增 CSS 檔案：

```css
/* static/custom.css */
.custom-style {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
}
```

然後在元件中引用：

```python
# 在元件中載入 CSS
st.markdown('<link rel="stylesheet" href="static/custom.css">', unsafe_allow_html=True)
```

## 授權條款

本專案遵循 Apache 2.0 授權條款。詳見 [LICENSE](../LICENSE) 檔案。

## 致謝

感謝 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 原始專案提供的優秀框架基礎。
