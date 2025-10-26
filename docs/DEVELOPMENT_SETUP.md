# 🛠️ 開發環境配置指南

## 📋 概述

本文档介紹如何配置TradingAgents-CN的開發環境，包括Docker映射配置和快速調試方法。

## 🐳 Docker開發環境

### Volume映射配置

項目已配置了以下目錄映射，支持實時代碼更新：

```yaml
volumes:
  - .env:/app/.env
  # 開發環境代碼映射
  - ./web:/app/web                    # Web界面代碼
  - ./tradingagents:/app/tradingagents # 核心分析代碼
  - ./scripts:/app/scripts            # 腳本文件
  - ./test_conversion.py:/app/test_conversion.py # 測試腳本
```

### 啟動開發環境

```bash
# 停止現有服務
docker-compose down

# 啟動開發環境（帶volume映射）
docker-compose up -d

# 查看服務狀態
docker-compose ps
```

## 🔧 快速調試流程

### 1. 代碼修改
在本地開發目錄直接修改代碼，無需重新構建鏡像。

### 2. 測試轉換功能
```bash
# 運行獨立轉換測試
docker exec TradingAgents-web python test_conversion.py

# 查看容器日誌
docker logs TradingAgents-web --follow

# 進入容器調試
docker exec -it TradingAgents-web bash
```

### 3. Web界面測試
- 訪問: http://localhost:8501
- 修改代碼後刷新页面即可看到更新

## 📁 目錄結構說明

```
TradingAgentsCN/
├── web/                    # Web界面代碼 (映射到容器)
│   ├── app.py             # 主應用
│   ├── utils/             # 工具模塊
│   │   ├── report_exporter.py  # 報告導出
│   │   └── docker_pdf_adapter.py # Docker適配器
│   └── pages/             # 页面模塊
├── tradingagents/         # 核心分析代碼 (映射到容器)
├── scripts/               # 腳本文件 (映射到容器)
├── test_conversion.py     # 轉換測試腳本 (映射到容器)
└── docker-compose.yml     # Docker配置
```

## 🧪 調試技巧

### 1. 實時日誌監控
```bash
# 監控Web應用日誌
docker logs TradingAgents-web --follow

# 監控所有服務日誌
docker-compose logs --follow
```

### 2. 容器內調試
```bash
# 進入Web容器
docker exec -it TradingAgents-web bash

# 檢查Python環境
docker exec TradingAgents-web python --version

# 檢查依賴
docker exec TradingAgents-web pip list | grep pandoc
```

### 3. 文件同步驗證
```bash
# 檢查文件是否同步
docker exec TradingAgents-web ls -la /app/web/utils/

# 檢查文件內容
docker exec TradingAgents-web head -10 /app/test_conversion.py
```

## 🔄 開發工作流

### 標準開發流程
1. **修改代碼** - 在本地IDE中編辑
2. **保存文件** - 自動同步到容器
3. **測試功能** - 刷新Web页面或運行測試腳本
4. **查看日誌** - 檢查錯誤和調試信息
5. **迭代優化** - 重複上述步骤

### 導出功能調試流程
1. **修改導出代碼** - 編辑 `web/utils/report_exporter.py`
2. **運行轉換測試** - `docker exec TradingAgents-web python test_conversion.py`
3. **檢查結果** - 查看生成的測試文件
4. **Web界面測試** - 在浏覽器中測試實际導出功能

## ⚠️ 註意事項

### 文件權限
- Windows用戶可能遇到文件權限問題
- 確保Docker有權限訪問項目目錄

### 性能考慮
- Volume映射可能影響I/O性能
- 生產環境建议使用鏡像構建方式

### 依賴更新
- 修改requirements.txt後需要重新構建鏡像
- 添加新的系統依賴需要更新Dockerfile

## 🚀 生產部署

開發完成後，生產部署流程：

```bash
# 1. 停止開發環境
docker-compose down

# 2. 重新構建鏡像
docker build -t tradingagents-cn:latest .

# 3. 啟動生產環境（不使用volume映射）
# 修改docker-compose.yml移除volume映射
docker-compose up -d
```

## 💡 最佳實踐

1. **代碼同步** - 確保本地修改及時保存
2. **日誌監控** - 保持日誌窗口開啟
3. **增量測試** - 小步快跑，頻繁測試
4. **备份重要** - 定期提交代碼到Git
5. **環境隔離** - 開發和生產環境分離

## 🎯 功能開發指南

### 導出功能開發

如果需要修改或擴展導出功能：

1. **核心文件位置**
   ```
   web/utils/report_exporter.py     # 主要導出逻辑
   web/utils/docker_pdf_adapter.py  # Docker環境適配
   test_conversion.py               # 轉換功能測試
   ```

2. **關键修複點**
   ```python
   # YAML解析問題修複
   extra_args = ['--from=markdown-yaml_metadata_block']

   # 內容清理函數
   def _clean_markdown_for_pandoc(self, content: str) -> str:
       # 保護表格分隔符，清理YAML冲突字符
   ```

3. **測試流程**
   ```bash
   # 測試基础轉換功能
   docker exec TradingAgents-web python test_conversion.py
   ```

### Memory功能開發

如果遇到memory相關錯誤：

1. **安全檢查模式**
   ```python
   # 在所有使用memory的地方添加檢查
   if memory is not None:
       past_memories = memory.get_memories(curr_situation, n_matches=2)
   else:
       past_memories = []
   ```

2. **相關文件**
   ```
   tradingagents/agents/researchers/bull_researcher.py
   tradingagents/agents/researchers/bear_researcher.py
   tradingagents/agents/managers/research_manager.py
   tradingagents/agents/managers/risk_manager.py
   ```

### 緩存功能開發

處理緩存相關錯誤：

1. **類型安全檢查**
   ```python
   # 檢查數據類型，避免 'str' object has no attribute 'empty'
   if cached_data is not None:
       if hasattr(cached_data, 'empty') and not cached_data.empty:
           # DataFrame處理
       elif isinstance(cached_data, str) and cached_data.strip():
           # 字符串處理
   ```

2. **相關文件**
   ```
   tradingagents/dataflows/tushare_adapter.py
   tradingagents/dataflows/tushare_utils.py
   tradingagents/dataflows/cache_manager.py
   ```

## 🚀 部署指南

### 生產環境部署

開發完成後的部署流程：

1. **停止開發環境**
   ```bash
   docker-compose down
   ```

2. **移除volume映射**
   ```yaml
   # 編辑 docker-compose.yml，註釋掉開發映射
   # volumes:
   #   - ./web:/app/web
   #   - ./tradingagents:/app/tradingagents
   ```

3. **重新構建鏡像**
   ```bash
   docker build -t tradingagents-cn:latest .
   ```

4. **啟動生產環境**
   ```bash
   docker-compose up -d
   ```

### 版本發布

1. **更新版本號**
   ```bash
   echo "cn-0.1.8" > VERSION
   ```

2. **提交代碼**
   ```bash
   git add .
   git commit -m "🎉 發布 v0.1.8 - 導出功能完善"
   git tag cn-0.1.8
   git push origin develop --tags
   ```

3. **更新文档**
   - 更新 README.md 中的版本信息
   - 更新 VERSION_*.md 發布說明
   - 更新相關功能文档

---

*最後更新: 2025-07-13*
*版本: v0.1.7*
