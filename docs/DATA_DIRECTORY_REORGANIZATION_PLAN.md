# 數據目錄重新規劃方案

## 📊 當前問題分析

### 🔍 現狀
項目中存在多個分散的數據目錄，導致數據管理混乱：

1. **項目根目錄 `data/`** - 數據庫數據、報告、會話
2. **Web目錄 `web/data/`** - Web應用相關數據
3. **Results目錄 `results/`** - 分析結果報告
4. **緩存目錄 `tradingagents/dataflows/data_cache/`** - 數據緩存

### ❌ 存在的問題
- 數據分散存储，難以管理
- 路徑配置複雜，容易出錯
- 备份和清理困難
- 開發和部署環境不一致

## 🎯 新的目錄結構設計

### 📁 統一數據根目錄：`data/`

```
data/
├── 📊 cache/                    # 數據緩存 (原 tradingagents/dataflows/data_cache/)
│   ├── stock_data/             # 股票數據緩存
│   ├── news_data/              # 新聞數據緩存
│   ├── fundamentals/           # 基本面數據緩存
│   └── metadata/               # 緩存元數據
│
├── 📈 analysis_results/         # 分析結果 (原 web/data/analysis_results/ + results/)
│   ├── summary/                # 分析摘要
│   ├── detailed/               # 詳細報告
│   └── exports/                # 導出文件 (PDF, Word, MD)
│
├── 🗄️ databases/               # 數據庫數據 (原 data/mongodb/, data/redis/)
│   ├── mongodb/                # MongoDB數據文件
│   └── redis/                  # Redis數據文件
│
├── 📝 sessions/                # 會話數據 (合並 data/sessions/ + web/data/sessions/)
│   ├── web_sessions/           # Web會話
│   └── cli_sessions/           # CLI會話
│
├── 📋 logs/                    # 日誌文件 (原 web/data/operation_logs/)
│   ├── application/            # 應用日誌
│   ├── operations/             # 操作日誌
│   └── user_activities/        # 用戶活動日誌 (原 web/data/user_activities/)
│
├── 🔧 config/                  # 配置文件緩存
│   ├── user_configs/           # 用戶配置
│   └── system_configs/         # 系統配置
│
└── 📦 temp/                    # 臨時文件
    ├── downloads/              # 下載的臨時文件
    └── processing/             # 處理中的臨時文件
```

## 🔧 環境變量配置

### 新增環境變量
```bash
# 統一數據根目錄
TRADINGAGENTS_DATA_DIR=./data

# 子目錄配置（可選，使用默認值）
TRADINGAGENTS_CACHE_DIR=${TRADINGAGENTS_DATA_DIR}/cache
TRADINGAGENTS_RESULTS_DIR=${TRADINGAGENTS_DATA_DIR}/analysis_results
TRADINGAGENTS_SESSIONS_DIR=${TRADINGAGENTS_DATA_DIR}/sessions
TRADINGAGENTS_LOGS_DIR=${TRADINGAGENTS_DATA_DIR}/logs
TRADINGAGENTS_CONFIG_DIR=${TRADINGAGENTS_DATA_DIR}/config
TRADINGAGENTS_TEMP_DIR=${TRADINGAGENTS_DATA_DIR}/temp
```

## 📋 迁移計劃

### 階段1：創建新目錄結構
1. 創建統一的 `data/` 目錄結構
2. 更新環境變量配置
3. 修改代碼中的路徑引用

### 階段2：數據迁移
1. 迁移緩存數據：`tradingagents/dataflows/data_cache/` → `data/cache/`
2. 迁移分析結果：`results/` + `web/data/analysis_results/` → `data/analysis_results/`
3. 迁移會話數據：`data/sessions/` + `web/data/sessions/` → `data/sessions/`
4. 迁移日誌數據：`web/data/operation_logs/` + `web/data/user_activities/` → `data/logs/`

### 階段3：代碼更新
1. 更新路徑配置逻辑
2. 修改文件操作代碼
3. 更新文档和示例

### 階段4：清理旧目錄
1. 驗證新目錄結構正常工作
2. 刪除旧的分散目錄
3. 更新 `.gitignore` 文件

## 🎯 實施優势

### ✅ 優點
1. **統一管理**：所有數據集中在一個根目錄下
2. **清晰分類**：按功能明確分類，易於理解
3. **便於备份**：只需备份一個 `data/` 目錄
4. **環境一致**：開發、測試、生產環境配置一致
5. **易於擴展**：新增數據類型時有明確的存放位置

### 🔧 配置灵活性
- 支持環境變量自定義路徑
- 支持相對路徑和絕對路徑
- 支持Docker容器化部署
- 支持多環境配置

## 📝 註意事項

1. **向後兼容**：迁移過程中保持向後兼容
2. **數據安全**：迁移前做好數據备份
3. **渐進式迁移**：分階段實施，降低風險
4. **文档更新**：及時更新相關文档和示例

## 🚀 下一步行動

1. 確認方案可行性
2. 創建迁移腳本
3. 在測試環境驗證
4. 逐步在生產環境實施