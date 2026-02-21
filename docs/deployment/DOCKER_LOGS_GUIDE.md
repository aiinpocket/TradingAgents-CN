# 🐳 TradingAgents Docker 日誌管理指南

## 📋 概述

本指南介紹如何在Docker環境中管理和獲取TradingAgents的日誌文件。

## 🔧 改進內容

### 1. **Docker Compose 配置優化**

在 `docker-compose.yml` 中添加了日誌目錄映射：

```yaml
volumes:
  - ./logs:/app/logs  # 將容器內日誌映射到本地logs目錄
```

### 2. **環境變量配置**

添加了詳細的日誌配置環境變量：

```yaml
environment:
  TRADINGAGENTS_LOG_LEVEL: "INFO"
  TRADINGAGENTS_LOG_DIR: "/app/logs"
  TRADINGAGENTS_LOG_FILE: "/app/logs/tradingagents.log"
  TRADINGAGENTS_LOG_MAX_SIZE: "100MB"
  TRADINGAGENTS_LOG_BACKUP_COUNT: "5"
```

### 3. **Docker 日誌配置**

添加了Docker級別的日誌輪轉：

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "3"
```

## 🚀 使用方法

### **方法1: 使用啟動腳本 (推薦)**

#### Linux/macOS:
```bash
# 給腳本執行權限
chmod +x start_docker.sh

# 啟動Docker服務
./start_docker.sh
```

#### Windows PowerShell:
```powershell
# 啟動Docker服務
.\start_docker.ps1
```

### **方法2: 手動啟動**

```bash
# 1. 確保logs目錄存在
python ensure_logs_dir.py

# 2. 啟動Docker容器
docker-compose up -d

# 3. 檢查容器狀態
docker-compose ps
```

## 📄 日誌文件位置

### **本地日誌文件**
- **位置**: `./logs/` 目錄
- **主日誌**: `logs/tradingagents.log`
- **錯誤日誌**: `logs/tradingagents_error.log` (如果有錯誤)
- **輪轉日誌**: `logs/tradingagents.log.1`, `logs/tradingagents.log.2` 等

### **Docker 標準日誌**
- **查看命令**: `docker-compose logs web`
- **實時跟蹤**: `docker-compose logs -f web`

## 🔍 日誌查看方法

### **1. 使用日誌查看工具**
```bash
# 交互式日誌查看工具
python view_logs.py
```

功能包括：
- 📋 顯示所有日誌文件
- 👀 查看日誌文件內容
- 📺 實時跟蹤日誌
- 🔍 搜索日誌內容
- 🐳 查看Docker日誌

### **2. 直接查看文件**

#### Linux/macOS:
```bash
# 查看最新日誌
tail -f logs/tradingagents.log

# 查看最後100行
tail -100 logs/tradingagents.log

# 搜索錯誤
grep -i error logs/tradingagents.log
```

#### Windows PowerShell:
```powershell
# 實時查看日誌
Get-Content logs\tradingagents.log -Wait

# 查看最後50行
Get-Content logs\tradingagents.log -Tail 50

# 搜索錯誤
Select-String -Path logs\tradingagents.log -Pattern "error" -CaseSensitive:$false
```

### **3. Docker 日誌命令**
```bash
# 查看容器日誌
docker logs TradingAgents-web

# 實時跟蹤容器日誌
docker logs -f TradingAgents-web

# 查看最近1小時的日誌
docker logs --since 1h TradingAgents-web

# 查看最後100行日誌
docker logs --tail 100 TradingAgents-web
```

## 📤 獲取日誌文件

### **發送給開發者的文件**

當遇到問題需要技術支持時，請發送以下文件：

1. **主日誌文件**: `logs/tradingagents.log`
2. **錯誤日誌文件**: `logs/tradingagents_error.log` (如果存在)
3. **Docker日誌**: 
   ```bash
   docker logs TradingAgents-web > docker_logs.txt 2>&1
   ```

### **快速打包日誌**

#### Linux/macOS:
```bash
# 創建日誌壓縮包
tar -czf tradingagents_logs_$(date +%Y%m%d_%H%M%S).tar.gz logs/ docker_logs.txt
```

#### Windows PowerShell:
```powershell
# 創建日誌壓縮包
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
Compress-Archive -Path logs\*,docker_logs.txt -DestinationPath "tradingagents_logs_$timestamp.zip"
```

## 🔧 故障排除

### **問題1: logs目錄為空**

**原因**: 容器內應用可能將日誌輸出到stdout而不是文件

**解決方案**:
1. 檢查Docker日誌: `docker-compose logs web`
2. 確認環境變量配置正確
3. 重啟容器: `docker-compose restart web`

### **問題2: 權限問題**

**Linux/macOS**:
```bash
# 修複目錄權限
sudo chown -R $USER:$USER logs/
chmod 755 logs/
```

**Windows**: 通常無權限問題

### **問題3: 日誌文件過大**

**自動輪轉**: 配置了自動輪轉，主日誌文件最大100MB
**手動清理**:
```bash
# 備份並清空日誌
cp logs/tradingagents.log logs/tradingagents.log.backup
> logs/tradingagents.log
```

### **問題4: 容器無法啟動**

**檢查步驟**:
1. 檢查Docker狀態: `docker info`
2. 檢查端口占用: `netstat -tlnp | grep 8501`
3. 查看啟動日誌: `docker-compose logs web`
4. 檢查配置文件: `.env` 文件是否存在

## 📊 日誌級別說明

- **DEBUG**: 詳細的調試信息，包含函數調用、變量值等
- **INFO**: 一般信息，程序正常運行的關鍵步驟
- **WARNING**: 警告信息，程序可以繼續運行但需要註意
- **ERROR**: 錯誤信息，程序遇到錯誤但可以恢復
- **CRITICAL**: 嚴重錯誤，程序可能無法繼續運行

## 🎯 最佳實踐

### **1. 定期檢查日誌**
```bash
# 每天檢查錯誤日誌
grep -i error logs/tradingagents.log | tail -20
```

### **2. 監控日誌大小**
```bash
# 檢查日誌文件大小
ls -lh logs/
```

### **3. 備份重要日誌**
```bash
# 定期備份日誌
cp logs/tradingagents.log backups/tradingagents_$(date +%Y%m%d).log
```

### **4. 實時監控**
```bash
# 在另一個終端實時監控日誌
tail -f logs/tradingagents.log | grep -i "error\|warning"
```

## 📞 技術支持

如果遇到問題：

1. **收集日誌**: 使用上述方法收集完整日誌
2. **描述問題**: 詳細描述問題現象和重現步驟
3. **環境信息**: 提供操作系統、Docker版本等信息
4. **發送文件**: 將日誌文件發送給開發者

---

**通過這些改進，現在可以方便地獲取和管理TradingAgents的日誌文件了！** 🎉