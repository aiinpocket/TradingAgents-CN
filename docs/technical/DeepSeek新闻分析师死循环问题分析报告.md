# DeepSeek新聞分析師死循環問題分析報告

## 問題描述

DeepSeek新聞分析師在執行新聞分析時出現死循環，表現為：
- 新聞分析師被重複調用
- 每次調用都使用不同的工具（get_stock_news_unified、get_finnhub_news、get_google_news等）
- 生成的報告長度為0字符
- 無法正常退出到下一個分析師

## 根本原因分析

### 1. 工作流圖的條件判斷機制

在 `conditional_logic.py` 中，新聞分析師的條件判斷逻辑為：

```python
def should_continue_news(self, state: AgentState):
    """Determine if news analysis should continue."""
    messages = state["messages"]
    last_message = messages[-1]

    # 只有AIMessage才有tool_calls屬性
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools_news"  # 繼续調用工具
    return "Msg Clear News"  # 清理消息並進入下一個分析師
```

### 2. 新聞分析師返回的消息結構問題

新聞分析師在 `news_analyst.py` 的最後返回：

```python
return {
    "messages": [result],  # result是LLM的原始響應
    "news_report": report,
}
```

**關键問題**：
- `result` 是LLM調用的原始響應，可能包含 `tool_calls`
- 當DeepSeek模型調用工具但生成空報告時，`result` 仍然包含 `tool_calls`
- 工作流圖檢測到 `tool_calls` 存在，認為需要繼续調用工具
- 這導致新聞分析師被重複調用，形成死循環

### 3. DeepSeek模型的特殊行為

從日誌分析可以看出：
1. **第1次調用**：DeepSeek使用 `get_stock_news_unified`，生成報告長度0字符
2. **第2次調用**：DeepSeek使用 `get_finnhub_news`，生成報告長度0字符  
3. **第3次調用**：DeepSeek使用 `get_google_news`，生成報告長度0字符
4. **第4次調用**：DeepSeek使用 `get_global_news_openai`，生成報告長度0字符
5. **第5次調用**：DeepSeek使用 `get_reddit_news`，生成報告長度0字符
6. **第6次調用**：DeepSeek没有調用任何工具，觸發補救機制

DeepSeek模型似乎在每次調用時都選擇不同的工具，但都無法生成有效的報告內容。

## 修複方案

### 方案1：修改消息返回結構（推薦）

在新聞分析師完成分析後，返回一個不包含 `tool_calls` 的清潔消息：

```python
# 在 news_analyst.py 的返回部分
from langchain_core.messages import AIMessage

# 創建一個不包含tool_calls的清潔消息
clean_message = AIMessage(content=report)

return {
    "messages": [clean_message],  # 使用清潔消息
    "news_report": report,
}
```

### 方案2：增加循環檢測機制

在條件逻辑中增加循環檢測：

```python
def should_continue_news(self, state: AgentState):
    """Determine if news analysis should continue."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # 檢查是否已經多次調用新聞分析師
    news_call_count = sum(1 for msg in messages if 
                         hasattr(msg, 'content') and 
                         '[新聞分析師]' in str(msg.content))
    
    # 如果調用次數過多，强制退出
    if news_call_count > 3:
        logger.warning(f"[工作流] 新聞分析師調用次數過多({news_call_count})，强制退出")
        return "Msg Clear News"
    
    # 原有逻辑
    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
        return "tools_news"
    return "Msg Clear News"
```

### 方案3：改進DeepSeek工具調用檢測

在新聞分析師中增加更嚴格的完成檢測：

```python
# 檢查是否真正完成了分析
analysis_completed = (
    report and 
    len(report.strip()) > 100 and 
    ('分析' in report or '新聞' in report or '影響' in report)
)

if analysis_completed:
    # 返回清潔消息，確保退出循環
    clean_message = AIMessage(content=report)
    return {
        "messages": [clean_message],
        "news_report": report,
    }
```

## 推薦實施方案

**立即實施方案1**，因為它：
1. 直接解決了根本問題（消息結構）
2. 不影響其他分析師的正常工作
3. 實施簡單，風險最低
4. 符合工作流圖的設計預期

## 驗證方法

修複後，驗證以下几點：
1. DeepSeek新聞分析師只被調用一次
2. 生成的報告長度大於0
3. 工作流能正常進入下一個分析師
4. 日誌中不再出現重複的新聞分析師調用

## 总結

這個死循環問題是由於新聞分析師返回包含 `tool_calls` 的原始LLM響應，導致工作流圖誤判需要繼续調用工具。通過返回清潔的AIMessage，可以確保工作流正常流轉，避免死循環。