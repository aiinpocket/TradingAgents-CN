# Docker

## 

TradingAgents-CN DockerWeb

## 

### 

```

 Docker Compose 

 
 TradingAgents MongoDB Redis 
 Web Database Cache 
 (Streamlit) 
 
 
 
 Volume Mongo Redis 
 Mapping Express Commander 
 () () () 
 

```

### 

1. ** TradingAgents-Web**
 - Streamlit Web
 - : 8501
 - : 

2. ** MongoDB**
 - 
 - : 27017
 - : 

3. ** Redis**
 - 
 - : 6379
 - : 

4. ** MongoDB Express**
 - 
 - : 8081
 - : 

5. ** Redis Commander**
 - 
 - : 8082
 - : 

## 

### 

- Docker 20.0+
- Docker Compose 2.0+
- 4GB+ 
- 10GB+ 

### 

```bash
# 1. 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 
cp .env.example .env
# .env API

# 3. 
docker-compose up -d --build
# Docker5-10

# 4. 
docker-compose ps
```

### Docker

****: TradingAgents-CNDocker

#### 

```bash
# 
1. (python:3.10-slim)
2. (pandoc, wkhtmltopdf, )
3. Python (requirements.txt)
4. 
5. 

# 
- : 5-10 ()
- : 1GB
- : 800MB
- : 2GB+
```

#### 

```bash
# 1. 
# 
docker-compose build --no-cache # 
docker-compose build # 

# 2. 
docker-compose up --build # 
```

### 



- ** **: http://localhost:8501
- ** **: http://localhost:8081
- ** **: http://localhost:8082

## 

### Docker Compose

```yaml
version: '3.8'

services:
 web:
 build: .
 ports:
 - "8501:8501"
 volumes:
 - .env:/app/.env
 # 
 - ./web:/app/web
 - ./tradingagents:/app/tradingagents
 depends_on:
 - mongodb
 - redis
 environment:
 - MONGODB_URL=mongodb://mongodb:27017/tradingagents
 - REDIS_URL=redis://redis:6379

 mongodb:
 image: mongo:4.4
 ports:
 - "27017:27017"
 volumes:
 - mongodb_data:/data/db
 environment:
 - MONGO_INITDB_DATABASE=tradingagents

 redis:
 image: redis:6-alpine
 ports:
 - "6379:6379"
 volumes:
 - redis_data:/data

 mongo-express:
 image: mongo-express
 ports:
 - "8081:8081"
 environment:
 - ME_CONFIG_MONGODB_SERVER=mongodb
 - ME_CONFIG_MONGODB_PORT=27017
 depends_on:
 - mongodb

 redis-commander:
 image: rediscommander/redis-commander
 ports:
 - "8082:8081"
 environment:
 - REDIS_HOSTS=local:redis:6379
 depends_on:
 - redis

volumes:
 mongodb_data:
 redis_data:
```

### 

```bash
# .env 
# LLM API
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# 
FINNHUB_API_KEY=your_finnhub_key

# 
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379

# 
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf
```

## 

### Volume



```yaml
volumes:
 - .env:/app/.env
 - ./web:/app/web # Web
 - ./tradingagents:/app/tradingagents # 
 - ./scripts:/app/scripts # 
 - ./test_conversion.py:/app/test_conversion.py # 
```

### 

```bash
# 1. 
docker-compose up -d

# 2. 
# 

# 3. 
docker logs TradingAgents-web --follow

# 4. 
docker exec -it TradingAgents-web bash

# 5. 
docker exec TradingAgents-web python test_conversion.py
```

## 

### 

```bash
# 
docker-compose ps

# 
docker logs TradingAgents-web
docker logs TradingAgents-mongodb
docker logs TradingAgents-redis

# 
docker stats
```

### 

```bash
# MongoDB
docker exec TradingAgents-mongodb mongodump --out /backup

# Redis
docker exec TradingAgents-redis redis-cli BGSAVE

# 
docker exec TradingAgents-redis redis-cli FLUSHALL
```

### 

```bash
# 
docker-compose restart web

# 
docker-compose restart

# 
docker-compose up -d --build
```

## 

### 

1. ****
 ```bash
 # 
 netstat -tulpn | grep :8501
 
 # 
 # docker-compose.yml ports 
 ```

2. ****
 ```bash
 # Docker
 # docker-compose.yml 
 deploy:
 resources:
 limits:
 memory: 4G
 ```

3. ****
 ```bash
 # 
 docker logs TradingAgents-mongodb
 
 # 
 docker exec TradingAgents-web ping mongodb
 ```

### 

1. ****
 ```yaml
 services:
 web:
 deploy:
 resources:
 limits:
 cpus: '2.0'
 memory: 4G
 reservations:
 memory: 2G
 ```

2. ****
 ```yaml
 volumes:
 mongodb_data:
 driver: local
 driver_opts:
 type: none
 o: bind
 device: /path/to/mongodb/data
 ```

## 

### 

```yaml
# 
services:
 mongodb:
 environment:
 - MONGO_INITDB_ROOT_USERNAME=admin
 - MONGO_INITDB_ROOT_PASSWORD=secure_password
 
 mongo-express:
 environment:
 - ME_CONFIG_BASICAUTH_USERNAME=admin
 - ME_CONFIG_BASICAUTH_PASSWORD=secure_password
```

### 

```yaml
networks:
 tradingagents:
 driver: bridge
 ipam:
 config:
 - subnet: 172.20.0.0/16

services:
 web:
 networks:
 - tradingagents
```

## 

### 

Docker **[@breeze303](https://github.com/breeze303)** 

- Docker Compose
- 
- 
- Volume
- 

TradingAgents-CN

---

*: 2025-07-13* 
*: cn-0.1.7* 
*: [@breeze303](https://github.com/breeze303)*
