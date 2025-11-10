# 🚀 TradingAgents-CN 快速開始

> ⏱️ **5分鐘快速上手** | 📋 **零基礎友好** | 🎯 **一鍵啟動**

## 🎯 選擇您的安裝方式

### 🐳 方式一：Docker安裝（推薦）
**適合**: 所有用戶，特別是新手用戶
**優勢**: 一鍵啟動，環境隔離，穩定可靠

```bash
# 1. 克隆專案
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 配置API密鑰
cp .env.example .env
# 編輯.env檔案，新增您的API密鑰

# 3. 啟動服務
docker-compose up -d

# 4. 訪問應用
# 瀏覽器開啟: http://localhost:8501
```

### 💻 方式二：本地安裝
**適合**: 開發者和進階用戶
**優勢**: 更多控制權，便於開發調試

```bash
# 1. 克隆專案
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 建立虛擬環境
python -m venv env

# 3. 啟動虛擬環境
# Windows: env\Scripts\activate
# macOS/Linux: source env/bin/activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 配置API密鑰
cp .env.example .env
# 編輯.env檔案，新增您的API密鑰

# 6. 啟動應用
python -m streamlit run web/app.py
```

### 🤖 方式三：自動安裝（最簡單）
```bash
# 下載並執行自動安裝腳本
python scripts/setup/quick_install.py
```

## 🔑 必需的API密鑰

### 推薦配置（選擇一個即可）

#### 1. OpenAI（功能強大）
- 🌐 **註冊地址**: https://platform.openai.com/
- 💰 **費用**: 按使用量計費，需美元支付
- 🔧 **配置**: 在`.env`檔案中設定 `OPENAI_API_KEY`

#### 2. Google AI（免費額度大）
- 🌐 **註冊地址**: https://aistudio.google.com/
- 💰 **費用**: 有較大免費額度
- 🔧 **配置**: 在`.env`檔案中設定 `GOOGLE_API_KEY`

## 📝 配置範例

編輯`.env`檔案，新增您的API密鑰：

```bash
# 選擇一個AI模型（必須）
OPENAI_API_KEY=sk-your-openai-key-here

# 或者使用Google AI
# GOOGLE_API_KEY=your-google-api-key-here

# 資料庫（可選，提升效能）
MONGODB_ENABLED=false
REDIS_ENABLED=false
```

## ✅ 驗證安裝

### 1. 訪問Web界面
開啟瀏覽器訪問: http://localhost:8501

### 2. 測試分析功能
- 輸入股票代碼（如：`AAPL`、`GOOGL`）
- 選擇分析師團隊
- 點擊「開始分析」

### 3. 檢查日誌
```bash
# Docker環境
docker-compose logs web

# 本地環境
tail -f logs/tradingagents.log
```

## 🎯 第一次使用

### 推薦測試股票

#### 美股測試
```
股票代碼: AAPL
市場類型: 美股
研究深度: 1級（快速測試）
分析師: 市場分析師 + 基本面分析師
```

## ❓ 常見問題

### Q: 啟動失敗怎麼辦？
**A**: 檢查以下幾點：
1. Python版本是否為3.10+
2. 是否正確配置了API密鑰
3. 網路連線是否正常
4. 埠號8501是否被佔用

### Q: 分析失敗怎麼辦？
**A**: 檢查以下幾點：
1. API密鑰是否有效
2. API餘額是否充足
3. 股票代碼格式是否正確
4. 網路是否能訪問相關API

### Q: 如何獲取更多幫助？
**A**:
- 📖 **詳細文檔**: [docs/INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- 🐛 **問題回饋**: https://github.com/hsliuping/TradingAgents-CN/issues
- 💬 **社群討論**: GitHub Issues 和 Discussions

## 🎉 開始使用

恭喜！您已成功安裝TradingAgents-CN。

**下一步**:
1. 🔍 **探索功能**: 嘗試不同的分析師組合和研究深度
2. 📊 **查看報告**: 分析完成後可匯出PDF/Word報告
3. ⚙️ **優化配置**: 根據需要調整資料庫和快取設定
4. 🚀 **進階功能**: 探索批次分析、自訂提示等功能

**享受您的AI股票分析之旅！** 🚀📈
