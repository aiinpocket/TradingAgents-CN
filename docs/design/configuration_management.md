# TradingAgents-CN 配置管理設計

## 📋 概述

本文档描述了TradingAgents-CN系統的配置管理機制，包括配置文件結構、環境變量管理、動態配置更新等。

---

## 🔧 配置文件結構

### 1. 主配置文件 (.env)

```bash
# ===========================================
# TradingAgents-CN 主配置文件
# ===========================================

# ===== LLM配置 =====
# DeepSeek配置
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 阿里百炼配置
DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI配置 (可選)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Gemini配置 (可選)
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ===== 數據源配置 =====
# Tushare配置
TUSHARE_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# FinnHub配置 (可選)
FINNHUB_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ===== 數據庫配置 =====
# MongoDB配置
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=tradingagents

# Redis配置
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# ===== 系統配置 =====
# 日誌級別
LOG_LEVEL=INFO

# 緩存配置
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# 並發配置
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30

# ===== Web界面配置 =====
# Streamlit配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 報告導出配置
EXPORT_FORMATS=markdown,docx,pdf
MAX_EXPORT_SIZE=50MB
```

### 2. 默認配置 (default_config.py)

```python
# TradingAgents-CN 默認配置
DEFAULT_CONFIG = {
    # ===== 系統配置 =====
    "system": {
        "version": "0.1.7",
        "debug": False,
        "log_level": "INFO",
        "timezone": "Asia/Shanghai"
    },
    
    # ===== LLM配置 =====
    "llm": {
        "default_model": "deepseek",
        "models": {
            "deepseek": {
                "model_name": "deepseek-chat",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 60
            },
            "qwen": {
                "model_name": "qwen-plus-latest",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 60
            },
            "gemini": {
                "model_name": "gemini-pro",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 60
            }
        }
    },
    
    # ===== 數據源配置 =====
    "data_sources": {
        "china": {
            "primary": "akshare",
            "fallback": ["tushare", "baostock"],
            "timeout": 30,
            "retry_count": 3
        },
        "us": {
            "primary": "yfinance",
            "fallback": ["finnhub"],
            "timeout": 30,
            "retry_count": 3
        },
        "hk": {
            "primary": "akshare",
            "fallback": ["yfinance"],
            "timeout": 30,
            "retry_count": 3
        }
    },
    
    # ===== 緩存配置 =====
    "cache": {
        "enabled": True,
        "backend": "redis",  # redis, memory, file
        "ttl": {
            "stock_data": 3600,      # 1小時
            "news_data": 1800,       # 30分鐘
            "analysis_result": 7200  # 2小時
        },
        "max_size": {
            "memory": 1000,
            "file": 10000
        }
    },
    
    # ===== 分析師配置 =====
    "analysts": {
        "enabled": ["fundamentals", "market", "news", "social"],
        "parallel_execution": True,
        "timeout": 180,  # 3分鐘
        "retry_count": 2
    },
    
    # ===== 風險管理配置 =====
    "risk_management": {
        "enabled": True,
        "risk_levels": ["aggressive", "conservative", "neutral"],
        "max_risk_score": 1.0,
        "default_risk_tolerance": 0.5
    },
    
    # ===== Web界面配置 =====
    "web": {
        "port": 8501,
        "host": "0.0.0.0",
        "theme": "light",
        "sidebar_width": 300,
        "max_upload_size": "50MB"
    },
    
    # ===== 導出配置 =====
    "export": {
        "formats": ["markdown", "docx", "pdf"],
        "default_format": "markdown",
        "include_charts": True,
        "watermark": True
    }
}
```

### 3. 環境特定配置

#### 開發環境 (config/development.py)
```python
DEVELOPMENT_CONFIG = {
    "system": {
        "debug": True,
        "log_level": "DEBUG"
    },
    "llm": {
        "models": {
            "deepseek": {
                "temperature": 0.2,  # 開發環境允許更多創造性
                "max_tokens": 2000   # 减少token使用
            }
        }
    },
    "cache": {
        "backend": "memory",  # 開發環境使用內存緩存
        "ttl": {
            "stock_data": 300,  # 5分鐘，便於測試
        }
    }
}
```

#### 生產環境 (config/production.py)
```python
PRODUCTION_CONFIG = {
    "system": {
        "debug": False,
        "log_level": "INFO"
    },
    "llm": {
        "models": {
            "deepseek": {
                "temperature": 0.1,  # 生產環境更保守
                "max_tokens": 4000
            }
        }
    },
    "cache": {
        "backend": "redis",   # 生產環境使用Redis
        "ttl": {
            "stock_data": 3600,  # 1小時
        }
    },
    "security": {
        "api_rate_limit": 100,  # 每分鐘100次請求
        "enable_auth": True,
        "session_timeout": 3600
    }
}
```

---

## 🔄 配置管理機制

### 1. 配置加載器

```python
class ConfigManager:
    def __init__(self, env: str = "development"):
        self.env = env
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加載配置的優先級顺序"""
        config = DEFAULT_CONFIG.copy()
        
        # 1. 加載環境特定配置
        env_config = self._load_env_config()
        config = self._merge_config(config, env_config)
        
        # 2. 加載環境變量
        env_vars = self._load_env_variables()
        config = self._merge_config(config, env_vars)
        
        # 3. 加載用戶自定義配置
        user_config = self._load_user_config()
        config = self._merge_config(config, user_config)
        
        return config
    
    def _load_env_variables(self) -> Dict[str, Any]:
        """從環境變量加載配置"""
        env_config = {}
        
        # LLM配置
        if os.getenv("DEEPSEEK_API_KEY"):
            env_config["deepseek_api_key"] = os.getenv("DEEPSEEK_API_KEY")
        
        if os.getenv("DASHSCOPE_API_KEY"):
            env_config["dashscope_api_key"] = os.getenv("DASHSCOPE_API_KEY")
        
        # 數據源配置
        if os.getenv("TUSHARE_TOKEN"):
            env_config["tushare_token"] = os.getenv("TUSHARE_TOKEN")
        
        # 數據庫配置
        if os.getenv("MONGODB_URL"):
            env_config["mongodb_url"] = os.getenv("MONGODB_URL")
        
        if os.getenv("REDIS_URL"):
            env_config["redis_url"] = os.getenv("REDIS_URL")
        
        return env_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值，支持點號分隔的嵌套键"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """設置配置值"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def validate(self) -> List[str]:
        """驗證配置的有效性"""
        errors = []
        
        # 驗證必需的API密鑰
        required_keys = [
            "deepseek_api_key",
            "dashscope_api_key", 
            "tushare_token"
        ]
        
        for key in required_keys:
            if not self.get(key):
                errors.append(f"缺少必需的配置: {key}")
        
        # 驗證數據庫連接
        mongodb_url = self.get("mongodb_url")
        if mongodb_url and not self._validate_mongodb_url(mongodb_url):
            errors.append("MongoDB連接URL格式錯誤")
        
        return errors
```

### 2. 動態配置更新

```python
class DynamicConfigManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.watchers = []
    
    def watch(self, key: str, callback: Callable[[Any], None]) -> None:
        """監聽配置變化"""
        self.watchers.append((key, callback))
    
    def update_config(self, key: str, value: Any) -> None:
        """更新配置並通知監聽者"""
        old_value = self.config_manager.get(key)
        self.config_manager.set(key, value)
        
        # 通知監聽者
        for watch_key, callback in self.watchers:
            if key.startswith(watch_key):
                callback(value)
        
        # 記錄配置變更
        logger.info(f"配置更新: {key} = {value} (原值: {old_value})")
    
    def reload_from_file(self, file_path: str) -> None:
        """從文件重新加載配置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)
            
            for key, value in new_config.items():
                self.update_config(key, value)
                
            logger.info(f"從文件重新加載配置: {file_path}")
        except Exception as e:
            logger.error(f"重新加載配置失败: {e}")
```

---

## 🔒 安全配置

### 1. API密鑰管理

```python
class SecureConfigManager:
    def __init__(self):
        self.encryption_key = self._get_encryption_key()
    
    def _get_encryption_key(self) -> bytes:
        """獲取加密密鑰"""
        key = os.getenv("CONFIG_ENCRYPTION_KEY")
        if not key:
            # 生成新的加密密鑰
            key = Fernet.generate_key()
            logger.warning("未找到加密密鑰，已生成新密鑰")
        return key.encode() if isinstance(key, str) else key
    
    def encrypt_value(self, value: str) -> str:
        """加密配置值"""
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """解密配置值"""
        f = Fernet(self.encryption_key)
        encrypted = base64.b64decode(encrypted_value.encode())
        return f.decrypt(encrypted).decode()
    
    def store_api_key(self, service: str, api_key: str) -> None:
        """安全存储API密鑰"""
        encrypted_key = self.encrypt_value(api_key)
        # 存储到安全的配置存储中
        self._store_encrypted_config(f"{service}_api_key", encrypted_key)
    
    def get_api_key(self, service: str) -> str:
        """獲取API密鑰"""
        encrypted_key = self._get_encrypted_config(f"{service}_api_key")
        if encrypted_key:
            return self.decrypt_value(encrypted_key)
        return None
```

### 2. 配置驗證

```python
class ConfigValidator:
    def __init__(self):
        self.validation_rules = {
            "deepseek_api_key": self._validate_deepseek_key,
            "tushare_token": self._validate_tushare_token,
            "mongodb_url": self._validate_mongodb_url,
            "redis_url": self._validate_redis_url
        }
    
    def validate_all(self, config: Dict[str, Any]) -> List[str]:
        """驗證所有配置"""
        errors = []
        
        for key, validator in self.validation_rules.items():
            value = config.get(key)
            if value:
                error = validator(value)
                if error:
                    errors.append(f"{key}: {error}")
        
        return errors
    
    def _validate_deepseek_key(self, key: str) -> str:
        """驗證DeepSeek API密鑰格式"""
        if not key.startswith("sk-"):
            return "DeepSeek API密鑰應以'sk-'開头"
        if len(key) < 20:
            return "DeepSeek API密鑰長度不足"
        return None
    
    def _validate_tushare_token(self, token: str) -> str:
        """驗證Tushare Token格式"""
        if len(token) != 32:
            return "Tushare Token應為32位字符"
        return None
    
    def _validate_mongodb_url(self, url: str) -> str:
        """驗證MongoDB連接URL"""
        if not url.startswith("mongodb://"):
            return "MongoDB URL應以'mongodb://'開头"
        return None
```

---

## 📊 配置監控

### 1. 配置使用統計

```python
class ConfigMonitor:
    def __init__(self):
        self.usage_stats = {}
        self.access_log = []
    
    def track_access(self, key: str, value: Any) -> None:
        """跟蹤配置訪問"""
        timestamp = datetime.now()
        
        # 更新使用統計
        if key not in self.usage_stats:
            self.usage_stats[key] = {
                "access_count": 0,
                "first_access": timestamp,
                "last_access": timestamp
            }
        
        self.usage_stats[key]["access_count"] += 1
        self.usage_stats[key]["last_access"] = timestamp
        
        # 記錄訪問日誌
        self.access_log.append({
            "timestamp": timestamp,
            "key": key,
            "value_type": type(value).__name__
        })
    
    def get_usage_report(self) -> Dict[str, Any]:
        """生成配置使用報告"""
        return {
            "total_configs": len(self.usage_stats),
            "most_accessed": max(
                self.usage_stats.items(),
                key=lambda x: x[1]["access_count"]
            )[0] if self.usage_stats else None,
            "usage_stats": self.usage_stats
        }
```

### 2. 配置健康檢查

```python
class ConfigHealthChecker:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
    
    def check_health(self) -> Dict[str, Any]:
        """檢查配置健康狀態"""
        health_status = {
            "overall": "healthy",
            "checks": {}
        }
        
        # 檢查API密鑰有效性
        api_checks = self._check_api_keys()
        health_status["checks"]["api_keys"] = api_checks
        
        # 檢查數據庫連接
        db_checks = self._check_database_connections()
        health_status["checks"]["databases"] = db_checks
        
        # 檢查緩存系統
        cache_checks = self._check_cache_system()
        health_status["checks"]["cache"] = cache_checks
        
        # 確定整體健康狀態
        if any(check["status"] == "error" for check in health_status["checks"].values()):
            health_status["overall"] = "unhealthy"
        elif any(check["status"] == "warning" for check in health_status["checks"].values()):
            health_status["overall"] = "degraded"
        
        return health_status
    
    def _check_api_keys(self) -> Dict[str, Any]:
        """檢查API密鑰狀態"""
        # 實現API密鑰有效性檢查
        pass
    
    def _check_database_connections(self) -> Dict[str, Any]:
        """檢查數據庫連接狀態"""
        # 實現數據庫連接檢查
        pass
```

---

## 🚀 部署配置

### 1. Docker環境配置

```dockerfile
# Dockerfile中的配置管理
ENV ENVIRONMENT=production
ENV CONFIG_PATH=/app/config
ENV LOG_LEVEL=INFO

# 複制配置文件
COPY config/ /app/config/
COPY .env.example /app/.env.example

# 設置配置文件權限
RUN chmod 600 /app/config/*
```

### 2. Kubernetes配置

```yaml
# ConfigMap for application configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: tradingagents-config
data:
  app.yaml: |
    system:
      log_level: INFO
      debug: false
    cache:
      backend: redis
      ttl:
        stock_data: 3600

---
# Secret for sensitive configuration
apiVersion: v1
kind: Secret
metadata:
  name: tradingagents-secrets
type: Opaque
data:
  deepseek-api-key: <base64-encoded-key>
  tushare-token: <base64-encoded-token>
```

---

## 📋 最佳實踐

### 1. 配置管理原則
- **分離關註點**: 将配置与代碼分離
- **環境隔離**: 不同環境使用不同配置
- **安全第一**: 敏感信息加密存储
- **版本控制**: 配置變更可追溯
- **驗證機制**: 配置加載前進行驗證

### 2. 配置更新流程
1. **開發階段**: 在開發環境測試配置變更
2. **測試驗證**: 在測試環境驗證配置有效性
3. **生產部署**: 通過自動化流程部署到生產環境
4. **監控檢查**: 部署後監控系統健康狀態
5. **回滚準备**: 準备配置回滚方案

### 3. 故障處理
- **配置备份**: 定期备份重要配置
- **降級策略**: 配置加載失败時的降級方案
- **告警機制**: 配置異常時及時告警
- **恢複流程**: 快速恢複配置的標準流程
