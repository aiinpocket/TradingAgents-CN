# TradingAgents 數據庫配置指南

## 📋 概述

TradingAgents現在支持MongoDB和Redis數據庫，提供數據持久化存储和高性能緩存功能。

## 🚀 快速啟動

### 1. 啟動Docker服務

```bash
# Windows
scripts\start_services_alt_ports.bat

# Linux/Mac
scripts/start_services_alt_ports.sh
```

### 2. 安裝Python依賴

```bash
pip install pymongo redis
```

### 3. 初始化數據庫

```bash
python scripts/init_database.py
```

### 4. 啟動Web應用

```bash
cd web
python -m streamlit run app.py
```

## 🔧 服務配置

### Docker服務端口

由於本地環境端口冲突，使用了替代端口：

| 服務 | 默認端口 | 實际端口 | 訪問地址 |
|------|----------|----------|----------|
| MongoDB | 27017 | **27018** | localhost:27018 |
| Redis | 6379 | **6380** | localhost:6380 |
| Redis Commander | 8081 | **8082** | http://localhost:8082 |

### 認證信息

- **用戶名**: admin
- **密碼**: tradingagents123
- **數據庫**: tradingagents

## 📊 數據庫結構

### MongoDB集合

1. **stock_data** - 股票歷史數據
   - 索引: (symbol, market_type), created_at, updated_at
   
2. **analysis_results** - 分析結果
   - 索引: (symbol, analysis_type), created_at
   
3. **user_sessions** - 用戶會話
   - 索引: session_id, created_at, last_activity
   
4. **configurations** - 系統配置
   - 索引: (config_type, config_name), updated_at

### Redis緩存結構

- **键前缀**: `tradingagents:`
- **TTL配置**:
  - 美股數據: 2小時
  - A股數據: 1小時
  - 新聞數據: 4-6小時
  - 基本面數據: 12-24小時

## 🛠️ 管理工具

### Redis Commander
- 訪問地址: http://localhost:8082
- 功能: Redis數據可視化管理

### 緩存管理页面
- 訪問地址: http://localhost:8501 -> 緩存管理
- 功能: 緩存統計、清理、測試

## 📝 配置文件

### 環境變量 (.env)

```bash
# MongoDB配置
MONGODB_HOST=localhost
MONGODB_PORT=27018
MONGODB_USERNAME=admin
MONGODB_PASSWORD=tradingagents123
MONGODB_DATABASE=tradingagents

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6380
REDIS_PASSWORD=tradingagents123
REDIS_DB=0
```

### 默認配置 (default_config.py)

數據庫配置已集成到默認配置中，支持環境變量覆蓋。

## 🔍 故障排除

### 常见問題

1. **端口冲突**
   ```bash
   # 檢查端口占用
   netstat -an | findstr :27018
   netstat -an | findstr :6380
   ```

2. **連接失败**
   ```bash
   # 檢查Docker容器狀態
   docker ps --filter "name=tradingagents-"
   
   # 查看容器日誌
   docker logs tradingagents-mongodb
   docker logs tradingagents-redis
   ```

3. **權限問題**
   ```bash
   # 重啟容器
   docker restart tradingagents-mongodb tradingagents-redis
   ```

### 重置數據庫

```bash
# 停止並刪除容器
docker stop tradingagents-mongodb tradingagents-redis tradingagents-redis-commander
docker rm tradingagents-mongodb tradingagents-redis tradingagents-redis-commander

# 刪除數據卷（可選，會丢失所有數據）
docker volume rm tradingagents_mongodb_data tradingagents_redis_data

# 重新啟動
scripts\start_services_alt_ports.bat
python scripts/init_database.py
```

## 📈 性能優化

### 緩存策略

1. **分層緩存**: Redis + 文件緩存
2. **智能TTL**: 根據數據類型設置不同過期時間
3. **壓縮存储**: 大數據自動壓縮（可配置）
4. **批量操作**: 支持批量讀寫

### 監控指標

- 緩存命中率
- 數據庫連接數
- 內存使用量
- 響應時間

## 🔐 安全配置

### 生產環境建议

1. **修改默認密碼**
2. **啟用SSL/TLS**
3. **配置防火墙規則**
4. **定期备份數據**
5. **監控異常訪問**

## 📚 API使用示例

### Python代碼示例

```python
from tradingagents.config.database_manager import get_database_manager

# 獲取數據庫管理器
db_manager = get_database_manager()

# 檢查數據庫可用性
if db_manager.is_mongodb_available():
    print("MongoDB可用")

if db_manager.is_redis_available():
    print("Redis可用")

# 獲取數據庫客戶端
mongodb_client = db_manager.get_mongodb_client()
redis_client = db_manager.get_redis_client()

# 獲取緩存統計
stats = db_manager.get_cache_stats()
```

## 🎯 下一步計劃

1. **數據同步**: 實現多實例數據同步
2. **备份策略**: 自動备份和恢複
3. **性能監控**: 集成監控儀表板
4. **集群支持**: MongoDB和Redis集群配置
5. **數據分析**: 內置數據分析工具

---

**註意**: 本配置適用於開發和測試環境。生產環境請參考安全配置章節進行相應調整。
