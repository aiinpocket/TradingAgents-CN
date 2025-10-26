# 快速開始指南

## 概述

本指南将幫助您快速上手 TradingAgents 框架，從安裝到運行第一個交易分析，只需几分鐘時間。

## 🎉 v0.1.7 新特性

### Docker容器化部署
- ✅ **一键部署**: Docker Compose完整環境
- ✅ **服務編排**: Web應用、MongoDB、Redis集成
- ✅ **開發優化**: Volume映射，實時代碼同步

### 專業報告導出
- ✅ **多格式支持**: Word/PDF/Markdown導出
- ✅ **商業級质量**: 專業排版，完整內容
- ✅ **一键下載**: Web界面直接導出

### DeepSeek V3集成
- ✅ **成本優化**: 比GPT-4便宜90%以上
- ✅ **工具調用**: 强大的數據分析能力
- ✅ **中文優化**: 專為中文金融場景設計
- ✅ **用戶界面更新**: 所有提示信息準確反映數據來源

### 推薦LLM配置
```bash
# 高性價比選擇
DASHSCOPE_API_KEY=your_dashscope_key  # 阿里百炼
DEEPSEEK_API_KEY=your_deepseek_key    # DeepSeek V3

# 數據源配置
TUSHARE_TOKEN=your_tushare_token      # Tushare數據
```

## 前置要求

### 系統要求
- **操作系統**: Windows 10+, macOS 10.15+, 或 Linux
- **Python**: 3.10 或更高版本
- **內存**: 至少 4GB RAM (推薦 8GB+)
- **存储**: 至少 2GB 可用空間

### API 密鑰
在開始之前，您需要獲取以下API密鑰：

1. **🇨🇳 阿里百炼 API Key** (推薦)
   - 訪問 [阿里云百炼平台](https://dashscope.aliyun.com/)
   - 註冊账戶並獲取API密鑰
   - 國產模型，無需科學上網，響應速度快

2. **FinnHub API Key** (必需)
   - 訪問 [FinnHub](https://finnhub.io/)
   - 註冊免費账戶並獲取API密鑰

3. **Google AI API Key** (推薦)
   - 訪問 [Google AI Studio](https://aistudio.google.com/)
   - 獲取免費API密鑰，支持Gemini模型

4. **其他API密鑰** (可選)
   - OpenAI API (需要科學上網)
   - Anthropic API (需要科學上網)

## 快速安裝

### 1. 克隆項目
```bash
# 克隆中文增强版
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
```

### 2. 創建虛擬環境
```bash
# 使用 conda
conda create -n tradingagents python=3.13
conda activate tradingagents

# 或使用 venv
python -m venv tradingagents
source tradingagents/bin/activate  # Linux/macOS
# tradingagents\Scripts\activate  # Windows
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 配置環境變量

創建 `.env` 文件（推薦方式）：
```bash
# 複制配置模板
cp .env.example .env

# 編辑 .env 文件，配置以下API密鑰：

# 🇨🇳 阿里百炼 (推薦)
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# FinnHub (必需)
FINNHUB_API_KEY=your_finnhub_api_key_here

# Google AI (可選)
GOOGLE_API_KEY=your_google_api_key_here

# 數據庫配置 (可選，默認禁用)
MONGODB_ENABLED=false
REDIS_ENABLED=false
```

## 第一次運行

### 🌐 使用Web界面 (推薦)

最簡單的開始方式是使用Web管理界面：

```bash
# 啟動Web界面
streamlit run web/app.py
```

然後在浏覽器中訪問 `http://localhost:8501`

Web界面提供：
1. 🎛️ 直觀的股票分析界面
2. ⚙️ API密鑰和配置管理
3. 📊 實時分析進度顯示
4. 💰 Token使用統計
5. 🇨🇳 完整的中文界面

### 使用命令行界面 (CLI)

如果您偏好命令行：

```bash
python -m cli.main
```

### 使用 Python API

創建一個簡單的Python腳本：

```python
# quick_start.py
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 創建配置
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "gpt-4o-mini"  # 使用較便宜的模型進行測試
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1  # 减少辩論轮次以節省成本
config["online_tools"] = True  # 使用在線數據

# 初始化交易智能體圖
ta = TradingAgentsGraph(debug=True, config=config)

# 執行分析
print("開始分析 AAPL...")
state, decision = ta.propagate("AAPL", "2024-01-15")

# 輸出結果
print("\n=== 分析結果 ===")
print(f"推薦動作: {decision.get('action', 'hold')}")
print(f"置信度: {decision.get('confidence', 0.5):.2f}")
print(f"風險評分: {decision.get('risk_score', 0.5):.2f}")
print(f"推理過程: {decision.get('reasoning', 'N/A')}")
```

運行腳本：
```bash
python quick_start.py
```

## 配置選項

### 基本配置
```python
config = {
    # LLM 設置
    "llm_provider": "openai",           # 或 "anthropic", "google"
    "deep_think_llm": "gpt-4o-mini",    # 深度思考模型
    "quick_think_llm": "gpt-4o-mini",   # 快速思考模型
    
    # 辩論設置
    "max_debate_rounds": 1,             # 辩論轮次 (1-5)
    "max_risk_discuss_rounds": 1,       # 風險討論轮次
    
    # 數據設置
    "online_tools": True,               # 使用在線數據
}
```

### 智能體選擇
```python
# 選擇要使用的分析師
selected_analysts = [
    "market",        # 技術分析師
    "fundamentals",  # 基本面分析師
    "news",         # 新聞分析師
    "social"        # 社交媒體分析師
]

ta = TradingAgentsGraph(
    selected_analysts=selected_analysts,
    debug=True,
    config=config
)
```

## 示例分析流程

### 完整的分析示例
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
import json

def analyze_stock(symbol, date):
    """分析指定股票"""
    
    # 配置
    config = DEFAULT_CONFIG.copy()
    config["deep_think_llm"] = "gpt-4o-mini"
    config["quick_think_llm"] = "gpt-4o-mini"
    config["max_debate_rounds"] = 2
    config["online_tools"] = True
    
    # 創建分析器
    ta = TradingAgentsGraph(
        selected_analysts=["market", "fundamentals", "news", "social"],
        debug=True,
        config=config
    )
    
    print(f"正在分析 {symbol} ({date})...")
    
    try:
        # 執行分析
        state, decision = ta.propagate(symbol, date)
        
        # 輸出詳細結果
        print("\n" + "="*50)
        print(f"股票: {symbol}")
        print(f"日期: {date}")
        print("="*50)
        
        print(f"\n📊 最终決策:")
        print(f"  動作: {decision.get('action', 'hold').upper()}")
        print(f"  數量: {decision.get('quantity', 0)}")
        print(f"  置信度: {decision.get('confidence', 0.5):.1%}")
        print(f"  風險評分: {decision.get('risk_score', 0.5):.1%}")
        
        print(f"\n💭 推理過程:")
        print(f"  {decision.get('reasoning', 'N/A')}")
        
        # 分析師報告摘要
        if hasattr(state, 'analyst_reports'):
            print(f"\n📈 分析師報告摘要:")
            for analyst, report in state.analyst_reports.items():
                score = report.get('overall_score', report.get('score', 0.5))
                print(f"  {analyst}: {score:.1%}")
        
        return decision
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        return None

# 運行示例
if __name__ == "__main__":
    # 分析苹果公司股票
    result = analyze_stock("AAPL", "2024-01-15")
    
    if result:
        print("\n✅ 分析完成!")
    else:
        print("\n❌ 分析失败!")
```

## 常见問題解決

### 1. API 密鑰錯誤
```
錯誤: OpenAI API key not found
解決: 確保正確設置了 OPENAI_API_KEY 環境變量
```

### 2. 網絡連接問題
```
錯誤: Connection timeout
解決: 檢查網絡連接，或使用代理設置
```

### 3. 內存不足
```
錯誤: Out of memory
解決: 减少 max_debate_rounds 或使用更小的模型
```

### 4. 數據獲取失败
```
錯誤: Failed to fetch data
解決: 檢查 FINNHUB_API_KEY 是否正確，或稍後重試
```

## 成本控制建议

### 1. 使用較小的模型
```python
config["deep_think_llm"] = "gpt-4o-mini"    # 而不是 "gpt-4o"
config["quick_think_llm"] = "gpt-4o-mini"   # 而不是 "gpt-4o"
```

### 2. 减少辩論轮次
```python
config["max_debate_rounds"] = 1              # 而不是 3-5
config["max_risk_discuss_rounds"] = 1        # 而不是 2-3
```

### 3. 選擇性使用分析師
```python
# 只使用核心分析師
selected_analysts = ["market", "fundamentals"]  # 而不是全部四個
```

### 4. 使用緩存數據
```python
config["online_tools"] = False  # 使用緩存數據而不是實時數據
```

## 下一步

現在您已經成功運行了第一個分析，可以：

1. **探索更多功能**: 查看 [API參考文档](../api/core-api.md)
2. **自定義配置**: 阅讀 [配置指南](../configuration/config-guide.md)
3. **開發自定義智能體**: 參考 [擴展開發指南](../development/extending.md)
4. **查看更多示例**: 浏覽 [示例和教程](../examples/basic-examples.md)

## 獲取幫助

如果遇到問題，可以：
- 查看 [常见問題](../faq/faq.md)
- 訪問 [GitHub Issues](https://github.com/TauricResearch/TradingAgents/issues)
- 加入 [Discord 社区](https://discord.com/invite/hk9PGKShPK)
- 查看 [故障排除指南](../faq/troubleshooting.md)

祝您使用愉快！🚀
