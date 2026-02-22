# TradingAgents-CN 

## 

TradingAgents-CN

---

## 

### 1. (.env)

```bash
# ===========================================
# TradingAgents-CN 
# ===========================================

# ===== LLM =====
# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ===== =====
# FinnHub
FINNHUB_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# ===== =====
# MongoDB
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=tradingagents

# Redis
REDIS_URL=redis://localhost:6379
REDIS_DB=0

# ===== =====
# 
LOG_LEVEL=INFO

# 
CACHE_TTL=3600
CACHE_MAX_SIZE=1000

# 
MAX_CONCURRENT_REQUESTS=10
REQUEST_TIMEOUT=30

# ===== Web =====
# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# 
EXPORT_FORMATS=markdown,docx,pdf
MAX_EXPORT_SIZE=50MB
```

### 2. (default_config.py)

```python
# TradingAgents-CN 
DEFAULT_CONFIG = {
 # ===== =====
 "system": {
 "version": "0.1.7",
 "debug": False,
 "log_level": "INFO",
 "timezone": "UTC"
 },

 # ===== LLM =====
 "llm": {
 "default_model": "openai",
 "models": {
 "openai": {
 "model_name": "gpt-4o",
 "temperature": 0.1,
 "max_tokens": 4000,
 "timeout": 60
 },
 "anthropic": {
 "model_name": "claude-sonnet-4",
 "temperature": 0.1,
 "max_tokens": 4000,
 "timeout": 60
 }
 }
 },

 # ===== =====
 "data_sources": {
 "us": {
 "primary": "yfinance",
 "fallback": ["finnhub"],
 "timeout": 30,
 "retry_count": 3
 }
 },

 # ===== =====
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

 # ===== =====
 "analysts": {
 "enabled": ["fundamentals", "market", "news", "social"],
 "parallel_execution": True,
 "timeout": 180,
 "retry_count": 2
 },

 # ===== =====
 "risk_management": {
 "enabled": True,
 "risk_levels": ["aggressive", "conservative", "neutral"],
 "max_risk_score": 1.0,
 "default_risk_tolerance": 0.5
 },

 # ===== Web =====
 "web": {
 "port": 8501,
 "host": "0.0.0.0",
 "theme": "light",
 "sidebar_width": 300,
 "max_upload_size": "50MB"
 },

 # ===== =====
 "export": {
 "formats": ["markdown", "docx", "pdf"],
 "default_format": "markdown",
 "include_charts": True,
 "watermark": True
 }
}
```

### 3. 

#### (config/development.py)
```python
DEVELOPMENT_CONFIG = {
 "system": {
 "debug": True,
 "log_level": "DEBUG"
 },
 "llm": {
 "models": {
 "openai": {
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

#### (config/production.py)
```python
PRODUCTION_CONFIG = {
 "system": {
 "debug": False,
 "log_level": "INFO"
 },
 "llm": {
 "models": {
 "openai": {
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

## 

### 1. 

```python
class ConfigManager:
 def __init__(self, env: str = "development"):
 self.env = env
 self.config = self._load_config()

 def _load_config(self) -> Dict[str, Any]:
 config = DEFAULT_CONFIG.copy()

 # 1. 
 env_config = self._load_env_config()
 config = self._merge_config(config, env_config)

 # 2. 
 env_vars = self._load_env_variables()
 config = self._merge_config(config, env_vars)

 # 3. 
 user_config = self._load_user_config()
 config = self._merge_config(config, user_config)

 return config

 def _load_env_variables(self) -> Dict[str, Any]:
 env_config = {}

 # LLM
 if os.getenv("OPENAI_API_KEY"):
 env_config["openai_api_key"] = os.getenv("OPENAI_API_KEY")

 if os.getenv("ANTHROPIC_API_KEY"):
 env_config["anthropic_api_key"] = os.getenv("ANTHROPIC_API_KEY")

 # 
 if os.getenv("FINNHUB_API_KEY"):
 env_config["finnhub_api_key"] = os.getenv("FINNHUB_API_KEY")

 # 
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

 # API
 required_keys = [
 "openai_api_key",
 "finnhub_api_key"
 ]

 for key in required_keys:
 if not self.get(key):
 errors.append(f": {key}")

 # 
 mongodb_url = self.get("mongodb_url")
 if mongodb_url and not self._validate_mongodb_url(mongodb_url):
 errors.append("MongoDBURL")

 return errors
```

### 2. 

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

 logger.info(f": {key} = {value} (: {old_value})")

 def reload_from_file(self, file_path: str) -> None:
 try:
 with open(file_path, 'r', encoding='utf-8') as f:
 new_config = json.load(f)

 for key, value in new_config.items():
 self.update_config(key, value)

 logger.info(f": {file_path}")
 except Exception as e:
 logger.error(f": {e}")
```

---

## 

### 1. API

```python
class SecureConfigManager:
 def __init__(self):
 self.encryption_key = self._get_encryption_key()

 def _get_encryption_key(self) -> bytes:
 key = os.getenv("CONFIG_ENCRYPTION_KEY")
 if not key:
 key = Fernet.generate_key()
 logger.warning("")
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

### 2. 

```python
class ConfigValidator:
 def __init__(self):
 self.validation_rules = {
 "openai_api_key": self._validate_openai_key,
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

 def _validate_openai_key(self, key: str) -> str:
 if len(key) < 20:
 return "OpenAI API"
 return None

 def _validate_finnhub_key(self, key: str) -> str:
 if len(key) < 20:
 return "FinnHub API"
 return None

 def _validate_mongodb_url(self, url: str) -> str:
 if not url.startswith("mongodb://"):
 return "MongoDB URL'mongodb://'"
 return None
```

---

## 

### 1. 

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

### 2. 

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

## 

### 1. Docker

```dockerfile
# Dockerfile
ENV ENVIRONMENT=production
ENV CONFIG_PATH=/app/config
ENV LOG_LEVEL=INFO

# 
COPY config/ /app/config/
COPY .env.example /app/.env.example

# 
RUN chmod 600 /app/config/*
```

### 2. Kubernetes

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
 openai-api-key: <base64-encoded-key>
 anthropic-api-key: <base64-encoded-key>
 finnhub-api-key: <base64-encoded-key>
```

---

## 

### 1. 
- ****: 
- ****: 
- ****: 
- ****: 
- ****: 

### 2. 
1. ****: 
2. ****: 
3. ****: 
4. ****: 
5. ****: 

### 3. 
- ****: 
- ****: 
- ****: 
- ****: 
