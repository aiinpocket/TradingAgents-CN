# TradingAgents 中文增強版

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-0.1.18-green.svg)](./VERSION)
[![Documentation](https://img.shields.io/badge/docs-中文文檔-green.svg)](./docs/)
[![Original](https://img.shields.io/badge/基於-TauricResearch/TradingAgents-orange.svg)](https://github.com/TauricResearch/TradingAgents)

>
> **核心功能**: OpenAI 支持 | Anthropic Claude 支持 | 智慧模型選擇 | 多LLM提供商支持 | 模型選擇持久化 | Docker容器化部署 | 專業報告匯出 | 美股分析 | 中文本地化

基於多智慧體大語言模型的**中文金融交易決策框架**。專為中文使用者優化，提供完整的美股分析能力。

## 🙏 致敬源專案

感謝 [Tauric Research](https://github.com/TauricResearch) 團隊創造的革命性多智慧體交易框架 [TradingAgents](https://github.com/TauricResearch/TradingAgents)！

**🎯 我們的使命**: 為中文使用者提供完整的中文化體驗，支持美股市場，推動AI金融技術在中文社群的普及應用。

## 🎉 v1.0.0-preview 內測版本 - 全新架構升級

> 🚀 **重磅發布**: v1.0.0-preview 版本現已開啟內測！全新的 FastAPI + Vue 3 架構，帶來企業級的效能和體驗！

### ✨ 核心特性

#### 🏗️ **全新技術架構**
- **後端升級**: 從 Streamlit 遷移到 FastAPI，提供更強大的 RESTful API
- **前端重構**: 採用 Vue 3 + Element Plus，打造現代化的單頁應用
- **資料庫優化**: MongoDB + Redis 雙資料庫架構，效能提升 10 倍
- **容器化部署**: 完整的 Docker 多架構支持（amd64 + arm64）

#### 🎯 **企業級功能**
- **開放存取**: 公開專案，無需登入即可使用所有功能
- **配置管理中心**: 視覺化的大模型配置、資料來源管理、系統設定
- **快取管理系統**: 智慧快取策略，支持 MongoDB/Redis/檔案多級快取
- **即時通知系統**: SSE 推送，即時跟蹤分析進度和系統狀態

#### 🤖 **智慧分析增強**
- **動態供應商管理**: 支持動態添加和配置 LLM 供應商
- **模型能力管理**: 智慧模型選擇，根據任務自動匹配最佳模型
- **多資料來源同步**: 統一的資料來源管理，支持 Yahoo Finance、FinnHub
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

v1.0.0-preview 版本現已開放使用！詳細安裝和使用說明請參閱下方文檔。

---

## 🆕 v0.1.15 重大更新

### 🤖 LLM生態系統大升級

- **多 LLM 提供商支援**: 支援 OpenAI、Anthropic Claude
- **LLM 適配器重構**: 統一的 OpenAI 相容適配器架構
- **純美股專注**: 移除所有中國 AI 模型，專注美股市場分析
- **整合指南**: 完整的 LLM 整合開發文檔和測試工具

### 🔥 熱門特區（全新功能）

- **宏觀經濟概覽**: 即時追蹤美股主要指數、國際指數、債券殖利率、商品價格
- **產業板塊熱力圖**: 以視覺化方式呈現各產業 ETF 近一週表現
- **熱門個股追蹤**: 自動篩選近一週波動最大的個股，依週漲跌幅排序
- **成交量異常偵測**: 自動識別成交量顯著偏離均值的股票
- **以「日」為分析單位**: 聚焦短中期市場動態，避免短線雜訊與長期預測

> 所有分析僅供資訊參考，不構成任何投資建議

### 🌐 國際化（i18n）支援

- **多語言架構**: 內建 i18n 翻譯框架，預設繁體中文，支援英文
- **語言切換**: 使用者可在介面中切換語言
- **翻譯檔案**: 結構化的 JSON 語言檔案，方便擴充新語言

### 🔐 安全性強化

- **API 密鑰保護**: Web 介面不再顯示任何 API 密鑰輸入欄位，所有密鑰僅透過 `.env` 檔案配置
- **開源友善**: 專為開源社群設計，不洩露任何敏感資訊

### 📚 學術研究支持

- **TradingAgents論文**: 完整的中文翻譯版本和深度解讀
- **技術博客**: 詳細的技術分析和實現原理解讀
- **學術資料**: PDF論文和相關研究資料
- **引用支持**: 標準的學術引用格式和參考文獻

### 🛠️ 開發者體驗升級

- **開發工作流**: 標準化的開發流程和分支管理規範
- **安裝驗證**: 完整的安裝測試和驗證腳本
- **文檔重構**: 結構化的文檔系統和快速開始指南
- **PR模板**: 標準化的Pull Request模板和代碼審查流程

### 🔧 企業級工具鏈

- **分支保護**: GitHub分支保護策略和安全規則
- **緊急程序**: 完整的緊急處理和故障恢複程序
- **測試框架**: 增強的測試覆蓋和驗證工具
- **部署指南**: 企業級部署和配置管理

## 📋 v0.1.14 功能回顧

### 🗄️ 數據管理優化

- **MongoDB集成增強**: 改進的MongoDB連接和數據管理
- **數據目錄重組**: 優化的數據存儲結構和管理
- **數據遷移腳本**: 完整的數據遷移和備份工具
- **緩存優化**: 提升數據加載和分析結果緩存性能

### 🧪 測試覆蓋增強

- **功能測試腳本**: 新增6個專項功能測試腳本
- **工具處理器測試**: Google工具處理器修複驗證
- **引導自動隐藏測試**: UI交互功能測試
- **在線工具配置測試**: 工具配置和選擇邏輯測試
- **真實場景測試**: 實際使用場景的端到端測試
- **美股獨立性測試**: 美股分析功能獨立性驗證

---

## 🆕 v0.1.13 重大更新

### 🤖 原生OpenAI端點支持

- **自定義OpenAI端點**: 支持配置任意OpenAI兼容的API端點
- **靈活模型選擇**: 可以使用任何OpenAI格式的模型，不限於官方模型
- **智能適配器**: 新增原生OpenAI適配器，提供更好的兼容性和性能
- **配置管理**: 統一的端點和模型配置管理系統

### LLM適配器架構優化

- **統一接口**: 所有LLM提供商使用統一的調用接口
- **錯誤處理增強**: 改進的異常處理和自動重試機制
- **性能監控**: 添加LLM調用性能監控和統計

### 🎨 Web界面智能優化

- **智能模型選擇**: 根據可用性自動選擇最佳模型
- **KeyError修複**: 徹底解決模型選擇中的KeyError問題
- **UI響應優化**: 改進模型切換的響應速度和用戶體驗
- **錯誤提示**: 更友好的錯誤提示和解決建議

## 🆕 v0.1.12 重大更新

### 🧠 智能新聞分析模塊

- **智能新聞過濾器**: 基於AI的新聞相關性評分和質量評估
- **多層次過濾機制**: 基礎過濾、增強過濾、集成過濾三級處理
- **新聞質量評估**: 自動識別和過濾低質量、重複、無關新聞
- **統一新聞工具**: 整合多個新聞源，提供統一的新聞獲取接口

### 🔧 技術修複和優化

- **LLM工具調用增強**: 提升工具調用的可靠性和穩定性
- **新聞檢索器優化**: 增強新聞數據獲取和處理能力

### 📚 完善測試和文檔

- **全面測試覆蓋**: 新增15+個測試文件，覆蓋所有新功能
- **詳細技術文檔**: 新增8個技術分析報告和修複文檔
- **用戶指南完善**: 新增新聞過濾使用指南和最佳實踐
- **演示腳本**: 提供完整的新聞過濾功能演示

### 🗂️ 項目結構優化

- **文檔分類整理**: 按功能將文檔分類到docs子目錄
- **示例代碼歸位**: 演示腳本統一到examples目錄
- **根目錄整潔**: 保持根目錄簡潔，提升項目專業度

## 🎯 核心特性

### 🤖 多智能體協作架構

- **專業分工**: 基本面、技術面、新聞面、社交媒體四大分析師
- **結構化辯論**: 看漲/看跌研究員進行深度分析
- **智能決策**: 交易員基於所有輸入做出最終投資建議
- **風險管理**: 多層次風險評估和管理機制

## 🖥️ Web界面展示

### 📸 界面截圖

> 🎨 **現代化Web界面**: 基於Streamlit構建的響應式Web應用，提供直觀的股票分析體驗

> ⚠️ **截圖更新中**: 界面截圖正在更新，將使用美股分析範例替換。請參考下方的功能描述和使用指南。

### 主要功能展示

#### 🏠 主界面 - 分析配置

智能配置面板特色：
- 支援美股市場股票分析（如 AAPL、TSLA、NVDA）
- 5級研究深度選擇（快速分析到深度研究）
- 多個LLM提供商選擇（OpenAI、Anthropic等）
- 即時API金鑰狀態檢查

#### 📊 實時分析進度

進度追蹤功能：
- 即時進度條顯示（百分比和預估時間）
- 可視化分析過程（當前執行步驟）
- 智能時間預估（基於歷史資料）
- 頁面刷新不丟失進度

#### 📈 分析結果展示

專業投資報告：
- 明確的投資決策（買入/持有/賣出）
- 多維度分析結果（技術面、基本面、新聞面）
- 置信度和風險評分
- 一鍵導出功能（Markdown/Word/PDF）

### 🎯 核心功能特色

#### 📋 **智能分析配置**

- **🌍 美股支持**: 專注美股市場深度分析
- **🎯 5級研究深度**: 從2分鐘快速分析到25分鐘全面研究
- **🤖 智慧體選擇**: 市場技術、基本面、新聞、社交媒體分析師
- **📅 彈性時間設定**: 支援歷史任意時間點分析

#### 🚀 **即時進度追蹤**

- **📊 視覺化進度**: 即時顯示分析進展和剩餘時間
- **🔄 智慧步驟識別**: 自動識別目前分析階段
- **⏱️ 準確時間預估**: 基於歷史資料的智慧時間計算
- **💾 狀態持久化**: 頁面重新整理不遺失分析進度

#### 📈 **專業結果展示**

- **🎯 投資決策**: 明確的買入/持有/賣出建議
- **📊 多維分析**: 技術面、基本面、新聞面綜合評估
- **🔢 量化指標**: 置信度、風險評分、目標價位
- **📄 專業報告**: 支援Markdown/Word/PDF格式匯出

#### 🤖 **多LLM模型管理**

- **多AI提供商**: OpenAI、Anthropic
- **🎯 60+模型選擇**: 從經濟型到旗艦級模型全覆蓋
- **💾 配置持久化**: URL參數儲存，重新整理保持設定
- **⚡ 快速切換**: 5個熱門模型一鍵選擇按鈕

### 🎮 Web界面操作指南

#### 🚀 **快速開始流程**

1. **啟動應用**: `python start_web.py` 或 `docker-compose up -d`
2. **訪問界面**: 瀏覽器開啟 `http://localhost:8501`
3. **配置模型**: 側邊欄選擇LLM提供商和模型
4. **輸入股票**: 輸入股票代碼（如 AAPL、TSLA、NVDA）
5. **選擇深度**: 根據需求選擇1-5級研究深度
6. **開始分析**: 點擊「開始分析」按鈕
7. **查看結果**: 即時追蹤進度，查看分析報告
8. **匯出報告**: 一鍵匯出專業格式報告

#### 📊 **支援的股票代碼格式**

- **🇺🇸 美股**: `AAPL`, `TSLA`, `MSFT`, `NVDA`, `GOOGL`

#### 🎯 **研究深度說明**

- **1級 (2-4分鐘)**: 快速概覽，基礎技術指標
- **2級 (4-6分鐘)**: 標準分析，技術+基本面
- **3級 (6-10分鐘)**: 深度分析，加入新聞情緒 ⭐ **推薦**
- **4級 (10-15分鐘)**: 全面分析，多輪智慧體辯論
- **5級 (15-25分鐘)**: 最深度分析，完整研究報告

#### 💡 **使用技巧**

- **🔄 即時重新整理**: 分析過程中可隨時重新整理頁面，進度不遺失
- **📱 行動裝置適配**: 支援手機和平板裝置訪問
- **🎨 深色模式**: 自動適配系統主題設定
- **⌨️ 快速鍵**: 支援Enter鍵快速提交分析
- **📋 歷史記錄**: 自動儲存最近的分析配置

> 📖 **詳細指南**: 完整的Web界面使用說明請參考 [🖥️ Web界面詳細使用指南](docs/usage/web-interface-detailed-guide.md)

## 🎯 功能特性

### 🚀  智能新聞分析✨ **v0.1.12重大升級**


| 功能特性               | 狀態        | 詳細說明                                 |
| ---------------------- | ----------- | ---------------------------------------- |
| **🧠 智能新聞分析**    | 🆕 v0.1.12  | AI新聞過濾，質量評估，相關性分析         |
| **🔧 新聞過濾器**      | 🆕 v0.1.12  | 多層次過濾，基礎/增強/集成三級處理       |
| **📰 統一新聞工具**    | 🆕 v0.1.12  | 整合多源新聞，統一接口，智能檢索         |
| **🤖 多LLM提供商**     | 🆕 v0.1.11  | 4大提供商，60+模型，智能分類管理         |
| **💾 模型選擇持久化**  | 🆕 v0.1.11  | URL參數存儲，刷新保持，配置分享          |
| **🎯 快速選擇按鈕**    | 🆕 v0.1.11  | 一鍵切換熱門模型，提升操作效率           |
| **📊 實時進度顯示**    | ✅ v0.1.10  | 異步進度跟蹤，智能步驟識別，準確時間計算 |
| **💾 智能會話管理**    | ✅ v0.1.10  | 狀態持久化，自動降級，跨頁面恢複         |
| **🎯 一鍵查看報告**    | ✅ v0.1.10  | 分析完成後一鍵查看，智能結果恢複         |
| **🖥️ Streamlit界面** | ✅ 完整支持 | 現代化響應式界面，實時交互和數據可視化   |
| **⚙️ 配置管理**      | ✅ 完整支持 | Web端API密鑰管理，模型選擇，參數配置     |

### 🎨 CLI用戶體驗 ✨ **v0.1.9優化**


| 功能特性                | 狀態        | 詳細說明                             |
| ----------------------- | ----------- | ------------------------------------ |
| **🖥️ 界面與日誌分離** | ✅ 完整支持 | 用戶界面清爽美觀，技術日誌獨立管理   |
| **🔄 智能進度顯示**     | ✅ 完整支持 | 多階段進度跟蹤，防止重複提示         |
| **⏱️ 時間預估功能**   | ✅ 完整支持 | 智能分析階段顯示預計耗時             |
| **🌈 Rich彩色輸出**     | ✅ 完整支持 | 彩色進度指示，狀態圖標，視覺效果提升 |

### 🧠 LLM模型支持 ✨ **v0.1.13全面升級**


| 模型提供商        | 支持模型                     | 特色功能                | 新增功能 |
| ----------------- | ---------------------------- | ----------------------- | -------- |
| **OpenAI**        | GPT-4o, GPT-4o-mini         | 通用能力強              | 集成     |
| **Anthropic**     | Claude Opus 4, Claude Sonnet 4 | 分析推理強           | 集成     |

**持久化**: URL參數存儲，刷新保持 | **智能切換**: 一鍵切換不同提供商

### 📊 數據源與市場


| 市場類型      | 數據源                 | 覆蓋範圍                 |
| ------------- | ---------------------- | ------------------------ |
| **🇺🇸 美股** | FinnHub, Yahoo Finance | NYSE, NASDAQ，實時數據   |
| **📰 新聞**   | Google News            | 實時新聞，多語言支持     |

### 🤖 智能體團隊

**分析師團隊**: 📈市場分析 | 💰基本面分析 | 📰新聞分析 | 💬情緒分析
**研究團隊**: 🐂看漲研究員 | 🐻看跌研究員 | 🎯交易決策員
**管理層**: 🛡️風險管理員 | 👔研究主管

## 🚀 快速開始

### 🐳 Docker部署 (推薦)

```bash
# 1. 克隆項目
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 配置環境變量
cp .env.example .env
# 編輯 .env 文件，填入API密鑰

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
pip install -r requirements-lock.txt
pip install -e . --no-deps

# 或一步安裝（會重新解析依賴，速度較慢）
# pip install -e .

# Windows 用戶如遇到 PyYAML 編譯錯誤，使用鎖定版本可避免此問題

# 3. 啟動應用
python start_web.py

# 4. 訪問 http://localhost:8501
```

### 📊 開始分析

1. **選擇模型**: OpenAI / Anthropic
2. **輸入股票**: `AAPL` (美股)
3. **開始分析**: 點擊"🚀 開始分析"按鈕
4. **實時跟蹤**: 觀察實時進度和分析步驟
5. **查看報告**: 點擊"📊 查看分析報告"按鈕
6. **導出報告**: 支持Word/PDF/Markdown格式

## 🎯 核心優勢

- **🧠 智能新聞分析**: v0.1.12新增AI驅動的新聞過濾和品質評估系統
- **🔧 多層次過濾**: 基礎、增強、集成三級新聞過濾機制
- **📰 統一新聞工具**: 整合多源新聞，提供統一的智能檢索接口
- **多LLM集成**: OpenAI 和 Anthropic 雙提供商支援
- **配置持久化**: 模型選擇真正持久化，URL參數存儲，刷新保持
- **🆕 實時進度**: v0.1.10異步進度跟蹤，告別黑盒等待
- **💾 智能會話**: 狀態持久化，頁面刷新不遺失分析結果
- **🌐 全球市場**: 美股數據 + 國際AI模型 + 中文界面
- **🐳 容器化**: Docker一鍵部署，環境隔離，快速擴展
- **📄 專業報告**: 多格式導出，自動生成投資建議
- **🛡️ 穩定可靠**: 多層數據源，智能降級，錯誤恢復

## 🔧 技術架構

**核心技術**: Python 3.10+ | LangChain | Streamlit | MongoDB | Redis
**AI模型**: OpenAI | Anthropic
**數據源**: FinnHub | Yahoo Finance | Google News
**部署**: Docker | Docker Compose | 本地部署

## 📚 文檔和支持

- **📖 完整文檔**: [docs/](./docs/) - 安裝指南、使用教程、API文檔
- **🚨 故障排除**: [troubleshooting/](./docs/troubleshooting/) - 常見問題解決方案
- **🔄 更新日誌**: [CHANGELOG.md](./docs/releases/CHANGELOG.md) - 詳細版本歷史
- **🚀 快速開始**: [QUICKSTART.md](./QUICKSTART.md) - 5分鐘快速部署指南

## 🆚 中文增強特色

**相比原版新增**: 智能新聞分析 | 多層次新聞過濾 | 新聞質量評估 | 統一新聞工具 | 多LLM提供商集成 | 模型選擇持久化 | 快速切換按鈕 | 即時進度顯示 | 智慧會話管理 | 中文介面 | Docker部署 | 專業報告匯出 | 統一日誌管理 | Web配置介面 | 成本優化

**Docker部署包含的服務**:

- 🌐 **Web應用**: TradingAgents-CN主程序
- 🗄️ **MongoDB**: 數據持久化存儲
- ⚡ **Redis**: 高速緩存
- 📊 **MongoDB Express**: 數據庫管理界面
- 🎛️ **Redis Commander**: 緩存管理界面

#### 💻 方式二：本地部署

**適用場景**: 開發環境、自定義配置、離線使用

### 環境要求

- Python 3.10+ (推薦 3.11)
- 4GB+ RAM (推薦 8GB+)
- 穩定的網絡連接

### 安裝步驟

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

# 註意：requirements.txt 已包含所有必需依賴：
# - 數據庫支持 (MongoDB + Redis)
# - 美股資料來源 (Yahoo Finance, FinnHub)
# - Web界面和報告導出功能
```

### 配置API密鑰

#### 配置 API 密鑰

```bash
# 複制配置模板
cp .env.example .env

# 編輯 .env 文件，配置以下必需的API密鑰：
FINNHUB_API_KEY=your_finnhub_api_key_here

# 可選：其他AI模型API
OPENAI_API_KEY=your_openai_api_key_here

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
> - 端口衝突：如果本地已有數據庫服務，可修改docker-compose.yml中的端口映射

#### 可選：Anthropic Claude 模型

```bash
# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 🗄️ 數據庫配置（MongoDB + Redis）

#### 高性能數據存儲支持

本項目支持 **MongoDB** 和 **Redis** 數據庫，提供：

- **📊 股票數據緩存**: 減少API調用，提升響應速度
- **🔄 智能降級機制**: MongoDB → API → 本地緩存的多層數據源
- **⚡ 高性能緩存**: Redis緩存熱點數據，毫秒級響應
- **🛡️ 數據持久化**: MongoDB存儲歷史數據，支持離線分析

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

**方式一：僅啟動數據庫服務**

```bash
# 僅啟動 MongoDB + Redis 服務（不啟動Web應用）
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
> - **💻 本地部署**: 可選擇僅啟動數據庫服務或完全本地安裝
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

- ✅ 股票基礎信息存儲
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
2. 📚 查詢 MongoDB 存儲 (秒級)
3. 🌐 調用 Yahoo Finance / FinnHub API (秒級)
4. 💾 本地文件緩存 (備用)
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

#### 性能優化建議

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

**常見問題解決**：

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
   # 右鍵PowerShell -> "以管理員身份運行"
   ```

   **詳細解決方案**：參考 [Windows 10兼容性指南](docs/troubleshooting/windows10-chromadb-fix.md)
2. **MongoDB連接失敗**

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

> 📚 **詳細文檔**: 更多數據庫配置信息請參考 [數據庫架構文檔](docs/architecture/database-architecture.md)

### 📤 報告導出功能

#### 新增功能：專業分析報告導出

本項目現已支持將股票分析結果導出為多種專業格式：

**支持的導出格式**：

- **📄 Markdown (.md)** - 輕量級標記語言，適合技術用戶和版本控制
- **📝 Word (.docx)** - Microsoft Word文檔，適合商務報告和進一步編輯
- **📊 PDF (.pdf)** - 便攜式文檔格式，適合正式分享和打印

**報告內容結構**：

- 🎯 **投資決策摘要** - 買入/持有/賣出建議，置信度，風險評分
- 📊 **詳細分析報告** - 技術分析，基本面分析，市場情緒，新聞事件
- ⚠️ **風險提示** - 完整的投資風險聲明和免責條款
- 📋 **配置信息** - 分析參數，模型信息，生成時間

**使用方法**：

1. 完成股票分析後，在結果頁面底部找到"📤 導出報告"部分
2. 選擇需要的格式：Markdown、Word或PDF
3. 點擊導出按鈕，系統自動生成並提供下載

**安裝導出依賴**：

```bash
# 安裝Python依賴
pip install markdown pypandoc

# 安裝系統工具（用於PDF導出）
# Windows: choco install pandoc wkhtmltopdf
# macOS: brew install pandoc wkhtmltopdf
# Linux: sudo apt-get install pandoc wkhtmltopdf
```

> 📚 **詳細文檔**: 完整的導出功能使用指南請參考 [導出功能指南](docs/EXPORT_GUIDE.md)

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

# 3. 啟動 Web 管理界面
# 方法1：使用項目啟動腳本（推薦）
python start_web.py

# 方法2：使用原始啟動腳本
python web/run_web.py

# 方法3：直接使用streamlit（需要先安裝項目）
streamlit run web/app.py
```

然後在瀏覽器中訪問 `http://localhost:8501`

**Web界面特色功能**:

- 🇺🇸 **美股分析**: 支持 AAPL, TSLA, NVDA 等美股代碼
- 📊 **實時數據**: FinnHub 和 Yahoo Finance 提供美股實時行情數據
- 🤖 **智能體選擇**: 可選擇不同的分析師組合
- 📤 **報告導出**: 一鍵導出Markdown/Word/PDF格式專業分析報告
- 🎯 **5級研究深度**: 從快速分析(2-4分鐘)到全面分析(15-25分鐘)
- 📊 **智能分析師選擇**: 市場技術、基本面、新聞、社交媒體分析師
- 🔄 **實時進度顯示**: 可視化分析過程，避免等待焦慮
- 📈 **結構化結構**: 投資建議、目標價位、置信度、風險評估
- 🇨🇳 **完全中文化**: 界面和分析結果全中文顯示

**研究深度級別說明**:

- **1級 - 快速分析** (2-4分鐘): 日常監控，基礎決策
- **2級 - 基礎分析** (4-6分鐘): 常規投資，平衡速度
- **3級 - 標準分析** (6-10分鐘): 重要決策，推薦默認
- **4級 - 深度分析** (10-15分鐘): 重大投資，詳細研究
- **5級 - 全面分析** (15-25分鐘): 最重要決策，最全面分析

#### 💻 代碼調用（適合開發者）

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 配置 OpenAI
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-4o"               # 深度分析
config["quick_think_llm"] = "gpt-4o-mini"          # 快速任務

# 創建交易智能體
ta = TradingAgentsGraph(debug=True, config=config)

# 分析股票 (以蘋果公司為例)
state, decision = ta.propagate("AAPL", "2024-01-15")

# 輸出分析結果
print(f"推薦動作: {decision['action']}")
print(f"置信度: {decision['confidence']:.1%}")
print(f"風險評分: {decision['risk_score']:.1%}")
print(f"推理過程: {decision['reasoning']}")
```

#### 快速啟動腳本

```bash
# OpenAI演示
python examples/simple_analysis_demo.py

# 自訂分析演示
python examples/custom_analysis_demo.py
```

#### 📁 數據目錄配置

**新功能**: 靈活配置數據存儲路徑，支持多種配置方式：

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


| 🎯**我想要...** | 📖**推薦文件**                                            | ⏱️**閱讀時間** |
| --------------- | --------------------------------------------------------- | ---------------- |
| **快速上手**    | [🚀 快速開始](docs/overview/quick-start.md)               | 10分鐘           |
| **了解架構**    | [🏛️ 系統架構](docs/architecture/system-architecture.md) | 15分鐘           |
| **看代碼示例**  | [📚 基礎示例](docs/examples/basic-examples.md)            | 20分鐘           |
| **解決問題**    | [🆘 常見問題](docs/faq/faq.md)                            | 5分鐘            |
| **深度學習**  | [📁 完整文檔目錄](#-詳細文檔目錄)                         | 2小時+           |

> 💡 **提示**: 我們的 `docs/` 目錄包含了 **50,000+字** 的詳細中文文檔，這是與原版最大的區別！

## 📚 完整文檔體系 - 核心亮點

> **🌟 這是本項目與原版最大的區別！** 我們構建了業界最完整的中文金融AI框架文檔體系，包含超過 **50,000字** 的詳細技術文檔，**20+** 個專業文檔文件，**100+** 個代碼示例。

### 🎯 為什麼選擇我們的文檔？


| 對比維度     | 原版 TradingAgents | 🚀**中文增強版**           |
| ------------ | ------------------ | -------------------------- |
| **文檔語言** | 英文基礎說明       | **完整中文體系**           |
| **文檔深度** | 簡單介紹           | **深度技術剖析**           |
| **架構說明** | 概念性描述         | **詳細設計文檔 + 架構圖**  |
| **使用指南** | 基礎示例           | **從入門到專家的完整路徑** |
| **故障排除** | 無                 | **詳細FAQ + 解決方案**     |
| **代碼示例** | 少量示例           | **100+ 實用示例**          |

### 📖 文檔導航 - 按學習路徑組織

#### 🚀 **新手入門路徑** (推薦從這裡開始)

1. [📋 項目概述](docs/overview/project-overview.md) - **了解項目背景和核心價值**
2. [⚙️ 詳細安裝](docs/overview/installation.md) - **各平台詳細安裝指南**
3. [🚀 快速開始](docs/overview/quick-start.md) - **10分鐘上手指南**
4. [📚 基礎示例](docs/examples/basic-examples.md) - **8個實用的入門示例**

#### 🏗️ **架構理解路徑** (深入了解系統設計)

1. [🏛️ 系統架構](docs/architecture/system-architecture.md) - **完整的系統架構設計**
2. [🤖 智能體架構](docs/architecture/agent-architecture.md) - **多智能體協作機制**
3. [📊 數據流架構](docs/architecture/data-flow-architecture.md) - **數據處理全流程**
4. [🔄 圖結構設計](docs/architecture/graph-structure.md) - **LangGraph工作流程**

#### 🤖 **智能體深度解析** (了解每個智能體的設計)

1. [📈 分析師團隊](docs/agents/analysts.md) - **四類專業分析師詳解**
2. [🔬 研究員團隊](docs/agents/researchers.md) - **看漲/看跌辯論機制**
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

#### 💡 **高級應用** (擴展開發和實戰)

1. [📚 基礎示例](docs/examples/basic-examples.md) - **8個實用基礎示例**
2. [🚀 高級示例](docs/examples/advanced-examples.md) - **複雜場景和擴展開發**

#### ❓ **問題解決** (遇到問題時查看)

1. [🆘 常見問題](docs/faq/faq.md) - **詳細FAQ和解決方案**

### 📊 文檔統計數據

- 📄 **文檔文件數**: 20+ 個專業文檔
- 📝 **總字數**: 50,000+ 字詳細內容
- 💻 **代碼示例**: 100+ 個實用示例
- 📈 **架構圖表**: 10+ 個專業圖表
- 🎯 **覆蓋範圍**: 從入門到專家的完整路徑

### 🎨 文檔特色

- **🇨🇳 完全中文化**: 專為中文用戶優化的表達方式
- **📊 圖文並茂**: 豐富的架構圖和流程圖
- **💻 代碼豐富**: 每個概念都有對應的代碼示例
- **🔍 深度剖析**: 不僅告訴你怎麼做，還告訴你為什麼這樣做
- **🛠️ 實用導向**: 所有文檔都面向實際應用場景

---

## 📚 詳細文檔目錄

### 📁 **docs/ 目錄結構** - 完整的知識體系

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
│   ├── researchers.md       # 🔬 看漲/看跌辯論機制
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
├── 💡 examples/             # 示例教程 - 實戰應用
│   ├── basic-examples.md    # 📚 8個基礎示例
│   └── advanced-examples.md # 🚀 高級開發示例
│
└── ❓ faq/                  # 問題解決 - 疑難解答
    └── faq.md              # 🆘 常見問題FAQ
```

### 🎯 **重點推薦文檔** (必讀精選)

#### 🔥 **最受歡迎的文檔**

1. **[📋 項目概述](docs/overview/project-overview.md)** - ⭐⭐⭐⭐⭐

   > 了解項目的核心價值和技術特色，5分鐘讀懂整個框架
   >
2. **[🏛️ 系統架構](docs/architecture/system-architecture.md)** - ⭐⭐⭐⭐⭐

   > 深度解析多智能體協作機制，包含詳細架構圖
   >
3. **[📚 基礎示例](docs/examples/basic-examples.md)** - ⭐⭐⭐⭐⭐

   > 8個實用示例，從股票分析到投資組合優化
   >

#### 🚀 **技術深度文檔**

1. **[🤖 智能體架構](docs/architecture/agent-architecture.md)**

   > 多智能體設計模式和協作機制詳解
   >
2. **[📊 數據流架構](docs/architecture/data-flow-architecture.md)**

   > 數據獲取、處理、緩存的完整流程
   >
3. **[🔬 研究員團隊](docs/agents/researchers.md)**

   > 看漲/看跌研究員辯論機制的創新設計
   >

#### 💼 **實用工具文檔**

1. **[🌐 Web界面指南](docs/usage/web-interface-guide.md)** - ⭐⭐⭐⭐⭐

   > 完整的Web界面使用教程，包含5級研究深度詳細說明
   >
2. **[💰 投資分析指南](docs/usage/investment_analysis_guide.md)**

   > 從基礎到高級的完整投資分析教程
   >
3. **[🧠 LLM配置](docs/configuration/llm-config.md)**

   > 多LLM模型配置和成本優化策略
   >
4. **[💾 緩存策略](docs/data/caching.md)**

   > 多層緩存設計，顯著降低API調用成本
   >
5. **[🆘 常見問題](docs/faq/faq.md)**

   > 詳細的FAQ和故障排除指南
   >

### 📖 **按模塊瀏覽文檔**

<details>
<summary><strong>📖 概覽文檔</strong> - 項目入門必讀</summary>

- [📋 項目概述](docs/overview/project-overview.md) - 詳細的項目背景和特性介紹
- [🚀 快速開始](docs/overview/quick-start.md) - 從安裝到第一次運行的完整指南
- [⚙️ 詳細安裝](docs/overview/installation.md) - 各平台詳細安裝說明

</details>

<details>
<summary><strong>🏗️ 架構文檔</strong> - 深度理解系統設計</summary>

- [🏛️ 系統架構](docs/architecture/system-architecture.md) - 完整的系統架構設計
- [🤖 智能體架構](docs/architecture/agent-architecture.md) - 智能體設計模式和協作機制
- [📊 數據流架構](docs/architecture/data-flow-architecture.md) - 數據獲取、處理和分發流程
- [🔄 圖結構設計](docs/architecture/graph-structure.md) - LangGraph工作流程設計

</details>

<details>
<summary><strong>🤖 智能體文檔</strong> - 核心組件詳解</summary>

- [📈 分析師團隊](docs/agents/analysts.md) - 四類專業分析師詳解
- [🔬 研究員團隊](docs/agents/researchers.md) - 看漲/看跌研究員和辯論機制
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
<summary><strong>⚙️ 配置與部署</strong> - 性能調優指南</summary>

- [📝 配置指南](docs/configuration/config-guide.md) - 詳細的配置選項說明
- [🧠 LLM配置](docs/configuration/llm-config.md) - 大語言模型配置優化

</details>

<details>
<summary><strong>💡 示例和教程</strong> - 實戰應用指南</summary>

- [📚 基礎示例](docs/examples/basic-examples.md) - 8個實用的基礎示例
- [🚀 高級示例](docs/examples/advanced-examples.md) - 複雜場景和擴展開發

</details>

<details>
<summary><strong>❓ 幫助文檔</strong> - 問題解決方案</summary>

- [🆘 常見問題](docs/faq/faq.md) - 詳細的FAQ和解決方案

</details>

## 💰 成本控制

### 典型使用成本

- **經濟模式**: $0.01-0.05/次分析 (使用 gpt-4o-mini)
- **標準模式**: $0.05-0.15/次分析 (使用 gpt-4o)
- **高精度模式**: $0.10-0.30/次分析 (使用 gpt-4o + 多輪辯論)

### 成本優化建議

```python
# 低成本配置示例
cost_optimized_config = {
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini", 
    "max_debate_rounds": 1,
    "online_tools": False  # 使用緩存數據
}
```

## 🤝 貢獻指南

我們歡迎各種形式的貢獻：

### 貢獻類型

- 🐛 **Bug修複** - 發現並修複問題
- ✨ **新功能** - 添加新的功能特性
- 📚 **文檔改進** - 完善文檔和教程
- 🌐 **本地化** - 翻譯和本地化工作
- 🎨 **代碼優化** - 性能優化和代碼重構

### 貢獻流程

1. Fork 本倉庫
2. 創建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 創建 Pull Request

### 📋 查看貢獻者

查看所有貢獻者和詳細貢獻內容：**[🤝 貢獻者名單](CONTRIBUTORS.md)**

## 📄 許可證

本項目基於 Apache 2.0 許可證開源。詳见 [LICENSE](LICENSE) 文件。

### 許可證說明

- ✅ 商業使用
- ✅ 修改和分發
- ✅ 私人使用
- ✅ 專利使用
- ❗ 需要保留版權聲明
- ❗ 需要包含許可證副本

## 🙏 致謝與感恩

### 🌟 向源項目開發者致敬

我們向 [Tauric Research](https://github.com/TauricResearch) 團隊表達最深的敬意和感謝：

- **🎯 願景領導者**: 感謝您們在AI金融領域的前瞻性思考和創新實踐
- **💎 珍貴源碼**: 感謝您們開源的每一行代碼，它們凝聚着無數的智慧和心血
- **🏗️ 架構大師**: 感謝您們設計了如此優雅、可擴展的多智能體框架
- **💡 技術先驅**: 感謝您們將前沿AI技術與金融實務完美結合
- **🔄 持續貢獻**: 感謝您們持續的維護、更新和改進工作

### 🤝 社區貢獻者致謝

感謝所有為TradingAgents-CN項目做出貢獻的開發者和用戶！

詳細的貢獻者名單和貢獻內容請查看：**[📋 貢獻者名單](CONTRIBUTORS.md)**

包括但不限於：

- 🐳 **Docker容器化** - 部署方案優化
- 📄 **報告導出功能** - 多格式輸出支持
- 🐛 **Bug修複** - 系統穩定性提升
- 🔧 **代碼優化** - 用戶體驗改進
- 📝 **文檔完善** - 使用指南和教程
- 🌍 **社區建設** - 問題回饋和推廣
- **🌍 開源貢獻**: 感謝您們選擇Apache 2.0協議，給予開發者最大的自由
- **📚 知識分享**: 感謝您們提供的詳細文檔和最佳實踐指導

**特別感謝**：[TradingAgents](https://github.com/TauricResearch/TradingAgents) 項目為我們提供了堅實的技術基礎。雖然Apache 2.0協議賦予了我們使用源碼的權利，但我們深知每一行代碼的珍貴價值，將永遠銘記並感謝您們的無私貢獻。

### 🌏 專案使命

創建這個中文增強版本，我們懷著以下初心：

- **🌉 技術傳播**: 讓優秀的TradingAgents技術得到更廣泛的應用
- **🎓 教育普及**: 為AI金融教育提供更好的工具和資源
- **🤝 文化橋梁**: 在技術社群之間搭建交流合作的橋梁
- **🚀 創新推動**: 推動金融科技領域的AI技術創新和應用

### 🌍 開源社區

感謝所有為本項目貢獻代碼、文檔、建議和回饋的開發者和用戶。正是因為有了大家的支持，我們才能更好地服務中文用戶社區。

### 🤝 合作共贏

我們承諾：

- **尊重原創**: 始終尊重源項目的知識產權和開源協議
- **反饋貢獻**: 將有價值的改進和創新反饋給源項目和開源社區
- **持續改進**: 不斷完善中文增強版本，提供更好的用戶體驗
- **開放合作**: 歡迎與源項目團隊和全球開發者進行技術交流與合作

## 📈 版本歷史

- **v0.1.13** (2025-08-02): 原生OpenAI支持與LLM適配器架構優化
- **v0.1.12** (2025-07-29): 🧠 智能新聞分析模塊與項目結構優化
- **v0.1.11** (2025-07-27): 🤖 多LLM提供商集成與模型選擇持久化
- **v0.1.10** (2025-07-18): 🚀 Web界面實時進度顯示與智能會話管理
- **v0.1.9** (2025-07-16): 🎯 CLI用戶體驗重大優化與統一日誌管理
- **v0.1.8** (2025-07-15): 🎨 Web界面全面優化與用戶體驗提升
- **v0.1.7** (2025-07-13): 🐳 容器化部署與專業報告導出
- **v0.1.6** (2025-07-11): 修復資料來源與系統升級
- **v0.1.5** (2025-07-08): 多模型支援與效能最佳化
- **v0.1.4** (2025-07-05): 🏗️ 架構優化與配置管理重構
- **v0.1.3** (2025-06-28): 📈 市場數據支持增強
- **v0.1.2** (2025-06-15): 🌐 Web界面和配置管理
- **v0.1.1** (2025-06-01): 🧠 多LLM提供商集成

📋 **詳細更新日誌**: [CHANGELOG.md](./docs/releases/CHANGELOG.md)

## 📞 聯系方式

- **GitHub Issues**: [提交問題和建議](https://github.com/hsliuping/TradingAgents-CN/issues)
- **Email**: hsliup@163.com
- **原項目**: [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents)
- **文檔**: [完整文檔目錄](docs/)

## ⚠️ 風險提示

**重要聲明**: 本框架僅用於研究和教育目的，不構成投資建議。

- 📊 交易表現可能因多種因素而異
- 🤖 AI模型的預測存在不確定性
- 💰 投資有風險，決策需謹慎
- 👨‍💼 建議諮詢專業財務顧問

---

<div align="center">

**🌟 如果這個項目對您有幫助，請給我們一個 Star！**

[⭐ Star this repo](https://github.com/hsliuping/TradingAgents-CN) | [🍴 Fork this repo](https://github.com/hsliuping/TradingAgents-CN/fork) | [📖 Read the docs](./docs/)

</div>
