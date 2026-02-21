# Docker

## 

TradingAgents-CNDockerDocker

## 

### 

1. ** **
 - 
 - 
 - 

2. ** **
 - 
 - 
 - 

3. ** **
 - 
 - 
 - 

4. ** **
 - 
 - 
 - 

## 

### Dockerfile

```dockerfile
# 
FROM python:3.10-slim

# 
RUN apt-get update && apt-get install -y \
 pandoc \
 wkhtmltopdf \
 fonts-wqy-zenhei \
 fonts-wqy-microhei \
 && rm -rf /var/lib/apt/lists/*

# Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 
COPY . /app
WORKDIR /app

# 
EXPOSE 8501
CMD ["streamlit", "run", "web/app.py"]
```

### 

#### 1: 
```bash
# python:3.10-slim
: ~200MB
: 1-3 ()
: Docker
```

#### 2: 
```bash
# 
: pandoc, wkhtmltopdf, 
: ~300MB
: 2-4
: apt
```

#### 3: Python
```bash
# Python
: requirements.txt
: ~500MB
: 2-5
: --no-cache-dir
```

#### 4: 
```bash
# 
: ~50MB
: <1
: .dockerignore
```

## 

### 1. 

```bash
# Docker
# 
COPY requirements.txt .
RUN pip install -r requirements.txt
# 
COPY . /app
```

### 2. ()

```dockerfile
# 
FROM python:3.10-slim as builder
RUN pip install --user -r requirements.txt

# 
FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
```

### 3. .dockerignore 

```bash
# .dockerignore
.git
.gitignore
README.md
Dockerfile
.dockerignore
.env
.env.*
node_modules
.pytest_cache
.coverage
.vscode
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.DS_Store
.mypy_cache
.pytest_cache
.hypothesis
```

## 

### 

```bash
# 
docker-compose build

# ()
docker-compose build --no-cache

# 
docker-compose up --build

# 
docker-compose up -d --build
```

### 

```bash
# ()
docker-compose build --parallel

# 
docker-compose build --build-arg HTTP_PROXY=http://proxy:8080

# 
docker-compose build --progress=plain

# 
docker-compose build web
```

## 

### 

```bash
# 
time docker-compose build

# 
docker history tradingagents-cn:latest

# 
docker images tradingagents-cn
```

### 

```bash
# 
docker stats

# 
docker system df

# 
docker builder prune
```

## 

### 1. 

#### 
```bash
# : 
# : 
RUN pip install -r requirements.txt --timeout 120 --retries 5
```

#### 
```bash
# : 
# : Docker
# Docker Desktop -> Settings -> Resources -> Memory (4GB+)
```

#### 
```bash
# : 
# : Dockerfile
RUN chmod +x /app/scripts/*.sh
```

### 2. 

#### 
```bash
# 
RUN pip install -r requirements.txt --timeout 120 --retries 5
```

#### 
```bash
# Dockerfile
# 
```

### 3. 

#### 
```bash
# RUN
RUN apt-get update && apt-get install -y package && rm -rf /var/lib/apt/lists/*
```

#### 
```bash
# 
FROM python:3.10-slim as builder
# ...
FROM python:3.10-slim
COPY --from=builder /app /app
```

## 

### 1. 

```bash
# 
docker-compose up --build # 

# 
docker-compose build && docker-compose up -d # 

# 
docker-compose build --no-cache && docker-compose up -d # 
```

### 2. 

```bash
# 
docker build -t tradingagents-cn:v0.1.7 .
docker build -t tradingagents-cn:latest .

# ()
docker tag tradingagents-cn:latest your-registry/tradingagents-cn:latest
docker push your-registry/tradingagents-cn:latest
```

### 3. 

```bash
# root
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# 
docker scan tradingagents-cn:latest
```

## 

### 1. 


- 
- CI/CD
- (amd64, arm64)

### 2. 

- 
- 
- 

### 3. 

- 
- 
- 

---

*: 2025-07-13* 
*: cn-0.1.7* 
*: [@breeze303](https://github.com/breeze303)*
