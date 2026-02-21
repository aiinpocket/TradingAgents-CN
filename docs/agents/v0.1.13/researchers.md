# 

## 

 TradingAgents 

## 

### 



```python
# 
from tradingagents.utils.tool_logging import log_researcher_module

# 
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")

@log_researcher_module("researcher_type")
def researcher_node(state):
 # 
 pass
```

### 

 `AgentState` 

```python
class AgentState:
 company_of_interest: str # 
 trade_date: str # 
 fundamentals_report: str # 
 market_report: str # 
 news_report: str # 
 sentiment_report: str # 
 debate_state: str # 
 messages: List # 
 memory: Any # 
```

## 

### 1. (Bull Researcher)

****: `tradingagents/agents/researchers/bull_researcher.py`

****:
- 
- 
- 
- 

****:
```python
def create_bull_researcher(llm, memory=None):
 @log_researcher_module("bull")
 def bull_node(state):
 # 
 company_name = state["company_of_interest"]
 debate_state = state.get("debate_state", "")
 
 # 
 from tradingagents.utils.stock_utils import get_stock_market_info
 market_info = get_stock_market_info(company_name)
 
 # 
 if memory is None:
 logger.warning(f" [DEBUG] memoryNone")
 
 # 
 messages = state.get("messages", [])
 
 # 
 market_report = state.get("market_report", "")
 sentiment_report = state.get("sentiment_report", "")
 news_report = state.get("news_report", "")
 fundamentals_report = state.get("fundamentals_report", "")
```

****:
- ****: 
- ****: 
- ****: 
- ****: 

### 2. (Bear Researcher)

****: `tradingagents/agents/researchers/bear_researcher.py`

****:
- 
- 
- 
- 

****:
```python
def create_bear_researcher(llm, memory=None):
 @log_researcher_module("bear")
 def bear_node(state):
 # 
 company_name = state["company_of_interest"]
 debate_state = state.get("debate_state", "")
 
 # 
 from tradingagents.utils.stock_utils import get_stock_market_info
 market_info = get_stock_market_info(company_name)
 
 # 
 if memory is None:
 logger.warning(f" [DEBUG] memoryNone")
 
 # 
 messages = state.get("messages", [])
 
 # 
 market_report = state.get("market_report", "")
 sentiment_report = state.get("sentiment_report", "")
 news_report = state.get("news_report", "")
 fundamentals_report = state.get("fundamentals_report", "")
```

****:
- ****: 
- ****: 
- ****: 
- ****: 

## 

### 

```mermaid
graph TB
 A[] --> B[]
 A --> C[]
 
 B --> D[]
 C --> E[]
 
 D --> F[]
 E --> F
 
 F --> G[]
 G --> H[]
 
 H --> I[]
```

### 

```python
# 
DEBATE_STATES = {
 "initial": "",
 "bull_turn": "",
 "bear_turn": "",
 "rebuttal": "",
 "conclusion": ""
}

# 
def update_debate_state(current_state, participant):
 if current_state == "initial":
 return "bull_turn" if participant == "bull" else "bear_turn"
 elif current_state in ["bull_turn", "bear_turn"]:
 return "rebuttal"
 elif current_state == "rebuttal":
 return "conclusion"
 return current_state
```

### 



1. ****: 
2. ****: 
3. ****: 
4. ****: 

```python
# 
if memory is not None:
 historical_debates = memory.get_relevant_debates(company_name)
 previous_analysis = memory.get_analysis_history(company_name)
else:
 logger.warning(f" [DEBUG] memoryNone")
```

## 

### 



```python
# 
from tradingagents.utils.stock_utils import get_stock_market_info
market_info = get_stock_market_info(ticker)

# 
if market_info.get("is_us"):
 analysis_context = ""
 currency = ""
```

### 

****:
- 
- 
- 
- 
- 
- 

## 

### 

1. ****:
 - 
 - 
 - /
 - 

2. ****:
 - 
 - 
 - 
 - 

3. ****:
 - 
 - 
 - 
 - 

4. ****:
 - 
 - 
 - 
 - 

### 

1. ****:
 - 
 - 
 - 
 - 

2. ****:
 - 
 - 
 - 
 - 

3. ****:
 - 
 - 
 - 
 - 

4. ****:
 - 
 - 
 - 
 - 

## 

### 

1. ****:
 - 
 - 
 - 
 - 

2. ****:
 - 
 - 
 - 
 - 

3. ****:
 - 
 - 
 - 
 - 

### 

```python
# 
class DebateResult:
 bull_arguments: List[str] # 
 bear_arguments: List[str] # 
 key_disagreements: List[str] # 
 consensus_points: List[str] # 
 confidence_level: float # 
 recommendation_strength: str # 
```

## 

### 

```python
researcher_config = {
 "enable_memory": True, # 
 "debate_rounds": 3, # 
 "argument_depth": "deep", # 
 "risk_tolerance": "moderate", # 
 "analysis_style": "balanced" # 
}
```

### 

```python
debate_params = {
 "max_rounds": 5, # 
 "time_limit": 300, # ()
 "evidence_weight": 0.7, # 
 "logic_weight": 0.3, # 
 "consensus_threshold": 0.8 # 
}
```

## 

### 

```python
# 
import asyncio

async def parallel_research(state):
 bull_task = asyncio.create_task(bull_researcher(state))
 bear_task = asyncio.create_task(bear_researcher(state))
 
 bull_result, bear_result = await asyncio.gather(bull_task, bear_task)
 return bull_result, bear_result
```

### 

```python
# 
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_analysis(ticker, date, report_hash):
 # 
 pass
```

## 

### 

```python
# 
logger.info(f" [] : {company_name}")
logger.info(f" [] : {company_name}")
logger.debug(f" [] : {debate_state}")
logger.warning(f" [] memoryNone")
```

### 

- 
- 
- 
- 
- 

## 

### 

1. ****
```python
# tradingagents/agents/researchers/neutral_researcher.py
from tradingagents.utils.tool_logging import log_researcher_module

def create_neutral_researcher(llm, memory=None):
 @log_researcher_module("neutral")
 def neutral_node(state):
 # 
 pass
 return neutral_node
```

2. ****
```python
# trading_graph.py
researchers = {
 "bull": create_bull_researcher(llm, memory),
 "bear": create_bear_researcher(llm, memory),
 "neutral": create_neutral_researcher(llm, memory)
}
```

### 

1. ****
```python
class DebateStrategy:
 def generate_arguments(self, reports, market_info):
 pass
 
 def evaluate_counterarguments(self, opponent_args):
 pass
 
 def synthesize_conclusion(self, all_arguments):
 pass
```

2. ****
```python
strategy_registry = {
 "aggressive_bull": AggressiveBullStrategy(),
 "conservative_bear": ConservativeBearStrategy(),
 "data_driven": DataDrivenStrategy()
}
```

## 

### 1. 
- 
- 
- 
- 

### 2. 
- 
- 
- 
- 

### 3. 
- 
- 
- 
- 

### 4. 
- 
- 
- 
- 

## 

### 

1. ****
 - 
 - 
 - 
 - 

2. ****
 - 
 - 
 - 
 - 

3. ****
 - 
 - 
 - 
 - 

### 

1. ****
```python
logger.debug(f": {round_number}")
logger.debug(f": {current_speaker}")
logger.debug(f": {len(arguments)}")
```

2. ****
```python
logger.debug(f": {validate_state(state)}")
logger.debug(f": {check_reports_availability(state)}")
```

3. ****
```python
import time
start_time = time.time()
# 
end_time = time.time()
logger.debug(f": {end_time - start_time:.2f}")
```

TradingAgents