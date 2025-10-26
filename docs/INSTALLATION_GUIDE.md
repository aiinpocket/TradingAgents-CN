# TradingAgents-CN 詳細安裝配置指南

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-支持-blue.svg)](https://www.docker.com/)

> 🎯 **本指南適用於**: 初學者到高級用戶，涵蓋Docker和本地安裝两種方式
> 
> 📋 **預計時間**: Docker安裝 15-30分鐘 | 本地安裝 30-60分鐘

## 📋 目錄

- [系統要求](#系統要求)
- [快速開始](#快速開始)
- [Docker安裝（推薦）](#docker安裝推薦)
- [本地安裝](#本地安裝)
- [環境配置](#環境配置)
- [API密鑰配置](#api密鑰配置)
- [驗證安裝](#驗證安裝)
- [常见問題](#常见問題)
- [故障排除](#故障排除)

## 🔧 系統要求

### 最低配置
- **操作系統**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **內存**: 4GB RAM（推薦 8GB+）
- **存储**: 5GB 可用空間
- **網絡**: 穩定的互聯網連接

### 推薦配置
- **操作系統**: Windows 11, macOS 12+, Ubuntu 20.04+
- **內存**: 16GB RAM
- **存储**: 20GB 可用空間（SSD推薦）
- **CPU**: 4核心以上

### 软件依賴

#### Docker安裝方式
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) 4.0+
- [Docker Compose](https://docs.docker.com/compose/install/) 2.0+

#### 本地安裝方式
- [Python](https://www.python.org/downloads/) 3.10+
- [Git](https://git-scm.com/downloads) 2.30+
- [Node.js](https://nodejs.org/) 16+ (可選，用於某些功能)

## 🚀 快速開始

### 方式一：Docker一键啟動（推薦新手）

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 複制環境配置
cp .env.example .env

# 3. 編辑API密鑰（必须）
# Windows: notepad .env
# macOS/Linux: nano .env

# 4. 啟動服務
docker-compose up -d

# 5. 訪問應用
# 打開浏覽器訪問: http://localhost:8501
```

### 方式二：本地快速啟動

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 創建虛擬環境
python -m venv env

# 3. 激活虛擬環境
# Windows:
env\Scripts\activate
# macOS/Linux:
source env/bin/activate

# 4. 升級pip (重要！避免安裝錯誤)
python -m pip install --upgrade pip

# 5. 安裝依賴
pip install -e .

# 6. 複制環境配置
cp .env.example .env

# 7. 編辑API密鑰（必须）
# Windows: notepad .env
# macOS/Linux: nano .env

# 8. 啟動應用
python start_web.py
```

## 🐳 Docker安裝（推薦）

Docker安裝是最簡單、最穩定的方式，適合所有用戶。

### 步骤1：安裝Docker

#### Windows
1. 下載 [Docker Desktop for Windows](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe)
2. 運行安裝程序，按提示完成安裝
3. 重啟計算機
4. 啟動Docker Desktop，等待啟動完成

#### macOS
1. 下載 [Docker Desktop for Mac](https://desktop.docker.com/mac/main/amd64/Docker.dmg)
2. 拖拽到Applications文件夹
3. 啟動Docker Desktop，按提示完成設置

#### Linux (Ubuntu/Debian)
```bash
# 更新包索引
sudo apt update

# 安裝必要的包
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release

# 添加Docker官方GPG密鑰
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加Docker仓庫
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安裝Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 啟動Docker服務
sudo systemctl start docker
sudo systemctl enable docker

# 将用戶添加到docker組（可選）
sudo usermod -aG docker $USER
```

### 步骤2：驗證Docker安裝

```bash
# 檢查Docker版本
docker --version
docker-compose --version

# 測試Docker運行
docker run hello-world
```

### 步骤3：克隆項目

```bash
# 克隆項目到本地
git clone https://github.com/hsliuping/TradingAgents-CN.git

# 進入項目目錄
cd TradingAgents-CN

# 查看項目結構
ls -la
```

### 步骤4：配置環境變量

```bash
# 複制環境配置模板
cp .env.example .env

# 編辑環境配置文件
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env
```

**重要**: 必须配置至少一個AI模型的API密鑰，否則無法正常使用。

### 步骤5：啟動Docker服務

```bash
# 啟動所有服務（後台運行）
docker-compose up -d

# 查看服務狀態
docker-compose ps

# 查看日誌（可選）
docker-compose logs -f web
```

### 步骤6：訪問應用

打開浏覽器訪問以下地址：

- **主應用**: http://localhost:8501
- **Redis管理**: http://localhost:8081 (用戶名/密碼: admin/tradingagents123)
- **MongoDB管理**: http://localhost:8082 (可選，需要啟動管理服務)

## 💻 本地安裝

本地安裝提供更多的控制和自定義選項，適合開發者和高級用戶。

### 步骤1：安裝Python

#### Windows
1. 訪問 [Python官網](https://www.python.org/downloads/windows/)
2. 下載Python 3.10或更高版本
3. 運行安裝程序，**確保勾選"Add Python to PATH"**
4. 驗證安裝：
   ```cmd
   python --version
   pip --version
   ```

#### macOS
```bash
# 使用Homebrew安裝（推薦）
brew install python@3.10

# 或者下載官方安裝包
# 訪問 https://www.python.org/downloads/macos/
```

#### Linux (Ubuntu/Debian)
```bash
# 更新包列表
sudo apt update

# 安裝Python 3.10+
sudo apt install python3.10 python3.10-venv python3.10-pip

# 創建软鏈接（可選）
sudo ln -sf /usr/bin/python3.10 /usr/bin/python
sudo ln -sf /usr/bin/pip3 /usr/bin/pip
```

### 步骤2：克隆項目

```bash
# 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
```

### 步骤3：創建虛擬環境

```bash
# 創建虛擬環境
python -m venv env

# 激活虛擬環境
# Windows:
env\Scripts\activate

# macOS/Linux:
source env/bin/activate

# 驗證虛擬環境
which python  # 應该顯示虛擬環境中的python路徑
```

### 步骤4：安裝依賴

```bash
# 升級pip
python -m pip install --upgrade pip

# 安裝項目依賴
pip install -r requirements.txt

# 驗證關键包安裝
python -c "import streamlit; print('Streamlit安裝成功')"
python -c "import openai; print('OpenAI安裝成功')"
python -c "import akshare; print('AKShare安裝成功')"
```

### 步骤5：配置環境

```bash
# 複制環境配置
cp .env.example .env

# 編辑配置文件
# Windows: notepad .env
# macOS: open -e .env  
# Linux: nano .env
```

### 步骤6：可選數據庫安裝

#### MongoDB (推薦)
```bash
# Windows: 下載MongoDB Community Server
# https://www.mongodb.com/try/download/community

# macOS:
brew tap mongodb/brew
brew install mongodb-community

# Ubuntu/Debian:
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update
sudo apt install mongodb-org
```

#### Redis (推薦)
```bash
# Windows: 下載Redis for Windows
# https://github.com/microsoftarchive/redis/releases

# macOS:
brew install redis

# Ubuntu/Debian:
sudo apt install redis-server
```

### 步骤7：啟動應用

```bash
# 確保虛擬環境已激活
# Windows: env\Scripts\activate
# macOS/Linux: source env/bin/activate

# 啟動Streamlit應用
python -m streamlit run web/app.py

# 或使用啟動腳本
# Windows: start_web.bat
# macOS/Linux: ./start_web.sh
```

## ⚙️ 環境配置

### .env文件詳細配置

創建`.env`文件並配置以下參數：

```bash
# =============================================================================
# AI模型配置 (至少配置一個)
# =============================================================================

# OpenAI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1  # 可選，自定義API端點

# DeepSeek配置 (推薦，性價比高)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# 通義千問配置 (阿里云)
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# Google Gemini配置
GOOGLE_API_KEY=your_google_api_key_here

# =============================================================================
# 數據源配置
# =============================================================================

# Tushare配置 (A股數據，推薦)
TUSHARE_TOKEN=your_tushare_token_here

# FinnHub配置 (美股數據)
FINNHUB_API_KEY=your_finnhub_api_key_here

# =============================================================================
# 數據庫配置 (可選，提升性能)
# =============================================================================

# MongoDB配置
MONGODB_ENABLED=false  # 設置為true啟用MongoDB
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_mongodb_password
MONGODB_DATABASE=tradingagents

# Redis配置
REDIS_ENABLED=false  # 設置為true啟用Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# =============================================================================
# 應用配置
# =============================================================================

# 日誌級別
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR

# 緩存配置
CACHE_ENABLED=true
CACHE_TTL=3600  # 緩存過期時間（秒）

# 網絡配置
REQUEST_TIMEOUT=30  # 網絡請求超時時間（秒）
MAX_RETRIES=3  # 最大重試次數
```

### 配置優先級說明

1. **必须配置**: 至少一個AI模型API密鑰
2. **推薦配置**: Tushare Token（A股分析）
3. **可選配置**: 數據庫（提升性能）
4. **高級配置**: 自定義參數

## 🔑 API密鑰配置

### 獲取AI模型API密鑰

#### 1. DeepSeek (推薦，性價比最高)
1. 訪問 [DeepSeek開放平台](https://platform.deepseek.com/)
2. 註冊账號並完成實名認證
3. 進入控制台 → API密鑰
4. 創建新的API密鑰
5. 複制密鑰到`.env`文件的`DEEPSEEK_API_KEY`

**費用**: 約 ¥1/万tokens，新用戶送免費額度

#### 2. 通義千問 (國產，穩定)
1. 訪問 [阿里云DashScope](https://dashscope.aliyun.com/)
2. 登錄阿里云账號
3. 開通DashScope服務
4. 獲取API-KEY
5. 複制到`.env`文件的`DASHSCOPE_API_KEY`

**費用**: 按量計費，有免費額度

#### 3. OpenAI (功能强大)
1. 訪問 [OpenAI平台](https://platform.openai.com/)
2. 註冊账號並绑定支付方式
3. 進入API Keys页面
4. 創建新的API密鑰
5. 複制到`.env`文件的`OPENAI_API_KEY`

**費用**: 按使用量計費，需要美元支付

#### 4. Google Gemini (免費額度大)
1. 訪問 [Google AI Studio](https://aistudio.google.com/)
2. 登錄Google账號
3. 創建API密鑰
4. 複制到`.env`文件的`GOOGLE_API_KEY`

**費用**: 有較大免費額度

### 獲取數據源API密鑰

#### Tushare (A股數據，强烈推薦)
1. 訪問 [Tushare官網](https://tushare.pro/)
2. 註冊账號
3. 獲取Token
4. 複制到`.env`文件的`TUSHARE_TOKEN`

**費用**: 免費，有積分限制

#### FinnHub (美股數據)
1. 訪問 [FinnHub](https://finnhub.io/)
2. 註冊免費账號
3. 獲取API密鑰
4. 複制到`.env`文件的`FINNHUB_API_KEY`

**費用**: 免費版有限制，付費版功能更全

### API密鑰安全建议

1. **不要提交到Git**: 確保`.env`文件在`.gitignore`中
2. **定期轮換**: 定期更換API密鑰
3. **權限最小化**: 只給必要的權限
4. **監控使用**: 定期檢查API使用情况

## ✅ 驗證安裝

### 基础功能驗證

```bash
# 1. 檢查Python環境
python --version  # 應该顯示3.10+

# 2. 檢查關键依賴
python -c "import streamlit; print('✅ Streamlit正常')"
python -c "import openai; print('✅ OpenAI正常')"
python -c "import akshare; print('✅ AKShare正常')"

# 3. 檢查環境變量
python -c "import os; print('✅ API密鑰已配置' if os.getenv('DEEPSEEK_API_KEY') else '❌ 需要配置API密鑰')"
```

### Web界面驗證

1. 啟動應用後訪問 http://localhost:8501
2. 檢查页面是否正常加載
3. 嘗試輸入股票代碼（如：000001）
4. 選擇分析師团隊
5. 點擊"開始分析"按钮
6. 觀察是否有錯誤信息

### Docker環境驗證

```bash
# 檢查容器狀態
docker-compose ps

# 查看應用日誌
docker-compose logs web

# 檢查數據庫連接
docker-compose logs mongodb
docker-compose logs redis
```

### 功能測試

#### 測試A股分析
```bash
# 在Web界面中測試
股票代碼: 000001
市場類型: A股
研究深度: 3級
分析師: 市場分析師 + 基本面分析師
```

#### 測試美股分析
```bash
股票代碼: AAPL
市場類型: 美股
研究深度: 3級
分析師: 市場分析師 + 基本面分析師
```

#### 測試港股分析
```bash
股票代碼: 0700.HK
市場類型: 港股
研究深度: 3級
分析師: 市場分析師 + 基本面分析師
```

## ❓ 常见問題

### Q1: 啟動時提示"ModuleNotFoundError"
**A**: 依賴包未正確安裝
```bash
# 解決方案
pip install -r requirements.txt --upgrade
```

### Q2: API密鑰配置後仍然報錯
**A**: 檢查密鑰格式和權限
```bash
# 檢查環境變量是否生效
python -c "import os; print(os.getenv('DEEPSEEK_API_KEY'))"

# 重新啟動應用
```

### Q3: Docker啟動失败
**A**: 檢查Docker服務和端口占用
```bash
# 檢查Docker狀態
docker info

# 檢查端口占用
netstat -an | grep 8501

# 重新構建鏡像
docker-compose build --no-cache
```

### Q4: 分析過程中斷或失败
**A**: 檢查網絡連接和API配額
- 確保網絡連接穩定
- 檢查API密鑰余額
- 查看應用日誌獲取詳細錯誤信息

### Q5: 數據獲取失败
**A**: 檢查數據源配置
- 確認Tushare Token有效
- 檢查股票代碼格式
- 驗證網絡訪問權限

### Q6: 中文顯示乱碼
**A**: 檢查系統編碼設置
```bash
# Windows: 設置控制台編碼
chcp 65001

# Linux/macOS: 檢查locale
locale
```

### Q7: 內存不足錯誤
**A**: 調整分析參數
- 降低研究深度
- 减少分析師數量
- 增加系統內存

### Q8: 報告導出失败
**A**: 檢查導出依賴
```bash
# 安裝pandoc (PDF導出需要)
# Windows: 下載安裝包
# macOS: brew install pandoc
# Linux: sudo apt install pandoc
```

## 🔧 故障排除

### 日誌查看

#### Docker環境
```bash
# 查看應用日誌
docker-compose logs -f web

# 查看數據庫日誌
docker-compose logs mongodb
docker-compose logs redis

# 查看所有服務日誌
docker-compose logs
```

#### 本地環境
```bash
# 查看應用日誌
tail -f logs/tradingagents.log

# 啟動時顯示詳細日誌
python -m streamlit run web/app.py --logger.level=debug
```

### 網絡問題

#### 代理設置
```bash
# 設置HTTP代理
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 或在.env文件中設置
HTTP_PROXY=http://proxy.company.com:8080
HTTPS_PROXY=http://proxy.company.com:8080
```

#### DNS問題
```bash
# 使用公共DNS
# Windows: 設置網絡適配器DNS為8.8.8.8
# Linux: 編辑/etc/resolv.conf
nameserver 8.8.8.8
nameserver 8.8.4.4
```

### 性能優化

#### 內存優化
```bash
# 在.env中設置
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200
```

#### 緩存優化
```bash
# 啟用Redis緩存
REDIS_ENABLED=true
CACHE_TTL=7200  # 增加緩存時間
```

### 數據庫問題

#### MongoDB連接失败
```bash
# 檢查MongoDB服務
# Windows: services.msc 查找MongoDB
# Linux: sudo systemctl status mongod
# macOS: brew services list | grep mongodb

# 重置MongoDB
docker-compose down
docker volume rm tradingagents_mongodb_data
docker-compose up -d mongodb
```

#### Redis連接失败
```bash
# 檢查Redis服務
redis-cli ping

# 重置Redis
docker-compose down
docker volume rm tradingagents_redis_data
docker-compose up -d redis
```

### 權限問題

#### Linux/macOS權限
```bash
# 給腳本執行權限
chmod +x start_web.sh

# 修複文件所有權
sudo chown -R $USER:$USER .
```

#### Windows權限
- 以管理員身份運行命令提示符
- 檢查防火墙設置
- 確保Python在PATH中

### 重置安裝

#### 完全重置Docker環境
```bash
# 停止所有服務
docker-compose down

# 刪除所有數據
docker volume prune
docker system prune -a

# 重新構建
docker-compose build --no-cache
docker-compose up -d
```

#### 重置本地環境
```bash
# 刪除虛擬環境
rm -rf env

# 重新創建
python -m venv env
source env/bin/activate  # Linux/macOS
# 或 env\Scripts\activate  # Windows

# 重新安裝依賴
pip install -r requirements.txt
```

## 📞 獲取幫助

### 官方資源
- **項目主页**: https://github.com/hsliuping/TradingAgents-CN
- **文档中心**: https://www.tradingagents.cn/
- **問題反馈**: https://github.com/hsliuping/TradingAgents-CN/issues

### 社区支持
- **微信群**: 扫描README中的二維碼
- **QQ群**: 詳见項目主页
- **邮件支持**: 见項目聯系方式

### 贡献代碼
欢迎提交Pull Request和Issue，幫助改進項目！

---

🎉 **恭喜！** 您已成功安裝TradingAgents-CN。開始您的AI股票分析之旅吧！
