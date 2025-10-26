# 🔧 導出功能故障排除指南

## 🎯 概述

本文档提供了TradingAgents-CN導出功能常见問題的詳細解決方案，包括Word、PDF、Markdown導出的各種故障排除方法。

## 📄 Word導出問題

### 問題1: YAML解析錯誤

**錯誤信息**:

```
Pandoc died with exitcode "64" during conversion: 
YAML parse exception at line 1, column 1,
while scanning an alias:
did not find expected alphabetic or numeric character
```

**原因分析**:

- Markdown內容中的表格分隔符 `|------|------| ` 被pandoc誤認為YAML文档分隔符
- 特殊字符導致YAML解析冲突

**解決方案**:

```python
# 已在代碼中自動修複
extra_args = ['--from=markdown-yaml_metadata_block']  # 禁用YAML解析
```

**驗證方法**:

```bash
# 測試Word導出
docker exec TradingAgents-web python test_conversion.py
```

### 問題2: 中文字符顯示異常

**錯誤現象**:

- Word文档中中文顯示為方塊或乱碼
- 特殊符號（¥、%等）顯示異常

**解決方案**:

1. **Docker環境**（推薦）:

   ```bash
   # Docker已預配置中文字體，無需額外設置
   docker-compose up -d
   ```
2. **本地環境**:

   ```bash
   # Windows
   # 確保系統已安裝中文字體

   # Linux
   sudo apt-get install fonts-noto-cjk

   # macOS
   # 系統自帶中文字體支持
   ```

### 問題3: Word文件損坏或無法打開

**錯誤現象**:

- 生成的.docx文件無法用Word打開
- 文件大小為0或異常小

**診斷步骤**:

```bash
# 1. 檢查生成的文件
docker exec TradingAgents-web ls -la /app/test_*.docx

# 2. 驗證pandoc安裝
docker exec TradingAgents-web pandoc --version

# 3. 測試基础轉換
docker exec TradingAgents-web python test_conversion.py
```

**解決方案**:

```bash
# 重新構建Docker鏡像
docker-compose down
docker build -t tradingagents-cn:latest . --no-cache
docker-compose up -d
```

## 📊 PDF導出問題

### 問題1: PDF引擎不可用

**錯誤信息**:

```
PDF生成失败，最後錯誤: wkhtmltopdf not found
```

**解決方案**:

1. **Docker環境**（推薦）:

   ```bash
   # 檢查PDF引擎安裝
   docker exec TradingAgents-web wkhtmltopdf --version
   docker exec TradingAgents-web weasyprint --version
   ```
2. **本地環境安裝**:

   ```bash
   # Windows
   choco install wkhtmltopdf

   # macOS
   brew install wkhtmltopdf

   # Linux
   sudo apt-get install wkhtmltopdf
   ```

### 問題2: PDF生成超時

**錯誤現象**:

- PDF生成過程卡住不動
- 長時間無響應

**解決方案**:

```python
# 增加超時設置（已在代碼中配置）
max_execution_time = 180  # 3分鐘超時
```

**臨時解決**:

```bash
# 重啟Web服務
docker-compose restart web
```

### 問題3: PDF中文顯示問題

**錯誤現象**:

- PDF中中文字符顯示為空白或方塊
- 布局錯乱

**解決方案**:

```bash
# Docker環境已預配置，如有問題請重新構建
docker build -t tradingagents-cn:latest . --no-cache
```

## 📝 Markdown導出問題

### 問題1: 特殊字符轉義

**錯誤現象**:

- 特殊字符（&、<、>等）顯示異常
- 表格格式錯乱

**解決方案**:

```python
# 自動字符轉義（已實現）
text = text.replace('&', '&')
text = text.replace('<', '<')
text = text.replace('>', '>')
```

### 問題2: 文件編碼問題

**錯誤現象**:

- 下載的Markdown文件乱碼
- 中文字符顯示異常

**解決方案**:

```python
# 確保UTF-8編碼（已配置）
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
```

## 🔧 通用故障排除

### 診斷工具

1. **測試轉換功能**:

   ```bash
   # 基础轉換測試
   docker exec TradingAgents-web python test_conversion.py

   # 實际數據轉換測試
   docker exec TradingAgents-web python test_real_conversion.py

   # 現有報告轉換測試
   docker exec TradingAgents-web python test_existing_reports.py
   ```
2. **檢查系統狀態**:

   ```bash
   # 查看容器狀態
   docker-compose ps

   # 查看日誌
   docker logs TradingAgents-web --tail 50

   # 檢查磁盘空間
   docker exec TradingAgents-web df -h
   ```
3. **驗證依賴**:

   ```bash
   # 檢查Python包
   docker exec TradingAgents-web pip list | grep -E "(pandoc|docx|pypandoc)"

   # 檢查系統工具
   docker exec TradingAgents-web which pandoc
   docker exec TradingAgents-web which wkhtmltopdf
   ```

### 環境重置

如果問題持续存在，可以嘗試完全重置環境：

```bash
# 1. 停止所有服務
docker-compose down

# 2. 清理Docker資源
docker system prune -f

# 3. 重新構建鏡像
docker build -t tradingagents-cn:latest . --no-cache

# 4. 重新啟動服務
docker-compose up -d

# 5. 驗證功能
docker exec TradingAgents-web python test_conversion.py
```

### 性能優化

1. **內存不足**:

   ```yaml
   # docker-compose.yml
   services:
     web:
       deploy:
         resources:
           limits:
             memory: 2G  # 增加內存限制
   ```
2. **磁盘空間**:

   ```bash
   # 清理臨時文件
   docker exec TradingAgents-web find /tmp -name "*.docx" -delete
   docker exec TradingAgents-web find /tmp -name "*.pdf" -delete
   ```

## 📞 獲取幫助

### 日誌收集

遇到問題時，請收集以下信息：

1. **錯誤日誌**:

   ```bash
   docker logs TradingAgents-web --tail 100 > error.log
   ```
2. **系統信息**:

   ```bash
   docker exec TradingAgents-web python --version
   docker exec TradingAgents-web pandoc --version
   docker --version
   docker-compose --version
   ```
3. **測試結果**:

   ```bash
   docker exec TradingAgents-web python test_conversion.py > test_result.log 2>&1
   ```

### 常见解決方案总結


| 問題類型     | 快速解決方案   | 詳細方案       |
| ------------ | -------------- | -------------- |
| YAML解析錯誤 | 重啟Web服務    | 檢查代碼修複   |
| PDF引擎缺失  | 使用Docker環境 | 手動安裝引擎   |
| 中文顯示問題 | 使用Docker環境 | 安裝中文字體   |
| 文件損坏     | 重新生成       | 重建Docker鏡像 |
| 內存不足     | 重啟容器       | 增加內存限制   |
| 網絡超時     | 檢查網絡       | 增加超時設置   |

### 預防措施

1. **定期更新**:

   ```bash
   git pull origin develop
   docker-compose pull
   ```
2. **監控資源**:

   ```bash
   docker stats TradingAgents-web
   ```
3. **备份配置**:

   ```bash
   cp .env .env.backup
   ```

---

*最後更新: 2025-07-13*
*版本: v0.1.7*
