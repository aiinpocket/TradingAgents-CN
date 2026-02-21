# Docker容器排查腳本
# 使用方法: .\scripts\debug_docker.ps1

Write-Host "=== Docker容器排查工具 ===" -ForegroundColor Green

# 1. 檢查Docker服務狀態
Write-Host "`n1. 檢查Docker服務狀態:" -ForegroundColor Yellow
try {
    docker version
    Write-Host "Docker服務正常運行" -ForegroundColor Green
} catch {
    Write-Host "Docker服務未運行或有問題" -ForegroundColor Red
    exit 1
}

# 2. 檢查容器狀態
Write-Host "`n2. 檢查容器狀態:" -ForegroundColor Yellow
docker-compose ps -a

# 3. 檢查網路狀態
Write-Host "`n3. 檢查Docker網路:" -ForegroundColor Yellow
docker network ls | Select-String "tradingagents"

# 4. 檢查資料卷狀態
Write-Host "`n4. 檢查資料卷:" -ForegroundColor Yellow
docker volume ls | Select-String "tradingagents"

# 5. 檢查連接埠佔用
Write-Host "`n5. 檢查連接埠佔用:" -ForegroundColor Yellow
$ports = @(8501, 27017, 6379, 8081, 8082)
foreach ($port in $ports) {
    $result = netstat -an | Select-String ":$port "
    if ($result) {
        Write-Host "連接埠 $port 被佔用: $result" -ForegroundColor Yellow
    } else {
        Write-Host "連接埠 $port 空閒" -ForegroundColor Green
    }
}

# 6. 檢查磁碟空間
Write-Host "`n6. 檢查磁碟空間:" -ForegroundColor Yellow
docker system df

Write-Host "`n=== 排查完成 ===" -ForegroundColor Green
Write-Host "如需查看詳細日誌，請執行:" -ForegroundColor Cyan
Write-Host "docker-compose logs [服務名]" -ForegroundColor Cyan
Write-Host "例如: docker-compose logs web" -ForegroundColor Cyan
