# 

## 

 TradingAgents 

## 1: 

### 
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# 
state, decision = ta.propagate("AAPL", "2024-01-15")

print(f": {decision['action']}")
print(f": {decision['confidence']:.2f}")
print(f": {decision['reasoning']}")
```

### 
```
: buy
: 0.75
: AAPL...
```

## 2: 

### 
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def analyze_with_custom_config(symbol, date):
 """"""
 
 # 
 config = DEFAULT_CONFIG.copy()
 config.update({
 "deep_think_llm": "gpt-4o-mini", # 
 "quick_think_llm": "gpt-4o-mini", # 
 "max_debate_rounds": 2, # 
 "max_risk_discuss_rounds": 1, # 
 "online_tools": True, # 
 })
 
 # 
 selected_analysts = ["market", "fundamentals", "news"]
 
 # 
 ta = TradingAgentsGraph(
 selected_analysts=selected_analysts,
 debug=True,
 config=config
 )
 
 print(f" {symbol} ({date})...")
 
 # 
 state, decision = ta.propagate(symbol, date)
 
 return state, decision

# 
state, decision = analyze_with_custom_config("TSLA", "2024-01-15")

print("\n=== ===")
print(f": TSLA")
print(f": {decision['action']}")
print(f": {decision.get('quantity', 0)}")
print(f": {decision['confidence']:.1%}")
print(f": {decision['risk_score']:.1%}")
```

## 3: 

### 
```python
import pandas as pd
from datetime import datetime, timedelta

def batch_analysis(symbols, date):
 """"""
 
 # 
 config = DEFAULT_CONFIG.copy()
 config["max_debate_rounds"] = 1 # 
 config["online_tools"] = True
 
 ta = TradingAgentsGraph(debug=False, config=config)
 
 results = []
 
 for symbol in symbols:
 try:
 print(f" {symbol}...")
 
 # 
 state, decision = ta.propagate(symbol, date)
 
 # 
 result = {
 "symbol": symbol,
 "action": decision.get("action", "hold"),
 "confidence": decision.get("confidence", 0.5),
 "risk_score": decision.get("risk_score", 0.5),
 "reasoning": decision.get("reasoning", "")[:100] + "..." # 100
 }
 
 results.append(result)
 print(f" {symbol}: {result['action']} (: {result['confidence']:.1%})")
 
 except Exception as e:
 print(f" {symbol}: - {e}")
 results.append({
 "symbol": symbol,
 "action": "error",
 "confidence": 0.0,
 "risk_score": 1.0,
 "reasoning": f": {e}"
 })
 
 return pd.DataFrame(results)

# 
tech_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
analysis_date = "2024-01-15"

results_df = batch_analysis(tech_stocks, analysis_date)

print("\n=== ===")
print(results_df[["symbol", "action", "confidence", "risk_score"]])

# 
buy_recommendations = results_df[results_df["action"] == "buy"]
print(f"\n ({len(buy_recommendations)} ):")
for _, row in buy_recommendations.iterrows():
 print(f" {row['symbol']}: {row['confidence']:.1%}")
```

## 4: LLM

### LLM
```python
def compare_llm_providers(symbol, date):
 """LLM"""
 
 providers_config = {
 "OpenAI": {
 "llm_provider": "openai",
 "deep_think_llm": "gpt-4o-mini",
 "quick_think_llm": "gpt-4o-mini",
 },
 "Google": {
 "llm_provider": "google",
 "deep_think_llm": "gemini-pro",
 "quick_think_llm": "gemini-pro",
 },
 # : API
 }
 
 results = {}
 
 for provider_name, provider_config in providers_config.items():
 try:
 print(f" {provider_name} {symbol}...")
 
 # 
 config = DEFAULT_CONFIG.copy()
 config.update(provider_config)
 config["max_debate_rounds"] = 1
 
 # 
 ta = TradingAgentsGraph(debug=False, config=config)
 
 # 
 state, decision = ta.propagate(symbol, date)
 
 results[provider_name] = {
 "action": decision.get("action", "hold"),
 "confidence": decision.get("confidence", 0.5),
 "risk_score": decision.get("risk_score", 0.5),
 }
 
 print(f" {provider_name}: {results[provider_name]['action']}")
 
 except Exception as e:
 print(f" {provider_name}: - {e}")
 results[provider_name] = {"error": str(e)}
 
 return results

# 
comparison_results = compare_llm_providers("AAPL", "2024-01-15")

print("\n=== LLM ===")
for provider, result in comparison_results.items():
 if "error" not in result:
 print(f"{provider}:")
 print(f" : {result['action']}")
 print(f" : {result['confidence']:.1%}")
 print(f" : {result['risk_score']:.1%}")
 else:
 print(f"{provider}: - {result['error']}")
```

## 5: 

### 
```python
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def historical_backtest(symbol, start_date, end_date, interval_days=7):
 """"""
 
 # 
 config = DEFAULT_CONFIG.copy()
 config["max_debate_rounds"] = 1
 config["online_tools"] = True
 
 ta = TradingAgentsGraph(debug=False, config=config)
 
 # 
 current_date = datetime.strptime(start_date, "%Y-%m-%d")
 end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
 
 results = []
 
 while current_date <= end_date_obj:
 date_str = current_date.strftime("%Y-%m-%d")
 
 try:
 print(f" {symbol} {date_str}...")
 
 # 
 state, decision = ta.propagate(symbol, date_str)
 
 result = {
 "date": date_str,
 "action": decision.get("action", "hold"),
 "confidence": decision.get("confidence", 0.5),
 "risk_score": decision.get("risk_score", 0.5),
 }
 
 results.append(result)
 print(f" {result['action']} (: {result['confidence']:.1%})")
 
 except Exception as e:
 print(f" : {e}")
 
 # 
 current_date += timedelta(days=interval_days)
 
 return pd.DataFrame(results)

# 
backtest_results = historical_backtest(
 symbol="AAPL",
 start_date="2024-01-01",
 end_date="2024-01-31",
 interval_days=7
)

print("\n=== ===")
print(backtest_results)

# 
action_counts = backtest_results["action"].value_counts()
print(f"\n:")
for action, count in action_counts.items():
 print(f" {action}: {count} ")

avg_confidence = backtest_results["confidence"].mean()
print(f"\n: {avg_confidence:.1%}")
```

## 6: 

### 
```python
import time
from datetime import datetime

def real_time_monitor(symbols, check_interval=300):
 """"""
 
 config = DEFAULT_CONFIG.copy()
 config["max_debate_rounds"] = 1
 config["online_tools"] = True
 
 ta = TradingAgentsGraph(debug=False, config=config)
 
 print(f" {len(symbols)} ...")
 print(f": {check_interval} ")
 print(" Ctrl+C \n")
 
 try:
 while True:
 current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 current_date = datetime.now().strftime("%Y-%m-%d")
 
 print(f"=== {current_time} ===")
 
 for symbol in symbols:
 try:
 # 
 state, decision = ta.propagate(symbol, current_date)
 
 action = decision.get("action", "hold")
 confidence = decision.get("confidence", 0.5)
 
 # 
 status_emoji = "" if action == "buy" else "" if action == "sell" else ""
 print(f"{status_emoji} {symbol}: {action.upper()} (: {confidence:.1%})")
 
 # /
 if confidence > 0.8 and action in ["buy", "sell"]:
 print(f" {action}!")
 
 except Exception as e:
 print(f" {symbol}: - {e}")
 
 print(f": {check_interval} \n")
 time.sleep(check_interval)
 
 except KeyboardInterrupt:
 print("\n")

# 
# watch_list = ["AAPL", "GOOGL", "TSLA"]
# real_time_monitor(watch_list, check_interval=300) # 5
```

## 7: 

### 
```python
import time
from typing import Optional, Tuple

def robust_analysis(symbol: str, date: str, max_retries: int = 3) -> Optional[Tuple[dict, dict]]:
 """"""
 
 config = DEFAULT_CONFIG.copy()
 config["max_debate_rounds"] = 1
 
 for attempt in range(max_retries):
 try:
 print(f" {symbol} ( {attempt + 1}/{max_retries})...")
 
 ta = TradingAgentsGraph(debug=False, config=config)
 state, decision = ta.propagate(symbol, date)
 
 # 
 if not decision or "action" not in decision:
 raise ValueError("")
 
 print(f" : {decision['action']}")
 return state, decision
 
 except Exception as e:
 print(f" {attempt + 1} : {e}")
 
 if attempt < max_retries - 1:
 wait_time = 2 ** attempt # 
 print(f" {wait_time} ...")
 time.sleep(wait_time)
 else:
 print(f"")
 return None

# 
result = robust_analysis("AAPL", "2024-01-15", max_retries=3)

if result:
 state, decision = result
 print(f": {decision['action']}")
else:
 print("")
```

## 8: 

### 
```python
import json
import pickle
from datetime import datetime

def save_analysis_result(symbol, date, state, decision, format="json"):
 """"""
 
 # 
 import os
 results_dir = "analysis_results"
 os.makedirs(results_dir, exist_ok=True)
 
 # 
 timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
 filename = f"{symbol}_{date}_{timestamp}"
 
 # 
 result_data = {
 "symbol": symbol,
 "date": date,
 "timestamp": timestamp,
 "decision": decision,
 "state_summary": {
 "analyst_reports": getattr(state, "analyst_reports", {}),
 "research_reports": getattr(state, "research_reports", {}),
 "trader_decision": getattr(state, "trader_decision", {}),
 "risk_assessment": getattr(state, "risk_assessment", {}),
 }
 }
 
 if format == "json":
 filepath = os.path.join(results_dir, f"{filename}.json")
 with open(filepath, "w", encoding="utf-8") as f:
 json.dump(result_data, f, indent=2, ensure_ascii=False)
 
 elif format == "pickle":
 filepath = os.path.join(results_dir, f"{filename}.pkl")
 with open(filepath, "wb") as f:
 pickle.dump(result_data, f)
 
 print(f": {filepath}")
 return filepath

# 
ta = TradingAgentsGraph(debug=False, config=DEFAULT_CONFIG.copy())
state, decision = ta.propagate("AAPL", "2024-01-15")

# 
save_analysis_result("AAPL", "2024-01-15", state, decision, format="json")
```

 TradingAgents 
