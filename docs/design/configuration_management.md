# TradingAgents-CN 配置管理設計

## 📋 概述

本文檔描述了TradingAgents-CN系統的配置管理機制，包括配置檔案結構、環境變數管理、動態配置更新等。

---

## 🔧 配置檔案結構

### 1. 主配置檔案 (.env)

```bash
# ===========================================
# TradingAgents-CN 主配置檔案
# ===========================================

# ===== LLM配置 =====
# Google Gemini配置
GOOGLE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# OpenAI配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ===== 數據源配置 =====
# FinnHub配置
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

### 2. 預設配置 (default_config.py)

```python
# TradingAgents-CN 預設配置
DEFAULT_CONFIG = {
    # ===== 系統配置 =====
    "system": {
        "version": "0.1.7",
        "debug": False,
        "log_level": "INFO",
        "timezone": "UTC"
    },

    # ===== LLM配置 =====
    "llm": {
        "default_model": "google",
        "models": {
            "google": {
                "model_name": "gemini-pro",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 60
            },
            "openai": {
                "model_name": "gpt-4",
                "temperature": 0.1,
                "max_tokens": 4000,
                "timeout": 60
            }
        }
    },

    # ===== 數據源配置 =====
    "data_sources": {
        "us": {
            "primary": "yfinance",
            "fallback": ["finnhub"],
            "timeout": 30,
            "retry_count": 3
        }
    },

    # ===== 緩存配置 =====
    "cache": {
        "enabled": True,
        "backend": "redis",
        "ttl": {
            "stock_data": 3600,
            "news_data": 1800,
            "analysis_result": 7200
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
        "timeout": 180,
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
            "google": {
                "temperature": 0.2,
                "max_tokens": 2000
            }
        }
    },
    "cache": {
        "backend": "memory",
        "ttl": {
            "stock_data": 300,
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
            "google": {
                "temperature": 0.1,
                "max_tokens": 4000
            }
        }
    },
    "cache": {
        "backend": "redis",
        "ttl": {
            "stock_data": 3600,
        }
    },
    "security": {
        "api_rate_limit": 100,
        "enable_auth": True,
        "session_timeout": 3600
    }
}
```

---

## 🔄 配置管理機制

### 1. 配置載入器

```python
class ConfigManager:
    def __init__(self, env: str = "development"):
        self.env = env
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        config = DEFAULT_CONFIG.copy()

        # 1. 載入環境特定配置
        env_config = self._load_env_config()
        config = self._merge_config(config, env_config)

        # 2. 載入環境變數
        env_vars = self._load_env_variables()
        config = self._merge_config(config, env_vars)

        # 3. 載入用戶自訂配置
        user_config = self._load_user_config()
        config = self._merge_config(config, user_config)

        return config

    def _load_env_variables(self) -> Dict[str, Any]:
        env_config = {}

        # LLM配置
        if os.getenv("GOOGLE_API_KEY"):
            env_config["google_api_key"] = os.getenv("GOOGLE_API_KEY")

        if os.getenv("OPENAI_API_KEY"):
            env_config["openai_api_key"] = os.getenv("OPENAI_API_KEY")

        # 數據源配置
        if os.getenv("FINNHUB_API_KEY"):
            env_config["finnhub_api_key"] = os.getenv("FINNHUB_API_KEY")

        # 數據庫配置
        if os.getenv("MONGODB_URL"):
            env_config["mongodb_url"] = os.getenv("MONGODB_URL")

        if os.getenv("REDIS_URL"):
            env_config["redis_url"] = os.getenv("REDIS_URL")

        return env_config

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value

    def validate(self) -> List[str]:
        errors = []

        # 驗證必需的API密鑰
        required_keys = [
            "google_api_key",
            "finnhub_api_key"
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
        self.watchers.append((key, callback))

    def update_config(self, key: str, value: Any) -> None:
        old_value = self.config_manager.get(key)
        self.config_manager.set(key, value)

        for watch_key, callback in self.watchers:
            if key.startswith(watch_key):
                callback(value)

        logger.info(f"配置更新: {key} = {value} (原值: {old_value})")

    def reload_from_file(self, file_path: str) -> None:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)

            for key, value in new_config.items():
                self.update_config(key, value)

            logger.info(f"從檔案重新載入配置: {file_path}")
        except Exception as e:
            logger.error(f"重新載入配置失敗: {e}")
```

---

## 🔒 安全配置

### 1. API密鑰管理

```python
class SecureConfigManager:
    def __init__(self):
        self.encryption_key = self._get_encryption_key()

    def _get_encryption_key(self) -> bytes:
        key = os.getenv("CONFIG_ENCRYPTION_KEY")
        if not key:
            key = Fernet.generate_key()
            logger.warning("未找到加密密鑰，已生成新密鑰")
        return key.encode() if isinstance(key, str) else key

    def encrypt_value(self, value: str) -> str:
        f = Fernet(self.encryption_key)
        encrypted = f.encrypt(value.encode())
        return base64.b64encode(encrypted).decode()

    def decrypt_value(self, encrypted_value: str) -> str:
        f = Fernet(self.encryption_key)
        encrypted = base64.b64decode(encrypted_value.encode())
        return f.decrypt(encrypted).decode()

    def store_api_key(self, service: str, api_key: str) -> None:
        encrypted_key = self.encrypt_value(api_key)
        self._store_encrypted_config(f"{service}_api_key", encrypted_key)

    def get_api_key(self, service: str) -> str:
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
            "google_api_key": self._validate_google_key,
            "finnhub_api_key": self._validate_finnhub_key,
            "mongodb_url": self._validate_mongodb_url,
            "redis_url": self._validate_redis_url
        }

    def validate_all(self, config: Dict[str, Any]) -> List[str]:
        errors = []

        for key, validator in self.validation_rules.items():
            value = config.get(key)
            if value:
                error = validator(value)
                if error:
                    errors.append(f"{key}: {error}")

        return errors

    def _validate_google_key(self, key: str) -> str:
        if len(key) < 20:
            return "Google API密鑰長度不足"
        return None

    def _validate_finnhub_key(self, key: str) -> str:
        if len(key) < 20:
            return "FinnHub API密鑰長度不足"
        return None

    def _validate_mongodb_url(self, url: str) -> str:
        if not url.startswith("mongodb://"):
            return "MongoDB URL應以'mongodb://'開頭"
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
        timestamp = datetime.now()

        if key not in self.usage_stats:
            self.usage_stats[key] = {
                "access_count": 0,
                "first_access": timestamp,
                "last_access": timestamp
            }

        self.usage_stats[key]["access_count"] += 1
        self.usage_stats[key]["last_access"] = timestamp

        self.access_log.append({
            "timestamp": timestamp,
            "key": key,
            "value_type": type(value).__name__
        })

    def get_usage_report(self) -> Dict[str, Any]:
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
        health_status = {
            "overall": "healthy",
            "checks": {}
        }

        api_checks = self._check_api_keys()
        health_status["checks"]["api_keys"] = api_checks

        db_checks = self._check_database_connections()
        health_status["checks"]["databases"] = db_checks

        cache_checks = self._check_cache_system()
        health_status["checks"]["cache"] = cache_checks

        if any(check["status"] == "error" for check in health_status["checks"].values()):
            health_status["overall"] = "unhealthy"
        elif any(check["status"] == "warning" for check in health_status["checks"].values()):
            health_status["overall"] = "degraded"

        return health_status
```

---

## 🚀 部署配置

### 1. Docker環境配置

```dockerfile
# Dockerfile中的配置管理
ENV ENVIRONMENT=production
ENV CONFIG_PATH=/app/config
ENV LOG_LEVEL=INFO

# 複製配置檔案
COPY config/ /app/config/
COPY .env.example /app/.env.example

# 設置配置檔案權限
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
  google-api-key: <base64-encoded-key>
  finnhub-api-key: <base64-encoded-key>
```

---

## 📋 最佳實踐

### 1. 配置管理原則
- **分離關注點**: 將配置與代碼分離
- **環境隔離**: 不同環境使用不同配置
- **安全第一**: 敏感資訊加密儲存
- **版本控制**: 配置變更可追溯
- **驗證機制**: 配置載入前進行驗證

### 2. 配置更新流程
1. **開發階段**: 在開發環境測試配置變更
2. **測試驗證**: 在測試環境驗證配置有效性
3. **生產部署**: 通過自動化流程部署到生產環境
4. **監控檢查**: 部署後監控系統健康狀態
5. **回滾準備**: 準備配置回滾方案

### 3. 故障處理
- **配置備份**: 定期備份重要配置
- **降級策略**: 配置載入失敗時的降級方案
- **告警機制**: 配置異常時及時告警
- **恢復流程**: 快速恢復配置的標準流程
