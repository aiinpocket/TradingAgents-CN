# 

## 



## 

### 

```bash
# 1. 
git clone -b feature/
cd TradingAgents-CN

# 2. 
python -m venv env
env\Scripts\activate # Windows
# source env/bin/activate # Linux/macOS

# 3. 
pip install -r requirements.txt

# 4. 
cp .env.example .env
```

### 

1. [OpenAI Platform](https://platform.openai.com/) [Google AI Studio](https://aistudio.google.com/)
2. 
3. → API Keys
4. API Key
5. API Key.env
 ```bash
 OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
 ```

### 

```bash
# 
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('
"

# 
python tests/test_fundamentals_analysis.py

# 
python tests/test_
```

## 

### 1. 

#### 1.1 API
```bash
# 
python -c "
from tradingagents.llm_adapters.
llm = Chat
response = llm.invoke('')
print(':', response.content[:100] + '...')
"
```

****
- [ ] API
- [ ] 
- [ ] 5-15
- [ ] 

#### 1.2 Token
```bash
# Token
python examples/demo_
```

****
- [ ] Token
- [ ] ¥0.001/1K¥0.002/1K
- [ ] 
- [ ] 

### 2. 

#### 2.1 
```bash
# 
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config.update({
 'llm_provider': '
 'llm_model': '
 'quick_think_llm': '
 'deep_think_llm': '
})

ta = TradingAgentsGraph(
 selected_analysts=['fundamentals'],
 config=config
)

# Apple
result = ta.run_analysis('AAPL', '2025-01-08')
print(':', result)
"
```

****
- `AAPL` - Apple Inc.
- `MSFT` - Microsoft Corp.
- `TSLA` - Tesla Inc.
- `GOOGL` - Alphabet Inc.
- `AMZN` - Amazon.com Inc.

****
- [ ] PEPBROE
- [ ] //
- [ ] 
- [ ] 0-10
- [ ] 

#### 2.2 
```bash
# 
python -c "
# 
result = ta.run_analysis('AAPL', '2025-01-08')
print(':', result)
"
```

****
- `AAPL` - 
- `MSFT` - 
- `GOOGL` - 
- `TSLA` - 

### 3. Web

```bash
# Web
streamlit run web/app.py
```

 http://localhost:8501 

#### 3.1 
- [ ] 
- [ ] API
- [ ] 

#### 3.2 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

#### 3.3 Token
- [ ] 
- [ ] 
- [ ] 

### 4. CLI

```bash
# CLI
python -m cli.main
```

****
1. "
2. "
3. 
4. 

****
- [ ] 
- [ ] 
- [ ] 
- [ ] 

## 

### 1API
```
Authentication failed
```
****
1. APIsk-
2. API
3. 

### 2Token¥0.0000
****
1. APIusage
2. Token

****
```bash
# 
export TRADINGAGENTS_LOG_LEVEL=DEBUG
python tests/test_
```

### 3
****
1. 
2. 

****
```bash
# 
python -c "
from tradingagents.dataflows.yfin_utils import get_stock_data
data = get_stock_data('AAPL', '2025-01-01', '2025-01-08')
print(':', data[:200] if data else '')
"
```

## 

### 
```markdown
## 

****
- Windows 11 / macOS / Ubuntu
- Python3.10.x
- 2025-01-08

****
- [x] 
- [x] Token
- [x] 
- [x] Web
- [x] CLI

****
- //
- //
- //
- //

****

```

### 
```markdown
## 

****


****
1. 
2. 
3. 

****
- 
- Python
- 
- 

****

```

## 

### 
1. **
2. **Token**
3. ****
4. ****

### 
1. **Web**
2. **CLI**
3. ****
4. ****

### 
1. ****
2. ****
3. ****

## 

- **GitHub Issues**https://github.com/hsliuping/TradingAgents-CN/issues
- ****GitHub Discussions
- ****Issue@hsliuping

---

**AI** 
