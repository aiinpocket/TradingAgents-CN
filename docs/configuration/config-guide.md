# 配置指南 (v0.1.7)

## 概述

TradingAgents-CN 提供了統一的配置系統，所有配置通過 `.env` 文件管理。本指南詳細介紹了所有可用的配置選項和最佳實踐，包括v0.1.7新增的Docker部署和報告導出配置。

## 🎯 v0.1.7 配置新特性

### 容器化部署配置
- ✅ **Docker環境變量**: 支持容器化部署的環境配置
- ✅ **服務發現**: 自動配置容器間服務連接
- ✅ **數據卷配置**: 持久化數據存储配置

### 報告導出配置
- ✅ **導出格式選擇**: 支持Word/PDF/Markdown格式配置
- ✅ **導出路徑配置**: 自定義導出文件存储路徑
- ✅ **格式轉換配置**: Pandoc和wkhtmltopdf配置選項

### LLM模型擴展
- ✅ **DeepSeek V3集成**: 成本優化的中文模型
- ✅ **智能模型路由**: 根據任務自動選擇最優模型
- ✅ **成本控制配置**: 詳細的成本監控和限制

## 配置文件結構

### .env 配置文件 (推薦)
```bash
# ===========================================
# TradingAgents-CN 配置文件 (v0.1.7)
# ===========================================

# 🧠 LLM 配置 (多模型支持)
# 🇨🇳 DeepSeek (推薦 - 成本低，中文優化)
DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here
DEEPSEEK_ENABLED=true

# 🇨🇳 阿里百炼通義千問 (推薦 - 中文理解好)
DASHSCOPE_API_KEY=your_dashscope_api_key_here
QWEN_ENABLED=true

# 🌍 Google AI Gemini (推薦 - 推理能力强)
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_ENABLED=true

# 🤖 OpenAI (可選 - 通用能力强，成本較高)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ENABLED=false

# 📊 數據源配置
FINNHUB_API_KEY=your_finnhub_api_key_here
TUSHARE_TOKEN=your_tushare_token

# 🗄️ 數據庫配置 (Docker自動配置)
MONGODB_ENABLED=false
REDIS_ENABLED=false
MONGODB_HOST=localhost
MONGODB_PORT=27018
REDIS_HOST=localhost
REDIS_PORT=6380

# 📁 路徑配置
TRADINGAGENTS_RESULTS_DIR=./results
TRADINGAGENTS_DATA_DIR=./data
```

## 配置選項詳解

### 1. 路徑配置

#### project_dir
- **類型**: `str`
- **默認值**: 項目根目錄
- **說明**: 項目根目錄路徑，用於定位其他相對路徑

#### results_dir
- **類型**: `str`
- **默認值**: `"./results"`
- **環境變量**: `TRADINGAGENTS_RESULTS_DIR`
- **說明**: 分析結果存储目錄

```python
config = {
    "results_dir": "/path/to/custom/results",  # 自定義結果目錄
}
```

#### data_cache_dir
- **類型**: `str`
- **默認值**: `"tradingagents/dataflows/data_cache"`
- **說明**: 數據緩存目錄

### 2. LLM 配置

#### llm_provider
- **類型**: `str`
- **可選值**: `"openai"`, `"anthropic"`, `"google"`
- **默認值**: `"openai"`
- **說明**: 大語言模型提供商

```python
# OpenAI 配置
config = {
    "llm_provider": "openai",
    "backend_url": "https://api.openai.com/v1",
    "deep_think_llm": "gpt-4o",
    "quick_think_llm": "gpt-4o-mini",
}

# Anthropic 配置
config = {
    "llm_provider": "anthropic",
    "backend_url": "https://api.anthropic.com",
    "deep_think_llm": "claude-3-opus-20240229",
    "quick_think_llm": "claude-3-haiku-20240307",
}

# Google 配置
config = {
    "llm_provider": "google",
    "backend_url": "https://generativelanguage.googleapis.com/v1",
    "deep_think_llm": "gemini-pro",
    "quick_think_llm": "gemini-pro",
}
```

#### deep_think_llm
- **類型**: `str`
- **默認值**: `"o4-mini"`
- **說明**: 用於深度思考任務的模型（如複雜分析、辩論）

**推薦模型**:
- **高性能**: `"gpt-4o"`, `"claude-3-opus-20240229"`
- **平衡**: `"gpt-4o-mini"`, `"claude-3-sonnet-20240229"`
- **經濟**: `"gpt-3.5-turbo"`, `"claude-3-haiku-20240307"`

#### quick_think_llm
- **類型**: `str`
- **默認值**: `"gpt-4o-mini"`
- **說明**: 用於快速任務的模型（如數據處理、格式化）

### 3. 辩論和討論配置

#### max_debate_rounds
- **類型**: `int`
- **默認值**: `1`
- **範围**: `1-10`
- **說明**: 研究員辩論的最大轮次

```python
# 不同場景的推薦配置
config_scenarios = {
    "quick_analysis": {"max_debate_rounds": 1},      # 快速分析
    "standard": {"max_debate_rounds": 2},            # 標準分析
    "thorough": {"max_debate_rounds": 3},            # 深度分析
    "comprehensive": {"max_debate_rounds": 5},       # 全面分析
}
```

#### max_risk_discuss_rounds
- **類型**: `int`
- **默認值**: `1`
- **範围**: `1-5`
- **說明**: 風險管理討論的最大轮次

#### max_recur_limit
- **類型**: `int`
- **默認值**: `100`
- **說明**: 遞歸調用的最大限制，防止無限循環

### 4. 工具配置

#### online_tools
- **類型**: `bool`
- **默認值**: `True`
- **說明**: 是否使用在線數據工具

```python
# 在線模式 - 獲取實時數據
config = {"online_tools": True}

# 離線模式 - 使用緩存數據
config = {"online_tools": False}
```

## 高級配置選項

### 1. 智能體權重配置
```python
config = {
    "analyst_weights": {
        "fundamentals": 0.3,    # 基本面分析權重
        "technical": 0.3,       # 技術分析權重
        "news": 0.2,           # 新聞分析權重
        "social": 0.2,         # 社交媒體分析權重
    }
}
```

### 2. 風險管理配置
```python
config = {
    "risk_management": {
        "risk_threshold": 0.8,           # 風險阈值
        "max_position_size": 0.1,        # 最大仓位比例
        "stop_loss_threshold": 0.05,     # 止損阈值
        "take_profit_threshold": 0.15,   # 止盈阈值
    }
}
```

### 3. 數據源配置
```python
config = {
    "data_sources": {
        "primary": "finnhub",            # 主要數據源
        "fallback": ["yahoo", "alpha_vantage"],  # 备用數據源
        "cache_ttl": {
            "price_data": 300,           # 價格數據緩存5分鐘
            "fundamental_data": 86400,   # 基本面數據緩存24小時
            "news_data": 3600,          # 新聞數據緩存1小時
        }
    }
}
```

### 4. 性能優化配置
```python
config = {
    "performance": {
        "parallel_analysis": True,       # 並行分析
        "max_workers": 4,               # 最大工作線程數
        "timeout": 300,                 # 超時時間（秒）
        "retry_attempts": 3,            # 重試次數
        "batch_size": 10,               # 批處理大小
    }
}
```

## 環境變量配置

### 必需的環境變量
```bash
# OpenAI API
export OPENAI_API_KEY="your_openai_api_key"

# FinnHub API
export FINNHUB_API_KEY="your_finnhub_api_key"

# 可選的環境變量
export ANTHROPIC_API_KEY="your_anthropic_api_key"
export GOOGLE_API_KEY="your_google_api_key"
export TRADINGAGENTS_RESULTS_DIR="/custom/results/path"
```

### .env 文件配置
```bash
# .env 文件
OPENAI_API_KEY=your_openai_api_key
FINNHUB_API_KEY=your_finnhub_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
TRADINGAGENTS_RESULTS_DIR=./custom_results
TRADINGAGENTS_LOG_LEVEL=INFO
```

## 配置最佳實踐

### 1. 成本優化配置
```python
# 低成本配置
cost_optimized_config = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "online_tools": False,  # 使用緩存數據
}
```

### 2. 高性能配置
```python
# 高性能配置
high_performance_config = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",
    "quick_think_llm": "gpt-4o",
    "max_debate_rounds": 3,
    "max_risk_discuss_rounds": 2,
    "online_tools": True,
    "performance": {
        "parallel_analysis": True,
        "max_workers": 8,
    }
}
```

### 3. 開發環境配置
```python
# 開發環境配置
dev_config = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 1,
    "online_tools": True,
    "debug": True,
    "log_level": "DEBUG",
}
```

### 4. 生產環境配置
```python
# 生產環境配置
prod_config = {
    "llm_provider": "openai",
    "deep_think_llm": "gpt-4o",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 2,
    "max_risk_discuss_rounds": 1,
    "online_tools": True,
    "performance": {
        "parallel_analysis": True,
        "max_workers": 4,
        "timeout": 600,
        "retry_attempts": 3,
    },
    "logging": {
        "level": "INFO",
        "file": "/var/log/tradingagents.log",
    }
}
```

## 配置驗證

### 配置驗證器
```python
class ConfigValidator:
    """配置驗證器"""
    
    def validate(self, config: Dict) -> Tuple[bool, List[str]]:
        """驗證配置的有效性"""
        errors = []
        
        # 檢查必需字段
        required_fields = ["llm_provider", "deep_think_llm", "quick_think_llm"]
        for field in required_fields:
            if field not in config:
                errors.append(f"Missing required field: {field}")
        
        # 檢查LLM提供商
        valid_providers = ["openai", "anthropic", "google"]
        if config.get("llm_provider") not in valid_providers:
            errors.append(f"Invalid llm_provider. Must be one of: {valid_providers}")
        
        # 檢查數值範围
        if config.get("max_debate_rounds", 1) < 1:
            errors.append("max_debate_rounds must be >= 1")
        
        return len(errors) == 0, errors

# 使用示例
validator = ConfigValidator()
is_valid, errors = validator.validate(config)
if not is_valid:
    print("Configuration errors:", errors)
```

## 動態配置更新

### 運行時配置更新
```python
class TradingAgentsGraph:
    def update_config(self, new_config: Dict):
        """運行時更新配置"""
        
        # 驗證新配置
        validator = ConfigValidator()
        is_valid, errors = validator.validate(new_config)
        
        if not is_valid:
            raise ValueError(f"Invalid configuration: {errors}")
        
        # 更新配置
        self.config.update(new_config)
        
        # 重新初始化受影響的組件
        self._reinitialize_components()
    
    def _reinitialize_components(self):
        """重新初始化組件"""
        # 重新初始化LLM
        self._setup_llms()
        
        # 重新初始化智能體
        self._setup_agents()
```

通過合理的配置，您可以根據不同的使用場景優化 TradingAgents-CN 的性能和成本。

## 🐳 Docker部署配置 (v0.1.7新增)

### Docker環境變量

```bash
# === Docker特定配置 ===
# 數據庫連接 (使用容器服務名)
MONGODB_URL=mongodb://mongodb:27017/tradingagents
REDIS_URL=redis://redis:6379

# 服務端口配置
WEB_PORT=8501
MONGODB_PORT=27017
REDIS_PORT=6379
MONGO_EXPRESS_PORT=8081
REDIS_COMMANDER_PORT=8082
```

## 📄 報告導出配置 (v0.1.7新增)

### 導出功能配置

```bash
# === 報告導出配置 ===
# 啟用導出功能
EXPORT_ENABLED=true

# 默認導出格式 (word,pdf,markdown)
EXPORT_DEFAULT_FORMAT=word,pdf

# 導出文件路徑
EXPORT_OUTPUT_PATH=./exports

# Pandoc配置
PANDOC_PATH=/usr/bin/pandoc
WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf
```

## 🧠 LLM模型路由配置 (v0.1.7新增)

### 智能模型選擇

```bash
# === 模型路由配置 ===
# 啟用智能路由
LLM_SMART_ROUTING=true

# 默認模型優先級
LLM_PRIORITY_ORDER=deepseek,qwen,gemini,openai

# 成本控制
LLM_DAILY_COST_LIMIT=10.0
LLM_COST_ALERT_THRESHOLD=8.0
```

## 最佳實踐 (v0.1.7更新)

### 1. 安全性
- 🔐 **API密鑰保護**: 永远不要将 `.env` 文件提交到版本控制
- 🔒 **權限控制**: 設置適當的文件權限 (600)
- 🛡️ **密鑰轮換**: 定期更換API密鑰

### 2. 性能優化
- ⚡ **模型選擇**: 根據任務選擇合適的模型
- 💾 **緩存策略**: 合理配置緩存TTL
- 🔄 **連接池**: 優化數據庫連接池大小

### 3. 成本控制
- 💰 **成本監控**: 設置合理的成本限制
- 📊 **使用統計**: 定期查看Token使用情况
- 🎯 **模型優化**: 優先使用成本效益高的模型

---

*最後更新: 2025-07-13*
*版本: cn-0.1.7*
