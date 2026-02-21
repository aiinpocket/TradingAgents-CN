# TradingAgents 

## 

TradingAgents 

## 

### 

TradingAgents 5

```mermaid
graph TD
 subgraph " (Management Layer)"
 RESMGR[]
 RISKMGR[]
 end

 subgraph " (Analysis Layer)"
 FA[]
 MA[]
 NA[]
 SA[]
 end

 subgraph " (Research Layer)"
 BR[]
 BEAR[]
 end

 subgraph " (Execution Layer)"
 TRADER[]
 end

 subgraph " (Risk Layer)"
 CONSERVATIVE[]
 NEUTRAL[]
 AGGRESSIVE[]
 end

 %% 
 --> 
 --> 
 --> 
 --> 
 --> 

 %% 
 classDef analysisNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
 classDef researchNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
 classDef executionNode fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
 classDef riskNode fill:#fff3e0,stroke:#e65100,stroke-width:2px
 classDef managementNode fill:#fce4ec,stroke:#880e4f,stroke-width:2px

 class FA,MA,NA,SA analysisNode
 class BR,BEAR researchNode
 class TRADER executionNode
 class CONSERVATIVE,NEUTRAL,AGGRESSIVE riskNode
 class RESMGR,RISKMGR managementNode
```

### 

- ****: 
- ****: 
- ****: 
- ****: 
- ****: 

## 

### AgentState 

 `tradingagents/agents/utils/agent_states.py` `AgentState` 

```python
from typing import Annotated
from langgraph.graph import MessagesState

class AgentState(MessagesState):
 """ - LangGraph MessagesState"""

 # 
 company_of_interest: Annotated[str, ""]
 trade_date: Annotated[str, ""]
 sender: Annotated[str, ""]

 # 
 market_report: Annotated[str, ""]
 sentiment_report: Annotated[str, ""]
 news_report: Annotated[str, ""]
 fundamentals_report: Annotated[str, ""]

 # 
 investment_debate_state: Annotated[InvestDebateState, ""]
 investment_plan: Annotated[str, ""]
 trader_investment_plan: Annotated[str, ""]

 # 
 risk_debate_state: Annotated[RiskDebateState, ""]
 final_trade_decision: Annotated[str, ""]
```

## 

### (Analysis Layer)

#### 1. 

****: `tradingagents/agents/analysts/fundamentals_analyst.py`

```python
from tradingagents.utils.tool_logging import log_analyst_module
from tradingagents.utils.logging_init import get_logger

def create_fundamentals_analyst(llm, toolkit):
 @log_analyst_module("fundamentals")
 def fundamentals_analyst_node(state):
 """"""
 logger = get_logger("default")

 # 
 current_date = state["trade_date"]
 ticker = state["company_of_interest"]

 # 
 if toolkit.config["online_tools"]:
 tools = [toolkit.get_stock_fundamentals_unified]
 else:
 tools = [toolkit.get_fundamentals_openai]

 # 
 # ...

 return state

 return fundamentals_analyst_node
```

### (Research Layer)

#### 1. 

****: `tradingagents/agents/researchers/bull_researcher.py`

```python
def create_bull_researcher(llm):
 def bull_researcher_node(state):
 """"""
 # 
 # ...
 return state

 return bull_researcher_node
```

### (Execution Layer)

****: `tradingagents/agents/trader/trader.py`

```python
def create_trader(llm, memory):
 def trader_node(state, name):
 """"""
 # 
 company_name = state["company_of_interest"]
 investment_plan = state["investment_plan"]
 market_research_report = state["market_report"]
 sentiment_report = state["sentiment_report"]
 news_report = state["news_report"]
 fundamentals_report = state["fundamentals_report"]

 # 
 if memory is not None:
 past_memories = memory.get_memories(curr_situation, n_matches=2)

 # 
 # ...

 return state

 return trader_node
```

## 

### 

1. ****: `AgentState` 
2. ****: 
3. ****: 
4. ****: 
5. ****: 
6. ****: 

### 

 `MessagesState` 

```python
# 
state["messages"].append({
 "role": "assistant",
 "content": "",
 "sender": "fundamentals_analyst"
})

# 
history = state["messages"]
```

## 

### 



```python
from tradingagents.utils.logging_init import get_logger

logger = get_logger("default")
logger.info(f" [] : {ticker}")
logger.debug(f" [DEBUG] : {market_info}")
```

## 

### 

```python
# 1. 
# tradingagents/agents/analysts/custom_analyst.py
def create_custom_analyst(llm, toolkit):
 @log_analyst_module("custom")
 def custom_analyst_node(state):
 # 
 return state

 return custom_analyst_node

# 2. 
# AgentState 
custom_report: Annotated[str, ""]

# 3. 
# 
workflow.add_node("custom_analyst", create_custom_analyst(llm, toolkit))
```

TradingAgents 
