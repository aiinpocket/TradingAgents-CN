# TradingAgents-CN v0.1.11 更新日誌

## 🚀 版本概述

**發布日期**: 2025-01-27  
**版本號**: cn-0.1.11  
**主題**: 多LLM提供商集成与模型選擇持久化

這是一個重大功能更新版本，全面集成了多個LLM提供商，實現了真正的模型選擇持久化，並大幅優化了Web界面用戶體驗。

## ✨ 新功能

### 🤖 多LLM提供商集成

#### 支持的提供商
- **DashScope (阿里百炼)**
  - qwen-turbo: 快速響應
  - qwen-plus-latest: 平衡性能
  - qwen-max: 最强性能

- **DeepSeek V3**
  - deepseek-chat: 最新V3模型

- **Google AI**
  - gemini-2.0-flash: 推薦使用
  - gemini-1.5-pro: 强大性能
  - gemini-1.5-flash: 快速響應

- **OpenRouter (60+模型)**
  - **OpenAI類別**: o4-mini-high, o3-pro, o1-pro, GPT-4o等
  - **Anthropic類別**: Claude 4 Opus, Claude 4 Sonnet, Claude 3.5等
  - **Meta類別**: Llama 4 Maverick, Llama 4 Scout, Llama 3.3等
  - **Google類別**: Gemini 2.5 Pro, Gemini 2.5 Flash等
  - **自定義模型**: 支持任意OpenRouter模型ID

#### 快速選擇按钮
- 🧠 Claude 3.7 Sonnet - 最新對話模型
- 💎 Claude 4 Opus - 顶級性能模型
- 🤖 GPT-4o - OpenAI旗舰模型
- 🦙 Llama 4 Scout - Meta最新模型
- 🌟 Gemini 2.5 Pro - Google多模態

### 💾 模型選擇持久化

#### 技術實現
- **URL參數存储**: 使用`st.query_params`實現真正的持久化
- **Session State緩存**: 內存中快速訪問配置
- **雙重保險**: URL參數 + Session State結合
- **自動恢複**: 页面加載時自動恢複設置

#### 功能特點
- ✅ 支持浏覽器刷新後配置保持
- ✅ 支持書簽保存特定配置
- ✅ 支持URL分享模型配置
- ✅ 支持跨會話持久化
- ✅ 無需外部存储依賴

### 🎨 Web界面優化

#### 侧邊栏優化
- **320px宽度**: 優化空間利用率
- **響應式設計**: 適配不同屏幕尺寸
- **清晰分類**: 模型按提供商和類別組織
- **詳細描述**: 每個模型都有清晰的功能說明

#### 用戶體驗改進
- **一键選擇**: 快速按钮提升操作效率
- **實時反馈**: 配置變化立即生效
- **錯誤處理**: 友好的錯誤提示和恢複機制
- **調試支持**: 詳細的日誌追蹤配置變化

## 🔧 技術改進

### 新增模塊

#### `web/utils/persistence.py`
```python
class ModelPersistence:
    """模型選擇持久化管理器"""
    
    def save_config(self, provider, category, model):
        """保存配置到session state和URL"""
    
    def load_config(self):
        """從session state或URL加載配置"""
    
    def clear_config(self):
        """清除配置"""
```

### 核心改進

#### 侧邊栏組件 (`web/components/sidebar.py`)
- 集成持久化模塊
- 支持4個LLM提供商
- 實現60+模型選擇
- 添加詳細的調試日誌
- 優化用戶界面布局

#### 內存管理 (`tradingagents/agents/utils/memory.py`)
- 解決ChromaDB並發冲突
- 實現單例模式
- 改進錯誤處理機制

#### 分析運行器 (`web/utils/analysis_runner.py`)
- 增强錯誤處理
- 改進日誌記錄
- 優化性能表現

## 📊 支持統計

### 模型覆蓋
- **4個LLM提供商**
- **5個OpenRouter類別**
- **60+個具體模型**
- **5個快速選擇按钮**
- **無限自定義模型**

### 功能覆蓋
- ✅ 所有提供商支持持久化
- ✅ 所有模型選擇支持持久化
- ✅ 快速按钮支持持久化
- ✅ 自定義模型支持持久化
- ✅ URL參數完整支持

## 🧪 測試驗證

### 基础測試場景
1. 選擇DashScope → qwen-max → 刷新 → 檢查保持
2. 選擇DeepSeek → deepseek-chat → 刷新 → 檢查保持
3. 選擇Google → gemini-2.0-flash → 刷新 → 檢查保持

### OpenRouter測試場景
1. 選擇OpenRouter → OpenAI → o4-mini-high → 刷新
2. 選擇OpenRouter → Anthropic → claude-opus-4 → 刷新
3. 選擇OpenRouter → Meta → llama-4-maverick → 刷新
4. 選擇OpenRouter → Google → gemini-2.5-pro → 刷新

### 自定義模型測試
1. 選擇OpenRouter → Custom → 輸入模型ID → 刷新
2. 選擇OpenRouter → Custom → 點擊快速按钮 → 刷新
3. 檢查URL參數是否包含正確配置

## 🔍 觀察要點

### 成功標誌
- 日誌顯示 `🔧 [Persistence] 恢複` 而不是 `初始化`
- URL包含參數: `?provider=...&category=...&model=...`
- 刷新後選擇完全保持
- 配置正確傳遞給分析系統

### 調試日誌
- `🔧 [Persistence] 恢複 llm_provider: xxx`
- `🔄 [Persistence] 模型變更: xxx → yyy`
- `💾 [Persistence] 模型已保存: xxx`
- `🔄 [Persistence] 返回配置 - provider: xxx, model: yyy`

## 🚀 升級指南

### 從v0.1.10升級

1. **拉取最新代碼**
   ```bash
   git pull origin main
   ```

2. **重新啟動應用**
   ```bash
   streamlit run web/app.py
   ```

3. **驗證功能**
   - 檢查侧邊栏是否顯示新的LLM提供商選項
   - 測試模型選擇是否在刷新後保持
   - 驗證URL參數是否正確更新

### 配置要求

確保`.env`文件包含所需的API密鑰：
```env
# DashScope (阿里百炼)
DASHSCOPE_API_KEY=your_dashscope_key

# DeepSeek
DEEPSEEK_API_KEY=your_deepseek_key

# Google AI
GOOGLE_API_KEY=your_google_key

# OpenRouter
OPENROUTER_API_KEY=your_openrouter_key
```

## 🎯 下一步計劃

### v0.1.12 規劃
- 更多LLM提供商集成 (Anthropic直連、OpenAI直連等)
- 模型性能對比和推薦系統
- 高級配置選項 (溫度、最大token等)
- 模型使用統計和成本分析

### 長期規劃
- 多模態模型支持 (圖像、語音等)
- 模型微調和個性化
- 企業級部署方案
- 更多語言支持

## 🙏 致谢

感谢所有用戶的反馈和建议，特別是對模型選擇持久化功能的需求。這個版本的改進直接來源於用戶的真實使用體驗。

---

**完整更新內容**: 8個文件修改，763行新增，408行刪除  
**核心新增**: `web/utils/persistence.py` 持久化模塊  
**主要優化**: 侧邊栏組件、內存管理、分析運行器
