// MongoDB初始化腳本
// 建立TradingAgents資料庫和使用者

// 切換到admin資料庫
db = db.getSiblingDB('admin');

// 建立應用使用者（密碼從環境變數 MONGO_INITDB_ROOT_PASSWORD 讀取）
// Docker Compose 中已透過環境變數設定 root 密碼
// 此腳本只負責建立資料庫結構，不額外建立應用使用者
// 應用程式使用 admin 帳戶連線（由 MONGODB_PASSWORD 環境變數控制）

// 切換到應用資料庫
db = db.getSiblingDB('tradingagents');

// 建立集合和索引
db.createCollection('stock_data');
db.createCollection('analysis_reports');
db.createCollection('user_sessions');
db.createCollection('system_logs');

// 為股票資料建立索引
db.stock_data.createIndex({ "symbol": 1, "date": 1 });
db.stock_data.createIndex({ "market": 1 });
db.stock_data.createIndex({ "created_at": 1 });

// 為分析報告建立索引
db.analysis_reports.createIndex({ "symbol": 1, "analysis_type": 1 });
db.analysis_reports.createIndex({ "created_at": 1 });

// 為使用者會話建立索引
db.user_sessions.createIndex({ "session_id": 1 });
db.user_sessions.createIndex({ "created_at": 1 }, { expireAfterSeconds: 86400 }); // 24小時過期

// 為系統日誌建立索引
db.system_logs.createIndex({ "level": 1, "timestamp": 1 });
db.system_logs.createIndex({ "timestamp": 1 }, { expireAfterSeconds: 604800 }); // 7天過期

print('TradingAgents資料庫初始化完成');
