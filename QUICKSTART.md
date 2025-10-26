# 🚀 TradingAgents-CN 快速開始指南

> 📋 **版本**: cn-0.1.10 | **更新時間**: 2025-07-18
> 🎯 **目標**: 5分鐘內完成部署並開始股票分析

## 🎯 選擇部署方式

### 🐳 方式一：Docker部署 (推薦)

**適用場景**: 生產環境、快速體驗、零配置啟動

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 配置環境變量
cp .env.example .env
# 編辑 .env 文件，填入API密鑰

# 3. 構建並啟動服務
docker-compose up -d --build

# 註意：首次運行會自動構建Docker鏡像，需要5-10分鐘時間
# 構建過程包括：
# - 下載基础鏡像和依賴 (~800MB)
# - 安裝系統工具 (pandoc, wkhtmltopdf等)
# - 安裝Python依賴包
# - 配置運行環境

# 4. 訪問應用
# Web界面: http://localhost:8501
# 數據庫管理: http://localhost:8081
# 緩存管理: http://localhost:8082
```

### 🔧 分步構建方式 (可選)

如果您希望分步進行，可以先單獨構建鏡像：

```bash
# 方式A: 分步構建
# 1. 先構建Docker鏡像
docker build -t tradingagents-cn:latest .

# 2. 再啟動所有服務
docker-compose up -d

# 方式B: 一键構建啟動 (推薦)
docker-compose up -d --build
```

### 💻 方式二：本地部署

**適用場景**: 開發環境、自定義配置、離線使用

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 創建虛擬環境
python -m venv env
env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/macOS

# 3. 升級pip (重要！避免安裝錯誤)
python -m pip install --upgrade pip

# 4. 安裝依賴（推薦使用鎖定版本，安裝速度最快）
pip install -r requirements-lock.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -e . --no-deps

# 或一步安裝（會重新解析依賴，速度較慢）
# pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 💡 國內用戶推薦使用鏡像加速（詳见 docs/installation-mirror.md）
# ⚠️ Windows 用戶如遇到 PyYAML 編譯錯誤，使用鎖定版本可避免此問題

# 5. 配置環境變量
cp .env.example .env
# 編辑 .env 文件

# 6. 啟動應用
# 方法1: 使用簡化啟動腳本（推薦）
python start_web.py

# 方法2: 使用項目啟動腳本
python web/run_web.py

# 方法3: 直接使用streamlit（需要先安裝項目）
streamlit run web/app.py
```

## 🔧 環境配置

### 📋 必需配置

創建 `.env` 文件並配置以下內容：

```bash
# === LLM模型配置 (至少選擇一個) ===

# 🇨🇳 DeepSeek (推薦 - 成本低，中文優化)
DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here
DEEPSEEK_ENABLED=true

# 🇨🇳 阿里百炼通義千問 (推薦 - 中文理解好)
QWEN_API_KEY=your_qwen_api_key
QWEN_ENABLED=true

# 🌍 Google AI Gemini (推薦 - 推理能力强)
GOOGLE_API_KEY=your_google_api_key
GOOGLE_ENABLED=true

# 🤖 OpenAI (可選 - 通用能力强，成本較高)
OPENAI_API_KEY=your_openai_api_key
OPENAI_ENABLED=true
```

### 🔑 API密鑰獲取


| 提供商        | 獲取地址                                                | 特色               | 成本      |
| ------------- | ------------------------------------------------------- | ------------------ | --------- |
| **DeepSeek**  | [platform.deepseek.com](https://platform.deepseek.com/) | 工具調用，中文優化 | 💰 極低   |
| **阿里百炼**  | [dashscope.aliyun.com](https://dashscope.aliyun.com/)   | 中文理解，響應快   | 💰 低     |
| **Google AI** | [aistudio.google.com](https://aistudio.google.com/)     | 推理能力，多模態   | 💰💰 中等 |
| **OpenAI**    | [platform.openai.com](https://platform.openai.com/)     | 通用能力强         | 💰💰💰 高 |

### 📊 可選配置

```bash
# === 數據源配置 (可選) ===
TUSHARE_TOKEN=your_tushare_token          # A股數據增强
FINNHUB_API_KEY=your_finnhub_key          # 美股數據

# === 數據庫配置 (Docker自動配置) ===
MONGODB_URL=mongodb://mongodb:27017/tradingagents  # Docker環境
REDIS_URL=redis://redis:6379                       # Docker環境

# === 導出功能配置 ===
EXPORT_ENABLED=true                       # 啟用報告導出
EXPORT_DEFAULT_FORMAT=word,pdf            # 默認導出格式
```

## 🚀 開始使用

### 1️⃣ 訪問Web界面

```bash
# 打開浏覽器訪問
http://localhost:8501
```

### 2️⃣ 配置分析參數

- **🧠 選擇LLM模型**: DeepSeek V3 / 通義千問 / Gemini
- **📊 選擇分析深度**: 快速 / 標準 / 深度
- **🎯 選擇分析師**: 市場分析 / 基本面分析 / 新聞分析

### 3️⃣ 輸入股票代碼

```bash
# 🇨🇳 A股示例
000001  # 平安銀行
600519  # 贵州茅台
000858  # 五粮液

# 🇺🇸 美股示例  
AAPL    # 苹果公司
TSLA    # 特斯拉
MSFT    # 微软
```

### 4️⃣ 開始分析

1. 點擊"🚀 開始分析"按钮
2. **📊 實時進度跟蹤**: 觀察分析進度和當前步骤
   - 顯示已用時間和預計剩余時間
   - 實時更新分析狀態和步骤說明
   - 支持手動刷新和自動刷新控制
3. **⏰ 分析完成**: 等待分析完成（2-10分鐘，取決於分析深度）
   - 顯示準確的总耗時
   - 自動顯示"🎉 分析完成"狀態
4. **📋 查看報告**: 點擊"📊 查看分析報告"按钮
   - 即時顯示詳細的投資建议和分析報告
   - 支持重複查看和页面刷新後恢複
5. **📄 導出報告**: 可選擇導出為Word/PDF/Markdown格式

### 🆕 v0.1.10 新功能亮點

#### 🚀 實時進度顯示
- **異步進度跟蹤**: 實時顯示分析進度，不再需要盲等
- **智能步骤识別**: 自動识別當前分析步骤和狀態
- **準確時間計算**: 顯示真實的分析耗時，不受查看時間影響

#### 📊 智能會話管理
- **狀態持久化**: 支持页面刷新後恢複分析狀態
- **自動降級**: Redis不可用時自動切換到文件存储
- **用戶體驗**: 提供更穩定可靠的會話管理

#### 🎨 界面優化
- **查看報告按钮**: 分析完成後一键查看報告
- **重複按钮清理**: 移除重複的刷新按钮，界面更簡潔
- **響應式設計**: 改進移動端和不同屏幕的適配

## 📄 報告導出功能

### 支持格式


| 格式            | 用途               | 特點               |
| --------------- | ------------------ | ------------------ |
| **📝 Markdown** | 在線查看，版本控制 | 轻量級，可編辑     |
| **📄 Word**     | 商業報告，編辑修改 | 專業格式，易編辑   |
| **📊 PDF**      | 正式發布，打印存档 | 固定格式，專業外觀 |

### 導出步骤

1. 完成股票分析
2. 在結果页面點擊導出按钮
3. 選擇導出格式
4. 自動下載到本地

## 🎯 功能特色

### 🤖 多智能體協作

- **📈 市場分析師**: 技術指標，趋势分析
- **💰 基本面分析師**: 財務數據，估值模型
- **📰 新聞分析師**: 新聞情绪，事件影響
- **🐂🐻 研究員**: 看涨看跌辩論
- **🎯 交易決策員**: 综合決策制定

### 🧠 智能模型選擇

- **DeepSeek V3**: 成本低，工具調用强，中文優化
- **通義千問**: 中文理解好，響應快，阿里云
- **Gemini**: 推理能力强，多模態，Google
- **GPT-4**: 通用能力最强，成本較高

### 📊 全面數據支持

- **🇨🇳 A股**: 實時行情，歷史數據，財務指標
- **🇺🇸 美股**: NYSE/NASDAQ，實時數據
- **📰 新聞**: 實時財經新聞，情绪分析
- **💬 社交**: Reddit情绪，市場熱度

## 🚨 常见問題

### ❓ 分析失败怎么办？

1. **檢查API密鑰**: 確認密鑰正確且有余額
2. **網絡連接**: 確保網絡穩定，可訪問API
3. **模型切換**: 嘗試切換其他LLM模型
4. **查看日誌**: 檢查控制台錯誤信息

### ❓ 如何提高分析速度？

1. **選擇快速模型**: DeepSeek V3 響應最快
2. **啟用緩存**: 使用Redis緩存重複數據
3. **快速模式**: 選擇快速分析深度
4. **網絡優化**: 確保網絡環境穩定

### ❓ Docker部署問題？

```bash
# 檢查服務狀態
docker-compose ps

# 查看日誌
docker logs TradingAgents-web

# 重啟服務
docker-compose restart
```

## 📚 下一步

### 🎯 深入使用

1. **📖 阅讀文档**: [完整文档](./docs/)
2. **🔧 開發環境**: [開發指南](./docs/DEVELOPMENT_SETUP.md)
3. **🚨 故障排除**: [問題解決](./docs/troubleshooting/)
4. **🏗️ 架構了解**: [技術架構](./docs/architecture/)

### 🤝 參与贡献

- 🐛 [報告問題](https://github.com/hsliuping/TradingAgents-CN/issues)
- 💡 [功能建议](https://github.com/hsliuping/TradingAgents-CN/discussions)
- 🔧 [提交代碼](https://github.com/hsliuping/TradingAgents-CN/pulls)
- 📚 [完善文档](https://github.com/hsliuping/TradingAgents-CN/tree/develop/docs)

---

## 🎉 恭喜完成快速開始！

**💡 提示**: 建议先用熟悉的股票代碼進行測試，體驗完整的分析流程。

**📞 技術支持**: [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)

---

*最後更新: 2025-07-13 | 版本: cn-0.1.7*
