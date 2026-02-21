# 📄 報告導出使用指南

## 📋 概述

TradingAgents-CN v0.1.7 引入了專業級的報告導出功能，支持將股票分析結果導出為Word、PDF、Markdown三種格式。本指南將詳細介紹如何使用報告導出功能。

## 🎯 導出功能特色

### 支持格式

| 格式 | 擴展名 | 適用場景 | 特點 |
|------|--------|----------|------|
| **📝 Markdown** | .md | 在線查看、版本控制、技術文檔 | 輕量級、可編辑、Git友好 |
| **📄 Word** | .docx | 商業報告、編辑修改、團隊協作 | 專業格式、易編辑、兼容性好 |
| **📊 PDF** | .pdf | 正式發布、打印存檔、客戶交付 | 固定格式、專業外觀、跨平台 |

### 技術特性

- ✅ **專業排版**: 自動格式化和美化
- ✅ **中文支持**: 完整的中文字體和排版
- ✅ **圖表集成**: 支持表格和數據可視化
- ✅ **模板定制**: 可自定義報告模板
- ✅ **批量導出**: 支持多個報告同時導出

## 🚀 快速開始

### 前置條件

#### Docker環境 (推薦)
```bash
# Docker環境已預配置所有依賴
docker-compose up -d
```

#### 本地環境
```bash
# 安裝Pandoc (文檔轉換引擎)
# Windows: 下載安裝包 https://pandoc.org/installing.html
# Linux: sudo apt install pandoc
# macOS: brew install pandoc

# 安裝wkhtmltopdf (PDF生成引擎)
# Windows: 下載安裝包 https://wkhtmltopdf.org/downloads.html
# Linux: sudo apt install wkhtmltopdf
# macOS: brew install wkhtmltopdf

# 驗證安裝
pandoc --version
wkhtmltopdf --version
```

### 啟用導出功能

```bash
# 在.env文件中配置
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf
EXPORT_OUTPUT_PATH=./exports
```

## 📊 使用指南

### 基礎導出流程

#### 1. 完成股票分析
```bash
# 訪問Web界面
http://localhost:8501

# 進行股票分析
# 1. 選擇LLM模型
# 2. 輸入股票代碼 (如: 000001, AAPL)
# 3. 選擇分析深度
# 4. 點擊"開始分析"
# 5. 等待分析完成
```

#### 2. 導出報告
```bash
# 在分析結果頁面
# 1. 滾動到頁面底部
# 2. 找到"報告導出"部分
# 3. 選擇導出格式:
#    - ☑️ Markdown
#    - ☑️ Word文檔
#    - ☑️ PDF文檔
# 4. 點擊"導出報告"按鈕
# 5. 等待生成完成
# 6. 點擊下載鏈接
```

### 導出格式詳解

#### 📝 Markdown導出

**特點**:
- 輕量級文本格式
- 支持版本控制
- 易於在線查看和編辑
- 適合技術文檔和協作

**使用場景**:
```bash
# 適用於:
✅ 技術團隊內部分享
✅ 版本控制和歷史追蹤
✅ 在線文檔平台發布
✅ 進一步編辑和加工
```

**示例內容**:
```markdown
# 股票分析報告: 平安銀行 (000001)

## 📊 基本信息
- **股票代碼**: 000001
- **股票名稱**: 平安銀行
- **分析時間**: 2025-07-13 14:30:00
- **當前價格**: ¥12.45

## 📈 技術分析
### 趨勢分析
當前股價處於上升通道中...
```

#### 📄 Word文檔導出

**特點**:
- 專業商業文檔格式
- 支持複雜排版和格式
- 易於編辑和修改
- 廣泛的兼容性

**使用場景**:
```bash
# 適用於:
✅ 正式商業報告
✅ 客戶交付文檔
✅ 團隊協作編辑
✅ 演示和匯報材料
```

**格式特性**:
- 📋 標準商業文檔模板
- 🎨 專業排版和字體
- 📊 表格和圖表支持
- 🔖 目錄和页碼
- 📝 页眉页腳

#### 📊 PDF文檔導出

**特點**:
- 固定格式，跨平台一致
- 專業外觀和排版
- 適合打印和存檔
- 不易被修改

**使用場景**:
```bash
# 適用於:
✅ 正式發布和交付
✅ 打印和存檔
✅ 客戶演示
✅ 監管報告
```

**品質特性**:
- 🖨️ 高品質打印輸出
- 📱 移動設備友好
- 🔒 內容保護
- 📏 標準頁面尺寸 (A4)

## ⚙️ 高級配置

### 自定義導出設置

```bash
# .env 高級配置
# === 導出功能詳細配置 ===
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf,markdown
EXPORT_OUTPUT_PATH=./exports
EXPORT_FILENAME_FORMAT={symbol}_analysis_{timestamp}

# === 格式轉換配置 ===
PANDOC_PATH=/usr/bin/pandoc
WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf

# === 品質配置 ===
EXPORT_INCLUDE_DEBUG=false
EXPORT_WATERMARK=false
EXPORT_COMPRESS_PDF=true

# === Word導出配置 ===
WORD_TEMPLATE_PATH=./templates/report_template.docx
WORD_REFERENCE_DOC=./templates/reference.docx

# === PDF導出配置 ===
PDF_PAGE_SIZE=A4
PDF_MARGIN_TOP=2cm
PDF_MARGIN_BOTTOM=2cm
PDF_MARGIN_LEFT=2cm
PDF_MARGIN_RIGHT=2cm
```

### 自定義模板

#### Word模板定制
```bash
# 1. 創建模板目錄
mkdir -p templates

# 2. 創建Word模板文件
# templates/report_template.docx
# - 設置標準樣式
# - 定義页眉页腳
# - 配置字體和顏色

# 3. 配置模板路徑
WORD_TEMPLATE_PATH=./templates/report_template.docx
```

#### PDF樣式定制
```bash
# 創建CSS樣式文件
# templates/pdf_style.css

body {
    font-family: "SimSun", serif;
    font-size: 12pt;
    line-height: 1.6;
    margin: 2cm;
}

h1 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 20px 0;
}
```

## 🔧 故障排除

### 常見問題

#### 1. 導出按鈕不顯示

**原因**: 導出功能未啟用

**解決方案**:
```bash
# 檢查.env配置
EXPORT_ENABLED=true

# 重啟應用
docker-compose restart web
# 或
streamlit run web/app.py
```

#### 2. Word導出失敗

**原因**: Pandoc未安裝或YAML衝突

**解決方案**:
```bash
# Docker環境 (自動修複)
docker-compose restart web

# 本地環境
# 1. 安裝Pandoc
sudo apt install pandoc  # Linux
brew install pandoc      # macOS

# 2. 檢查Pandoc版本
pandoc --version
```

#### 3. PDF導出失敗

**原因**: wkhtmltopdf未安裝或中文字體問題

**解決方案**:
```bash
# Docker環境 (已預配置)
docker logs TradingAgents-web

# 本地環境
# 1. 安裝wkhtmltopdf
sudo apt install wkhtmltopdf  # Linux
brew install wkhtmltopdf      # macOS

# 2. 安裝中文字體
sudo apt install fonts-wqy-zenhei  # Linux
```

#### 4. 文件下載失敗

**原因**: 瀏覽器阻止下載或文件權限問題

**解決方案**:
```bash
# 1. 檢查瀏覽器下載設置
# 2. 檢查文件權限
chmod 755 exports/
chmod 644 exports/*.pdf

# 3. 手動下載
# 文件保存在 exports/ 目錄中
```

### 性能優化

```bash
# 1. 啟用並行導出
EXPORT_PARALLEL=true
EXPORT_MAX_WORKERS=3

# 2. 啟用緩存
EXPORT_CACHE_ENABLED=true
EXPORT_CACHE_TTL=3600

# 3. 壓縮輸出
EXPORT_COMPRESS_PDF=true
EXPORT_OPTIMIZE_IMAGES=true
```

## 📊 批量導出

### 批量導出多個分析

```python
# 使用Python腳本批量導出
import os
from tradingagents.export.report_exporter import ReportExporter

# 初始化導出器
exporter = ReportExporter()

# 批量導出
symbols = ['000001', '600519', '000858', 'AAPL', 'TSLA']
for symbol in symbols:
    # 獲取分析結果
    analysis_result = get_analysis_result(symbol)
    
    # 導出所有格式
    exporter.export_all_formats(
        analysis_result, 
        output_dir=f'exports/{symbol}'
    )
```

### 定時導出

```bash
# 創建定時任務
crontab -e

# 每日導出重要股票分析
0 18 * * 1-5 cd /path/to/TradingAgents-CN && python scripts/daily_export.py
```

## 📈 最佳實踐

### 1. 文件命名規範
```bash
# 推薦命名格式
{股票代碼}_{分析類型}_{日期}.{格式}

# 示例
000001_comprehensive_20250713.pdf
AAPL_technical_20250713.docx
600519_fundamental_20250713.md
```

### 2. 存儲管理
```bash
# 定期清理舊文件
find exports/ -name "*.pdf" -mtime +30 -delete
find exports/ -name "*.docx" -mtime +30 -delete

# 壓縮存檔
tar -czf exports_archive_$(date +%Y%m).tar.gz exports/
```

### 3. 品質控制
```bash
# 導出前檢查
✅ 分析結果完整性
✅ 數據準確性
✅ 格式配置正確
✅ 模板文件存在

# 導出後驗證
✅ 文件生成成功
✅ 文件大小合理
✅ 內容格式正確
✅ 中文顯示正常
```

---

## 📞 獲取幫助

如果在使用報告導出功能時遇到問題：

- 🐛 [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)
- 💬 [GitHub Discussions](https://github.com/hsliuping/TradingAgents-CN/discussions)
- 📚 [Pandoc文檔](https://pandoc.org/MANUAL.html)

---

*最後更新: 2025-07-13*  
*版本: cn-0.1.7*  
*貢獻者: [@baiyuxiong](https://github.com/baiyuxiong)*
