# TradingAgents-CN 文档中心 (v0.1.12)

欢迎來到 TradingAgents-CN 多智能體金融交易框架的文档中心。本文档適用於中文增强版 v0.1.12，包含智能新聞分析模塊、多LLM提供商集成、模型選擇持久化、完整的A股支持、國產LLM集成、Docker容器化部署和專業報告導出功能。

## 🎯 版本亮點 (v0.1.12)

- 🧠 **智能新聞分析模塊** - AI驱動的新聞過濾、质量評估、相關性分析
- 🔍 **多層次新聞過濾** - 智能過濾器、增强過濾器、統一新聞工具
- 📊 **新聞质量評估** - 深度語義分析、情感倾向识別、關键詞提取
- 🛠️ **技術修複優化** - DashScope適配器修複、DeepSeek死循環修複
- 📚 **完善測試文档** - 15+測試文件、8個技術文档、用戶指南
- 🗂️ **項目結構優化** - 文档分類整理、測試文件統一、根目錄整潔
- 🤖 **多LLM提供商集成** - 4大提供商，60+模型，一站式AI體驗
- 💾 **模型選擇持久化** - URL參數存储，刷新保持，配置分享

## 文档結構

### 📋 概覽文档
- [項目概述](./overview/project-overview.md) - 項目的基本介紹和目標
- [快速開始](./overview/quick-start.md) - 快速上手指南
- [安裝指南](./overview/installation.md) - 詳細的安裝說明

### 🏗️ 架構文档
- [系統架構](./architecture/system-architecture.md) - 整體系統架構設計 (v0.1.7更新) ✨
- [容器化架構](./architecture/containerization-architecture.md) - Docker容器化架構設計 (v0.1.7新增) ✨
- [數據庫架構](./architecture/database-architecture.md) - MongoDB+Redis數據庫架構
- [智能體架構](./architecture/agent-architecture.md) - 智能體設計模式
- [數據流架構](./architecture/data-flow-architecture.md) - 數據處理流程
- [圖結構設計](./architecture/graph-structure.md) - LangGraph 圖結構設計
- [配置優化指南](./architecture/configuration-optimization.md) - 架構優化歷程詳解

### 🤖 智能體文档
- [分析師团隊](./agents/analysts.md) - 各類分析師智能體詳解
- [研究員团隊](./agents/researchers.md) - 研究員智能體設計
- [交易員](./agents/trader.md) - 交易決策智能體
- [風險管理](./agents/risk-management.md) - 風險管理智能體
- [管理層](./agents/managers.md) - 管理層智能體

### 📊 數據處理
- [數據源集成](./data/data-sources.md) - 支持的數據源和API (含A股支持) ✨
- [Tushare數據接口集成](./data/china_stock-api-integration.md) - A股數據源詳解 ✨
- [數據處理流程](./data/data-processing.md) - 數據獲取和處理
- [緩存機制](./data/caching.md) - 數據緩存策略

### 🎯 核心功能
- [🧠 智能新聞分析模塊](./features/NEWS_FILTERING_SOLUTION_DESIGN.md) - AI驱動的新聞過濾与质量評估 (v0.1.12新增) ✨
- [📊 新聞质量分析](./features/NEWS_QUALITY_ANALYSIS_REPORT.md) - 新聞质量評估与相關性分析 (v0.1.12新增) ✨
- [🔧 新聞分析師工具修複](./features/NEWS_ANALYST_TOOL_CALL_FIX_REPORT.md) - 工具調用修複報告 (v0.1.12新增) ✨
- [🤖 多LLM提供商集成](./features/multi-llm-integration.md) - 4大提供商，60+模型支持 (v0.1.11) ✨
- [💾 模型選擇持久化](./features/model-persistence.md) - URL參數存储，配置保持 (v0.1.11) ✨
- [📄 報告導出功能](./features/report-export.md) - Word/PDF/Markdown多格式導出 (v0.1.7) ✨
- [🐳 Docker容器化部署](./features/docker-deployment.md) - 一键部署完整環境 (v0.1.7) ✨
- [📰 新聞分析系統](./features/news-analysis-system.md) - 多源實時新聞聚合与分析 ✨

### ⚙️ 配置与部署
- [配置說明](./configuration/config-guide.md) - 配置文件詳解 (v0.1.11更新) ✨
- [LLM配置](./configuration/llm-config.md) - 大語言模型配置 (v0.1.11更新) ✨
- [多提供商配置](./configuration/multi-provider-config.md) - 4大LLM提供商配置指南 (v0.1.11新增) ✨
- [OpenRouter配置](./configuration/openrouter-config.md) - OpenRouter 60+模型配置 (v0.1.11新增) ✨
- [Docker配置](./configuration/docker-config.md) - Docker環境配置指南 (v0.1.7) ✨
- [DeepSeek配置](./configuration/deepseek-config.md) - DeepSeek V3模型配置 ✨
- [阿里百炼配置](./configuration/dashscope-config.md) - 阿里百炼模型配置 ✨
- [Google AI配置](./configuration/google-ai-setup.md) - Google AI (Gemini)模型配置指南 ✨
- [Token追蹤指南](./configuration/token-tracking-guide.md) - Token使用監控 (v0.1.7更新) ✨
- [數據目錄配置](./configuration/data-directory-configuration.md) - 數據存储路徑配置
- [Web界面配置](../web/README.md) - Web管理界面使用指南

### 🤖 LLM集成專区
- [📚 LLM文档目錄](./llm/README.md) - 大語言模型集成完整文档 ✨
- [🔧 LLM集成指南](./llm/LLM_INTEGRATION_GUIDE.md) - 新LLM提供商接入指導 ✨
- [🧪 LLM測試驗證](./llm/LLM_TESTING_VALIDATION_GUIDE.md) - LLM功能測試指南 ✨
- [🎯 千帆模型接入](./llm/QIANFAN_INTEGRATION_GUIDE.md) - 百度千帆專項接入指南 ✨

### 🔧 開發指南
- [開發環境搭建](./development/dev-setup.md) - 開發環境配置
- [代碼結構](./development/code-structure.md) - 代碼組織結構
- [擴展開發](./development/extending.md) - 如何擴展框架
- [測試指南](./development/testing.md) - 測試策略和方法

### 📋 版本發布 (v0.1.7更新)
- [更新日誌](./releases/CHANGELOG.md) - 所有版本更新記錄 ✨
- [v0.1.7發布說明](./releases/v0.1.7-release-notes.md) - 最新版本詳細說明 ✨
- [版本對比](./releases/version-comparison.md) - 各版本功能對比 ✨
- [升級指南](./releases/upgrade-guide.md) - 版本升級詳細指南 ✨

### 📚 API參考
- [核心API](./api/core-api.md) - 核心類和方法
- [智能體API](./api/agents-api.md) - 智能體接口
- [數據API](./api/data-api.md) - 數據處理接口

### 🌐 使用指南
- [🧠 新聞過濾使用指南](./guides/NEWS_FILTERING_USER_GUIDE.md) - 智能新聞分析模塊使用方法 (v0.1.12新增) ✨
- [🤖 多LLM提供商使用指南](./guides/multi-llm-usage-guide.md) - 4大提供商使用方法 (v0.1.11) ✨
- [💾 模型選擇持久化指南](./guides/model-persistence-guide.md) - 配置保存和分享方法 (v0.1.11) ✨
- [🔗 OpenRouter使用指南](./guides/openrouter-usage-guide.md) - 60+模型使用指南 (v0.1.11) ✨
- [🌐 Web界面指南](./usage/web-interface-guide.md) - Web界面詳細使用指南 (v0.1.11更新) ✨
- [📊 投資分析指南](./usage/investment_analysis_guide.md) - 投資分析完整流程
- [🇨🇳 A股分析指南](./guides/a-share-analysis-guide.md) - A股市場分析專項指南 (v0.1.7) ✨
- [⚙️ 配置管理指南](./guides/config-management-guide.md) - 配置管理和成本統計使用方法 (v0.1.7) ✨
- [🐳 Docker部署指南](./guides/docker-deployment-guide.md) - Docker容器化部署詳細指南 (v0.1.7) ✨
- [📄 報告導出指南](./guides/report-export-guide.md) - 專業報告導出使用指南 (v0.1.7) ✨
- [🧠 DeepSeek使用指南](./guides/deepseek-usage-guide.md) - DeepSeek V3模型使用指南 (v0.1.7) ✨
- [📰 新聞分析系統使用指南](./guides/news-analysis-guide.md) - 實時新聞獲取与分析指南 ✨

### 💡 示例和教程
- [基础示例](./examples/basic-examples.md) - 基本使用示例
- [高級示例](./examples/advanced-examples.md) - 高級功能示例
- [自定義智能體](./examples/custom-agents.md) - 創建自定義智能體

### ❓ 常见問題
- [FAQ](./faq/faq.md) - 常见問題解答
- [故障排除](./faq/troubleshooting.md) - 問題診斷和解決

### 📋 版本歷史
- [📄 v0.1.12 發布說明](./releases/v0.1.12-release-notes.md) - 智能新聞分析模塊与項目結構優化 ✨
- [📄 v0.1.12 更新日誌](./releases/CHANGELOG_v0.1.12.md) - 詳細技術更新記錄 ✨
- [📄 v0.1.11 發布說明](./releases/v0.1.11-release-notes.md) - 多LLM提供商集成与模型選擇持久化
- [📄 v0.1.11 更新日誌](./releases/CHANGELOG_v0.1.11.md) - 詳細技術更新記錄
- [📄 完整更新日誌](./releases/CHANGELOG.md) - 所有版本歷史記錄
- [📄 升級指南](./releases/upgrade-guide.md) - 版本升級操作指南
- [📄 版本對比](./releases/version-comparison.md) - 各版本功能對比

## 贡献指南

如果您想為文档做出贡献，請參考 [贡献指南](../CONTRIBUTING.md)。

## 聯系我們

- **GitHub Issues**: [提交問題和建议](https://github.com/hsliuping/TradingAgents-CN/issues)
- **邮箱**: hsliup@163.com
- 項目ＱＱ群：782124367
- **原項目**: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
