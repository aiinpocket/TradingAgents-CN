# 📄 報告導出功能詳解

## 🎯 功能概述

TradingAgents-CN 提供了強大的報告導出功能，支持將股票分析結果導出為多種專業格式，方便用戶保存、分享和進一步分析。

## 📋 支持的導出格式

### 1. **📝 Markdown格式**

- **用途**: 在線查看、版本控制、技術文檔
- **特點**: 輕量級、可編辑、支持版本控制
- **適用場景**: 開發者文檔、在線分享、技術博客

### 2. **📄 Word文檔 (.docx)**

- **用途**: 商業報告、正式文檔、打印輸出
- **特點**: 專業格式、易於編辑、廣泛兼容
- **適用場景**: 投資報告、客戶演示、存檔備份

### 3. **📊 PDF文檔 (.pdf)**

- **用途**: 正式發布、打印、長期保存
- **特點**: 格式固定、跨平台兼容、專業外觀
- **適用場景**: 正式報告、監管提交、客戶交付

## 🚀 使用方法

### Web界面導出

1. **完成股票分析**

   - 在Web界面輸入股票代碼
   - 選擇分析深度和配置
   - 等待分析完成
2. **選擇導出格式**

   - 在分析結果頁面找到導出按鈕
   - 點擊對應格式的導出按鈕：
     - 📝 **導出 Markdown**
     - 📄 **導出 Word**
     - 📊 **導出 PDF**
3. **下載文件**

   - 系統自動生成文件
   - 瀏覽器自動下載到本地
   - 文件名格式：`{股票代碼}_analysis_{時間戳}.{格式}`

### 命令行導出

```bash
# 使用CLI進行分析並導出
python main.py --symbol 000001 --export-format word,pdf
```

## 📊 報告內容結構

### 標準報告包含以下章節：

1. **📈 股票基本信息**

   - 股票代碼和名稱
   - 當前價格和漲跌幅
   - 市場板塊信息
   - 分析時間戳
2. **🎯 投資決策摘要**

   - 投資建議（買入/賣出/持有）
   - 置信度評分
   - 風險評分
   - 目標價位
3. **📊 詳細分析報告**

   - 市場技術分析
   - 基本面分析
   - 情緒分析（如啟用）
   - 新聞分析（如啟用）
4. **🔬 專家辩論記錄**

   - 看漲分析師觀點
   - 看跌分析師觀點
   - 辩論過程記錄
5. **⚠️ 風險提示**

   - 市場風險警告
   - 投資建議免责聲明
   - 數據來源說明
6. **📝 技術信息**

   - 使用的LLM模型
   - 分析師配置
   - 數據源信息
   - 生成時間

## ⚙️ 技術實現

### 導出引擎

- **核心引擎**: Pandoc
- **Word轉換**: pypandoc + python-docx
- **PDF生成**: wkhtmltopdf / weasyprint
- **格式處理**: 自動清理YAML衝突

### Docker環境優化

```yaml
# Docker環境已預裝所有依賴
- pandoc: 文檔轉換核心
- wkhtmltopdf: PDF生成引擎
- python-docx: Word文檔處理
- 中文字體支持: 完整中文顯示
```

### 錯誤處理機制

1. **YAML解析保護**

   ```python
   # 自動禁用YAML元數據解析
   extra_args = ['--from=markdown-yaml_metadata_block']
   ```
2. **內容清理**

   ```python
   # 清理可能導致衝突的字符
   content = content.replace('---', '—')  # 表格分隔符保護
   content = content.replace('...', '…')  # 省略號處理
   ```
3. **降級策略**

   ```python
   # PDF引擎降級顺序
   engines = ['wkhtmltopdf', 'weasyprint', 'default']
   ```

## 🔧 配置選項

### 環境變量配置

```bash
# .env 文件配置
EXPORT_ENABLED=true                    # 啟用導出功能
EXPORT_DEFAULT_FORMAT=word,pdf         # 默認導出格式
EXPORT_INCLUDE_DEBUG=false             # 是否包含調試信息
EXPORT_WATERMARK=false                 # 是否添加水印
```

### Web界面配置

- **導出格式選擇**: 用戶可選擇單個或多個格式
- **文件命名**: 自動生成帶時間戳的文件名
- **下載管理**: 自動觸發瀏覽器下載

## 📁 文件管理

### 文件命名規則

```
格式: {股票代碼}_analysis_{YYYYMMDD_HHMMSS}.{擴展名}
示例: 
- 000001_analysis_20250113_143022.docx
- AAPL_analysis_20250113_143022.pdf
- 600519_analysis_20250113_143022.md
```

### 存储位置

- **Web導出**: 臨時文件，自動下載後清理
- **CLI導出**: 保存到 `./exports/` 目錄
- **Docker環境**: 映射到主機目錄（如配置）

## 🚨 故障排除

### 常見問題

1. **Word導出失敗**

   ```
   錯誤: YAML parse exception
   解決: 系統已自動修複，重試即可
   ```
2. **PDF生成失敗**

   ```
   錯誤: wkhtmltopdf not found
   解決: Docker環境已預裝，本地環境需安裝
   ```
3. **中文顯示問題**

   ```
   錯誤: 中文字符顯示為方塊
   解決: Docker環境已配置中文字體
   ```

### 調試方法

1. **查看詳細日誌**

   ```bash
   docker logs TradingAgents-web --follow
   ```
2. **測試轉換功能**

   ```bash
   docker exec TradingAgents-web python test_conversion.py
   ```
3. **檢查依賴**

   ```bash
   docker exec TradingAgents-web pandoc --version
   docker exec TradingAgents-web wkhtmltopdf --version
   ```

## 🎯 最佳實踐

### 使用建議

1. **格式選擇**

   - **日常使用**: Markdown（輕量、可編辑）
   - **商業報告**: Word（專業、可編辑）
   - **正式發布**: PDF（固定格式、專業外觀）
2. **性能優化**

   - 大批量導出時使用CLI模式
   - 避免同時導出多種格式（按需選擇）
   - 定期清理導出文件
3. **品質保證**

   - 導出前檢查分析結果完整性
   - 驗證關鍵數據（價格、建議等）
   - 確認時間戳和股票代碼正確

## 🔮 未來規劃

### 計劃增强功能

1. **📊 圖表集成**
   - 技術指標圖表
   - 價格走勢圖
   - 風險評估圖表

2. **🎨 模板定制**
   - 多種報告模板
   - 企業品牌定制
   - 個性化樣式

3. **📧 自動分發**
   - 邮件自動發送
   - 定時報告生成
   - 多人協作分享

4. **📱 移動優化**
   - 移動端適配
   - 響應式布局
   - 觸屏操作優化

## 🙏 致謝

### 功能貢獻者

報告導出功能由社群貢獻者 **[@baiyuxiong](https://github.com/baiyuxiong)** (baiyuxiong@163.com) 設計並實現，包括：

- 📄 多格式報告導出系統架構設計
- 🔧 Pandoc集成和格式轉換實現
- 📝 Word/PDF導出功能開發
- 🛠️ 錯誤處理和降級策略設計
- 🧪 完整的測試和驗證流程

感謝他的傑出貢獻，讓TradingAgents-CN擁有了專業級的報告導出能力！

---

*最後更新: 2025-07-13*
*版本: cn-0.1.7*
*功能貢獻: [@baiyuxiong](https://github.com/baiyuxiong)*
