# Docker

## 

### 1. 

```bash
# 
docker-compose ps -a

# Docker
docker version

# 
docker system df
```

### 2. 

```bash
# 
docker-compose logs

# 
docker-compose logs web
docker-compose logs mongodb
docker-compose logs redis

# 
docker-compose logs -f web

# 
docker-compose logs --tail=50 web
```

### 3. 

#### 
```bash
# Windows
netstat -an | findstr :8501
netstat -an | findstr :27017
netstat -an | findstr :6379

# 
taskkill /PID <ID> /F
```

#### 
```bash
# 
docker volume ls | findstr tradingagents

# 
docker volume rm tradingagents_mongodb_data
docker volume rm tradingagents_redis_data

# 
docker volume create tradingagents_mongodb_data
docker volume create tradingagents_redis_data
```

#### 
```bash
# 
docker network ls | findstr tradingagents

# 
docker network rm tradingagents-network

# 
docker network create tradingagents-network
```

#### 
```bash
# 
docker images | findstr tradingagents

# 
docker-compose build --no-cache

# 
docker rmi tradingagents-cn:latest
docker-compose up -d --build
```

### 4. 

```bash
# .env
ls .env

# 
docker-compose config
```

### 5. 

```bash
# Docker
docker system df

# 
docker system prune -f

# 
docker system prune -a -f
```

## 

### Web (FastAPI)
```bash
# Web
docker-compose logs web

# 
docker-compose exec web bash

# Python
docker-compose exec web python --version
docker-compose exec web pip list
```

### MongoDB
```bash
# MongoDB
docker-compose logs mongodb

# MongoDB
docker-compose exec mongodb mongo -u admin -p <your-password>

# 
docker-compose exec mongodb mongo --eval "db.adminCommand('ping')"
```

### Redis
```bash
# Redis
docker-compose logs redis

# Redis
docker-compose exec redis redis-cli -a <your-password>

# Redis
docker-compose exec redis redis-cli -a <your-password> ping
```

## 

### 
```bash
# 
docker-compose down

# 
docker-compose down -v --remove-orphans

# 
docker system prune -f

# 
docker-compose up -d --build
```

### 
```bash
# 
docker-compose down

# 
docker-compose up -d
```

## 

### 

1. ****: `bind: address already in use`
2. ****: `permission denied`
3. ****: `no space left on device`
4. ****: `out of memory`
5. ****: `network not found`
6. ****: `image not found`

### 
```bash
# 
docker-compose logs | findstr ERROR

# 
docker-compose logs | findstr WARN

# 
docker-compose logs --since="2025-01-01T00:00:00"
```

## 

1. ****: `docker system prune -f`
2. ****: `docker system df`
3. ****: 
4. ****: 
5. ****: 

## 



1. 
2. 
3. 
4. docker-compose.yml