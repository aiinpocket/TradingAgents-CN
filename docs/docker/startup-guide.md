# Docker啟動指南

## 🚀 快速啟動

### 📋 基本啟動命令

```bash
# 日常啟動（推薦）- 使用現有鏡像
docker-compose up -d

# 首次啟動或代碼變更 - 重新構建鏡像
docker-compose up -d --build
```

### 🧠 智能啟動（推薦）

智能啟動腳本會自動判斷是否需要重新構建鏡像：

#### Windows環境
```powershell
# 方法1：直接運行
powershell -ExecutionPolicy Bypass -File scripts\smart_start.ps1

# 方法2：在PowerShell中運行
.\scripts\smart_start.ps1
```

#### Linux/Mac環境
```bash
# 添加執行權限並運行
chmod +x scripts/smart_start.sh
./scripts/smart_start.sh

# 或者一行命令
chmod +x scripts/smart_start.sh && ./scripts/smart_start.sh
```

## 🔧 啟動參數說明

### `--build` 參數使用場景

| 場景 | 是否需要 `--build` | 原因 |
|------|-------------------|------|
| 首次啟動 | ✅ 需要 | 鏡像不存在，需要構建 |
| 代碼修改後 | ✅ 需要 | 需要将新代碼打包到鏡像 |
| 依賴更新後 | ✅ 需要 | requirements.txt變化 |
| Dockerfile修改 | ✅ 需要 | 構建配置變化 |
| 日常重啟 | ❌ 不需要 | 鏡像已存在且無變化 |
| 容器異常重啟 | ❌ 不需要 | 問題通常不在鏡像層面 |

### 智能啟動判斷逻辑

1. **檢查鏡像存在性**
   - 鏡像不存在 → 執行 `docker-compose up -d --build`
   
2. **檢查代碼變化**
   - 有未提交的代碼變化 → 執行 `docker-compose up -d --build`
   - 無代碼變化 → 執行 `docker-compose up -d`

## 🛠️ 故障排除

### 常见啟動問題

1. **端口冲突**
   ```bash
   # 檢查端口占用
   netstat -ano | findstr :8501  # Windows
   lsof -i :8501                 # Linux/Mac
   ```

2. **鏡像構建失败**
   ```bash
   # 清理並重新構建
   docker-compose down
   docker system prune -f
   docker-compose up -d --build
   ```

3. **容器啟動失败**
   ```bash
   # 查看詳細日誌
   docker-compose logs web
   docker-compose logs mongodb
   docker-compose logs redis
   ```

### 排查工具

使用項目提供的排查腳本：

```bash
# Windows
powershell -ExecutionPolicy Bypass -File scripts\debug_docker.ps1

# Linux/Mac
chmod +x scripts/debug_docker.sh && ./scripts/debug_docker.sh
```

## 📊 性能對比

| 啟動方式 | 首次啟動時間 | 後续啟動時間 | 適用場景 |
|----------|-------------|-------------|----------|
| `docker-compose up -d --build` | ~3-5分鐘 | ~3-5分鐘 | 開發環境，代碼頻繁變更 |
| `docker-compose up -d` | ~3-5分鐘 | ~10-30秒 | 生產環境，穩定運行 |
| 智能啟動腳本 | ~3-5分鐘 | ~10-30秒 | 推薦，自動優化 |

## 🎯 最佳實踐

1. **開發環境**：使用智能啟動腳本
2. **生產環境**：首次部署用 `--build`，後续用普通啟動
3. **CI/CD**：始终使用 `--build` 確保最新代碼
4. **故障排除**：先嘗試普通重啟，再考慮重新構建