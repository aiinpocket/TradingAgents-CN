# 

## 

TradingAgents API

## 

### 

```mermaid
graph TB
 subgraph ""
 AGENT1[]
 AGENT2[]
 AGENT3[]
 end
 
 subgraph ""
 L1[L1: <br/>]
 L2[L2: <br/>]
 L3[L3: Redis<br/>]
 L4[L4: <br/>]
 end
 
 subgraph ""
 API1[FinnHub API]
 API2[Yahoo Finance]
 API3[Reddit API]
 API4[Google News]
 end
 
 AGENT1 --> L1
 AGENT2 --> L1
 AGENT3 --> L1
 
 L1 --> L2
 L2 --> L3
 L3 --> L4
 
 L4 --> API1
 L4 --> API2
 L4 --> API3
 L4 --> API4
```

## 1. 

### 
```python
class CacheManager:
 """ - """
 
 def __init__(self, config: Dict):
 self.config = config
 self.memory_cache = MemoryCache(config.get("memory_cache", {}))
 self.file_cache = FileCache(config.get("file_cache", {}))
 self.redis_cache = RedisCache(config.get("redis_cache", {})) if config.get("redis_enabled") else None
 self.db_cache = DatabaseCache(config.get("db_cache", {})) if config.get("db_enabled") else None
 
 # 
 self.cache_strategies = self._load_cache_strategies()
 self.ttl_config = self._load_ttl_config()
 
 def get(self, key: str, data_type: str = "default") -> Optional[Any]:
 """ - """
 
 # L1: 
 data = self.memory_cache.get(key)
 if data is not None:
 self._record_cache_hit("memory", key, data_type)
 return data
 
 # L2: 
 data = self.file_cache.get(key)
 if data is not None:
 # 
 self.memory_cache.set(key, data, self._get_ttl(data_type))
 self._record_cache_hit("file", key, data_type)
 return data
 
 # L3: Redis
 if self.redis_cache:
 data = self.redis_cache.get(key)
 if data is not None:
 # 
 self.file_cache.set(key, data, self._get_ttl(data_type))
 self.memory_cache.set(key, data, self._get_ttl(data_type))
 self._record_cache_hit("redis", key, data_type)
 return data
 
 # L4: 
 if self.db_cache:
 data = self.db_cache.get(key)
 if data is not None:
 # 
 if self.redis_cache:
 self.redis_cache.set(key, data, self._get_ttl(data_type))
 self.file_cache.set(key, data, self._get_ttl(data_type))
 self.memory_cache.set(key, data, self._get_ttl(data_type))
 self._record_cache_hit("database", key, data_type)
 return data
 
 # 
 self._record_cache_miss(key, data_type)
 return None
 
 def set(self, key: str, data: Any, data_type: str = "default", ttl: Optional[int] = None) -> None:
 """ - """
 
 if ttl is None:
 ttl = self._get_ttl(data_type)
 
 # 
 cache_strategy = self._determine_cache_strategy(data, data_type)
 
 # L1: ()
 if cache_strategy["memory"]:
 self.memory_cache.set(key, data, ttl)
 
 # L2: ()
 if cache_strategy["file"]:
 self.file_cache.set(key, data, ttl)
 
 # L3: Redis ()
 if cache_strategy["redis"] and self.redis_cache:
 self.redis_cache.set(key, data, ttl)
 
 # L4: ()
 if cache_strategy["database"] and self.db_cache:
 self.db_cache.set(key, data, ttl)
 
 def _determine_cache_strategy(self, data: Any, data_type: str) -> Dict[str, bool]:
 """"""
 
 data_size = self._estimate_data_size(data)
 data_importance = self._assess_data_importance(data_type)
 
 strategy = {
 "memory": data_size < 1024 * 1024, # 1MB
 "file": data_size < 10 * 1024 * 1024, # 10MB
 "redis": data_importance >= 0.7, # 
 "database": data_importance >= 0.8 or data_type in ["fundamental_data", "company_profile"]
 }
 
 return strategy
 
 def _get_ttl(self, data_type: str) -> int:
 """TTL"""
 return self.ttl_config.get(data_type, self.ttl_config["default"])
```

## 2. (L1)

### 
```python
class MemoryCache:
 """ - """
 
 def __init__(self, config: Dict):
 self.config = config
 self.cache = {}
 self.access_times = {}
 self.max_size = config.get("max_size", 1000)
 self.cleanup_threshold = config.get("cleanup_threshold", 0.8)
 
 def get(self, key: str) -> Optional[Any]:
 """"""
 if key in self.cache:
 item = self.cache[key]
 
 # 
 if self._is_expired(item):
 del self.cache[key]
 if key in self.access_times:
 del self.access_times[key]
 return None
 
 # 
 self.access_times[key] = time.time()
 return item["data"]
 
 return None
 
 def set(self, key: str, data: Any, ttl: int) -> None:
 """"""
 
 # 
 if len(self.cache) >= self.max_size * self.cleanup_threshold:
 self._cleanup_cache()
 
 # 
 self.cache[key] = {
 "data": data,
 "timestamp": time.time(),
 "ttl": ttl
 }
 self.access_times[key] = time.time()
 
 def _cleanup_cache(self) -> None:
 """"""
 
 current_time = time.time()
 
 # 
 expired_keys = []
 for key, item in self.cache.items():
 if self._is_expired(item):
 expired_keys.append(key)
 
 for key in expired_keys:
 del self.cache[key]
 if key in self.access_times:
 del self.access_times[key]
 
 # LRU 
 if len(self.cache) >= self.max_size * self.cleanup_threshold:
 # 
 sorted_keys = sorted(self.access_times.keys(), key=lambda k: self.access_times[k])
 keys_to_remove = sorted_keys[:len(sorted_keys) // 4] # 25%
 
 for key in keys_to_remove:
 if key in self.cache:
 del self.cache[key]
 if key in self.access_times:
 del self.access_times[key]
 
 def _is_expired(self, item: Dict) -> bool:
 """"""
 return time.time() - item["timestamp"] > item["ttl"]
```

## 3. (L2)

### 
```python
class FileCache:
 """ - """
 
 def __init__(self, config: Dict):
 self.config = config
 self.cache_dir = Path(config.get("cache_dir", "./cache"))
 self.cache_dir.mkdir(parents=True, exist_ok=True)
 self.compression_enabled = config.get("compression", True)
 self.max_file_size = config.get("max_file_size", 50 * 1024 * 1024) # 50MB
 
 def get(self, key: str) -> Optional[Any]:
 """"""
 
 cache_file = self._get_cache_file_path(key)
 
 if not cache_file.exists():
 return None
 
 try:
 # 
 if self._is_file_expired(cache_file, key):
 cache_file.unlink() # 
 return None
 
 # 
 with open(cache_file, 'rb') as f:
 if self.compression_enabled:
 compressed_data = f.read()
 data = self._decompress_data(compressed_data)
 else:
 data = pickle.load(f)
 
 return data
 
 except Exception as e:
 print(f"Error reading cache file {cache_file}: {e}")
 # 
 if cache_file.exists():
 cache_file.unlink()
 return None
 
 def set(self, key: str, data: Any, ttl: int) -> None:
 """"""
 
 cache_file = self._get_cache_file_path(key)
 
 try:
 # 
 data_size = self._estimate_data_size(data)
 if data_size > self.max_file_size:
 print(f"Data too large for file cache: {data_size} bytes")
 return
 
 # 
 cache_data = {
 "data": data,
 "timestamp": time.time(),
 "ttl": ttl,
 "key": key
 }
 
 # 
 with open(cache_file, 'wb') as f:
 if self.compression_enabled:
 compressed_data = self._compress_data(cache_data)
 f.write(compressed_data)
 else:
 pickle.dump(cache_data, f)
 
 except Exception as e:
 print(f"Error writing cache file {cache_file}: {e}")
 
 def _get_cache_file_path(self, key: str) -> Path:
 """"""
 # 
 key_hash = hashlib.md5(key.encode()).hexdigest()
 return self.cache_dir / f"{key_hash}.cache"
 
 def _is_file_expired(self, cache_file: Path, key: str) -> bool:
 """"""
 try:
 with open(cache_file, 'rb') as f:
 if self.compression_enabled:
 compressed_data = f.read()
 cache_data = self._decompress_data(compressed_data)
 else:
 cache_data = pickle.load(f)
 
 return time.time() - cache_data["timestamp"] > cache_data["ttl"]
 
 except Exception:
 return True # 
 
 def _compress_data(self, data: Any) -> bytes:
 """"""
 import gzip
 pickled_data = pickle.dumps(data)
 return gzip.compress(pickled_data)
 
 def _decompress_data(self, compressed_data: bytes) -> Any:
 """"""
 import gzip
 pickled_data = gzip.decompress(compressed_data)
 return pickle.loads(pickled_data)
 
 def cleanup_expired_files(self) -> None:
 """"""
 for cache_file in self.cache_dir.glob("*.cache"):
 try:
 if self._is_file_expired(cache_file, ""):
 cache_file.unlink()
 except Exception as e:
 print(f"Error checking cache file {cache_file}: {e}")
```

## 4. Redis (L3)

### 
```python
class RedisCache:
 """Redis - """
 
 def __init__(self, config: Dict):
 self.config = config
 self.redis_client = self._initialize_redis_client()
 self.key_prefix = config.get("key_prefix", "tradingagents:")
 self.serialization_format = config.get("serialization", "pickle") # pickle, json, msgpack
 
 def _initialize_redis_client(self):
 """Redis"""
 try:
 import redis
 
 redis_config = {
 "host": self.config.get("host", "localhost"),
 "port": self.config.get("port", 6379),
 "db": self.config.get("db", 0),
 "password": self.config.get("password"),
 "socket_timeout": self.config.get("timeout", 5),
 "socket_connect_timeout": self.config.get("connect_timeout", 5),
 "retry_on_timeout": True,
 "health_check_interval": 30
 }
 
 # None
 redis_config = {k: v for k, v in redis_config.items() if v is not None}
 
 client = redis.Redis(**redis_config)
 
 # 
 client.ping()
 print("Redis connection established")
 
 return client
 
 except Exception as e:
 print(f"Failed to connect to Redis: {e}")
 return None
 
 def get(self, key: str) -> Optional[Any]:
 """Redis"""
 if not self.redis_client:
 return None
 
 try:
 full_key = self.key_prefix + key
 data = self.redis_client.get(full_key)
 
 if data is None:
 return None
 
 # 
 return self._deserialize_data(data)
 
 except Exception as e:
 print(f"Error getting data from Redis: {e}")
 return None
 
 def set(self, key: str, data: Any, ttl: int) -> None:
 """Redis"""
 if not self.redis_client:
 return
 
 try:
 full_key = self.key_prefix + key
 
 # 
 serialized_data = self._serialize_data(data)
 
 # TTL
 self.redis_client.setex(full_key, ttl, serialized_data)
 
 except Exception as e:
 print(f"Error setting data to Redis: {e}")
 
 def _serialize_data(self, data: Any) -> bytes:
 """"""
 if self.serialization_format == "pickle":
 return pickle.dumps(data)
 elif self.serialization_format == "json":
 import json
 return json.dumps(data, default=str).encode('utf-8')
 elif self.serialization_format == "msgpack":
 import msgpack
 return msgpack.packb(data, default=str)
 else:
 raise ValueError(f"Unsupported serialization format: {self.serialization_format}")
 
 def _deserialize_data(self, data: bytes) -> Any:
 """"""
 if self.serialization_format == "pickle":
 return pickle.loads(data)
 elif self.serialization_format == "json":
 import json
 return json.loads(data.decode('utf-8'))
 elif self.serialization_format == "msgpack":
 import msgpack
 return msgpack.unpackb(data, raw=False)
 else:
 raise ValueError(f"Unsupported serialization format: {self.serialization_format}")
 
 def delete(self, key: str) -> None:
 """Redis"""
 if not self.redis_client:
 return
 
 try:
 full_key = self.key_prefix + key
 self.redis_client.delete(full_key)
 except Exception as e:
 print(f"Error deleting data from Redis: {e}")
 
 def clear_expired(self) -> None:
 """RedisTTL"""
 # Redis
 pass
```

## 5. 

### TTL
```python
# TTL
TTL_CONFIG = {
 "price_data": 60, # 1 - 
 "fundamental_data": 3600, # 1 - 
 "company_profile": 86400, # 24 - 
 "news_data": 1800, # 30 - 
 "social_data": 900, # 15 - 
 "technical_indicators": 300, # 5 - 
 "market_data": 600, # 10 - 
 "historical_data": 7200, # 2 - 
 "default": 1800 # 30 - TTL
}

# 
DATA_IMPORTANCE = {
 "price_data": 0.9, # 
 "fundamental_data": 0.8, # 
 "company_profile": 0.7, # 
 "news_data": 0.6, # 
 "social_data": 0.5, # 
 "technical_indicators": 0.7, # 
 "market_data": 0.6, # 
 "historical_data": 0.8, # 
}
```

## 6. 

### 
```python
class CacheMonitor:
 """"""
 
 def __init__(self):
 self.metrics = {
 "hits": defaultdict(int),
 "misses": defaultdict(int),
 "hit_rates": defaultdict(float),
 "response_times": defaultdict(list),
 "cache_sizes": defaultdict(int)
 }
 
 def record_hit(self, cache_level: str, key: str, data_type: str, response_time: float = None):
 """"""
 self.metrics["hits"][cache_level] += 1
 if response_time:
 self.metrics["response_times"][cache_level].append(response_time)
 
 self._update_hit_rate(cache_level)
 
 def record_miss(self, key: str, data_type: str):
 """"""
 self.metrics["misses"]["total"] += 1
 self._update_hit_rate("total")
 
 def _update_hit_rate(self, cache_level: str):
 """"""
 hits = self.metrics["hits"][cache_level]
 misses = self.metrics["misses"].get(cache_level, 0)
 total = hits + misses
 
 if total > 0:
 self.metrics["hit_rates"][cache_level] = hits / total
 
 def get_performance_report(self) -> Dict:
 """"""
 return {
 "hit_rates": dict(self.metrics["hit_rates"]),
 "total_hits": sum(self.metrics["hits"].values()),
 "total_misses": sum(self.metrics["misses"].values()),
 "avg_response_times": {
 level: sum(times) / len(times) if times else 0
 for level, times in self.metrics["response_times"].items()
 },
 "cache_efficiency": self._calculate_cache_efficiency()
 }
 
 def _calculate_cache_efficiency(self) -> float:
 """"""
 total_hits = sum(self.metrics["hits"].values())
 total_requests = total_hits + sum(self.metrics["misses"].values())
 
 return total_hits / total_requests if total_requests > 0 else 0.0
```

## 7. 

### 
```python
class CacheBestPractices:
 """"""
 
 @staticmethod
 def generate_cache_key(symbol: str, data_type: str, date: str = None, **kwargs) -> str:
 """"""
 
 key_parts = [symbol.upper(), data_type]
 
 if date:
 key_parts.append(date)
 
 # 
 for k, v in sorted(kwargs.items()):
 key_parts.append(f"{k}:{v}")
 
 return ":".join(key_parts)
 
 @staticmethod
 def should_cache_data(data: Any, data_type: str) -> bool:
 """"""
 
 # 
 if not data:
 return False
 
 # 
 if isinstance(data, dict) and "error" in data:
 return False
 
 # 
 data_size = CacheBestPractices._estimate_size(data)
 if data_size > 100 * 1024 * 1024: # 100MB
 return False
 
 return True
 
 @staticmethod
 def _estimate_size(obj: Any) -> int:
 """"""
 try:
 return len(pickle.dumps(obj))
 except:
 return 0
```

TradingAgents API
