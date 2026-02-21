// MongoDB初始化腳本
// 建立TradingAgents資料庫和使用者

// 切換到admin資料庫
db = db.getSiblingDB('admin');

// 建立應用使用者
db.createUser({
  user: 'tradingagents',
  pwd: 'tradingagents123',
  roles: [
    {
      role: 'readWrite',
      db: 'tradingagents'
    }
  ]
});

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
