# 🐳 Docker鏡像構建指南

## 📋 概述

TradingAgents-CN採用本地構建Docker鏡像的方式，而不是提供預構建鏡像。本文檔詳細說明了Docker鏡像的構建過程、優化方法和常見問題解決方案。

## 🎯 為什么需要本地構建？

### 設計理念

1. **🔧 定制化需求**
   - 用戶可能需要不同的配置選項
   - 支持自定義依賴和擴展
   - 適應不同的部署環境

2. **🔒 安全考慮**
   - 避免在公共鏡像中包含敏感信息
   - 用戶完全控制構建過程
   - 減少供應鏈安全風險

3. **📦 版本靈活性**
   - 支持用戶自定義修改
   - 便於開發和調試
   - 適應快速迭代需求

4. **⚡ 依賴優化**
   - 根據實際需求安裝依賴
   - 避免不必要的組件
   - 優化鏡像大小

## 🏗️ 構建過程詳解

### Dockerfile結構

```dockerfile
# 基礎鏡像
FROM python:3.10-slim

# 系統依賴安裝
RUN apt-get update && apt-get install -y \
    pandoc \
    wkhtmltopdf \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    && rm -rf /var/lib/apt/lists/*

# Python依賴安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 應用代碼複制
COPY . /app
WORKDIR /app

# 運行配置
EXPOSE 8501
CMD ["streamlit", "run", "web/app.py"]
```

### 構建階段分析

#### 階段1: 基礎鏡像下載
```bash
# 下載python:3.10-slim鏡像
大小: ~200MB
時間: 1-3分鐘 (取決於網絡)
緩存: Docker會自動緩存，後續構建更快
```

#### 階段2: 系統依賴安裝
```bash
# 安裝系統包
包含: pandoc, wkhtmltopdf, 中文字體
大小: ~300MB
時間: 2-4分鐘
優化: 清理apt緩存減少鏡像大小
```

#### 階段3: Python依賴安裝
```bash
# 安裝Python包
來源: requirements.txt
大小: ~500MB
時間: 2-5分鐘
優化: 使用--no-cache-dir減少鏡像大小
```

#### 階段4: 應用代碼複制
```bash
# 複制源代碼
大小: ~50MB
時間: <1分鐘
優化: 使用.dockerignore排除不必要文件
```

## ⚡ 構建優化

### 1. 使用構建緩存

```bash
# 利用Docker層緩存
# 將不經常變化的步驟放在前面
COPY requirements.txt .
RUN pip install -r requirements.txt
# 將經常變化的代碼放在後面
COPY . /app
```

### 2. 多階段構建 (高級)

```dockerfile
# 構建階段
FROM python:3.10-slim as builder
RUN pip install --user -r requirements.txt

# 運行階段
FROM python:3.10-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
```

### 3. 使用國內鏡像源

```dockerfile
# 加速pip安裝
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 加速apt安裝
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list
```

### 4. .dockerignore優化

```bash
# .dockerignore文件內容
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

## 🚀 構建命令詳解

### 基礎構建

```bash
# 標準構建
docker-compose build

# 強制重新構建 (不使用緩存)
docker-compose build --no-cache

# 構建並啟動
docker-compose up --build

# 後台構建並啟動
docker-compose up -d --build
```

### 高級構建選項

```bash
# 並行構建 (如果有多個服務)
docker-compose build --parallel

# 指定構建參數
docker-compose build --build-arg HTTP_PROXY=http://proxy:8080

# 查看構建過程
docker-compose build --progress=plain

# 構建特定服務
docker-compose build web
```

## 📊 構建性能監控

### 構建時間優化

```bash
# 測量構建時間
time docker-compose build

# 分析構建層
docker history tradingagents-cn:latest

# 查看鏡像大小
docker images tradingagents-cn
```

### 資源使用監控

```bash
# 監控構建過程資源使用
docker stats

# 查看磁盘使用
docker system df

# 清理構建緩存
docker builder prune
```

## 🚨 常見問題解決

### 1. 構建失敗

#### 網絡問題
```bash
# 症狀: 下載依賴失敗
# 解決: 使用國內鏡像源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

#### 內存不足
```bash
# 症狀: 構建過程中內存耗尽
# 解決: 增加Docker內存限制
# Docker Desktop -> Settings -> Resources -> Memory (建議4GB+)
```

#### 權限問題
```bash
# 症狀: 文件權限錯誤
# 解決: 在Dockerfile中設置正確權限
RUN chmod +x /app/scripts/*.sh
```

### 2. 構建緩慢

#### 網絡優化
```bash
# 使用多線程下載
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
```

#### 緩存優化
```bash
# 合理安排Dockerfile層顺序
# 將不變的依賴放在前面，變化的代碼放在後面
```

### 3. 鏡像過大

#### 清理優化
```bash
# 在同一RUN指令中清理緩存
RUN apt-get update && apt-get install -y package && rm -rf /var/lib/apt/lists/*
```

#### 多階段構建
```bash
# 使用多階段構建減少最终鏡像大小
FROM python:3.10-slim as builder
# 構建步驟...
FROM python:3.10-slim
COPY --from=builder /app /app
```

## 📈 最佳實踐

### 1. 構建策略

```bash
# 開發環境
docker-compose up --build  # 每次都重新構建

# 測試環境  
docker-compose build && docker-compose up -d  # 先構建再啟動

# 生產環境
docker-compose build --no-cache && docker-compose up -d  # 完全重新構建
```

### 2. 版本管理

```bash
# 為鏡像打標簽
docker build -t tradingagents-cn:v0.1.7 .
docker build -t tradingagents-cn:latest .

# 推送到私有倉庫 (可選)
docker tag tradingagents-cn:latest your-registry/tradingagents-cn:latest
docker push your-registry/tradingagents-cn:latest
```

### 3. 安全考慮

```bash
# 使用非root用戶運行
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# 掃描安全漏洞
docker scan tradingagents-cn:latest
```

## 🔮 未來優化方向

### 1. 預構建鏡像

考慮在未來版本提供官方預構建鏡像：
- 🏷️ 穩定版本的預構建鏡像
- 🔄 自動化CI/CD構建流程
- 📦 多架構支持 (amd64, arm64)

### 2. 構建優化

- ⚡ 更快的構建速度
- 📦 更小的鏡像大小
- 🔧 更好的緩存策略

### 3. 部署簡化

- 🎯 一鍵部署腳本
- 📋 預配置模板
- 🔧 自動化配置檢查

---

*最後更新: 2025-07-13*  
*版本: cn-0.1.7*  
*貢獻者: [@breeze303](https://github.com/breeze303)*
