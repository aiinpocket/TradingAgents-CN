# 常見問題解答 (FAQ)

## 概述

本文檔收集了用戶在使用 TradingAgents 框架時最常遇到的問題和解答，幫助您快速解決常見問題。

## 🚀 安裝和配置

### Q1: 安裝時出現依賴衝突怎麼辦？

**A:** 依賴衝突通常是由於不同套件的版本要求不兼容導致的。解決方法：

```bash
# 方法1: 使用新的虛擬環境
conda create -n tradingagents-clean python=3.11
conda activate tradingagents-clean
pip install -r requirements.txt

# 方法2: 使用 pip-tools 解決衝突
pip install pip-tools
pip-compile requirements.in
pip-sync requirements.txt

# 方法3: 逐個安裝核心依賴
pip install langchain-openai langgraph finnhub-python pandas
```

### Q2: API 密鑰設置後仍然報錯？

**A:** 檢查以下幾個方面：

1. **環境變數設置**：
```bash
# 檢查環境變數是否正確設置
echo $OPENAI_API_KEY
echo $FINNHUB_API_KEY

# Windows 用戶
echo %OPENAI_API_KEY%
echo %FINNHUB_API_KEY%
```

2. **密鑰格式驗證**：
```python
import os
# OpenAI 密鑰應該以 'sk-' 開頭
openai_key = os.getenv('OPENAI_API_KEY')
print(f"OpenAI Key: {openai_key[:10]}..." if openai_key else "Not set")

# FinnHub 密鑰是字母數字組合
finnhub_key = os.getenv('FINNHUB_API_KEY')
print(f"FinnHub Key: {finnhub_key[:10]}..." if finnhub_key else "Not set")
```

3. **權限檢查**：
```python
# 測試 API 連接
import openai
import finnhub

# 測試 OpenAI
try:
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}],
        max_tokens=5
    )
    print("OpenAI API 連接成功")
except Exception as e:
    print(f"OpenAI API 錯誤: {e}")

# 測試 FinnHub
try:
    finnhub_client = finnhub.Client(api_key=os.getenv('FINNHUB_API_KEY'))
    quote = finnhub_client.quote('AAPL')
    print("FinnHub API 連接成功")
except Exception as e:
    print(f"FinnHub API 錯誤: {e}")
```

### Q3: 支援哪些 Python 版本？

**A:** TradingAgents 支援 Python 3.10, 3.11, 和 3.12。推薦使用 Python 3.11 以獲得最佳性能和兼容性。

```bash
# 檢查 Python 版本
python --version

# 如果版本不符合要求，使用 pyenv 安裝
pyenv install 3.11.7
pyenv global 3.11.7
```

## 💰 成本和使用

### Q4: 使用 TradingAgents 的成本是多少？

**A:** 成本主要來自 LLM API 調用：

**典型成本估算**（單次分析）：
- **經濟模式**：$0.01-0.05（使用 gpt-4o-mini）
- **標準模式**：$0.05-0.15（使用 gpt-4o）
- **高精度模式**：$0.10-0.30（使用 gpt-4o + 多輪辯論）

**成本優化建議**：
```python
# 低成本配置
cost_optimized_config = {
    "deep_think_llm": "gpt-4o-mini",
    "quick_think_llm": "gpt-4o-mini",
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "online_tools": False  # 使用緩存數據
}
```

### Q5: 如何控制 API 調用成本？

**A:** 多種成本控制策略：

1. **設置預算限制**：
```python
class BudgetController:
    def __init__(self, daily_budget=50):
        self.daily_budget = daily_budget
        self.current_usage = 0

    def check_budget(self, estimated_cost):
        if self.current_usage + estimated_cost > self.daily_budget:
            raise Exception("Daily budget exceeded")
        return True
```

2. **使用緩存**：
```python
config = {
    "online_tools": False,  # 使用緩存數據
    "cache_duration": 3600  # 1小時緩存
}
```

3. **選擇性分析師**：
```python
# 只使用核心分析師
selected_analysts = ["market", "fundamentals"]  # 而不是全部四個
```

## 🔧 技術問題

### Q6: 分析速度太慢怎麼辦？

**A:** 多種優化方法：

1. **並行處理**：
```python
config = {
    "parallel_analysis": True,
    "max_workers": 4
}
```

2. **使用更快的模型**：
```python
config = {
    "deep_think_llm": "gpt-4o-mini",  # 更快的模型
    "quick_think_llm": "gpt-4o-mini"
}
```

3. **減少辯論輪次**：
```python
config = {
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1
}
```

4. **啟用緩存**：
```python
config = {
    "online_tools": True,
    "cache_enabled": True
}
```

### Q7: 內存使用過高怎麼解決？

**A:** 內存優化策略：

1. **限制緩存大小**：
```python
config = {
    "memory_cache": {
        "max_size": 500,  # 減少緩存項數量
        "cleanup_threshold": 0.7
    }
}
```

2. **分批處理**：
```python
# 分批分析多只股票
def batch_analysis(symbols, batch_size=5):
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i+batch_size]
        # 處理批次
        yield analyze_batch(batch)
```

3. **清理資源**：
```python
import gc

def analyze_with_cleanup(symbol, date):
    try:
        result = ta.propagate(symbol, date)
        return result
    finally:
        gc.collect()  # 強制垃圾回收
```

### Q8: 網路連接不穩定導致分析失敗？

**A:** 網路問題解決方案：

1. **重試機制**：
```python
import time
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(delay * (2 ** attempt))
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3)
def robust_analysis(symbol, date):
    return ta.propagate(symbol, date)
```

2. **超時設置**：
```python
config = {
    "timeout": 60,  # 60秒超時
    "connect_timeout": 10
}
```

3. **代理設置**：
```python
import os
os.environ['HTTP_PROXY'] = 'http://proxy.company.com:8080'
os.environ['HTTPS_PROXY'] = 'https://proxy.company.com:8080'
```

## 📊 數據和分析

### Q9: 某些股票無法獲取數據？

**A:** 數據獲取問題排查：

1. **檢查股票代碼**：
```python
# 確保使用正確的股票代碼格式
symbols = {
    "US": "AAPL",           # 美股
}
```

2. **驗證數據源**：
```python
def check_data_availability(symbol):
    try:
        # 檢查 FinnHub
        finnhub_data = finnhub_client.quote(symbol)
        print(f"FinnHub: {symbol} - OK")
    except:
        print(f"FinnHub: {symbol} - Failed")

    try:
        # 檢查 Yahoo Finance
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info
        print(f"Yahoo: {symbol} - OK")
    except:
        print(f"Yahoo: {symbol} - Failed")
```

3. **使用備用數據源**：
```python
config = {
    "data_sources": {
        "primary": "finnhub",
        "fallback": ["yahoo", "alpha_vantage"]
    }
}
```

### Q10: 分析結果不準確或不合理？

**A:** 提高分析準確性的方法：

1. **增加辯論輪次**：
```python
config = {
    "max_debate_rounds": 3,  # 增加辯論輪次
    "max_risk_discuss_rounds": 2
}
```

2. **使用更強的模型**：
```python
config = {
    "deep_think_llm": "gpt-4o",  # 使用更強的模型
    "quick_think_llm": "gpt-4o-mini"
}
```

3. **調整分析師權重**：
```python
config = {
    "analyst_weights": {
        "fundamentals": 0.4,  # 增加基本面權重
        "technical": 0.3,
        "news": 0.2,
        "social": 0.1
    }
}
```

4. **啟用更多數據源**：
```python
config = {
    "online_tools": True,
    "data_sources": ["finnhub", "yahoo", "reddit", "google_news"]
}
```

## 🛠️ 開發和擴展

### Q11: 如何創建自訂智能體？

**A:** 創建自訂智能體的步驟：

1. **繼承基礎類**：
```python
from tradingagents.agents.analysts.base_analyst import BaseAnalyst

class CustomAnalyst(BaseAnalyst):
    def __init__(self, llm, config):
        super().__init__(llm, config)
        self.custom_tools = self._initialize_custom_tools()

    def perform_analysis(self, data: Dict) -> Dict:
        # 實現自訂分析邏輯
        return {
            "custom_score": 0.75,
            "custom_insights": ["insight1", "insight2"],
            "recommendation": "buy"
        }
```

2. **註冊到框架**：
```python
# 在配置中添加自訂智能體
config = {
    "custom_analysts": {
        "custom": CustomAnalyst
    }
}
```

### Q12: 如何集成新的數據源？

**A:** 集成新數據源的方法：

1. **創建數據提供器**：
```python
class CustomDataProvider:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_data(self, symbol):
        # 實現數據獲取邏輯
        return {"custom_metric": 0.85}
```

2. **註冊數據源**：
```python
config = {
    "custom_data_sources": {
        "custom_provider": CustomDataProvider
    }
}
```

## 🚨 錯誤處理

### Q13: 常見錯誤代碼及解決方法

**A:** 主要錯誤類型和解決方案：

| 錯誤類型 | 原因 | 解決方法 |
|---------|------|---------|
| `API_KEY_INVALID` | API密鑰無效 | 檢查密鑰格式和權限 |
| `RATE_LIMIT_EXCEEDED` | 超過API限制 | 降低調用頻率或升級帳戶 |
| `NETWORK_TIMEOUT` | 網路超時 | 檢查網路連接，增加超時時間 |
| `DATA_NOT_FOUND` | 數據不存在 | 檢查股票代碼，使用備用數據源 |
| `INSUFFICIENT_MEMORY` | 內存不足 | 減少緩存大小，分批處理 |

### Q14: 如何啟用調試模式？

**A:** 調試模式配置：

```python
# 啟用詳細日誌
import logging
logging.basicConfig(level=logging.DEBUG)

# 啟用調試模式
config = {
    "debug": True,
    "log_level": "DEBUG",
    "save_intermediate_results": True
}

# 使用調試配置
ta = TradingAgentsGraph(debug=True, config=config)
```

## 📞 獲取幫助

### Q15: 在哪裡可以獲得更多幫助？

**A:** 多種獲取幫助的渠道：

1. **官方文檔**: [docs/README.md](../README.md)
2. **GitHub Issues**: [提交問題](https://github.com/TauricResearch/TradingAgents/issues)
3. **Discord 社群**: [加入討論](https://discord.com/invite/hk9PGKShPK)
4. **郵箱支援**: support@tauric.ai

### Q16: 如何報告 Bug？

**A:** Bug 報告模板：

```markdown
## Bug 描述
簡要描述遇到的問題

## 複現步驟
1. 執行的代碼
2. 使用的配置
3. 輸入的參數

## 預期行為
描述期望的結果

## 實際行為
描述實際發生的情況

## 環境資訊
- Python 版本:
- TradingAgents 版本:
- 作業系統:
- 相關依賴版本:

## 錯誤日誌
貼上完整的錯誤資訊
```

如果您的問題沒有在這裡找到答案，請通過上述渠道聯繫我們獲取幫助。
