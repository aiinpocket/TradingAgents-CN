# 文档目錄結構

```
docs/
├── README.md                           # 文档主页和導航
├── STRUCTURE.md                        # 本文件 - 文档結構說明
│
├── overview/                           # 📋 概覽文档
│   ├── project-overview.md            # ✅ 項目概述
│   ├── quick-start.md                 # ✅ 快速開始指南
│   └── installation.md                # 🔄 詳細安裝說明
│
├── architecture/                      # 🏗️ 架構文档
│   ├── system-architecture.md         # ✅ 系統架構設計
│   ├── agent-architecture.md          # ✅ 智能體架構設計
│   ├── data-flow-architecture.md      # ✅ 數據流架構
│   └── graph-structure.md             # ✅ LangGraph 圖結構設計
│
├── agents/                            # 🤖 智能體文档
│   ├── analysts.md                    # ✅ 分析師团隊詳解
│   ├── researchers.md                 # 🔄 研究員团隊設計
│   ├── trader.md                      # 🔄 交易員智能體
│   ├── risk-management.md             # 🔄 風險管理智能體
│   └── managers.md                    # 🔄 管理層智能體
│
├── data/                              # 📊 數據處理文档
│   ├── data-sources.md                # 🔄 支持的數據源和API
│   ├── data-processing.md             # 🔄 數據獲取和處理
│   └── caching.md                     # 🔄 數據緩存策略
│
├── configuration/                     # ⚙️ 配置与部署
│   ├── config-guide.md               # 🔄 配置文件詳解
│   └── llm-config.md                 # 🔄 大語言模型配置
│
├── deployment/                        # 🚀 部署文档
│   └── deployment-guide.md           # 🔄 生產環境部署
│
├── development/                       # 🔧 開發指南
│   ├── dev-setup.md                  # 🔄 開發環境搭建
│   ├── code-structure.md             # 🔄 代碼組織結構
│   ├── extending.md                  # 🔄 如何擴展框架
│   └── testing.md                    # 🔄 測試策略和方法
│
├── api/                               # 📚 API參考
│   ├── core-api.md                   # 🔄 核心類和方法
│   ├── agents-api.md                 # 🔄 智能體接口
│   └── data-api.md                   # 🔄 數據處理接口
│
├── examples/                          # 💡 示例和教程
│   ├── basic-examples.md             # 🔄 基本使用示例
│   ├── advanced-examples.md          # 🔄 高級功能示例
│   └── custom-agents.md              # 🔄 創建自定義智能體
│
└── faq/                               # ❓ 常见問題
    ├── faq.md                         # 🔄 常见問題解答
    └── troubleshooting.md             # 🔄 問題診斷和解決
```

## 圖例說明

- ✅ **已完成**: 文档已創建並包含完整內容
- 🔄 **待完成**: 文档結構已規劃，內容待補充
- 📋 **概覽類**: 項目介紹和快速上手
- 🏗️ **架構類**: 系統設計和技術架構
- 🤖 **智能體類**: 各類智能體的詳細說明
- 📊 **數據類**: 數據處理和管理
- ⚙️ **配置類**: 系統配置和設置
- 🚀 **部署類**: 部署和運維
- 🔧 **開發類**: 開發和擴展指南
- 📚 **API類**: 接口和方法參考
- 💡 **示例類**: 使用示例和教程
- ❓ **幫助類**: 問題解答和故障排除

## 文档編寫規範

### 1. 文件命名
- 使用小寫字母和連字符
- 文件名應簡潔明了，體現內容主題
- 使用 `.md` 擴展名

### 2. 內容結構
- 每個文档都應包含清晰的標題層次
- 使用適當的Markdown語法
- 包含代碼示例和圖表說明
- 提供相關鏈接和參考

### 3. 代碼示例
- 提供完整可運行的代碼示例
- 包含必要的註釋和說明
- 使用一致的代碼風格
- 提供預期的輸出結果

### 4. 圖表和圖像
- 使用Mermaid圖表展示架構和流程
- 圖片應存储在適當的目錄中
- 提供圖表的文字描述
- 確保圖表在不同設备上的可讀性

## 維護指南

### 1. 定期更新
- 隨着代碼更新同步更新文档
- 定期檢查鏈接的有效性
- 更新過時的信息和示例

### 2. 质量控制
- 確保文档的準確性和完整性
- 檢查語法和拼寫錯誤
- 驗證代碼示例的可執行性

### 3. 用戶反馈
- 收集用戶對文档的反馈
- 根據常见問題完善文档
- 持续改進文档的可讀性

## 贡献指南

### 如何贡献文档

1. **Fork 項目**: 在GitHub上fork TradingAgents項目
2. **創建分支**: 為文档更新創建新分支
3. **編寫文档**: 按照規範編寫或更新文档
4. **提交PR**: 提交Pull Request並描述更改內容
5. **代碼審查**: 等待維護者審查和合並

### 文档贡献類型

- **新增文档**: 創建缺失的文档內容
- **內容完善**: 補充現有文档的詳細信息
- **錯誤修正**: 修複文档中的錯誤和過時信息
- **示例補充**: 添加更多使用示例和教程
- **翻譯工作**: 将文档翻譯成其他語言

### 贡献者認可

我們會在文档中認可所有贡献者的工作，包括：
- 在README中列出贡献者
- 在相關文档中標註作者信息
- 在發布說明中感谢贡献者

## 聯系方式

如果您對文档有任何建议或問題，請通過以下方式聯系我們：

- **GitHub Issues**: [提交文档相關問題](https://github.com/TauricResearch/TradingAgents/issues)
- **Discord**: [加入討論](https://discord.com/invite/hk9PGKShPK)
- **邮箱**: docs@tauric.ai

感谢您對TradingAgents文档建設的關註和支持！
