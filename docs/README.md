# TradingAgents-CN 文檔中心 (v0.1.12)

歡迎來到 TradingAgents-CN 多智能體金融交易框架的文檔中心。本文檔適用於中文增強版 v0.1.12，包含智能新聞分析模組、多LLM提供商集成、模型選擇持久化、Docker容器化部署和專業報告匯出功能。

## 🎯 版本亮點 (v0.1.12)

- 🧠 **智能新聞分析模組** - AI驅動的新聞過濾、品質評估、相關性分析
- 🔍 **多層次新聞過濾** - 智能過濾器、增強過濾器、統一新聞工具
- 📊 **新聞品質評估** - 深度語義分析、情感傾向識別、關鍵詞提取
- 📚 **完善測試文檔** - 15+測試文件、8個技術文檔、用戶指南
- 🗂️ **專案結構優化** - 文檔分類整理、測試文件統一、根目錄整潔
- 🤖 **多LLM提供商集成** - 多個提供商，60+模型，一站式AI體驗
- 💾 **模型選擇持久化** - URL參數儲存，刷新保持，配置分享

## 文檔結構

### 📋 概覽文檔
- [專案概述](./overview/project-overview.md) - 專案的基本介紹和目標
- [快速開始](./overview/quick-start.md) - 快速上手指南
- [安裝指南](./overview/installation.md) - 詳細的安裝說明

### 🏗️ 架構文檔
- [系統架構](./architecture/system-architecture.md) - 整體系統架構設計 (v0.1.7更新) ✨
- [容器化架構](./architecture/containerization-architecture.md) - Docker容器化架構設計 (v0.1.7新增) ✨
- [資料庫架構](./architecture/database-architecture.md) - MongoDB+Redis資料庫架構
- [智慧體架構](./architecture/agent-architecture.md) - 智慧體設計模式
- [資料流架構](./architecture/data-flow-architecture.md) - 資料處理流程
- [圖結構設計](./architecture/graph-structure.md) - LangGraph 圖結構設計
- [配置優化指南](./architecture/configuration-optimization.md) - 架構優化歷程詳解

### 🤖 智慧體文檔
- [分析師團隊](./agents/analysts.md) - 各類分析師智慧體詳解
- [研究員團隊](./agents/researchers.md) - 研究員智慧體設計
- [交易員](./agents/trader.md) - 交易決策智慧體
- [風險管理](./agents/risk-management.md) - 風險管理智慧體
- [管理層](./agents/managers.md) - 管理層智慧體

### 📊 資料處理
- [資料源集成](./data/data-sources.md) - 支援的資料源和API ✨
- [資料處理流程](./data/data-processing.md) - 資料獲取和處理
- [快取機制](./data/caching.md) - 資料快取策略

### 🎯 核心功能
- [🧠 智能新聞分析模組](./features/NEWS_FILTERING_SOLUTION_DESIGN.md) - AI驅動的新聞過濾與品質評估 (v0.1.12新增) ✨
- [📊 新聞品質分析](./features/NEWS_QUALITY_ANALYSIS_REPORT.md) - 新聞品質評估與相關性分析 (v0.1.12新增) ✨
- [🔧 新聞分析師工具修復](./features/NEWS_ANALYST_TOOL_CALL_FIX_REPORT.md) - 工具調用修復報告 (v0.1.12新增) ✨
- [🤖 多LLM提供商集成](./features/multi-llm-integration.md) - 多個提供商，60+模型支援 (v0.1.11) ✨
- [💾 模型選擇持久化](./features/model-persistence.md) - URL參數儲存，配置保持 (v0.1.11) ✨
- [📄 報告匯出功能](./features/report-export.md) - Word/PDF/Markdown多格式匯出 (v0.1.7) ✨
- [🐳 Docker容器化部署](./features/docker-deployment.md) - 一鍵部署完整環境 (v0.1.7) ✨
- [📰 新聞分析系統](./features/news-analysis-system.md) - 多源即時新聞聚合與分析 ✨

### ⚙️ 配置與部署
- [配置說明](./configuration/config-guide.md) - 配置檔案詳解 (v0.1.11更新) ✨
- [LLM配置](./configuration/llm-config.md) - 大語言模型配置 (v0.1.11更新) ✨
- [多提供商配置](./configuration/multi-provider-config.md) - 多個LLM提供商配置指南 (v0.1.11新增) ✨
- [OpenRouter配置](./configuration/openrouter-config.md) - OpenRouter 60+模型配置 (v0.1.11新增) ✨
- [Docker配置](./configuration/docker-config.md) - Docker環境配置指南 (v0.1.7) ✨
- [Google AI配置](./configuration/google-ai-setup.md) - Google AI (Gemini)模型配置指南 ✨
- [Token追蹤指南](./configuration/token-tracking-guide.md) - Token使用監控 (v0.1.7更新) ✨
- [資料目錄配置](./configuration/data-directory-configuration.md) - 資料儲存路徑配置
- [Web界面配置](../web/README.md) - Web管理界面使用指南

### 🤖 LLM集成專區
- [📚 LLM文檔目錄](./llm/README.md) - 大語言模型集成完整文檔 ✨
- [🔧 LLM集成指南](./llm/LLM_INTEGRATION_GUIDE.md) - 新LLM提供商接入指導 ✨
- [🧪 LLM測試驗證](./llm/LLM_TESTING_VALIDATION_GUIDE.md) - LLM功能測試指南 ✨

### 🔧 開發指南
- [開發環境搭建](./development/dev-setup.md) - 開發環境配置
- [程式碼結構](./development/code-structure.md) - 程式碼組織結構
- [擴充開發](./development/extending.md) - 如何擴充框架
- [測試指南](./development/testing.md) - 測試策略和方法

### 📋 版本發布 (v0.1.7更新)
- [更新日誌](./releases/CHANGELOG.md) - 所有版本更新記錄 ✨
- [v0.1.7發布說明](./releases/v0.1.7-release-notes.md) - 最新版本詳細說明 ✨
- [版本對比](./releases/version-comparison.md) - 各版本功能對比 ✨
- [升級指南](./releases/upgrade-guide.md) - 版本升級詳細指南 ✨

### 📚 API參考
- [核心API](./api/core-api.md) - 核心類別和方法
- [智慧體API](./api/agents-api.md) - 智慧體介面
- [資料API](./api/data-api.md) - 資料處理介面

### 🌐 使用指南
- [🧠 新聞過濾使用指南](./guides/NEWS_FILTERING_USER_GUIDE.md) - 智能新聞分析模組使用方法 (v0.1.12新增) ✨
- [🤖 多LLM提供商使用指南](./guides/multi-llm-usage-guide.md) - 多個提供商使用方法 (v0.1.11) ✨
- [💾 模型選擇持久化指南](./guides/model-persistence-guide.md) - 配置保存和分享方法 (v0.1.11) ✨
- [🔗 OpenRouter使用指南](./guides/openrouter-usage-guide.md) - 60+模型使用指南 (v0.1.11) ✨
- [🌐 Web界面指南](./usage/web-interface-guide.md) - Web界面詳細使用指南 (v0.1.11更新) ✨
- [📊 投資分析指南](./usage/investment_analysis_guide.md) - 投資分析完整流程
- [⚙️ 配置管理指南](./guides/config-management-guide.md) - 配置管理和成本統計使用方法 (v0.1.7) ✨
- [🐳 Docker部署指南](./guides/docker-deployment-guide.md) - Docker容器化部署詳細指南 (v0.1.7) ✨
- [📄 報告匯出指南](./guides/report-export-guide.md) - 專業報告匯出使用指南 (v0.1.7) ✨
- [📰 新聞分析系統使用指南](./guides/news-analysis-guide.md) - 即時新聞獲取與分析指南 ✨

### 💡 範例和教學
- [基礎範例](./examples/basic-examples.md) - 基本使用範例
- [進階範例](./examples/advanced-examples.md) - 進階功能範例
- [自訂智慧體](./examples/custom-agents.md) - 建立自訂智慧體

### ❓ 常見問題
- [FAQ](./faq/faq.md) - 常見問題解答
- [故障排除](./faq/troubleshooting.md) - 問題診斷和解決

### 📋 版本歷史
- [📄 v0.1.12 發布說明](./releases/v0.1.12-release-notes.md) - 智能新聞分析模組與專案結構優化 ✨
- [📄 v0.1.12 更新日誌](./releases/CHANGELOG_v0.1.12.md) - 詳細技術更新記錄 ✨
- [📄 v0.1.11 發布說明](./releases/v0.1.11-release-notes.md) - 多LLM提供商集成與模型選擇持久化
- [📄 v0.1.11 更新日誌](./releases/CHANGELOG_v0.1.11.md) - 詳細技術更新記錄
- [📄 完整更新日誌](./releases/CHANGELOG.md) - 所有版本歷史記錄
- [📄 升級指南](./releases/upgrade-guide.md) - 版本升級操作指南
- [📄 版本對比](./releases/version-comparison.md) - 各版本功能對比

## 貢獻指南

如果您想為文檔做出貢獻，請參考 [貢獻指南](../CONTRIBUTING.md)。

## 聯絡我們

- **GitHub Issues**: [提交問題和建議](https://github.com/hsliuping/TradingAgents-CN/issues)
- **Email**: hsliup@163.com
- **原專案**: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
