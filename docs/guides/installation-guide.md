---
version: cn-0.1.14-preview
last_updated: 2025-01-13
code_compatibility: cn-0.1.14-preview
status: updated
---

# TradingAgents-CN 安裝配置指導

> **版本說明**: 本文檔基於 `cn-0.1.14-preview` 版本編寫  
> **最後更新**: 2025-01-13  
> **狀態**: ✅ 已更新 - 包含最新的安裝和配置步驟

## 📋 目錄

1. [系統要求](#系統要求)
2. [環境準備](#環境準備)
3. [項目安裝](#項目安裝)
4. [環境配置](#環境配置)
5. [數據庫配置](#數據庫配置)
6. [啟動應用](#啟動應用)
7. [驗證安裝](#驗證安裝)
8. [常見問題](#常見問題)
9. [高級配置](#高級配置)

## 🖥️ 系統要求

### 操作系統支援
- ✅ **Windows 10/11** (推薦)
- ✅ **macOS 10.15+**
- ✅ **Linux (Ubuntu 20.04+, CentOS 8+)**

### 硬件要求
- **CPU**: 4核心以上 (推薦8核心)
- **內存**: 8GB以上 (推薦16GB)
- **存儲**: 10GB可用空間
- **網絡**: 穩定的互聯網連接

### 軟體依賴
- **Python**: 3.10+ (必需)
- **Git**: 最新版本
- **Redis**: 6.2+ (可選，用於緩存)
- **MongoDB**: 4.4+ (可選，用於數據存儲)

## 🔧 環境準備

### 1. 安裝Python 3.10+

#### Windows
```bash
# 下載並安裝Python 3.10+
# 訪問 https://www.python.org/downloads/
# 確保勾選 "Add Python to PATH"
```

#### macOS
```bash
# 使用Homebrew安裝
brew install python@3.10

# 或使用pyenv
pyenv install 3.10.12
pyenv global 3.10.12
```

#### Linux (Ubuntu)
```bash
# 更新包列表
sudo apt update

# 安裝Python 3.10
sudo apt install python3.10 python3.10-venv python3.10-pip

# 驗證安裝
python3.10 --version
```

### 2. 安裝Git
```bash
# Windows: 下載Git for Windows
# https://git-scm.com/download/win

# macOS
brew install git

# Linux
sudo apt install git  # Ubuntu
sudo yum install git   # CentOS
```

### 3. 安裝uv (推薦的包管理器)
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 驗證安裝
uv --version
```

## 📦 項目安裝

### 1. 克隆項目
```bash
# 克隆項目到本地
git clone https://github.com/your-repo/TradingAgents-CN.git
cd TradingAgents-CN

# 查看當前版本
cat VERSION
```

### 2. 創建虛擬環境
```bash
# 使用uv創建虛擬環境 (推薦)
uv venv

# 激活虛擬環境
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 驗證虛擬環境
which python  # 應該指向虛擬環境中的python
```

### 3. 安裝依賴

#### 方法1: 使用uv安裝 (推薦)
```bash
# 安裝核心依賴
uv pip install -e .

# 安裝額外依賴
uv pip install yfinance langgraph 

# 驗證安裝
python -c "import tradingagents; print('安裝成功!')"
```

#### 方法2: 使用傳統pip
```bash
# 安裝核心依賴
pip install -e .

# 安裝缺失的依賴包
pip install yfinance langgraph 

# 或一次性安裝所有依賴
pip install -r requirements.txt

# 驗證安裝
python -c "import tradingagents; print('安裝成功!')"
```

#### 方法3: 分步安裝 (推薦用於解決依賴衝突)
```bash
# 1. 安裝基礎依賴
pip install streamlit pandas numpy requests plotly

# 2. 安裝LLM相關依賴
pip install openai langchain langgraph 

# 3. 安裝數據源依賴
pip install yfinance  

# 4. 安裝數據庫依賴 (可選)
pip install redis pymongo

# 5. 安裝項目
pip install -e .
```

## ⚙️ 環境配置

### 1. 創建環境變量文件
```bash
# 複制環境變量模板
cp .env.example .env

# 編辑環境變量文件
# Windows: notepad .env
# macOS/Linux: nano .env
```

### 2. 配置API密鑰

在 `.env` 文件中添加以下配置：

```bash
# ===========================================
# TradingAgents-CN 環境配置
# ===========================================

# 基礎配置
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# ===========================================
# LLM API 配置 (選擇一個或多個)
# ===========================================

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic Claude配置
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# ===========================================
# 數據源API配置
# ===========================================

# FinnHub配置 (美股數據)
FINNHUB_API_KEY=your_finnhub_api_key_here

# Alpha Vantage配置
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here

# ===========================================
# 數據庫配置 (可選)
# ===========================================

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# MongoDB配置
MONGODB_URI=mongodb://localhost:27017/tradingagents
MONGODB_DATABASE=tradingagents

# ===========================================
# 應用配置
# ===========================================

# Web應用配置
WEB_HOST=localhost
WEB_PORT=8501
WEB_DEBUG=true

# 數據緩存目錄
DATA_CACHE_DIR=./data/cache

# 日誌配置
LOG_DIR=./logs
LOG_FILE=tradingagents.log
```

### 3. 獲取API密鑰指南

#### OpenAI API密鑰
1. 訪問 [OpenAI Platform](https://platform.openai.com/)
2. 註冊/登錄帳戶
3. 進入 API Keys 頁面
4. 建立新的API密鑰

#### Anthropic Claude API
1. 訪問 [Anthropic Console](https://console.anthropic.com/)
2. 註冊帳戶並登入
3. 建立新的API密鑰
4. 複製API Key

#### FinnHub API
1. 訪問 [FinnHub](https://finnhub.io/)
2. 註冊免費帳戶
3. 獲取API Key

#### Alpha Vantage API
1. 訪問 [Alpha Vantage](https://www.alphavantage.co/)
2. 註冊免費帳戶
3. 獲取API Key

## 🗄️ 數據庫配置

### Redis配置 (推薦)

#### Windows
```bash
# 下載Redis for Windows
# https://github.com/microsoftarchive/redis/releases

# 或使用Docker
docker run -d --name redis -p 6379:6379 redis:latest
```

#### macOS
```bash
# 使用Homebrew安裝
brew install redis

# 啟動Redis服務
brew services start redis

# 驗證連接
redis-cli ping
```

#### Linux
```bash
# Ubuntu
sudo apt install redis-server

# CentOS
sudo yum install redis

# 啟動服務
sudo systemctl start redis
sudo systemctl enable redis
```

### MongoDB配置 (可選)

#### 使用Docker (推薦)
```bash
# 啟動MongoDB容器
docker run -d --name mongodb -p 27017:27017 mongo:latest

# 驗證連接
docker exec -it mongodb mongosh
```

#### 本地安裝
```bash
# 訪問MongoDB官網下載安裝包
# https://www.mongodb.com/try/download/community

## 🚀 啟動應用

### 1. 啟動Web應用

#### 方法1: 使用啟動腳本 (推薦)
```bash
# 確保虛擬環境已激活
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 啟動Web應用
python start_web.py
```

#### 方法2: 直接啟動Streamlit
```bash
# 進入web目錄
cd web

# 啟動Streamlit應用
streamlit run app.py --server.port 8501
```

#### 方法3: 使用批處理文件 (Windows)
```bash
# 雙擊運行
start_web.bat
```

### 2. 訪問應用
打開瀏覽器訪問: http://localhost:8501

### 3. 首次使用配置

1. **選擇LLM提供商**: 在側邊欄選擇已配置的LLM提供商
2. **選擇模型**: 根據需要選擇具體的模型
3. **配置分析參數**: 設置分析日期、股票代碼等
4. **開始分析**: 輸入股票代碼進行測試

## ✅ 驗證安裝

### 1. 基礎功能測試
```bash
# 測試Python環境
python -c "import tradingagents; print('✅ 模塊導入成功')"

# 測試依賴包
python -c "import streamlit, pandas, yfinance; print('✅ 依賴包正常')"

# 測試配置文件
python -c "from tradingagents.config import get_config; print('✅ 配置加載成功')"
```

### 2. API連接測試
```bash
# 進入項目目錄
cd examples

# 測試LLM連接
python test_llm_connection.py

# 測試數據源連接
python test_data_sources.py
```

### 3. Web應用測試
1. 啟動應用後訪問 http://localhost:8501
2. 檢查側邊欄是否正常顯示
3. 嘗試選擇不同的LLM提供商
4. 輸入測試股票代碼 (如: AAPL, 000001)

## 🔧 常見問題

### 1. 模塊導入錯誤
```bash
# 問題: ModuleNotFoundError: No module named 'tradingagents'
# 解決方案:
pip install -e .

# 或重新安裝
pip uninstall tradingagents
pip install -e .
```

### 2. 虛擬環境問題
```bash
# 問題: 虛擬環境未激活
# 解決方案:
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# 驗證
which python
```

### 3. 端口占用問題
```bash
# 問題: Port 8501 is already in use
# 解決方案:
streamlit run app.py --server.port 8502

# 或杀死占用進程
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8501 | xargs kill -9
```

### 4. API密鑰錯誤
```bash
# 問題: API密鑰驗證失敗
# 解決方案:
1. 檢查.env文件中的API密鑰格式
2. 確認API密鑰有效性
3. 檢查網絡連接
4. 查看日誌文件: logs/tradingagents.log
```

### 5. 數據獲取失敗
```bash
# 問題: 無法獲取股票數據
# 解決方案:
1. 檢查網絡連接
2. 驗證數據源API密鑰
3. 檢查股票代碼格式
4. 查看緩存目錄: data/cache
```

## ⚡ 高級配置

### 1. 性能優化

#### 啟用Redis緩存
```bash
# 在.env文件中配置Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_ENABLED=true
```

#### 配置並發設置
```python
# 在config/settings.json中調整
{
  "max_workers": 4,
  "request_timeout": 30,
  "cache_ttl": 3600
}
```

### 2. 日誌配置

#### 自定義日誌級別
```bash
# 在.env文件中設置
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/tradingagents.log
```

#### 結構化日誌
```python
# 編辑config/logging.toml
[loggers.tradingagents]
level = "INFO"
handlers = ["console", "file"]
```

### 3. 數據源配置

#### 優先級設置
```python
# 在config/settings.json中配置數據源優先級
{
  "data_sources": {
    "china_stocks": ["", "", "tdx"],
    "us_stocks": ["yfinance", "finnhub", "alpha_vantage"],
    "hk_stocks": ["", "yfinance"]
  }
}
```

### 4. 模型配置

#### 自定義模型參數
```python
# 在config/models.json中配置
{
  "openai": {
    "temperature": 0.1,
    "max_tokens": 4000,
    "timeout": 60
  }
}
```

## 🐳 Docker部署 (可選)

### 1. 構建Docker鏡像
```bash
# 構建鏡像
docker build -t tradingagents-cn .

# 運行容器
docker run -d \
  --name tradingagents \
  -p 8501:8501 \
  -v $(pwd)/.env:/app/.env \
  tradingagents-cn
```

### 2. 使用Docker Compose
```bash
# 啟動完整服務棧
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌
docker-compose logs -f
```

## 📚 下一步

安裝完成後，建議閱讀以下文檔：

1. **[快速開始指南](../QUICK_START.md)** - 了解基本使用方法
2. **[配置管理指南](./config-management-guide.md)** - 深入了解配置選項
3. **[分析指南](./a-share-analysis-guide.md)** - 市場分析教程
4. **[Docker部署指南](./docker-deployment-guide.md)** - 生產環境部署
5. **[故障排除指南](../troubleshooting/)** - 常見問題解決方案

## 🆘 獲取幫助

如果遇到問題，可以通過以下方式獲取幫助：

- **GitHub Issues**: [提交問題](https://github.com/your-repo/TradingAgents-CN/issues)
- **文檔**: [查看完整文檔](../README.md)
- **社群**: [加入討論群](https://your-community-link)

---

**祝你使用愉快！** 🎉
```
