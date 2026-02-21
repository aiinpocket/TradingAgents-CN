# 基本使用示例

## 概述

本文檔提供了 TradingAgents 框架的基本使用示例，幫助您快速上手並了解各種功能的使用方法。

## 示例 1: 基本股票分析

### 最簡單的使用方式
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 使用默認配置
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())

# 分析蘋果公司股票
state, decision = ta.propagate("AAPL", "2024-01-15")

print(f"推薦動作: {decision['action']}")
print(f"置信度: {decision['confidence']:.2f}")
print(f"推理: {decision['reasoning']}")
```

### 輸出示例
```
推薦動作: buy
置信度: 0.75
推理: 基於強勁的基本面數據和積極的技術指標，建議買入AAPL股票...
```

## 示例 2: 自定義配置分析

### 配置優化的分析
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

def analyze_with_custom_config(symbol, date):
    """使用自定義配置進行分析"""
    
    # 創建自定義配置
    config = DEFAULT_CONFIG.copy()
    config.update({
        "deep_think_llm": "gpt-4o-mini",      # 使用經濟模型
        "quick_think_llm": "gpt-4o-mini",     # 使用經濟模型
        "max_debate_rounds": 2,               # 增加辩論輪次
        "max_risk_discuss_rounds": 1,         # 風險討論輪次
        "online_tools": True,                 # 使用實時數據
    })
    
    # 選擇特定的分析師
    selected_analysts = ["market", "fundamentals", "news"]
    
    # 初始化分析器
    ta = TradingAgentsGraph(
        selected_analysts=selected_analysts,
        debug=True,
        config=config
    )
    
    print(f"開始分析 {symbol} ({date})...")
    
    # 執行分析
    state, decision = ta.propagate(symbol, date)
    
    return state, decision

# 使用示例
state, decision = analyze_with_custom_config("TSLA", "2024-01-15")

print("\n=== 分析結果 ===")
print(f"股票: TSLA")
print(f"動作: {decision['action']}")
print(f"數量: {decision.get('quantity', 0)}")
print(f"置信度: {decision['confidence']:.1%}")
print(f"風險評分: {decision['risk_score']:.1%}")
```

## 示例 3: 批量股票分析

### 分析多只股票
```python
import pandas as pd
from datetime import datetime, timedelta

def batch_analysis(symbols, date):
    """批量分析多只股票"""
    
    # 配置
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = 1  # 減少辩論輪次以提高速度
    config["online_tools"] = True
    
    ta = TradingAgentsGraph(debug=False, config=config)
    
    results = []
    
    for symbol in symbols:
        try:
            print(f"正在分析 {symbol}...")
            
            # 執行分析
            state, decision = ta.propagate(symbol, date)
            
            # 收集結果
            result = {
                "symbol": symbol,
                "action": decision.get("action", "hold"),
                "confidence": decision.get("confidence", 0.5),
                "risk_score": decision.get("risk_score", 0.5),
                "reasoning": decision.get("reasoning", "")[:100] + "..."  # 截取前100字符
            }
            
            results.append(result)
            print(f"✅ {symbol}: {result['action']} (置信度: {result['confidence']:.1%})")
            
        except Exception as e:
            print(f"❌ {symbol}: 分析失敗 - {e}")
            results.append({
                "symbol": symbol,
                "action": "error",
                "confidence": 0.0,
                "risk_score": 1.0,
                "reasoning": f"分析失敗: {e}"
            })
    
    return pd.DataFrame(results)

# 使用示例
tech_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
analysis_date = "2024-01-15"

results_df = batch_analysis(tech_stocks, analysis_date)

print("\n=== 批量分析結果 ===")
print(results_df[["symbol", "action", "confidence", "risk_score"]])

# 筛選買入建議
buy_recommendations = results_df[results_df["action"] == "buy"]
print(f"\n買入建議 ({len(buy_recommendations)} 只):")
for _, row in buy_recommendations.iterrows():
    print(f"  {row['symbol']}: 置信度 {row['confidence']:.1%}")
```

## 示例 4: 不同LLM提供商對比

### 對比不同LLM的分析結果
```python
def compare_llm_providers(symbol, date):
    """對比不同LLM提供商的分析結果"""
    
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
        # 註意: 需要相應的API密鑰
    }
    
    results = {}
    
    for provider_name, provider_config in providers_config.items():
        try:
            print(f"使用 {provider_name} 分析 {symbol}...")
            
            # 創建配置
            config = DEFAULT_CONFIG.copy()
            config.update(provider_config)
            config["max_debate_rounds"] = 1
            
            # 初始化分析器
            ta = TradingAgentsGraph(debug=False, config=config)
            
            # 執行分析
            state, decision = ta.propagate(symbol, date)
            
            results[provider_name] = {
                "action": decision.get("action", "hold"),
                "confidence": decision.get("confidence", 0.5),
                "risk_score": decision.get("risk_score", 0.5),
            }
            
            print(f"✅ {provider_name}: {results[provider_name]['action']}")
            
        except Exception as e:
            print(f"❌ {provider_name}: 失敗 - {e}")
            results[provider_name] = {"error": str(e)}
    
    return results

# 使用示例
comparison_results = compare_llm_providers("AAPL", "2024-01-15")

print("\n=== LLM提供商對比結果 ===")
for provider, result in comparison_results.items():
    if "error" not in result:
        print(f"{provider}:")
        print(f"  動作: {result['action']}")
        print(f"  置信度: {result['confidence']:.1%}")
        print(f"  風險評分: {result['risk_score']:.1%}")
    else:
        print(f"{provider}: 錯誤 - {result['error']}")
```

## 示例 5: 歷史回測分析

### 簡單的歷史回測
```python
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def historical_backtest(symbol, start_date, end_date, interval_days=7):
    """簡單的歷史回測"""
    
    # 配置
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = 1
    config["online_tools"] = True
    
    ta = TradingAgentsGraph(debug=False, config=config)
    
    # 生成日期列表
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = []
    
    while current_date <= end_date_obj:
        date_str = current_date.strftime("%Y-%m-%d")
        
        try:
            print(f"分析 {symbol} 在 {date_str}...")
            
            # 執行分析
            state, decision = ta.propagate(symbol, date_str)
            
            result = {
                "date": date_str,
                "action": decision.get("action", "hold"),
                "confidence": decision.get("confidence", 0.5),
                "risk_score": decision.get("risk_score", 0.5),
            }
            
            results.append(result)
            print(f"  {result['action']} (置信度: {result['confidence']:.1%})")
            
        except Exception as e:
            print(f"  錯誤: {e}")
        
        # 移動到下一個日期
        current_date += timedelta(days=interval_days)
    
    return pd.DataFrame(results)

# 使用示例
backtest_results = historical_backtest(
    symbol="AAPL",
    start_date="2024-01-01",
    end_date="2024-01-31",
    interval_days=7
)

print("\n=== 歷史回測結果 ===")
print(backtest_results)

# 統計分析
action_counts = backtest_results["action"].value_counts()
print(f"\n動作分布:")
for action, count in action_counts.items():
    print(f"  {action}: {count} 次")

avg_confidence = backtest_results["confidence"].mean()
print(f"\n平均置信度: {avg_confidence:.1%}")
```

## 示例 6: 實時監控

### 實時股票監控
```python
import time
from datetime import datetime

def real_time_monitor(symbols, check_interval=300):
    """實時監控股票"""
    
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = 1
    config["online_tools"] = True
    
    ta = TradingAgentsGraph(debug=False, config=config)
    
    print(f"開始監控 {len(symbols)} 只股票...")
    print(f"檢查間隔: {check_interval} 秒")
    print("按 Ctrl+C 停止監控\n")
    
    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            print(f"=== {current_time} ===")
            
            for symbol in symbols:
                try:
                    # 執行分析
                    state, decision = ta.propagate(symbol, current_date)
                    
                    action = decision.get("action", "hold")
                    confidence = decision.get("confidence", 0.5)
                    
                    # 輸出結果
                    status_emoji = "🟢" if action == "buy" else "🔴" if action == "sell" else "🟡"
                    print(f"{status_emoji} {symbol}: {action.upper()} (置信度: {confidence:.1%})")
                    
                    # 高置信度買入/賣出提醒
                    if confidence > 0.8 and action in ["buy", "sell"]:
                        print(f"  ⚠️  高置信度{action}信號!")
                
                except Exception as e:
                    print(f"❌ {symbol}: 分析失敗 - {e}")
            
            print(f"下次檢查: {check_interval} 秒後\n")
            time.sleep(check_interval)
    
    except KeyboardInterrupt:
        print("\n監控已停止")

# 使用示例（註釋掉以避免長時間運行）
# watch_list = ["AAPL", "GOOGL", "TSLA"]
# real_time_monitor(watch_list, check_interval=300)  # 每5分鐘檢查一次
```

## 示例 7: 錯誤處理和重試

### 健壯的分析函數
```python
import time
from typing import Optional, Tuple

def robust_analysis(symbol: str, date: str, max_retries: int = 3) -> Optional[Tuple[dict, dict]]:
    """帶錯誤處理和重試的分析函數"""
    
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = 1
    
    for attempt in range(max_retries):
        try:
            print(f"分析 {symbol} (嘗試 {attempt + 1}/{max_retries})...")
            
            ta = TradingAgentsGraph(debug=False, config=config)
            state, decision = ta.propagate(symbol, date)
            
            # 驗證結果
            if not decision or "action" not in decision:
                raise ValueError("分析結果無效")
            
            print(f"✅ 分析成功: {decision['action']}")
            return state, decision
            
        except Exception as e:
            print(f"❌ 嘗試 {attempt + 1} 失敗: {e}")
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指數退避
                print(f"等待 {wait_time} 秒後重試...")
                time.sleep(wait_time)
            else:
                print(f"所有嘗試都失敗了")
                return None

# 使用示例
result = robust_analysis("AAPL", "2024-01-15", max_retries=3)

if result:
    state, decision = result
    print(f"最終結果: {decision['action']}")
else:
    print("分析失敗")
```

## 示例 8: 結果保存和加載

### 保存分析結果
```python
import json
import pickle
from datetime import datetime

def save_analysis_result(symbol, date, state, decision, format="json"):
    """保存分析結果"""
    
    # 創建結果目錄
    import os
    results_dir = "analysis_results"
    os.makedirs(results_dir, exist_ok=True)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_{date}_{timestamp}"
    
    # 準備數據
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
    
    print(f"結果已保存到: {filepath}")
    return filepath

# 使用示例
ta = TradingAgentsGraph(debug=False, config=DEFAULT_CONFIG.copy())
state, decision = ta.propagate("AAPL", "2024-01-15")

# 保存結果
save_analysis_result("AAPL", "2024-01-15", state, decision, format="json")
```

這些基本示例展示了 TradingAgents 框架的主要功能和使用模式。您可以根據自己的需求修改和擴展這些示例。
