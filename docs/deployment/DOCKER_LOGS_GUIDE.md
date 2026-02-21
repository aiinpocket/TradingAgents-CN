# TradingAgents Docker 

## 

DockerTradingAgents

## 

### 1. **Docker Compose **

 `docker-compose.yml` 

```yaml
volumes:
 - ./logs:/app/logs # logs
```

### 2. ****



```yaml
environment:
 TRADINGAGENTS_LOG_LEVEL: "INFO"
 TRADINGAGENTS_LOG_DIR: "/app/logs"
 TRADINGAGENTS_LOG_FILE: "/app/logs/tradingagents.log"
 TRADINGAGENTS_LOG_MAX_SIZE: "100MB"
 TRADINGAGENTS_LOG_BACKUP_COUNT: "5"
```

### 3. **Docker **

Docker

```yaml
logging:
 driver: "json-file"
 options:
 max-size: "100m"
 max-file: "3"
```

## 

### **1: ()**

#### Linux/macOS:
```bash
# 
chmod +x start_docker.sh

# Docker
./start_docker.sh
```

#### Windows PowerShell:
```powershell
# Docker
.\start_docker.ps1
```

### **2: **

```bash
# 1. logs
python ensure_logs_dir.py

# 2. Docker
docker-compose up -d

# 3. 
docker-compose ps
```

## 

### ****
- ****: `./logs/` 
- ****: `logs/tradingagents.log`
- ****: `logs/tradingagents_error.log` ()
- ****: `logs/tradingagents.log.1`, `logs/tradingagents.log.2` 

### **Docker **
- ****: `docker-compose logs web`
- ****: `docker-compose logs -f web`

## 

### **1. **
```bash
# 
python view_logs.py
```


- 
- 
- 
- 
- Docker

### **2. **

#### Linux/macOS:
```bash
# 
tail -f logs/tradingagents.log

# 100
tail -100 logs/tradingagents.log

# 
grep -i error logs/tradingagents.log
```

#### Windows PowerShell:
```powershell
# 
Get-Content logs\tradingagents.log -Wait

# 50
Get-Content logs\tradingagents.log -Tail 50

# 
Select-String -Path logs\tradingagents.log -Pattern "error" -CaseSensitive:$false
```

### **3. Docker **
```bash
# 
docker logs TradingAgents-web

# 
docker logs -f TradingAgents-web

# 1
docker logs --since 1h TradingAgents-web

# 100
docker logs --tail 100 TradingAgents-web
```

## 

### ****



1. ****: `logs/tradingagents.log`
2. ****: `logs/tradingagents_error.log` ()
3. **Docker**: 
 ```bash
 docker logs TradingAgents-web > docker_logs.txt 2>&1
 ```

### ****

#### Linux/macOS:
```bash
# 
tar -czf tradingagents_logs_$(date +%Y%m%d_%H%M%S).tar.gz logs/ docker_logs.txt
```

#### Windows PowerShell:
```powershell
# 
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path logs\*,docker_logs.txt -DestinationPath "tradingagents_logs_$timestamp.zip"
```

## 

### **1: logs**

****: stdout

****:
1. Docker: `docker-compose logs web`
2. 
3. : `docker-compose restart web`

### **2: **

**Linux/macOS**:
```bash
# 
sudo chown -R $USER:$USER logs/
chmod 755 logs/
```

**Windows**: 

### **3: **

****: 100MB
****:
```bash
# 
cp logs/tradingagents.log logs/tradingagents.log.backup
> logs/tradingagents.log
```

### **4: **

****:
1. Docker: `docker info`
2. : `netstat -tlnp | grep 8501`
3. : `docker-compose logs web`
4. : `.env` 

## 

- **DEBUG**: 
- **INFO**: 
- **WARNING**: 
- **ERROR**: 
- **CRITICAL**: 

## 

### **1. **
```bash
# 
grep -i error logs/tradingagents.log | tail -20
```

### **2. **
```bash
# 
ls -lh logs/
```

### **3. **
```bash
# 
cp logs/tradingagents.log backups/tradingagents_$(date +%Y%m%d).log
```

### **4. **
```bash
# 
tail -f logs/tradingagents.log | grep -i "error\|warning"
```

## 



1. ****: 
2. ****: 
3. ****: Docker
4. ****: 

---

**TradingAgents** 