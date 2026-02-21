// MongoDB初始化腳本
// 建立TradingAgents資料庫和初始集合

// 切換到tradingagents資料庫
db = db.getSiblingDB('tradingagents');

// 建立股票資料集合
db.createCollection('stock_data');

// 建立股票資料索引
db.stock_data.createIndex({ "symbol": 1, "market_type": 1 });
db.stock_data.createIndex({ "created_at": -1 });
db.stock_data.createIndex({ "updated_at": -1 });

print('股票資料集合和索引建立完成');

// 建立分析結果集合
db.createCollection('analysis_results');

// 建立分析結果索引
db.analysis_results.createIndex({ "symbol": 1, "analysis_type": 1 });
db.analysis_results.createIndex({ "created_at": -1 });
db.analysis_results.createIndex({ "symbol": 1, "created_at": -1 });

print('分析結果集合和索引建立完成');

// 建立使用者會話集合
db.createCollection('user_sessions');

// 建立使用者會話索引
db.user_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.user_sessions.createIndex({ "created_at": -1 });
db.user_sessions.createIndex({ "last_activity": -1 });

print('使用者會話集合和索引建立完成');

// 建立配置集合
db.createCollection('configurations');

// 建立配置索引
db.configurations.createIndex({ "config_type": 1, "config_name": 1 }, { unique: true });
db.configurations.createIndex({ "updated_at": -1 });

print('配置集合和索引建立完成');

// 插入初始配置資料
var currentTime = new Date();

// 快取TTL配置
db.configurations.insertOne({
    "config_type": "cache",
    "config_name": "ttl_settings",
    "config_value": {
        "us_stock_data": 7200,      // 美股資料2小時
        "us_news": 21600,           // 美股新聞6小時
        "us_fundamentals": 86400    // 美股基本面24小時
    },
    "description": "快取TTL配置",
    "created_at": currentTime,
    "updated_at": currentTime
});

// 預設LLM模型配置
db.configurations.insertOne({
    "config_type": "llm",
    "config_name": "default_models",
    "config_value": {
        "default_provider": "openai",
        "models": {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-sonnet-4"
        }
    },
    "description": "預設LLM模型配置",
    "created_at": currentTime,
    "updated_at": currentTime
});

// 系統設定配置
db.configurations.insertOne({
    "config_type": "system",
    "config_name": "general_settings",
    "config_value": {
        "version": "0.1.2",
        "initialized_at": currentTime,
        "features": {
            "cache_enabled": true,
            "mongodb_enabled": true,
            "redis_enabled": true,
            "web_interface": true
        }
    },
    "description": "系統通用設定",
    "created_at": currentTime,
    "updated_at": currentTime
});

print('初始配置資料插入完成');

// 建立範例股票資料
db.stock_data.insertOne({
    "symbol": "AAPL",
    "market_type": "us",
    "data": {
        "company_name": "Apple Inc.",
        "sector": "Technology",
        "last_price": 150.00,
        "currency": "USD"
    },
    "created_at": currentTime,
    "updated_at": currentTime
});

print('範例股票資料插入完成');

// 顯示統計資訊
print('資料庫初始化統計:');
print('  - 股票資料: ' + db.stock_data.countDocuments({}) + ' 筆記錄');
print('  - 分析結果: ' + db.analysis_results.countDocuments({}) + ' 筆記錄');
print('  - 使用者會話: ' + db.user_sessions.countDocuments({}) + ' 筆記錄');
print('  - 配置項: ' + db.configurations.countDocuments({}) + ' 筆記錄');

print('TradingAgents MongoDB資料庫初始化完成!');
