# TradingAgents 中文增強版

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-cn--0.1.15-green.svg)](./VERSION)
[![Documentation](https://img.shields.io/badge/docs-中文文檔-green.svg)](./docs/)
[![Original](https://img.shields.io/badge/基於-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)

>
> 🎯 **核心功能**: 原生OpenAI支持 | Google AI全面集成 | 自訂端點配置 | 智慧模型選擇 | 多LLM提供商支持 | 模型選擇持久化 | Docker容器化部署 | 專業報告匯出 | 完整A股支持 | 中文本地化

基於多智慧體大語言模型的**中文金融交易決策框架**。專為中文使用者優化，提供完整的A股/港股/美股分析能力。

## 🙏 致敬源專案

感謝 [Tauric Research](https://github.com/TauricResearch) 團隊創造的革命性多智慧體交易框架 [TradingAgents](https://github.com/TauricResearch/TradingAgents)！

**🎯 我們的使命**: 為中國使用者提供完整的中文化體驗，支持A股/港股市場，集成國產大模型，推動AI金融技術在中文社群的普及應用。

## 🎉 v1.0.0-preview 內測版本 - 全新架構升級

> 🚀 **重磅發布**: v1.0.0-preview 版本現已開啟內測！全新的 FastAPI + Vue 3 架構，帶來企業級的效能和體驗！

### ✨ 核心特性

#### 🏗️ **全新技術架構**
- **後端升級**: 從 Streamlit 遷移到 FastAPI，提供更強大的 RESTful API
- **前端重構**: 採用 Vue 3 + Element Plus，打造現代化的單頁應用
- **資料庫優化**: MongoDB + Redis 雙資料庫架構，效能提升 10 倍
- **容器化部署**: 完整的 Docker 多架構支持（amd64 + arm64）

#### 🎯 **企業級功能**
- **使用者權限管理**: 完整的使用者認證、角色管理、操作日誌系統
- **配置管理中心**: 視覺化的大模型配置、資料來源管理、系統設定
- **快取管理系統**: 智慧快取策略，支持 MongoDB/Redis/檔案多級快取
- **即時通知系統**: SSE 推送，即時跟蹤分析進度和系統狀態

#### 🤖 **智慧分析增強**
- **動態供應商管理**: 支持動態添加和配置 LLM 供應商
- **模型能力管理**: 智慧模型選擇，根據任務自動匹配最佳模型
- **多資料來源同步**: 統一的資料來源管理，支持 Tushare、AkShare、BaoStock
- **報告匯出功能**: 支持 Markdown/Word/PDF 多格式專業報告匯出

#### 🐳 **Docker 多架構支持**
- **跨平台部署**: 支持 x86_64 和 ARM64 架構（Apple Silicon、樹莓派、AWS Graviton）
- **GitHub Actions**: 自動化建構和發布 Docker 映像
- **一鍵部署**: 完整的 Docker Compose 配置，5 分鐘快速啟動

### 📊 技術棧升級

| 組件 | v0.1.x | v1.0.0-preview |
|------|--------|----------------|
| **後端框架** | Streamlit | FastAPI + Uvicorn |
| **前端框架** | Streamlit | Vue 3 + Vite + Element Plus |
| **資料庫** | 可選 MongoDB | MongoDB + Redis |
| **API 架構** | 單體應用 | RESTful API + WebSocket |
| **部署方式** | 本機/Docker | Docker 多架構 + GitHub Actions |

### 🎯 內測申請

v1.0.0-preview 版本目前處於**內測階段**，我們誠邀您參與體驗和測試！

####  使用指南

在申請試用前，建議先閱讀詳細的使用指南：

**[📘 TradingAgents-CN v1.0.0-preview 使用指南](https://mp.weixin.qq.com/s/ppsYiBncynxlsfKFG8uEbw)**

使用指南包含：
- ✅ 完整的功能介紹和操作演示
- ✅ 詳細的配置說明和最佳實踐
- ✅ 常見問題解答和故障排除
- ✅ 實際使用案例和效果展示

#### 如何申請試用

1. **關註公眾號**: 微信搜尋 **"TradingAgents-CN"** 並關註
2. **提交申請**: 透過公眾號私訊發送以下資訊：
   - 您的姓名/暱稱
   - 使用場景（個人學習/企業應用/學術研究）
   - 技術背景（可選）
   - 期望的功能或建議（可選）
3. **獲取權限**: 我們會在 1-2 個工作日內回覆，並提供：
   - 內測版本訪問地址
   - 詳細的使用文檔
   - 技術支持和交流群

#### 🎁 內測使用者福利

- ✅ **優先體驗**: 第一時間體驗最新功能
- ✅ **技術支持**: 專屬技術支持和問題解答
- ✅ **功能定製**: 您的需求將優先納入開發計劃
- ✅ **社群榮譽**: 內測貢獻者將在專案中特別致謝

#### 📱 聯絡方式

- **微信公眾號**: TradingAgents-CN（推薦）

  <img src="assets/weixin.png" alt="微信公眾號" width="200"/>

---

## 🆕 v0.1.15 重大更新

### 🤖 LLM生態系統大升級

- **千帆大模型支持**: 新增百度千帆(ERNIE)大模型完整集成
- **LLM適配器重構**: 統一的OpenAI兼容適配器架構
- **多厂商支持**: 支持更多國產大模型提供商
- **集成指南**: 完整的LLM集成開發文档和測試工具

### 📚 學術研究支持

- **TradingAgents論文**: 完整的中文翻譯版本和深度解讀
- **技術博客**: 詳細的技術分析和實現原理解讀
- **學術資料**: PDF論文和相關研究資料
- **引用支持**: 標準的學術引用格式和參考文献

### 🛠️ 開發者體驗升級

- **開發工作流**: 標準化的開發流程和分支管理規範
- **安裝驗證**: 完整的安裝測試和驗證腳本
- **文档重構**: 結構化的文档系統和快速開始指南
- **PR模板**: 標準化的Pull Request模板和代碼審查流程

### 🔧 企業級工具鏈

- **分支保護**: GitHub分支保護策略和安全規則
- **緊急程序**: 完整的緊急處理和故障恢複程序
- **測試框架**: 增强的測試覆蓋和驗證工具
- **部署指南**: 企業級部署和配置管理

## 📋 v0.1.14 功能回顧

### 👥 用戶權限管理系統

- **完整用戶管理**: 新增用戶註冊、登錄、權限控制功能
- **角色權限**: 支持多級用戶角色和權限管理
- **會話管理**: 安全的用戶會話和狀態管理
- **用戶活動日誌**: 完整的用戶操作記錄和審計功能

### 🔐 Web用戶認證系統

- **登錄組件**: 現代化的用戶登錄界面
- **認證管理器**: 統一的用戶認證和授權管理
- **安全增强**: 密碼加密、會話安全等安全機制
- **用戶儀表板**: 個性化的用戶活動儀表板

### 🗄️ 數據管理優化

- **MongoDB集成增强**: 改進的MongoDB連接和數據管理
- **數據目錄重組**: 優化的數據存储結構和管理
- **數據迁移腳本**: 完整的數據迁移和备份工具
- **緩存優化**: 提升數據加載和分析結果緩存性能

### 🧪 測試覆蓋增强

- **功能測試腳本**: 新增6個專項功能測試腳本
- **工具處理器測試**: Google工具處理器修複驗證
- **引導自動隐藏測試**: UI交互功能測試
- **在線工具配置測試**: 工具配置和選擇逻辑測試
- **真實場景測試**: 實际使用場景的端到端測試
- **美股獨立性測試**: 美股分析功能獨立性驗證

---

## 🆕 v0.1.13 重大更新

### 🤖 原生OpenAI端點支持

- **自定義OpenAI端點**: 支持配置任意OpenAI兼容的API端點
- **灵活模型選擇**: 可以使用任何OpenAI格式的模型，不限於官方模型
- **智能適配器**: 新增原生OpenAI適配器，提供更好的兼容性和性能
- **配置管理**: 統一的端點和模型配置管理系統

### 🧠 Google AI生態系統全面集成

- **三大Google AI包支持**: langchain-google-genai、google-generativeai、google-genai
- **9個驗證模型**: gemini-2.5-pro, gemini-2.5-flash, gemini-2.0-flash等最新模型
- **Google工具處理器**: 專門的Google AI工具調用處理器
- **智能降級機制**: 高級功能失败時自動降級到基础功能

### 🔧 LLM適配器架構優化

- **GoogleOpenAIAdapter**: 新增Google AI的OpenAI兼容適配器
- **統一接口**: 所有LLM提供商使用統一的調用接口
- **錯誤處理增强**: 改進的異常處理和自動重試機制
- **性能監控**: 添加LLM調用性能監控和統計

### 🎨 Web界面智能優化

- **智能模型選擇**: 根據可用性自動選擇最佳模型
- **KeyError修複**: 彻底解決模型選擇中的KeyError問題
- **UI響應優化**: 改進模型切換的響應速度和用戶體驗
- **錯誤提示**: 更友好的錯誤提示和解決建议

## 🆕 v0.1.12 重大更新

### 🧠 智能新聞分析模塊

- **智能新聞過濾器**: 基於AI的新聞相關性評分和质量評估
- **多層次過濾機制**: 基础過濾、增强過濾、集成過濾三級處理
- **新聞质量評估**: 自動识別和過濾低质量、重複、無關新聞
- **統一新聞工具**: 整合多個新聞源，提供統一的新聞獲取接口

### 🔧 技術修複和優化

- **DashScope適配器修複**: 解決工具調用兼容性問題
- **DeepSeek死循環修複**: 修複新聞分析師的無限循環問題
- **LLM工具調用增强**: 提升工具調用的可靠性和穩定性
- **新聞檢索器優化**: 增强新聞數據獲取和處理能力

### 📚 完善測試和文档

- **全面測試覆蓋**: 新增15+個測試文件，覆蓋所有新功能
- **詳細技術文档**: 新增8個技術分析報告和修複文档
- **用戶指南完善**: 新增新聞過濾使用指南和最佳實踐
- **演示腳本**: 提供完整的新聞過濾功能演示

### 🗂️ 項目結構優化

- **文档分類整理**: 按功能将文档分類到docs子目錄
- **示例代碼歸位**: 演示腳本統一到examples目錄
- **根目錄整潔**: 保持根目錄簡潔，提升項目專業度

## 🎯 核心特性

### 🤖 多智能體協作架構

- **專業分工**: 基本面、技術面、新聞面、社交媒體四大分析師
- **結構化辩論**: 看涨/看跌研究員進行深度分析
- **智能決策**: 交易員基於所有輸入做出最终投資建议
- **風險管理**: 多層次風險評估和管理機制

## 🖥️ Web界面展示

### 📸 界面截圖

> 🎨 **現代化Web界面**: 基於Streamlit構建的響應式Web應用，提供直觀的股票分析體驗

#### 🏠 主界面 - 分析配置

![1755003162925](images/README/1755003162925.png)

![1755002619976](images/README/1755002619976.png)

*智能配置面板，支持多市場股票分析，5級研究深度選擇*

#### 📊 實時分析進度

![1755002731483](images/README/1755002731483.png)

*實時進度跟蹤，可視化分析過程，智能時間預估*

#### 📈 分析結果展示

![1755002901204](images/README/1755002901204.png)

![1755002924844](images/README/1755002924844.png)

![1755002939905](images/README/1755002939905.png)

![1755002968608](images/README/1755002968608.png)

![1755002985903](images/README/1755002985903.png)

![1755003004403](images/README/1755003004403.png)

![1755003019759](images/README/1755003019759.png)

![1755003033939](images/README/1755003033939.png)

![1755003048242](images/README/1755003048242.png)

![1755003064598](images/README/1755003064598.png)

![1755003090603](images/README/1755003090603.png)

*專業投資報告，多維度分析結果，一键導出功能*

### 🎯 核心功能特色

#### 📋 **智能分析配置**

- **🌍 多市場支持**: 美股、A股、港股一站式分析
- **🎯 5級研究深度**: 從2分鐘快速分析到25分鐘全面研究
- **🤖 智能體選擇**: 市場技術、基本面、新聞、社交媒體分析師
- **📅 灵活時間設置**: 支持歷史任意時間點分析

#### 🚀 **實時進度跟蹤**

- **📊 可視化進度**: 實時顯示分析進展和剩余時間
- **🔄 智能步骤识別**: 自動识別當前分析階段
- **⏱️ 準確時間預估**: 基於歷史數據的智能時間計算
- **💾 狀態持久化**: 页面刷新不丢失分析進度

#### 📈 **專業結果展示**

- **🎯 投資決策**: 明確的买入/持有/卖出建议
- **📊 多維分析**: 技術面、基本面、新聞面综合評估
- **🔢 量化指標**: 置信度、風險評分、目標價位
- **📄 專業報告**: 支持Markdown/Word/PDF格式導出

#### 🤖 **多LLM模型管理**

- **🌐 4大提供商**: DashScope、DeepSeek、Google AI、OpenRouter
- **🎯 60+模型選擇**: 從經濟型到旗舰級模型全覆蓋
- **💾 配置持久化**: URL參數存储，刷新保持設置
- **⚡ 快速切換**: 5個熱門模型一键選擇按钮

### 🎮 Web界面操作指南

#### 🚀 **快速開始流程**

1. **啟動應用**: `python start_web.py` 或 `docker-compose up -d`
2. **訪問界面**: 浏覽器打開 `http://localhost:8501`
3. **配置模型**: 侧邊栏選擇LLM提供商和模型
4. **輸入股票**: 輸入股票代碼（如 AAPL、000001、0700.HK）
5. **選擇深度**: 根據需求選擇1-5級研究深度
6. **開始分析**: 點擊"🚀 開始分析"按钮
7. **查看結果**: 實時跟蹤進度，查看分析報告
8. **導出報告**: 一键導出專業格式報告

#### 📊 **支持的股票代碼格式**

- **🇺🇸 美股**: `AAPL`, `TSLA`, `MSFT`, `NVDA`, `GOOGL`
- **🇨🇳 A股**: `000001`, `600519`, `300750`, `002415`
- **🇭🇰 港股**: `0700.HK`, `9988.HK`, `3690.HK`, `1810.HK`

#### 🎯 **研究深度說明**

- **1級 (2-4分鐘)**: 快速概覽，基础技術指標
- **2級 (4-6分鐘)**: 標準分析，技術+基本面
- **3級 (6-10分鐘)**: 深度分析，加入新聞情绪 ⭐ **推薦**
- **4級 (10-15分鐘)**: 全面分析，多轮智能體辩論
- **5級 (15-25分鐘)**: 最深度分析，完整研究報告

#### 💡 **使用技巧**

- **🔄 實時刷新**: 分析過程中可隨時刷新页面，進度不丢失
- **📱 移動適配**: 支持手機和平板設备訪問
- **🎨 深色模式**: 自動適配系統主題設置
- **⌨️ 快捷键**: 支持Enter键快速提交分析
- **📋 歷史記錄**: 自動保存最近的分析配置

> 📖 **詳細指南**: 完整的Web界面使用說明請參考 [🖥️ Web界面詳細使用指南](docs/usage/web-interface-detailed-guide.md)

## 🎯 功能特性

### 🚀  智能新聞分析✨ **v0.1.12重大升級**


| 功能特性               | 狀態        | 詳細說明                                 |
| ---------------------- | ----------- | ---------------------------------------- |
| **🧠 智能新聞分析**    | 🆕 v0.1.12  | AI新聞過濾，质量評估，相關性分析         |
| **🔧 新聞過濾器**      | 🆕 v0.1.12  | 多層次過濾，基础/增强/集成三級處理       |
| **📰 統一新聞工具**    | 🆕 v0.1.12  | 整合多源新聞，統一接口，智能檢索         |
| **🤖 多LLM提供商**     | 🆕 v0.1.11  | 4大提供商，60+模型，智能分類管理         |
| **💾 模型選擇持久化**  | 🆕 v0.1.11  | URL參數存储，刷新保持，配置分享          |
| **🎯 快速選擇按钮**    | 🆕 v0.1.11  | 一键切換熱門模型，提升操作效率           |
| **📊 實時進度顯示**    | ✅ v0.1.10  | 異步進度跟蹤，智能步骤识別，準確時間計算 |
| **💾 智能會話管理**    | ✅ v0.1.10  | 狀態持久化，自動降級，跨页面恢複         |
| **🎯 一键查看報告**    | ✅ v0.1.10  | 分析完成後一键查看，智能結果恢複         |
| **🖥️ Streamlit界面** | ✅ 完整支持 | 現代化響應式界面，實時交互和數據可視化   |
| **⚙️ 配置管理**      | ✅ 完整支持 | Web端API密鑰管理，模型選擇，參數配置     |

### 🎨 CLI用戶體驗 ✨ **v0.1.9優化**


| 功能特性                | 狀態        | 詳細說明                             |
| ----------------------- | ----------- | ------------------------------------ |
| **🖥️ 界面与日誌分離** | ✅ 完整支持 | 用戶界面清爽美觀，技術日誌獨立管理   |
| **🔄 智能進度顯示**     | ✅ 完整支持 | 多階段進度跟蹤，防止重複提示         |
| **⏱️ 時間預估功能**   | ✅ 完整支持 | 智能分析階段顯示預計耗時             |
| **🌈 Rich彩色輸出**     | ✅ 完整支持 | 彩色進度指示，狀態圖標，視觉效果提升 |

### 🧠 LLM模型支持 ✨ **v0.1.13全面升級**


| 模型提供商        | 支持模型                     | 特色功能                | 新增功能 |
| ----------------- | ---------------------------- | ----------------------- | -------- |
| **🇨🇳 阿里百炼** | qwen-turbo/plus/max          | 中文優化，成本效益高    | ✅ 集成  |
| **🇨🇳 DeepSeek** | deepseek-chat                | 工具調用，性價比極高    | ✅ 集成  |
| **🌍 Google AI**  | **9個驗證模型**              | 最新Gemini 2.5系列      | 🆕 升級  |
| ├─**最新旗舰**  | gemini-2.5-pro/flash         | 最新旗舰，超快響應      | 🆕 新增  |
| ├─**穩定推薦**  | gemini-2.0-flash             | 推薦使用，平衡性能      | 🆕 新增  |
| ├─**經典强大**  | gemini-1.5-pro/flash         | 經典穩定，高质量分析    | ✅ 集成  |
| └─**轻量快速**  | gemini-2.5-flash-lite        | 轻量級任務，快速響應    | 🆕 新增  |
| **🌐 原生OpenAI** | **自定義端點支持**           | 任意OpenAI兼容端點      | 🆕 新增  |
| **🌐 OpenRouter** | **60+模型聚合平台**          | 一個API訪問所有主流模型 | ✅ 集成  |
| ├─**OpenAI**    | o4-mini-high, o3-pro, GPT-4o | 最新o系列，推理專業版   | ✅ 集成  |
| ├─**Anthropic** | Claude 4 Opus/Sonnet/Haiku   | 顶級性能，平衡版本      | ✅ 集成  |
| ├─**Meta**      | Llama 4 Maverick/Scout       | 最新Llama 4系列         | ✅ 集成  |
| └─**自定義**    | 任意OpenRouter模型ID         | 無限擴展，個性化選擇    | ✅ 集成  |

**🎯 快速選擇**: 5個熱門模型快速按钮 | **💾 持久化**: URL參數存储，刷新保持 | **🔄 智能切換**: 一键切換不同提供商

### 📊 數據源与市場


| 市場類型      | 數據源                   | 覆蓋範围                     |
| ------------- | ------------------------ | ---------------------------- |
| **🇨🇳 A股**  | Tushare, AkShare, 通達信 | 沪深两市，實時行情，財報數據 |
| **🇭🇰 港股** | AkShare, Yahoo Finance   | 港交所，實時行情，基本面     |
| **🇺🇸 美股** | FinnHub, Yahoo Finance   | NYSE, NASDAQ，實時數據       |
| **📰 新聞**   | Google News              | 實時新聞，多語言支持         |

### 🤖 智能體团隊

**分析師团隊**: 📈市場分析 | 💰基本面分析 | 📰新聞分析 | 💬情绪分析
**研究团隊**: 🐂看涨研究員 | 🐻看跌研究員 | 🎯交易決策員
**管理層**: 🛡️風險管理員 | 👔研究主管

## 🚀 快速開始

### 🐳 Docker部署 (推薦)

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 配置環境變量
cp .env.example .env
# 編辑 .env 文件，填入API密鑰

# 3. 啟動服務
# 首次啟動或代碼變更時（需要構建鏡像）
docker-compose up -d --build

# 日常啟動（鏡像已存在，無代碼變更）
docker-compose up -d

# 智能啟動（自動判斷是否需要構建）
# Windows環境
powershell -ExecutionPolicy Bypass -File scripts\smart_start.ps1

# Linux/Mac環境
chmod +x scripts/smart_start.sh && ./scripts/smart_start.sh

# 4. 訪問應用
# Web界面: http://localhost:8501
```

### 💻 本地部署

```bash
# 1. 升級pip (重要！避免安裝錯誤)
python -m pip install --upgrade pip

# 2. 安裝依賴（推薦使用鎖定版本，安裝速度最快）
pip install -r requirements-lock.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -e . --no-deps

# 或一步安裝（會重新解析依賴，速度較慢）
# pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 💡 國內用戶推薦使用鏡像加速（詳见 docs/installation-mirror.md）
# ⚠️ Windows 用戶如遇到 PyYAML 編譯錯誤，使用鎖定版本可避免此問題

# 3. 啟動應用
python start_web.py

# 4. 訪問 http://localhost:8501
```

### 📊 開始分析

1. **選擇模型**: DeepSeek V3 / 通義千問 / Gemini
2. **輸入股票**: `000001` (A股) / `AAPL` (美股) / `0700.HK` (港股)
3. **開始分析**: 點擊"🚀 開始分析"按钮
4. **實時跟蹤**: 觀察實時進度和分析步骤
5. **查看報告**: 點擊"📊 查看分析報告"按钮
6. **導出報告**: 支持Word/PDF/Markdown格式

## 🔐 用戶權限管理

### 🔑 默認账號信息

系統提供以下默認账號，首次啟動時自動創建：

| 用戶名 | 密碼 | 角色 | 權限說明 |
|--------|------|------|----------|
| **admin** | **admin123** | 管理員 | 完整系統權限，用戶管理，系統配置 |
| **user** | **user123** | 普通用戶 | 股票分析，報告查看，基础功能 |

> ⚠️ **安全提醒**: 首次登錄後請立即修改默認密碼！

### 🛡️ 權限控制體系

- **🔐 登錄認證**: 基於用戶名密碼的安全認證
- **👥 角色管理**: 管理員、普通用戶等多級權限
- **⏰ 會話管理**: 自動超時保護，安全登出
- **📊 操作日誌**: 完整的用戶活動記錄

### 🛠️ 用戶管理工具

系統提供完整的命令行用戶管理工具：

#### Windows 用戶
```powershell
# 使用 PowerShell 腳本
.\scripts\user_manager.ps1 list                    # 列出所有用戶
.\scripts\user_manager.ps1 change-password admin   # 修改密碼
.\scripts\user_manager.ps1 create newuser trader  # 創建新用戶
.\scripts\user_manager.ps1 delete olduser         # 刪除用戶

# 或使用批處理文件
.\scripts\user_manager.bat list
```

#### Python 腳本（跨平台）
```bash
# 直接使用 Python 腳本
python scripts/user_password_manager.py list
python scripts/user_password_manager.py change-password admin
python scripts/user_password_manager.py create newuser --role trader
python scripts/user_password_manager.py delete olduser
python scripts/user_password_manager.py reset  # 重置為默認配置
```

### 📋 支持的用戶操作

- **📝 列出用戶**: 查看所有用戶及其角色權限
- **🔑 修改密碼**: 安全的密碼更新機制
- **👤 創建用戶**: 支持自定義角色和權限
- **🗑️ 刪除用戶**: 安全的用戶刪除功能
- **🔄 重置配置**: 恢複默認用戶設置

### 📁 配置文件位置

用戶配置存储在：`web/config/users.json`

> 📚 **詳細文档**: 完整的用戶管理指南請參考 [scripts/USER_MANAGEMENT.md](scripts/USER_MANAGEMENT.md)

### 🚧 當前版本限制

- ❌ 暂不支持在線用戶註冊
- ❌ 暂不支持Web界面的角色管理
- ✅ 支持完整的命令行用戶管理
- ✅ 支持完整的權限控制框架

---

## 🎯 核心優势

- **🧠 智能新聞分析**: v0.1.12新增AI驱動的新聞過濾和质量評估系統
- **🔧 多層次過濾**: 基础、增强、集成三級新聞過濾機制
- **📰 統一新聞工具**: 整合多源新聞，提供統一的智能檢索接口
- **🆕 多LLM集成**: v0.1.11新增4大提供商，60+模型，一站式AI體驗
- **💾 配置持久化**: 模型選擇真正持久化，URL參數存储，刷新保持
- **🎯 快速切換**: 5個熱門模型快速按钮，一键切換不同AI
- **🆕 實時進度**: v0.1.10異步進度跟蹤，告別黑盒等待
- **💾 智能會話**: 狀態持久化，页面刷新不丢失分析結果
- **🔐 用戶權限**: v0.1.14新增完整的用戶認證和權限管理體系
- **🇨🇳 中國優化**: A股/港股數據 + 國產LLM + 中文界面
- **🐳 容器化**: Docker一键部署，環境隔離，快速擴展
- **📄 專業報告**: 多格式導出，自動生成投資建议
- **🛡️ 穩定可靠**: 多層數據源，智能降級，錯誤恢複

## 🔧 技術架構

**核心技術**: Python 3.10+ | LangChain | Streamlit | MongoDB | Redis
**AI模型**: DeepSeek V3 | 阿里百炼 | Google AI | OpenRouter(60+模型) | OpenAI
**數據源**: Tushare | AkShare | FinnHub | Yahoo Finance
**部署**: Docker | Docker Compose | 本地部署

## 📚 文档和支持

- **📖 完整文档**: [docs/](./docs/) - 安裝指南、使用教程、API文档
- **🚨 故障排除**: [troubleshooting/](./docs/troubleshooting/) - 常见問題解決方案
- **🔄 更新日誌**: [CHANGELOG.md](./docs/releases/CHANGELOG.md) - 詳細版本歷史
- **🚀 快速開始**: [QUICKSTART.md](./QUICKSTART.md) - 5分鐘快速部署指南

## 🆚 中文增强特色

**相比原版新增**: 智能新聞分析 | 多層次新聞過濾 | 新聞质量評估 | 統一新聞工具 | 多LLM提供商集成 | 模型選擇持久化 | 快速切換按钮 | | 實時進度顯示 | 智能會話管理 | 中文界面 | A股數據 | 國產LLM | Docker部署 | 專業報告導出 | 統一日誌管理 | Web配置界面 | 成本優化

**Docker部署包含的服務**:

- 🌐 **Web應用**: TradingAgents-CN主程序
- 🗄️ **MongoDB**: 數據持久化存储
- ⚡ **Redis**: 高速緩存
- 📊 **MongoDB Express**: 數據庫管理界面
- 🎛️ **Redis Commander**: 緩存管理界面

#### 💻 方式二：本地部署

**適用場景**: 開發環境、自定義配置、離線使用

### 環境要求

- Python 3.10+ (推薦 3.11)
- 4GB+ RAM (推薦 8GB+)
- 穩定的網絡連接

### 安裝步骤

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 創建虛擬環境
python -m venv env
# Windows
env\Scripts\activate
# Linux/macOS
source env/bin/activate

# 3. 升級pip
python -m pip install --upgrade pip

# 4. 安裝所有依賴
pip install -e .

# 💡 國內用戶推薦使用鏡像加速（詳见 docs/installation-mirror.md）
# pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 註意：requirements.txt已包含所有必需依賴：
# - 數據庫支持 (MongoDB + Redis)
# - 多市場數據源 (Tushare, AKShare, FinnHub等)
# - Web界面和報告導出功能
```

### 配置API密鑰

#### 🇨🇳 推薦：使用阿里百炼（國產大模型）

```bash
# 複制配置模板
cp .env.example .env

# 編辑 .env 文件，配置以下必需的API密鑰：
DASHSCOPE_API_KEY=your_dashscope_api_key_here
FINNHUB_API_KEY=your_finnhub_api_key_here

# 推薦：Tushare API（專業A股數據）
TUSHARE_TOKEN=your_tushare_token_here
TUSHARE_ENABLED=true

# 可選：其他AI模型API
GOOGLE_API_KEY=your_google_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# 數據庫配置（可選，提升性能）
# 本地部署使用標準端口
MONGODB_ENABLED=false  # 設為true啟用MongoDB
REDIS_ENABLED=false    # 設為true啟用Redis
MONGODB_HOST=localhost
MONGODB_PORT=27017     # 標準MongoDB端口
REDIS_HOST=localhost
REDIS_PORT=6379        # 標準Redis端口

# Docker部署時需要修改主機名
# MONGODB_HOST=mongodb
# REDIS_HOST=redis
```

#### 📋 部署模式配置說明

**本地部署模式**：

```bash
# 數據庫配置（本地部署）
MONGODB_ENABLED=true
REDIS_ENABLED=true
MONGODB_HOST=localhost      # 本地主機
MONGODB_PORT=27017         # 標準端口
REDIS_HOST=localhost       # 本地主機
REDIS_PORT=6379           # 標準端口
```

**Docker部署模式**：

```bash
# 數據庫配置（Docker部署）
MONGODB_ENABLED=true
REDIS_ENABLED=true
MONGODB_HOST=mongodb       # Docker容器服務名
MONGODB_PORT=27017        # 標準端口
REDIS_HOST=redis          # Docker容器服務名
REDIS_PORT=6379          # 標準端口
```

> 💡 **配置提示**：
>
> - 本地部署：需要手動啟動MongoDB和Redis服務
> - Docker部署：數據庫服務通過docker-compose自動啟動
> - 端口冲突：如果本地已有數據庫服務，可修改docker-compose.yml中的端口映射

#### 🌍 可選：使用國外模型

```bash
# OpenAI (需要科學上網)
OPENAI_API_KEY=your_openai_api_key

# Anthropic (需要科學上網)
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 🗄️ 數據庫配置（MongoDB + Redis）

#### 高性能數據存储支持

本項目支持 **MongoDB** 和 **Redis** 數據庫，提供：

- **📊 股票數據緩存**: 减少API調用，提升響應速度
- **🔄 智能降級機制**: MongoDB → API → 本地緩存的多層數據源
- **⚡ 高性能緩存**: Redis緩存熱點數據，毫秒級響應
- **🛡️ 數據持久化**: MongoDB存储歷史數據，支持離線分析

#### 數據庫部署方式

**🐳 Docker部署（推薦）**

如果您使用Docker部署，數據庫已自動包含在內：

```bash
# Docker部署會自動啟動所有服務，包括：
docker-compose up -d --build
# - Web應用 (端口8501)
# - MongoDB (端口27017)
# - Redis (端口6379)
# - 數據庫管理界面 (端口8081, 8082)
```

**💻 本地部署 - 數據庫配置**

如果您使用本地部署，可以選擇以下方式：

**方式一：仅啟動數據庫服務**

```bash
# 仅啟動 MongoDB + Redis 服務（不啟動Web應用）
docker-compose up -d mongodb redis mongo-express redis-commander

# 查看服務狀態
docker-compose ps

# 停止服務
docker-compose down
```

**方式二：完全本地安裝**

```bash
# 數據庫依賴已包含在requirements.txt中，無需額外安裝

# 啟動 MongoDB (默認端口 27017)
mongod --dbpath ./data/mongodb

# 啟動 Redis (默認端口 6379)
redis-server
```

> ⚠️ **重要說明**:
>
> - **🐳 Docker部署**: 數據庫自動包含，無需額外配置
> - **💻 本地部署**: 可選擇仅啟動數據庫服務或完全本地安裝
> - **📋 推薦**: 使用Docker部署以獲得最佳體驗和一致性

#### 數據庫配置選項

**環境變量配置**（推薦）：

```bash
# MongoDB 配置
MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DATABASE=trading_agents
MONGODB_USERNAME=admin
MONGODB_PASSWORD=your_password

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0
```

**配置文件方式**：

```python
# config/database_config.py
DATABASE_CONFIG = {
    'mongodb': {
        'host': 'localhost',
        'port': 27017,
        'database': 'trading_agents',
        'username': 'admin',
        'password': 'your_password'
    },
    'redis': {
        'host': 'localhost',
        'port': 6379,
        'password': 'your_redis_password',
        'db': 0
    }
}
```

#### 數據庫功能特性

**MongoDB 功能**：

- ✅ 股票基础信息存储
- ✅ 歷史價格數據緩存
- ✅ 分析結果持久化
- ✅ 用戶配置管理
- ✅ 自動數據同步

**Redis 功能**：

- ⚡ 實時價格數據緩存
- ⚡ API響應結果緩存
- ⚡ 會話狀態管理
- ⚡ 熱點數據預加載
- ⚡ 分布式鎖支持

#### 智能降級機制

系統採用多層數據源降級策略，確保高可用性：

```
📊 數據獲取流程：
1. 🔍 檢查 Redis 緩存 (毫秒級)
2. 📚 查詢 MongoDB 存储 (秒級)
3. 🌐 調用通達信API (秒級)
4. 💾 本地文件緩存 (备用)
5. ❌ 返回錯誤信息
```

**配置降級策略**：

```python
# 在 .env 文件中配置
ENABLE_MONGODB=true
ENABLE_REDIS=true
ENABLE_FALLBACK=true

# 緩存過期時間（秒）
REDIS_CACHE_TTL=300
MONGODB_CACHE_TTL=3600
```

#### 性能優化建议

**生產環境配置**：

```bash
# MongoDB 優化
MONGODB_MAX_POOL_SIZE=50
MONGODB_MIN_POOL_SIZE=5
MONGODB_MAX_IDLE_TIME=30000

# Redis 優化
REDIS_MAX_CONNECTIONS=20
REDIS_CONNECTION_POOL_SIZE=10
REDIS_SOCKET_TIMEOUT=5
```

#### 數據庫管理工具

```bash
# 初始化數據庫
python scripts/setup/init_database.py

# 系統狀態檢查
python scripts/validation/check_system_status.py

# 清理緩存工具
python scripts/maintenance/cleanup_cache.py --days 7
```

#### 故障排除

**常见問題解決**：

1. **🪟 Windows 10 ChromaDB兼容性問題**

   **問題現象**：在Windows 10上出現 `Configuration error: An instance of Chroma already exists for ephemeral with different settings` 錯誤，而Windows 11正常。

   **快速解決方案**：

   ```bash
   # 方案1：禁用內存功能（推薦）
   # 在 .env 文件中添加：
   MEMORY_ENABLED=false

   # 方案2：使用專用修複腳本
   powershell -ExecutionPolicy Bypass -File scripts\fix_chromadb_win10.ps1

   # 方案3：管理員權限運行
   # 右键PowerShell -> "以管理員身份運行"
   ```

   **詳細解決方案**：參考 [Windows 10兼容性指南](docs/troubleshooting/windows10-chromadb-fix.md)
2. **MongoDB連接失败**

   **Docker部署**：

   ```bash
   # 檢查服務狀態
   docker-compose logs mongodb

   # 重啟服務
   docker-compose restart mongodb
   ```

   **本地部署**：

   ```bash
   # 檢查MongoDB進程
   ps aux | grep mongod

   # 重啟MongoDB
   sudo systemctl restart mongod  # Linux
   brew services restart mongodb  # macOS
   ```
3. **Redis連接超時**

   ```bash
   # 檢查Redis狀態
   redis-cli ping

   # 清理Redis緩存
   redis-cli flushdb
   ```
4. **緩存問題**

   ```bash
   # 檢查系統狀態和緩存
   python scripts/validation/check_system_status.py

   # 清理過期緩存
   python scripts/maintenance/cleanup_cache.py --days 7
   ```

> 💡 **提示**: 即使不配置數據庫，系統仍可正常運行，會自動降級到API直接調用模式。數據庫配置是可選的性能優化功能。

> 📚 **詳細文档**: 更多數據庫配置信息請參考 [數據庫架構文档](docs/architecture/database-architecture.md)

### 📤 報告導出功能

#### 新增功能：專業分析報告導出

本項目現已支持将股票分析結果導出為多種專業格式：

**支持的導出格式**：

- **📄 Markdown (.md)** - 轻量級標記語言，適合技術用戶和版本控制
- **📝 Word (.docx)** - Microsoft Word文档，適合商務報告和進一步編辑
- **📊 PDF (.pdf)** - 便攜式文档格式，適合正式分享和打印

**報告內容結構**：

- 🎯 **投資決策摘要** - 买入/持有/卖出建议，置信度，風險評分
- 📊 **詳細分析報告** - 技術分析，基本面分析，市場情绪，新聞事件
- ⚠️ **風險提示** - 完整的投資風險聲明和免责條款
- 📋 **配置信息** - 分析參數，模型信息，生成時間

**使用方法**：

1. 完成股票分析後，在結果页面底部找到"📤 導出報告"部分
2. 選擇需要的格式：Markdown、Word或PDF
3. 點擊導出按钮，系統自動生成並提供下載

**安裝導出依賴**：

```bash
# 安裝Python依賴
pip install markdown pypandoc

# 安裝系統工具（用於PDF導出）
# Windows: choco install pandoc wkhtmltopdf
# macOS: brew install pandoc wkhtmltopdf
# Linux: sudo apt-get install pandoc wkhtmltopdf
```

> 📚 **詳細文档**: 完整的導出功能使用指南請參考 [導出功能指南](docs/EXPORT_GUIDE.md)

### 🚀 啟動應用

#### 🐳 Docker啟動（推薦）

如果您使用Docker部署，應用已經自動啟動：

```bash
# 應用已在Docker中運行，直接訪問：
# Web界面: http://localhost:8501
# 數據庫管理: http://localhost:8081
# 緩存管理: http://localhost:8082

# 查看運行狀態
docker-compose ps

# 查看日誌
docker-compose logs -f web
```

#### 💻 本地啟動

如果您使用本地部署：

```bash
# 1. 激活虛擬環境
# Windows
.\env\Scripts\activate
# Linux/macOS
source env/bin/activate

# 2. 安裝項目到虛擬環境（重要！）
pip install -e .

# 💡 國內用戶推薦使用鏡像加速（詳见 docs/installation-mirror.md）
# pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 啟動Web管理界面
# 方法1：使用項目啟動腳本（推薦）
python start_web.py

# 方法2：使用原始啟動腳本
python web/run_web.py

# 方法3：直接使用streamlit（需要先安裝項目）
streamlit run web/app.py
```

然後在浏覽器中訪問 `http://localhost:8501`

**Web界面特色功能**:

- 🇺🇸 **美股分析**: 支持 AAPL, TSLA, NVDA 等美股代碼
- 🇨🇳 **A股分析**: 支持 000001, 600519, 300750 等A股代碼
- 📊 **實時數據**: 通達信API提供A股實時行情數據
- 🤖 **智能體選擇**: 可選擇不同的分析師組合
- 📤 **報告導出**: 一键導出Markdown/Word/PDF格式專業分析報告
- 🎯 **5級研究深度**: 從快速分析(2-4分鐘)到全面分析(15-25分鐘)
- 📊 **智能分析師選擇**: 市場技術、基本面、新聞、社交媒體分析師
- 🔄 **實時進度顯示**: 可視化分析過程，避免等待焦慮
- 📈 **結構化結果**: 投資建议、目標價位、置信度、風險評估
- 🇨🇳 **完全中文化**: 界面和分析結果全中文顯示

**研究深度級別說明**:

- **1級 - 快速分析** (2-4分鐘): 日常監控，基础決策
- **2級 - 基础分析** (4-6分鐘): 常規投資，平衡速度
- **3級 - 標準分析** (6-10分鐘): 重要決策，推薦默認
- **4級 - 深度分析** (10-15分鐘): 重大投資，詳細研究
- **5級 - 全面分析** (15-25分鐘): 最重要決策，最全面分析

#### 💻 代碼調用（適合開發者）

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 配置阿里百炼
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "dashscope"
config["deep_think_llm"] = "qwen-plus"      # 深度分析
config["quick_think_llm"] = "qwen-turbo"    # 快速任務

# 創建交易智能體
ta = TradingAgentsGraph(debug=True, config=config)

# 分析股票 (以苹果公司為例)
state, decision = ta.propagate("AAPL", "2024-01-15")

# 輸出分析結果
print(f"推薦動作: {decision['action']}")
print(f"置信度: {decision['confidence']:.1%}")
print(f"風險評分: {decision['risk_score']:.1%}")
print(f"推理過程: {decision['reasoning']}")
```

#### 快速啟動腳本

```bash
# 阿里百炼演示（推薦中文用戶）
python examples/dashscope/demo_dashscope_chinese.py

# 阿里百炼完整演示
python examples/dashscope/demo_dashscope.py

# 阿里百炼簡化測試
python examples/dashscope/demo_dashscope_simple.py

# OpenAI演示（需要國外API）
python examples/openai/demo_openai.py

# 集成測試
python tests/integration/test_dashscope_integration.py
```

#### 📁 數據目錄配置

**新功能**: 灵活配置數據存储路徑，支持多種配置方式：

```bash
# 查看當前數據目錄配置
python -m cli.main data-config --show

# 設置自定義數據目錄
python -m cli.main data-config --set /path/to/your/data

# 重置為默認配置
python -m cli.main data-config --reset
```

**環境變量配置**:

```bash
# Windows
set TRADING_AGENTS_DATA_DIR=C:\MyTradingData

# Linux/macOS
export TRADING_AGENTS_DATA_DIR=/home/user/trading_data
```

**程序化配置**:

```python
from tradingagents.config_manager import ConfigManager

# 設置數據目錄
config_manager = ConfigManager()
config_manager.set_data_directory("/path/to/data")

# 獲取配置
data_dir = config_manager.get_data_directory()
print(f"數據目錄: {data_dir}")
```

**配置優先級**: 程序設置 > 環境變量 > 配置文件 > 默認值

詳細說明請參考: [📁 數據目錄配置指南](docs/configuration/data-directory-configuration.md)

### 交互式分析

```bash
# 啟動交互式命令行界面
python -m cli.main
```

## 🎯 **快速導航** - 找到您需要的內容


| 🎯**我想要...** | 📖**推薦文档**                                            | ⏱️**阅讀時間** |
| --------------- | --------------------------------------------------------- | ---------------- |
| **快速上手**    | [🚀 快速開始](docs/overview/quick-start.md)               | 10分鐘           |
| **了解架構**    | [🏛️ 系統架構](docs/architecture/system-architecture.md) | 15分鐘           |
| **看代碼示例**  | [📚 基础示例](docs/examples/basic-examples.md)            | 20分鐘           |
| **解決問題**    | [🆘 常见問題](docs/faq/faq.md)                            | 5分鐘            |
| **深度學习**  | [📁 完整文档目錄](#-詳細文档目錄)                         | 2小時+           |

> 💡 **提示**: 我們的 `docs/` 目錄包含了 **50,000+字** 的詳細中文文档，這是与原版最大的区別！

## 📚 完整文档體系 - 核心亮點

> **🌟 這是本項目与原版最大的区別！** 我們構建了業界最完整的中文金融AI框架文档體系，包含超過 **50,000字** 的詳細技術文档，**20+** 個專業文档文件，**100+** 個代碼示例。

### 🎯 為什么選擇我們的文档？


| 對比維度     | 原版 TradingAgents | 🚀**中文增强版**           |
| ------------ | ------------------ | -------------------------- |
| **文档語言** | 英文基础說明       | **完整中文體系**           |
| **文档深度** | 簡單介紹           | **深度技術剖析**           |
| **架構說明** | 概念性描述         | **詳細設計文档 + 架構圖**  |
| **使用指南** | 基础示例           | **從入門到專家的完整路徑** |
| **故障排除** | 無                 | **詳細FAQ + 解決方案**     |
| **代碼示例** | 少量示例           | **100+ 實用示例**          |

### 📖 文档導航 - 按學习路徑組織

#### 🚀 **新手入門路徑** (推薦從這里開始)

1. [📋 項目概述](docs/overview/project-overview.md) - **了解項目背景和核心價值**
2. [⚙️ 詳細安裝](docs/overview/installation.md) - **各平台詳細安裝指南**
3. [🚀 快速開始](docs/overview/quick-start.md) - **10分鐘上手指南**
4. [📚 基础示例](docs/examples/basic-examples.md) - **8個實用的入門示例**

#### 🏗️ **架構理解路徑** (深入了解系統設計)

1. [🏛️ 系統架構](docs/architecture/system-architecture.md) - **完整的系統架構設計**
2. [🤖 智能體架構](docs/architecture/agent-architecture.md) - **多智能體協作機制**
3. [📊 數據流架構](docs/architecture/data-flow-architecture.md) - **數據處理全流程**
4. [🔄 圖結構設計](docs/architecture/graph-structure.md) - **LangGraph工作流程**

#### 🤖 **智能體深度解析** (了解每個智能體的設計)

1. [📈 分析師团隊](docs/agents/analysts.md) - **四類專業分析師詳解**
2. [🔬 研究員团隊](docs/agents/researchers.md) - **看涨/看跌辩論機制**
3. [💼 交易員智能體](docs/agents/trader.md) - **交易決策制定流程**
4. [🛡️ 風險管理](docs/agents/risk-management.md) - **多層次風險評估**
5. [👔 管理層智能體](docs/agents/managers.md) - **協調和決策管理**

#### 📊 **數據處理專題** (掌握數據處理技術)

1. [🔌 數據源集成](docs/data/data-sources.md) - **多數據源API集成**
2. [⚙️ 數據處理流程](docs/data/data-processing.md) - **數據清洗和轉換**
3. [💾 緩存策略](docs/data/caching.md) - **多層緩存優化性能**

#### ⚙️ **配置和優化** (性能調優和定制)

1. [📝 配置指南](docs/configuration/config-guide.md) - **詳細配置選項說明**
2. [🧠 LLM配置](docs/configuration/llm-config.md) - **大語言模型優化**

#### 💡 **高級應用** (擴展開發和實战)

1. [📚 基础示例](docs/examples/basic-examples.md) - **8個實用基础示例**
2. [🚀 高級示例](docs/examples/advanced-examples.md) - **複雜場景和擴展開發**

#### ❓ **問題解決** (遇到問題時查看)

1. [🆘 常见問題](docs/faq/faq.md) - **詳細FAQ和解決方案**

### 📊 文档統計數據

- 📄 **文档文件數**: 20+ 個專業文档
- 📝 **总字數**: 50,000+ 字詳細內容
- 💻 **代碼示例**: 100+ 個實用示例
- 📈 **架構圖表**: 10+ 個專業圖表
- 🎯 **覆蓋範围**: 從入門到專家的完整路徑

### 🎨 文档特色

- **🇨🇳 完全中文化**: 專為中文用戶優化的表達方式
- **📊 圖文並茂**: 丰富的架構圖和流程圖
- **💻 代碼丰富**: 每個概念都有對應的代碼示例
- **🔍 深度剖析**: 不仅告诉你怎么做，还告诉你為什么這樣做
- **🛠️ 實用導向**: 所有文档都面向實际應用場景

---

## 📚 詳細文档目錄

### 📁 **docs/ 目錄結構** - 完整的知识體系

```
docs/
├── 📖 overview/              # 項目概覽 - 新手必讀
│   ├── project-overview.md   # 📋 項目詳細介紹
│   ├── quick-start.md        # 🚀 10分鐘快速上手
│   └── installation.md       # ⚙️ 詳細安裝指南
│
├── 🏗️ architecture/          # 系統架構 - 深度理解
│   ├── system-architecture.md    # 🏛️ 整體架構設計
│   ├── agent-architecture.md     # 🤖 智能體協作機制
│   ├── data-flow-architecture.md # 📊 數據流處理架構
│   └── graph-structure.md        # 🔄 LangGraph工作流
│
├── 🤖 agents/               # 智能體詳解 - 核心組件
│   ├── analysts.md          # 📈 四類專業分析師
│   ├── researchers.md       # 🔬 看涨/看跌辩論機制
│   ├── trader.md           # 💼 交易決策制定
│   ├── risk-management.md  # 🛡️ 多層風險評估
│   └── managers.md         # 👔 管理層協調
│
├── 📊 data/                 # 數據處理 - 技術核心
│   ├── data-sources.md      # 🔌 多數據源集成
│   ├── data-processing.md   # ⚙️ 數據處理流程
│   └── caching.md          # 💾 緩存優化策略
│
├── ⚙️ configuration/        # 配置優化 - 性能調優
│   ├── config-guide.md      # 📝 詳細配置說明
│   └── llm-config.md       # 🧠 LLM模型優化
│
├── 💡 examples/             # 示例教程 - 實战應用
│   ├── basic-examples.md    # 📚 8個基础示例
│   └── advanced-examples.md # 🚀 高級開發示例
│
└── ❓ faq/                  # 問題解決 - 疑難解答
    └── faq.md              # 🆘 常见問題FAQ
```

### 🎯 **重點推薦文档** (必讀精選)

#### 🔥 **最受欢迎的文档**

1. **[📋 項目概述](docs/overview/project-overview.md)** - ⭐⭐⭐⭐⭐

   > 了解項目的核心價值和技術特色，5分鐘讀懂整個框架
   >
2. **[🏛️ 系統架構](docs/architecture/system-architecture.md)** - ⭐⭐⭐⭐⭐

   > 深度解析多智能體協作機制，包含詳細架構圖
   >
3. **[📚 基础示例](docs/examples/basic-examples.md)** - ⭐⭐⭐⭐⭐

   > 8個實用示例，從股票分析到投資組合優化
   >

#### 🚀 **技術深度文档**

1. **[🤖 智能體架構](docs/architecture/agent-architecture.md)**

   > 多智能體設計模式和協作機制詳解
   >
2. **[📊 數據流架構](docs/architecture/data-flow-architecture.md)**

   > 數據獲取、處理、緩存的完整流程
   >
3. **[🔬 研究員团隊](docs/agents/researchers.md)**

   > 看涨/看跌研究員辩論機制的創新設計
   >

#### 💼 **實用工具文档**

1. **[🌐 Web界面指南](docs/usage/web-interface-guide.md)** - ⭐⭐⭐⭐⭐

   > 完整的Web界面使用教程，包含5級研究深度詳細說明
   >
2. **[💰 投資分析指南](docs/usage/investment_analysis_guide.md)**

   > 從基础到高級的完整投資分析教程
   >
3. **[🧠 LLM配置](docs/configuration/llm-config.md)**

   > 多LLM模型配置和成本優化策略
   >
4. **[💾 緩存策略](docs/data/caching.md)**

   > 多層緩存設計，顯著降低API調用成本
   >
5. **[🆘 常见問題](docs/faq/faq.md)**

   > 詳細的FAQ和故障排除指南
   >

### 📖 **按模塊浏覽文档**

<details>
<summary><strong>📖 概覽文档</strong> - 項目入門必讀</summary>

- [📋 項目概述](docs/overview/project-overview.md) - 詳細的項目背景和特性介紹
- [🚀 快速開始](docs/overview/quick-start.md) - 從安裝到第一次運行的完整指南
- [⚙️ 詳細安裝](docs/overview/installation.md) - 各平台詳細安裝說明

</details>

<details>
<summary><strong>🏗️ 架構文档</strong> - 深度理解系統設計</summary>

- [🏛️ 系統架構](docs/architecture/system-architecture.md) - 完整的系統架構設計
- [🤖 智能體架構](docs/architecture/agent-architecture.md) - 智能體設計模式和協作機制
- [📊 數據流架構](docs/architecture/data-flow-architecture.md) - 數據獲取、處理和分發流程
- [🔄 圖結構設計](docs/architecture/graph-structure.md) - LangGraph工作流程設計

</details>

<details>
<summary><strong>🤖 智能體文档</strong> - 核心組件詳解</summary>

- [📈 分析師团隊](docs/agents/analysts.md) - 四類專業分析師詳解
- [🔬 研究員团隊](docs/agents/researchers.md) - 看涨/看跌研究員和辩論機制
- [💼 交易員智能體](docs/agents/trader.md) - 交易決策制定流程
- [🛡️ 風險管理](docs/agents/risk-management.md) - 多層次風險評估體系
- [👔 管理層智能體](docs/agents/managers.md) - 協調和決策管理

</details>

<details>
<summary><strong>📊 數據處理</strong> - 技術核心實現</summary>

- [🔌 數據源集成](docs/data/data-sources.md) - 支持的數據源和API集成
- [⚙️ 數據處理流程](docs/data/data-processing.md) - 數據清洗、轉換和驗證
- [💾 緩存策略](docs/data/caching.md) - 多層緩存優化性能

</details>

<details>
<summary><strong>⚙️ 配置与部署</strong> - 性能調優指南</summary>

- [📝 配置指南](docs/configuration/config-guide.md) - 詳細的配置選項說明
- [🧠 LLM配置](docs/configuration/llm-config.md) - 大語言模型配置優化

</details>

<details>
<summary><strong>💡 示例和教程</strong> - 實战應用指南</summary>

- [📚 基础示例](docs/examples/basic-examples.md) - 8個實用的基础示例
- [🚀 高級示例](docs/examples/advanced-examples.md) - 複雜場景和擴展開發

</details>

<details>
<summary><strong>❓ 幫助文档</strong> - 問題解決方案</summary>

- [🆘 常见問題](docs/faq/faq.md) - 詳細的FAQ和解決方案

</details>

## 💰 成本控制

### 典型使用成本

- **經濟模式**: $0.01-0.05/次分析 (使用 gpt-4o-mini)
- **標準模式**: $0.05-0.15/次分析 (使用 gpt-4o)
- **高精度模式**: $0.10-0.30/次分析 (使用 gpt-4o + 多轮辩論)

### 成本優化建议

```python
# 低成本配置示例
cost_optimized_config = {
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini", 
    "max_debate_rounds": 1,
    "online_tools": False  # 使用緩存數據
}
```

## 🤝 贡献指南

我們欢迎各種形式的贡献：

### 贡献類型

- 🐛 **Bug修複** - 發現並修複問題
- ✨ **新功能** - 添加新的功能特性
- 📚 **文档改進** - 完善文档和教程
- 🌐 **本地化** - 翻譯和本地化工作
- 🎨 **代碼優化** - 性能優化和代碼重構

### 贡献流程

1. Fork 本仓庫
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 創建 Pull Request

### 📋 查看贡献者

查看所有贡献者和詳細贡献內容：**[🤝 贡献者名單](CONTRIBUTORS.md)**

## 📄 許可證

本項目基於 Apache 2.0 許可證開源。詳见 [LICENSE](LICENSE) 文件。

### 許可證說明

- ✅ 商業使用
- ✅ 修改和分發
- ✅ 私人使用
- ✅ 專利使用
- ❗ 需要保留版權聲明
- ❗ 需要包含許可證副本

## 🙏 致谢与感恩

### 🌟 向源項目開發者致敬

我們向 [Tauric Research](https://github.com/TauricResearch) 团隊表達最深的敬意和感谢：

- **🎯 愿景領導者**: 感谢您們在AI金融領域的前瞻性思考和創新實踐
- **💎 珍贵源碼**: 感谢您們開源的每一行代碼，它們凝聚着無數的智慧和心血
- **🏗️ 架構大師**: 感谢您們設計了如此優雅、可擴展的多智能體框架
- **💡 技術先驱**: 感谢您們将前沿AI技術与金融實務完美結合
- **🔄 持续贡献**: 感谢您們持续的維護、更新和改進工作

### 🤝 社区贡献者致谢

感谢所有為TradingAgents-CN項目做出贡献的開發者和用戶！

詳細的贡献者名單和贡献內容請查看：**[📋 贡献者名單](CONTRIBUTORS.md)**

包括但不限於：

- 🐳 **Docker容器化** - 部署方案優化
- 📄 **報告導出功能** - 多格式輸出支持
- 🐛 **Bug修複** - 系統穩定性提升
- 🔧 **代碼優化** - 用戶體驗改進
- 📝 **文档完善** - 使用指南和教程
- 🌍 **社区建設** - 問題反馈和推廣
- **🌍 開源贡献**: 感谢您們選擇Apache 2.0協议，給予開發者最大的自由
- **📚 知识分享**: 感谢您們提供的詳細文档和最佳實踐指導

**特別感谢**：[TradingAgents](https://github.com/TauricResearch/TradingAgents) 項目為我們提供了坚實的技術基础。虽然Apache 2.0協议赋予了我們使用源碼的權利，但我們深知每一行代碼的珍贵價值，将永远铭記並感谢您們的無私贡献。

### 🇨🇳 推廣使命的初心

創建這個中文增强版本，我們怀着以下初心：

- **🌉 技術傳播**: 让優秀的TradingAgents技術在中國得到更廣泛的應用
- **🎓 教育普及**: 為中國的AI金融教育提供更好的工具和資源
- **🤝 文化桥梁**: 在中西方技術社区之間搭建交流合作的桥梁
- **🚀 創新推動**: 推動中國金融科技領域的AI技術創新和應用

### 🌍 開源社区

感谢所有為本項目贡献代碼、文档、建议和反馈的開發者和用戶。正是因為有了大家的支持，我們才能更好地服務中文用戶社区。

### 🤝 合作共赢

我們承诺：

- **尊重原創**: 始终尊重源項目的知识產權和開源協议
- **反馈贡献**: 将有價值的改進和創新反馈給源項目和開源社区
- **持续改進**: 不斷完善中文增强版本，提供更好的用戶體驗
- **開放合作**: 欢迎与源項目团隊和全球開發者進行技術交流与合作

## 📈 版本歷史

- **v0.1.13** (2025-08-02): 🤖 原生OpenAI支持与Google AI生態系統全面集成 ✨ **最新版本**
- **v0.1.12** (2025-07-29): 🧠 智能新聞分析模塊与項目結構優化
- **v0.1.11** (2025-07-27): 🤖 多LLM提供商集成与模型選擇持久化
- **v0.1.10** (2025-07-18): 🚀 Web界面實時進度顯示与智能會話管理
- **v0.1.9** (2025-07-16): 🎯 CLI用戶體驗重大優化与統一日誌管理
- **v0.1.8** (2025-07-15): 🎨 Web界面全面優化与用戶體驗提升
- **v0.1.7** (2025-07-13): 🐳 容器化部署与專業報告導出
- **v0.1.6** (2025-07-11): 🔧 阿里百炼修複与數據源升級
- **v0.1.5** (2025-07-08): 📊 添加Deepseek模型支持
- **v0.1.4** (2025-07-05): 🏗️ 架構優化与配置管理重構
- **v0.1.3** (2025-06-28): 🇨🇳 A股市場完整支持
- **v0.1.2** (2025-06-15): 🌐 Web界面和配置管理
- **v0.1.1** (2025-06-01): 🧠 國產LLM集成

📋 **詳細更新日誌**: [CHANGELOG.md](./docs/releases/CHANGELOG.md)

## 📞 聯系方式

- **GitHub Issues**: [提交問題和建议](https://github.com/hsliuping/TradingAgents-CN/issues)
- **邮箱**: hsliup@163.com
- 項目ＱＱ群：187537480
- 項目微信公眾號：TradingAgents-CN

  <img src="assets/weixin.png" alt="微信公眾號" width="200"/>

- **原項目**: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- **文档**: [完整文档目錄](docs/)

## ⚠️ 風險提示

**重要聲明**: 本框架仅用於研究和教育目的，不構成投資建议。

- 📊 交易表現可能因多種因素而異
- 🤖 AI模型的預測存在不確定性
- 💰 投資有風險，決策需谨慎
- 👨‍💼 建议咨詢專業財務顧問

---

<div align="center">

**🌟 如果這個項目對您有幫助，請給我們一個 Star！**

[⭐ Star this repo](https://github.com/hsliuping/TradingAgents-CN) | [🍴 Fork this repo](https://github.com/hsliuping/TradingAgents-CN/fork) | [📖 Read the docs](./docs/)

</div>
