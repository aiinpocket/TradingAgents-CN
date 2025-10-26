# 🚀 TradingAgents-CN 快速開始

> ⏱️ **5分鐘快速上手** | 📋 **零基础友好** | 🎯 **一键啟動**

## 🎯 選擇您的安裝方式

### 🐳 方式一：Docker安裝（推薦）
**適合**: 所有用戶，特別是新手用戶
**優势**: 一键啟動，環境隔離，穩定可靠

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 配置API密鑰
cp .env.example .env
# 編辑.env文件，添加您的API密鑰

# 3. 啟動服務
docker-compose up -d

# 4. 訪問應用
# 浏覽器打開: http://localhost:8501
```

### 💻 方式二：本地安裝
**適合**: 開發者和高級用戶
**優势**: 更多控制權，便於開發調試

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 創建虛擬環境
python -m venv env

# 3. 激活虛擬環境
# Windows: env\Scripts\activate
# macOS/Linux: source env/bin/activate

# 4. 安裝依賴
pip install -r requirements.txt

# 5. 配置API密鑰
cp .env.example .env
# 編辑.env文件，添加您的API密鑰

# 6. 啟動應用
python -m streamlit run web/app.py
```

### 🤖 方式三：自動安裝（最簡單）
```bash
# 下載並運行自動安裝腳本
python scripts/setup/quick_install.py
```

## 🔑 必需的API密鑰

### 推薦配置（選擇一個即可）

#### 1. DeepSeek（推薦，性價比最高）
- 🌐 **註冊地址**: https://platform.deepseek.com/
- 💰 **費用**: ~¥1/万tokens，新用戶有免費額度
- 🔧 **配置**: 在`.env`文件中設置 `DEEPSEEK_API_KEY`

#### 2. 通義千問（國產，穩定）
- 🌐 **註冊地址**: https://dashscope.aliyun.com/
- 💰 **費用**: 按量計費，有免費額度
- 🔧 **配置**: 在`.env`文件中設置 `DASHSCOPE_API_KEY`

#### 3. OpenAI（功能强大）
- 🌐 **註冊地址**: https://platform.openai.com/
- 💰 **費用**: 按使用量計費，需美元支付
- 🔧 **配置**: 在`.env`文件中設置 `OPENAI_API_KEY`

### 可選配置（提升體驗）

#### Tushare（A股數據）
- 🌐 **註冊地址**: https://tushare.pro/
- 💰 **費用**: 免費，有積分限制
- 🔧 **配置**: 在`.env`文件中設置 `TUSHARE_TOKEN`

## 📝 配置示例

編辑`.env`文件，添加您的API密鑰：

```bash
# 選擇一個AI模型（必须）
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# 或者使用通義千問
# DASHSCOPE_API_KEY=your-dashscope-key-here

# 或者使用OpenAI
# OPENAI_API_KEY=sk-your-openai-key-here

# A股數據源（推薦）
TUSHARE_TOKEN=your-tushare-token-here

# 數據庫（可選，提升性能）
MONGODB_ENABLED=false
REDIS_ENABLED=false
```

## ✅ 驗證安裝

### 1. 訪問Web界面
打開浏覽器訪問: http://localhost:8501

### 2. 測試分析功能
- 輸入股票代碼（如：`000001`、`AAPL`、`0700.HK`）
- 選擇分析師团隊
- 點擊"開始分析"

### 3. 檢查日誌
```bash
# Docker環境
docker-compose logs web

# 本地環境
tail -f logs/tradingagents.log
```

## 🎯 第一次使用

### 推薦測試股票

#### A股測試
```
股票代碼: 000001
市場類型: A股
研究深度: 1級（快速測試）
分析師: 市場分析師 + 基本面分析師
```

#### 美股測試
```
股票代碼: AAPL
市場類型: 美股
研究深度: 1級（快速測試）
分析師: 市場分析師 + 基本面分析師
```

#### 港股測試
```
股票代碼: 0700.HK
市場類型: 港股
研究深度: 1級（快速測試）
分析師: 市場分析師 + 基本面分析師
```

## ❓ 常见問題

### Q: 啟動失败怎么办？
**A**: 檢查以下几點：
1. Python版本是否為3.10+
2. 是否正確配置了API密鑰
3. 網絡連接是否正常
4. 端口8501是否被占用

### Q: 分析失败怎么办？
**A**: 檢查以下几點：
1. API密鑰是否有效
2. API余額是否充足
3. 股票代碼格式是否正確
4. 網絡是否能訪問相關API

### Q: 如何獲取更多幫助？
**A**: 
- 📖 **詳細文档**: [docs/INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)
- 🐛 **問題反馈**: https://github.com/hsliuping/TradingAgents-CN/issues
- 💬 **社区討論**: 见項目主页的微信群二維碼

## 🎉 開始使用

恭喜！您已成功安裝TradingAgents-CN。

**下一步**:
1. 🔍 **探索功能**: 嘗試不同的分析師組合和研究深度
2. 📊 **查看報告**: 分析完成後可導出PDF/Word報告
3. ⚙️ **優化配置**: 根據需要調整數據庫和緩存設置
4. 🚀 **高級功能**: 探索批量分析、自定義提示等功能

**享受您的AI股票分析之旅！** 🚀📈
