# 🔄 TradingAgents-CN 升級指南

## 📋 概述

本指南提供TradingAgents-CN各版本之間的升級方法，確保用戶能夠安全、顺利地升級到最新版本。

## 🚀 v0.1.12 升級指南 (2025-07-29)

### 🎯 升級亮點

- **智能新聞分析模塊**: AI驱動的新聞過濾、质量評估、相關性分析
- **多層次新聞過濾**: 智能過濾器、增强過濾器、統一新聞工具
- **技術修複優化**: DashScope適配器修複、DeepSeek死循環修複
- **項目結構優化**: 文档分類整理、測試文件統一、根目錄整潔

### 📋 升級步骤

#### 1. 從v0.1.11升級

```bash
# 1. 备份當前配置
cp .env .env.backup.v0111

# 2. 拉取最新代碼
git pull origin main

# 3. 檢查新的配置選項
diff .env.example .env

# 4. 重新啟動應用
streamlit run web/app.py
```

#### 2. 新增配置項

v0.1.12新增以下可選配置，添加到您的`.env`文件：

```env
# 🧠 新聞過濾配置
NEWS_FILTER_ENABLED=true
NEWS_RELEVANCE_THRESHOLD=0.6
NEWS_QUALITY_THRESHOLD=0.7
NEWS_ENHANCED_FILTER_ENABLED=true
NEWS_SENTIMENT_ANALYSIS_ENABLED=true
NEWS_CACHE_ENABLED=true
NEWS_CACHE_TTL=3600

# 🔧 工具調用優化
TOOL_CALL_RETRY_ENABLED=true
TOOL_CALL_MAX_RETRIES=3
TOOL_CALL_TIMEOUT=30

# 📊 性能監控
PERFORMANCE_MONITORING_ENABLED=true
DEBUG_LOGGING_ENABLED=false
```

#### 3. 功能驗證

升級完成後，請驗證以下功能：

```bash
# 1. 檢查新聞過濾功能
✅ 新聞分析模塊正常工作

# 2. 測試智能新聞過濾器
✅ 新聞相關性評分功能

# 3. 驗證增强新聞過濾器
✅ 情感分析和關键詞提取

# 4. 測試統一新聞工具
✅ 多源新聞整合功能

# 5. 驗證技術修複
✅ DashScope適配器工具調用正常
✅ DeepSeek新聞分析師無死循環
```

#### 4. 兼容性說明

- ✅ **完全向後兼容**: v0.1.11的所有配置繼续有效
- ✅ **無需數據迁移**: 現有數據和緩存無需處理
- ✅ **API密鑰複用**: 現有的API密鑰繼续使用
- ✅ **配置保持**: 所有現有設置保持不變
- ✅ **新功能可選**: 新聞分析功能默認啟用，可通過配置關闭

#### 5. 新功能使用示例

##### 智能新聞過濾
```python
from tradingagents.utils.news_filter import NewsFilter

# 創建新聞過濾器
filter = NewsFilter()

# 過濾新聞
filtered_news = filter.filter_news(
    news_list=news_data,
    stock_symbol="AAPL",
    relevance_threshold=0.6,
    quality_threshold=0.7
)
```

##### 統一新聞工具
```python
from tradingagents.tools.unified_news_tool import UnifiedNewsTool

# 創建新聞工具
news_tool = UnifiedNewsTool()

# 獲取新聞
news = news_tool.get_news(
    symbol="000001",
    limit=10,
    days_back=7
)
```

---

## 🚀 v0.1.11 升級指南 (2025-07-27)

### 🎯 升級亮點

- **多LLM提供商集成**: 支持4大提供商，60+個AI模型
- **模型選擇持久化**: 彻底解決页面刷新配置丢失問題
- **Web界面優化**: 320px侧邊栏，快速選擇按钮

### 📋 升級步骤

#### 1. 從v0.1.10升級

```bash
# 1. 备份當前配置
cp .env .env.backup.v0110

# 2. 拉取最新代碼
git pull origin main

# 3. 檢查新的配置選項
diff .env.example .env

# 4. 重新啟動應用
streamlit run web/app.py
```

#### 2. 新增配置項

v0.1.11新增以下可選配置，添加到您的`.env`文件：

```env
# 🚀 DeepSeek V3 (推薦，性價比極高)
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 🌐 OpenRouter (60+模型聚合)
OPENROUTER_API_KEY=your_openrouter_api_key_here

# 🌟 Google AI (Gemini系列)
GOOGLE_API_KEY=your_google_api_key_here
```

#### 3. 功能驗證

升級完成後，請驗證以下功能：

```bash
# 1. 檢查LLM提供商選項
✅ 侧邊栏顯示4個提供商選項

# 2. 測試模型選擇持久化
✅ 選擇模型 → 刷新页面 → 配置保持

# 3. 驗證URL參數
✅ URL包含 ?provider=xxx&model=yyy 參數

# 4. 測試快速選擇按钮
✅ 點擊快速按钮 → 模型立即切換
```

#### 4. 兼容性說明

- ✅ **完全向後兼容**: v0.1.10的所有配置繼续有效
- ✅ **無需數據迁移**: 現有數據和緩存無需處理
- ✅ **API密鑰複用**: 現有的DASHSCOPE_API_KEY等繼续使用
- ✅ **配置保持**: 所有現有設置保持不變

---

## 🎯 升級前準备

### 1. 备份重要數據

```bash
# 备份配置文件
cp .env .env.backup.$(date +%Y%m%d)

# 备份數據庫 (如果使用MongoDB)
mongodump --out backup_$(date +%Y%m%d)

# 备份Redis數據 (如果使用Redis)
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb backup_redis_$(date +%Y%m%d).rdb

# 备份自定義配置
cp -r config config_backup_$(date +%Y%m%d)
```

### 2. 檢查系統要求


| 組件               | 最低要求 | 推薦配置 |
| ------------------ | -------- | -------- |
| **Python**         | 3.10+    | 3.11+    |
| **內存**           | 4GB      | 8GB+     |
| **磁盘空間**       | 5GB      | 10GB+    |
| **Docker**         | 20.0+    | 最新版   |
| **Docker Compose** | 2.0+     | 最新版   |

### 3. 檢查當前版本

```bash
# 檢查當前版本
cat VERSION

# 或在Python中檢查
python -c "
import sys
sys.path.append('.')
from tradingagents import __version__
print(f'當前版本: {__version__}')
"
```

## 🚀 升級到v0.1.7

### 從v0.1.6升級 (推薦路徑)

#### 步骤1: 停止當前服務

```bash
# 如果使用Docker
docker-compose down

# 如果使用本地部署
# 停止Streamlit應用 (Ctrl+C)
```

#### 步骤2: 更新代碼

```bash
# 拉取最新代碼
git fetch origin
git checkout main
git pull origin main

# 檢查更新內容
git log --oneline v0.1.6..v0.1.7
```

#### 步骤3: 更新配置

```bash
# 比較配置文件差異
diff .env.example .env

# 添加新的配置項
cat >> .env << 'EOF'

# === v0.1.7 新增配置 ===
# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_ENABLED=true

# 報告導出配置
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf

# Docker環境配置 (如果使用Docker)
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379
EOF
```

#### 步骤4: 選擇部署方式

**選項A: Docker部署 (推薦)**

```bash
# 安裝Docker (如果未安裝)
# Windows: 下載Docker Desktop
# Linux: sudo apt install docker.io docker-compose

# 啟動服務
docker-compose up -d

# 驗證服務狀態
docker-compose ps
```

**選項B: 本地部署**

```bash
# 更新依賴
pip install -r requirements.txt

# 啟動應用
streamlit run web/app.py
```

#### 步骤5: 驗證升級

```bash
# 檢查版本
curl http://localhost:8501/health

# 測試核心功能
# 1. 訪問Web界面: http://localhost:8501
# 2. 進行一次股票分析
# 3. 測試報告導出功能
# 4. 檢查數據庫連接 (如果使用)
```

### 從v0.1.5及以下升級

#### 重要提醒

⚠️ **建议全新安裝**: 由於架構變化較大，建议全新安裝而非直接升級

#### 步骤1: 導出重要數據

```bash
# 導出分析歷史 (如果有)
python -c "
import json
from tradingagents.config.config_manager import config_manager
history = config_manager.get_analysis_history()
with open('analysis_history_backup.json', 'w') as f:
    json.dump(history, f, indent=2)
"

# 導出自定義配置
cp .env custom_config_backup.env
```

#### 步骤2: 全新安裝

```bash
# 創建新目錄
mkdir TradingAgents-CN-v0.1.7
cd TradingAgents-CN-v0.1.7

# 克隆最新版本
git clone https://github.com/hsliuping/TradingAgents-CN.git .

# 恢複配置
cp ../custom_config_backup.env .env
# 手動調整配置以適應新版本
```

#### 步骤3: 迁移數據

```bash
# 如果使用MongoDB，導入歷史數據
mongorestore backup_20250713/

# 如果使用文件存储，複制數據文件
cp -r ../old_version/data/ ./data/
```

## 🐳 Docker升級專門指南

### 首次使用Docker

```bash
# 1. 確保Docker已安裝
docker --version
docker-compose --version

# 2. 停止本地服務
# 停止本地Streamlit、MongoDB、Redis等服務

# 3. 配置環境變量
cp .env.example .env
# 編辑.env文件，註意Docker環境的特殊配置

# 4. 啟動Docker服務
docker-compose up -d

# 5. 訪問服務
# Web界面: http://localhost:8501
# 數據庫管理: http://localhost:8081
# 緩存管理: http://localhost:8082
```

### Docker環境配置調整

```bash
# 數據庫連接配置調整
sed -i 's/localhost:27017/mongodb:27017/g' .env
sed -i 's/localhost:6379/redis:6379/g' .env

# 或手動編辑.env文件
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379
```

## 🔧 常见升級問題

### 問題1: 依賴冲突

**症狀**: `pip install` 失败，依賴版本冲突

**解決方案**:

```bash
# 創建新的虛擬環境
python -m venv env_new
source env_new/bin/activate  # Linux/macOS
# env_new\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 問題2: 配置文件格式變化

**症狀**: 應用啟動失败，配置錯誤

**解決方案**:

```bash
# 使用新的配置模板
cp .env .env.old
cp .env.example .env

# 手動迁移配置
# 對比.env.old和.env，迁移必要的配置
```

### 問題3: 數據庫連接失败

**症狀**: MongoDB/Redis連接失败

**解決方案**:

```bash
# Docker環境
# 確保使用容器服務名
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379

# 本地環境
# 確保使用localhost
MONGODB_URL=mongodb://localhost:27017/tradingagents
REDIS_URL=redis://localhost:6379
```

### 問題4: 端口冲突

**症狀**: 服務啟動失败，端口被占用

**解決方案**:

```bash
# 檢查端口占用
netstat -tulpn | grep :8501

# 修改端口配置
# 編辑docker-compose.yml或.env文件
WEB_PORT=8502
MONGODB_PORT=27018
```

### 問題5: 權限問題

**症狀**: Docker容器無法訪問文件

**解決方案**:

```bash
# Linux/macOS
sudo chown -R $USER:$USER .
chmod -R 755 .

# Windows
# 確保Docker Desktop有足夠權限
```

## 📊 升級驗證清單

### 功能驗證

- [ ]  **Web界面正常訪問** (http://localhost:8501)
- [ ]  **股票分析功能正常**
  - [ ]  A股分析 (如: 000001)
  - [ ]  美股分析 (如: AAPL)
- [ ]  **LLM模型正常工作**
  - [ ]  DeepSeek模型 (v0.1.7新增)
  - [ ]  阿里百炼模型
  - [ ]  Google AI模型
- [ ]  **數據庫連接正常**
  - [ ]  MongoDB連接
  - [ ]  Redis連接
- [ ]  **報告導出功能** (v0.1.7新增)
  - [ ]  Markdown導出
  - [ ]  Word導出
  - [ ]  PDF導出
- [ ]  **Docker服務正常** (如果使用)
  - [ ]  所有容器運行正常
  - [ ]  管理界面可訪問

### 性能驗證

- [ ]  **響應速度**: 分析時間在預期範围內
- [ ]  **內存使用**: 系統內存使用正常
- [ ]  **錯誤處理**: 異常情况處理正常
- [ ]  **數據持久化**: 數據正確保存和讀取

## 🔄 回滚方案

### 如果升級失败

```bash
# 1. 停止新版本服務
docker-compose down
# 或停止本地服務

# 2. 恢複代碼
git checkout v0.1.6  # 或之前的版本

# 3. 恢複配置
cp .env.backup .env

# 4. 恢複數據
mongorestore backup_20250713/

# 5. 重啟服務
docker-compose up -d
# 或啟動本地服務
```

## 📞 獲取幫助

### 升級支持

如果在升級過程中遇到問題，可以通過以下方式獲取幫助：

- 🐛 [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)
- 💬 [GitHub Discussions](https://github.com/hsliuping/TradingAgents-CN/discussions)
- 📚 [完整文档](https://github.com/hsliuping/TradingAgents-CN/tree/main/docs)

### 提交問題時請包含

1. **當前版本**: 升級前的版本號
2. **目標版本**: 要升級到的版本號
3. **部署方式**: Docker或本地部署
4. **錯誤信息**: 完整的錯誤日誌
5. **系統環境**: 操作系統、Python版本等

---

*最後更新: 2025-07-13*
*版本: cn-0.1.7*
*維護团隊: TradingAgents-CN開發团隊*
