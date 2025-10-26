# TradingAgents-CN Web管理界面

基於Streamlit構建的TradingAgents Web管理界面，提供直觀的股票分析體驗。支持多種LLM提供商和AI模型，让您轻松進行專業的股票投資分析。

## ✨ 功能特性

### 🌐 現代化Web界面
- 🎯 直觀的股票分析界面
- 📊 實時分析進度顯示  
- 📱 響應式設計，支持移動端
- 🎨 專業的UI設計和用戶體驗

### 🤖 多LLM提供商支持
- **阿里百炼**: qwen-turbo, qwen-plus-latest, qwen-max
- **Google AI**: gemini-2.0-flash, gemini-1.5-pro, gemini-1.5-flash
- **智能切換**: 一键切換不同的AI模型
- **混合嵌入**: Google AI推理 + 阿里百炼嵌入

### 📈 專業分析功能
- **多分析師協作**: 市場技術、基本面、新聞、社交媒體分析師
- **可視化結果**: 專業的分析報告和圖表展示
- **配置信息**: 顯示使用的模型和分析師信息
- **風險評估**: 多維度風險分析和提示

## 🚀 快速開始

### 1. 環境準备

```bash
# 激活虛擬環境
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS

# 確保已安裝依賴
pip install -r requirements.txt

# 安裝項目到虛擬環境（重要！）
pip install -e .

# 配置API密鑰
cp .env.example .env
# 編辑.env文件，添加您的API密鑰
```

### 2. 啟動Web界面

```bash
# 方法1: 使用簡化啟動腳本（推薦）
python start_web.py

# 方法2: 使用項目啟動腳本
python web/run_web.py

# 方法3: 使用快捷腳本
# Windows
start_web.bat

# Linux/macOS
./start_web.sh

# 方法4: 直接啟動（需要先安裝項目）
python -m streamlit run web/app.py
```

### 3. 訪問界面

在浏覽器中打開 `http://localhost:8501`

## 📋 使用指南

### 🔧 配置分析參數

#### 左侧邊栏配置：

1. **🔑 API密鑰狀態**
   - 查看已配置的API密鑰狀態
   - 绿色✅表示已配置，红色❌表示未配置

2. **🧠 AI模型配置**
   - **選擇LLM提供商**: 阿里百炼 或 Google AI
   - **選擇具體模型**: 
     - 阿里百炼: qwen-turbo(快速) / qwen-plus-latest(平衡) / qwen-max(最强)
     - Google AI: gemini-2.0-flash(推薦) / gemini-1.5-pro(强大) / gemini-1.5-flash(快速)

3. **⚙️ 高級設置**
   - **啟用記忆功能**: 让AI學习和記住分析歷史
   - **調試模式**: 顯示詳細的分析過程信息
   - **最大輸出長度**: 控制AI回複的詳細程度

#### 主界面配置：

1. **📊 股票分析配置**
   - **股票代碼**: 輸入要分析的股票代碼（如AAPL、TSLA）
   - **分析日期**: 選擇分析的基準日期
   - **分析師選擇**: 選擇參与分析的AI分析師
     - 📈 市場技術分析師 - 技術指標和圖表分析
     - 💰 基本面分析師 - 財務數據和公司基本面
     - 📰 新聞分析師 - 新聞事件影響分析
     - 💭 社交媒體分析師 - 社交媒體情绪分析
   - **研究深度**: 設置分析的詳細程度（1-5級）

### 🎯 開始分析

1. **點擊"開始分析"按钮**
2. **觀察實時進度**:
   - 📋 配置分析參數
   - 🔍 檢查環境變量
   - 🚀 初始化分析引擎
   - 📊 執行股票分析
   - ✅ 分析完成

3. **等待分析完成** (通常需要2-5分鐘)

### 📊 查看分析結果

#### 🎯 投資決策摘要
- **投資建议**: BUY/SELL/HOLD
- **置信度**: AI對建议的信心程度
- **風險評分**: 投資風險等級
- **目標價格**: 預期價格目標

#### 📋 分析配置信息
- **LLM提供商**: 使用的AI服務商
- **AI模型**: 具體使用的模型名稱
- **分析師數量**: 參与分析的AI分析師
- **分析師列表**: 具體的分析師類型

#### 📈 詳細分析報告
- **市場技術分析**: 技術指標、圖表模式、趋势分析
- **基本面分析**: 財務健康度、估值分析、行業對比
- **新聞分析**: 最新新聞事件對股價的影響
- **社交媒體分析**: 投資者情绪和討論熱度
- **風險評估**: 多維度風險分析和建议

## 🏗️ 技術架構

### 📁 目錄結構

```
web/
├── app.py                 # 主應用入口
├── run_web.py            # 啟動腳本
├── components/           # UI組件
│   ├── __init__.py
│   ├── sidebar.py        # 左侧配置栏
│   ├── analysis_form.py  # 分析表單
│   ├── results_display.py # 結果展示
│   └── header.py         # 页面头部
├── utils/                # 工具函數
│   ├── __init__.py
│   ├── analysis_runner.py # 分析執行器
│   ├── api_checker.py    # API檢查
│   └── progress_tracker.py # 進度跟蹤
├── static/               # 静態資源
└── README.md            # 本文件
```

### 🔄 數據流程

```
用戶輸入 → 參數驗證 → API檢查 → 分析執行 → 結果展示
    ↓           ↓           ↓           ↓           ↓
  表單組件   → 配置驗證   → 密鑰檢查   → 進度跟蹤   → 結果組件
```

### 🧩 組件說明

- **sidebar.py**: 左侧配置栏，包含API狀態、模型選擇、高級設置
- **analysis_form.py**: 主分析表單，股票代碼、分析師選擇等
- **results_display.py**: 結果展示組件，包含決策摘要、詳細報告等
- **analysis_runner.py**: 核心分析執行器，支持多LLM提供商
- **progress_tracker.py**: 實時進度跟蹤，提供用戶反馈

## ⚙️ 配置說明

### 🔑 環境變量配置

在項目根目錄的 `.env` 文件中配置：

```env
# 阿里百炼API（推薦，國產模型）
DASHSCOPE_API_KEY=sk-your_dashscope_key

# Google AI API（可選，支持Gemini模型）
GOOGLE_API_KEY=your_google_api_key

# 金融數據API（可選）
FINNHUB_API_KEY=your_finnhub_key

# Reddit API（可選，用於社交媒體分析）
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=TradingAgents-CN/1.0
```

### 🤖 模型配置說明

#### 阿里百炼模型
- **qwen-turbo**: 快速響應，適合簡單分析
- **qwen-plus-latest**: 平衡性能，推薦日常使用
- **qwen-max**: 最强性能，適合複雜分析

#### Google AI模型  
- **gemini-2.0-flash**: 最新模型，推薦使用
- **gemini-1.5-pro**: 强大性能，適合深度分析
- **gemini-1.5-flash**: 快速響應，適合簡單分析

## 🔧 故障排除

### ❌ 常见問題

#### 1. 页面無法加載
```bash
# 檢查Python環境
python --version  # 需要3.10+

# 檢查依賴安裝
pip list | grep streamlit

# 檢查端口占用
netstat -an | grep 8501
```

#### 2. API密鑰問題
- ✅ 檢查 `.env` 文件是否存在
- ✅ 確認API密鑰格式正確
- ✅ 驗證API密鑰有效性和余額

#### 3. 分析失败
- ✅ 檢查網絡連接
- ✅ 確認股票代碼有效
- ✅ 查看浏覽器控制台錯誤信息

#### 4. 結果顯示異常
- ✅ 刷新页面重試
- ✅ 清除浏覽器緩存
- ✅ 檢查模型配置是否正確

### 🐛 調試模式

啟用詳細日誌查看問題：

```bash
# 啟用Streamlit調試模式
streamlit run web/app.py --logger.level=debug

# 啟用應用調試模式
# 在左侧邊栏勾選"調試模式"
```

### 📞 獲取幫助

如果遇到問題：

1. 📖 查看 [完整文档](../docs/)
2. 🧪 運行 [測試程序](../tests/test_web_interface.py)
3. 💬 提交 [GitHub Issue](https://github.com/hsliuping/TradingAgents-CN/issues)

## 🚀 開發指南

### 添加新組件

1. 在 `components/` 目錄創建新文件
2. 實現組件函數
3. 在 `app.py` 中導入和使用

```python
# components/new_component.py
import streamlit as st

def render_new_component():
    """渲染新組件"""
    st.subheader("新組件")
    # 組件逻辑
    return component_data

# app.py
from components.new_component import render_new_component

# 在主應用中使用
data = render_new_component()
```

### 自定義樣式

在 `static/` 目錄中添加CSS文件：

```css
/* static/custom.css */
.custom-style {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
}
```

然後在組件中引用：

```python
# 在組件中加載CSS
st.markdown('<link rel="stylesheet" href="static/custom.css">', unsafe_allow_html=True)
```

## 📄 許可證

本項目遵循Apache 2.0許可證。詳见 [LICENSE](../LICENSE) 文件。

## 🙏 致谢

感谢 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 原始項目提供的優秀框架基础。
