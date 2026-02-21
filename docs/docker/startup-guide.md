# Docker

## 

### 

```bash
# - 
docker-compose up -d

# - 
docker-compose up -d --build
```

### 



#### Windows
```powershell
# 1
powershell -ExecutionPolicy Bypass -File scripts\smart_start.ps1

# 2PowerShell
.\scripts\smart_start.ps1
```

#### Linux/Mac
```bash
# 
chmod +x scripts/smart_start.sh
./scripts/smart_start.sh

# 
chmod +x scripts/smart_start.sh && ./scripts/smart_start.sh
```

## 

### `--build` 

| | `--build` | |
|------|-------------------|------|
| | | |
| | | |
| | | requirements.txt |
| Dockerfile | | |
| | | |
| | | |

### 

1. ****
 - → `docker-compose up -d --build`
 
2. ****
 - → `docker-compose up -d --build`
 - → `docker-compose up -d`

## 

### 

1. ****
 ```bash
 # 
 netstat -ano | findstr :8501 # Windows
 lsof -i :8501 # Linux/Mac
 ```

2. ****
 ```bash
 # 
 docker-compose down
 docker system prune -f
 docker-compose up -d --build
 ```

3. ****
 ```bash
 # 
 docker-compose logs web
 docker-compose logs mongodb
 docker-compose logs redis
 ```

### 



```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts\debug_docker.ps1

# Linux/Mac
chmod +x scripts/debug_docker.sh && ./scripts/debug_docker.sh
```

## 

| | | | |
|----------|-------------|-------------|----------|
| `docker-compose up -d --build` | ~3-5 | ~3-5 | |
| `docker-compose up -d` | ~3-5 | ~10-30 | |
| | ~3-5 | ~10-30 | |

## 

1. ****
2. **** `--build`
3. **CI/CD** `--build` 
4. ****