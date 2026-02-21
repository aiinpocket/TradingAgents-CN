# TradingAgents 範例程式

本目錄包含了 TradingAgents 框架的各種範例程式，幫助使用者快速上手和理解如何使用不同的 LLM 提供商。

## 目錄結構

```
examples/
├── README.md                        # 本檔案
├── simple_analysis_demo.py          # 簡單分析演示
├── cli_demo.py                      # CLI 命令列演示
├── batch_analysis.py                # 批量股票分析範例
├── custom_analysis_demo.py          # 自訂分析演示
├── config_management_demo.py        # 設定管理演示
├── data_dir_config_demo.py          # 資料目錄設定演示
├── my_stock_analysis.py             # 個人股票分析範例
├── stock_query_examples.py          # 股票查詢範例
├── test_news_timeout.py             # 新聞超時測試
├── token_tracking_demo.py           # Token 追蹤演示
├── enhanced_history_demo.py         # 增強歷史功能演示
└── test_installation.py             # 安裝驗證腳本
```

## 快速開始

### 使用 OpenAI 模型

#### 1. 設定 API 密鑰

```bash
# 設定環境變數
set OPENAI_API_KEY=your_openai_api_key
set FINNHUB_API_KEY=your_finnhub_api_key

# 或編輯專案根目錄的 .env 檔案
```

#### 2. 執行範例

```bash
# 簡單分析演示
python examples/simple_analysis_demo.py

# CLI 命令列演示
python examples/cli_demo.py

# 批量分析
python examples/batch_analysis.py
```

### 使用 Anthropic Claude 模型

如果您有 Anthropic API 密鑰，可以使用：

#### 1. 設定 API 密鑰

```bash
set ANTHROPIC_API_KEY=your_anthropic_api_key
set FINNHUB_API_KEY=your_finnhub_api_key
```

#### 2. 執行範例

```bash
python examples/simple_analysis_demo.py
```

## 範例程式說明

### 核心分析範例

| 檔案名稱 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `simple_analysis_demo.py` | 簡單分析演示 | 初學者入門 |
| `custom_analysis_demo.py` | 自訂分析演示 | 進階設定展示 |
| `batch_analysis.py` | 批量股票分析範例 | 處理多支股票 |

### 工具和設定範例

| 檔案名稱 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `cli_demo.py` | CLI 命令列演示 | 命令列介面使用 |
| `config_management_demo.py` | 設定管理演示 | 設定檔操作 |
| `data_dir_config_demo.py` | 資料目錄設定演示 | 自訂資料儲存路徑 |
| `token_tracking_demo.py` | Token 追蹤演示 | 監控 API 使用情況 |
| `my_stock_analysis.py` | 個人股票分析範例 | 個人化設定 |

### 資料來源範例

| 檔案名稱 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `stock_query_examples.py` | 股票查詢範例 | 各種查詢方式 |
| `enhanced_history_demo.py` | 增強歷史功能演示 | 歷史分析對比 |

### 測試和調試

| 檔案名稱 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `test_news_timeout.py` | 新聞超時測試 | 網路連接調試 |
| `test_installation.py` | 安裝驗證測試 | 驗證系統安裝 |

## 使用指南

### 新手推薦路徑

1. **第一步**: 驗證安裝
   ```bash
   python examples/test_installation.py
   ```

2. **第二步**: 從簡單範例開始
   ```bash
   python examples/simple_analysis_demo.py
   ```

3. **第三步**: 嘗試 CLI 介面
   ```bash
   python examples/cli_demo.py
   ```

4. **第四步**: 體驗完整分析
   ```bash
   python examples/custom_analysis_demo.py
   ```

### 進階使用者路徑

1. **設定管理**: 學習如何管理設定
   ```bash
   python examples/config_management_demo.py
   ```

2. **批量分析**: 處理多支股票
   ```bash
   python examples/batch_analysis.py
   ```

3. **自訂分析**: 進階設定和定制
   ```bash
   python examples/custom_analysis_demo.py
   ```

4. **Token 監控**: 監控 API 使用情況
   ```bash
   python examples/token_tracking_demo.py
   ```

### 模型選擇指南

| 模型 | 優勢 | 適用場景 | 設定方式 |
|------|------|----------|----------|
| OpenAI GPT-4 | 功能強大 | 高品質分析 | OPENAI_API_KEY |
| Anthropic Claude | 分析推理強 | 深度分析 | ANTHROPIC_API_KEY |

## 獲取 API 密鑰

### FinnHub API 密鑰

1. 訪問 [FinnHub 官網](https://finnhub.io/)
2. 註冊免費帳戶
3. 在儀表板獲取 API 密鑰

### OpenAI API 密鑰

1. 訪問 [OpenAI 平台](https://platform.openai.com/)
2. 註冊帳戶並完成驗證
3. 在 API 密鑰頁面建立新密鑰

### Anthropic API 密鑰

1. 訪問 [Anthropic Console](https://console.anthropic.com/)
2. 註冊帳戶並完成驗證
3. 在 API 密鑰頁面建立新密鑰

## 故障排除

### 常見問題

1. **API 密鑰錯誤**
   - 檢查密鑰是否正確複製
   - 確認已開通相應服務

2. **網路連接問題**
   - 檢查網路連接狀態
   - 確認防火牆設定

3. **相依套件問題**
   - 確保已安裝所有相依套件：`pip install -r requirements.txt`
   - 檢查虛擬環境是否啟動

### 獲取幫助

- 查看專案文件：`docs/` 目錄
- 執行整合測試：`tests/integration/` 目錄
- 提交 Issue：專案 GitHub 頁面

## 貢獻

歡迎提交新的範例程式！請確保：

1. 程式碼清晰易懂
2. 包含詳細註釋
3. 提供使用說明
4. 遵循專案程式碼規範

## 支援

如果遇到問題，請：

1. 查看 [故障排除指南](../docs/troubleshooting/)
2. 提交 [Issue](https://github.com/your-repo/issues)
3. 加入我們的社群討論

## 授權

本專案遵循專案根目錄的 LICENSE 檔案。
