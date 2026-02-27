from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import MessagesState


# 投資辯論狀態
class InvestDebateState(TypedDict):
    bull_history: Annotated[str, "看漲方對話歷史"]
    bear_history: Annotated[str, "看跌方對話歷史"]
    history: Annotated[str, "完整對話歷史"]
    current_response: Annotated[str, "最新回應"]
    judge_decision: Annotated[str, "裁判最終決定"]
    count: Annotated[int, "目前對話輪數"]


# 風險辯論狀態
class RiskDebateState(TypedDict):
    risky_history: Annotated[str, "激進分析師對話歷史"]
    safe_history: Annotated[str, "保守分析師對話歷史"]
    neutral_history: Annotated[str, "中性分析師對話歷史"]
    history: Annotated[str, "完整對話歷史"]
    latest_speaker: Annotated[str, "最後發言的分析師"]
    current_risky_response: Annotated[str, "激進分析師最新回應"]
    current_safe_response: Annotated[str, "保守分析師最新回應"]
    current_neutral_response: Annotated[str, "中性分析師最新回應"]
    judge_decision: Annotated[str, "裁判決定"]
    count: Annotated[int, "目前對話輪數"]


# 主要代理狀態（繼承 LangGraph MessagesState）
class AgentState(MessagesState):
    company_of_interest: Annotated[str, "分析目標公司"]
    trade_date: Annotated[str, "分析日期"]

    sender: Annotated[str, "訊息發送者"]

    # 分析報告階段
    market_report: Annotated[str, "市場技術分析報告"]
    sentiment_report: Annotated[str, "社群情緒分析報告"]
    news_report: Annotated[str, "新聞事件分析報告"]
    fundamentals_report: Annotated[str, "基本面分析報告"]

    # 投資辯論階段
    investment_debate_state: Annotated[
        InvestDebateState, "投資辯論目前狀態"
    ]
    investment_plan: Annotated[str, "Research Manager 投資計劃"]

    trader_investment_plan: Annotated[str, "交易員投資計劃"]

    # 風險評估階段
    risk_debate_state: Annotated[
        RiskDebateState, "風險辯論目前狀態"
    ]
    final_trade_decision: Annotated[str, "風險評估最終決定"]
