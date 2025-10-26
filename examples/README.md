# TradingAgents 示例程序 - DeepSeek V3 預覽版

本目錄包含了 TradingAgents 框架的各種示例程序，幫助用戶快速上手和理解如何使用不同的LLM提供商。

## ⚠️ 預覽版說明

當前為DeepSeek V3集成預覽版，重點展示DeepSeek V3的高性價比AI金融分析能力。

## 目錄結構

```
examples/
├── README.md                        # 本文件
├── demo_deepseek_analysis.py        # 🆕 DeepSeek V3股票分析演示（推薦）
├── demo_news_filtering.py           # 新聞過濾演示 (v0.1.12新增)
├── simple_analysis_demo.py          # 簡單分析演示
├── cli_demo.py                      # CLI命令行演示
├── batch_analysis.py                # 批量股票分析示例
├── custom_analysis_demo.py          # 自定義分析演示
├── config_management_demo.py        # 配置管理演示
├── data_dir_config_demo.py          # 數據目錄配置演示
├── my_stock_analysis.py             # 個人股票分析示例
├── stock_list_example.py            # 股票列表示例
├── stock_query_examples.py          # 股票查詢示例
├── test_news_timeout.py             # 新聞超時測試
├── token_tracking_demo.py           # Token跟蹤演示
├── tushare_demo.py                  # Tushare數據源演示
├── dashscope_examples/              # 阿里百炼大模型示例
│   ├── demo_dashscope.py           # 完整的阿里百炼演示
│   ├── demo_dashscope_chinese.py   # 中文優化版本
│   ├── demo_dashscope_simple.py    # 簡化版本（仅LLM測試）
│   └── demo_dashscope_no_memory.py # 禁用記忆功能版本
└── openai/                          # OpenAI 模型示例
    └── demo_openai.py              # OpenAI 演示程序
```

## 🚀 快速開始

### 🆕 使用DeepSeek V3（預覽版推薦）

DeepSeek V3是新集成的高性價比大模型，具有以下優势：
- 💰 **超低成本**：相比GPT-4節省90%+費用
- 🇨🇳 **中文優化**：優秀的中文理解和生成能力
- 📊 **專業分析**：適合金融投資分析場景
- 🔧 **完整集成**：支持Token統計和成本跟蹤

#### 1. 配置API密鑰

```bash
# 獲取DeepSeek API密鑰
# 1. 訪問 https://platform.deepseek.com/
# 2. 註冊账號並創建API Key

# 設置環境變量
set DEEPSEEK_API_KEY=sk-your_deepseek_api_key
set FINNHUB_API_KEY=your_finnhub_api_key

# 或編辑項目根目錄的 .env 文件
```

#### 2. 運行DeepSeek示例

```bash
# DeepSeek V3股票分析演示（推薦）
python examples/demo_deepseek_analysis.py
```

**示例特點**：
- 🎯 展示DeepSeek V3的基本面分析能力
- 💰 實時顯示Token使用量和成本
- 📊 包含真實財務指標和投資建议
- 🇨🇳 完全中文化的分析報告

### 🇨🇳 使用阿里百炼大模型

阿里百炼是國產大模型，具有以下優势：
- 無需翻墙，網絡穩定
- 中文理解能力强
- 成本相對較低
- 符合國內合規要求

#### 1. 配置API密鑰

```bash
# 設置環境變量
set DASHSCOPE_API_KEY=your_dashscope_api_key
set FINNHUB_API_KEY=your_finnhub_api_key

# 或編辑項目根目錄的 .env 文件
```

#### 2. 運行示例

```bash
# 中文優化版本（推薦）
python examples/dashscope_examples/demo_dashscope_chinese.py

# 完整功能版本
python examples/dashscope_examples/demo_dashscope.py

# 簡化測試版本
python examples/dashscope_examples/demo_dashscope_simple.py

# 無記忆功能版本（兼容性更好）
python examples/dashscope_examples/demo_dashscope_no_memory.py

# 其他示例
python examples/simple_analysis_demo.py
python examples/cli_demo.py
python examples/demo_news_filtering.py
```

### 🌍 使用OpenAI模型

如果您有OpenAI API密鑰，可以使用：

#### 1. 配置API密鑰

```bash
set OPENAI_API_KEY=your_openai_api_key
set FINNHUB_API_KEY=your_finnhub_api_key
```

#### 2. 運行示例

```bash
python examples/openai/demo_openai.py
```

## 示例程序說明

### 🎯 核心分析示例

| 文件名 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `demo_deepseek_analysis.py` | DeepSeek V3股票分析演示 | 完整分析流程展示 |
| `demo_news_filtering.py` | 新聞過濾演示 (v0.1.12新增) | 智能新聞分析 |
| `simple_analysis_demo.py` | 簡單分析演示 | 初學者入門 |
| `custom_analysis_demo.py` | 自定義分析演示 | 高級配置展示 |
| `batch_analysis.py` | 批量股票分析示例 | 處理多只股票 |

### 🤖 LLM模型示例

#### 阿里百炼示例

| 文件名 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `demo_dashscope_chinese.py` | 專門優化的中文股票分析 | 中文用戶，完整分析報告 |
| `demo_dashscope.py` | 完整的TradingAgents演示 | 完整功能測試 |
| `demo_dashscope_simple.py` | 簡化的LLM測試 | 快速驗證模型連接 |
| `demo_dashscope_no_memory.py` | 禁用記忆功能的版本 | 兼容性問題排查 |

#### OpenAI示例

| 文件名 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `demo_openai.py` | OpenAI模型演示 | 有OpenAI API密鑰的用戶 |

### 🛠️ 工具和配置示例

| 文件名 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `cli_demo.py` | CLI命令行演示 | 命令行界面使用 |
| `config_management_demo.py` | 配置管理演示 | 配置文件操作 |
| `data_dir_config_demo.py` | 數據目錄配置演示 | 自定義數據存储路徑 |
| `token_tracking_demo.py` | Token跟蹤演示 | 監控API使用情况 |
| `my_stock_analysis.py` | 個人股票分析示例 | 個性化配置 |

### 📊 數據源示例

| 文件名 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `tushare_demo.py` | Tushare數據源演示 | 數據獲取展示 |
| `stock_list_example.py` | 股票列表示例 | 批量處理股票代碼 |
| `stock_query_examples.py` | 股票查詢示例 | 各種查詢方式 |

### 🧪 測試和調試

| 文件名 | 功能描述 | 適用場景 |
|--------|----------|----------|
| `test_news_timeout.py` | 新聞超時測試 | 網絡連接調試 |

## 📖 使用指南

### 🎯 新手推薦路徑

1. **第一步**: 從簡單示例開始
   ```bash
   python examples/simple_analysis_demo.py
   ```

2. **第二步**: 嘗試CLI界面
   ```bash
   python examples/cli_demo.py
   ```

3. **第三步**: 體驗完整分析
   ```bash
   python examples/demo_deepseek_analysis.py
   ```

4. **第四步**: 探索新聞分析 (v0.1.12新增)
   ```bash
   python examples/demo_news_filtering.py
   ```

### 🔧 高級用戶路徑

1. **配置管理**: 學习如何管理配置
   ```bash
   python examples/config_management_demo.py
   ```

2. **批量分析**: 處理多只股票
   ```bash
   python examples/batch_analysis.py
   ```

3. **自定義分析**: 高級配置和定制
   ```bash
   python examples/custom_analysis_demo.py
   ```

4. **Token監控**: 監控API使用情况
   ```bash
   python examples/token_tracking_demo.py
   ```

### 📊 數據源選擇

- **Tushare用戶**: 使用 `tushare_demo.py`
- **股票列表處理**: 使用 `stock_list_example.py`
- **查詢功能測試**: 使用 `stock_query_examples.py`

### 🤖 模型選擇指南

| 模型 | 優势 | 適用場景 | 示例文件 |
|------|------|----------|----------|
| DeepSeek V3 | 免費、中文友好 | 日常使用、學习 | `demo_deepseek_analysis.py` |
| 阿里百炼 | 穩定、企業級 | 生產環境 | `dashscope_examples/` |
| OpenAI | 功能强大 | 高质量分析 | `openai/demo_openai.py` |

## 獲取API密鑰

### 阿里百炼 API 密鑰

1. 訪問 [阿里百炼控制台](https://dashscope.console.aliyun.com/)
2. 註冊/登錄阿里云账號
3. 開通百炼服務
4. 在控制台獲取API密鑰

### FinnHub API 密鑰

1. 訪問 [FinnHub官網](https://finnhub.io/)
2. 註冊免費账戶
3. 在儀表板獲取API密鑰

### OpenAI API 密鑰

1. 訪問 [OpenAI平台](https://platform.openai.com/)
2. 註冊账戶並完成驗證
3. 在API密鑰页面創建新密鑰

## 故障排除

### 常见問題

1. **API密鑰錯誤**
   - 檢查密鑰是否正確複制
   - 確認已開通相應服務

2. **網絡連接問題**
   - 阿里百炼：檢查國內網絡連接
   - OpenAI：可能需要科學上網

3. **依賴包問題**
   - 確保已安裝所有依賴：`pip install -r requirements.txt`
   - 檢查虛擬環境是否激活

4. **記忆功能錯誤**
   - 使用 `demo_dashscope_no_memory.py` 版本
   - 或參考測試目錄的集成測試

### 獲取幫助

- 查看項目文档：`docs/` 目錄
- 運行集成測試：`tests/integration/` 目錄
- 提交Issue：項目GitHub页面

## 🤝 贡献

欢迎提交新的示例程序！請確保：

1. 代碼清晰易懂
2. 包含詳細註釋
3. 提供使用說明
4. 遵循項目代碼規範

## 📞 支持

如果遇到問題，請：

1. 查看 [故障排除指南](../docs/troubleshooting/)
2. 提交 [Issue](https://github.com/your-repo/issues)
3. 加入我們的社区討論

## 📝 更新日誌

### v0.1.12 (2025-01-03)
- ✅ **修複**: 更正目錄結構路徑 (`dashscope/` → `dashscope_examples/`)
- ✅ **新增**: 完整的示例程序列表和分類說明
- ✅ **新增**: 新手和高級用戶使用指南
- ✅ **新增**: 模型選擇指南和數據源選擇建议
- ✅ **優化**: 文档結構和可讀性
- ✅ **覆蓋**: 19個示例文件的完整說明

### 文档統計
- **总示例文件**: 19個
- **文档覆蓋率**: 100%
- **分類數量**: 5個主要分類
- **使用指南**: 新手路徑 + 高級路徑

---

📍 **當前版本**: v0.1.12 | **最後更新**: 2025-01-03 | **文档狀態**: ✅ 已同步

## 許可證

本項目遵循項目根目錄的LICENSE文件。
