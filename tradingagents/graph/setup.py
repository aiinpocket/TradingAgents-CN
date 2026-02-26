# TradingAgents/graph/setup.py

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START

from tradingagents.agents import (
    create_fundamentals_analyst,
    create_market_analyst,
    create_news_analyst,
    create_social_media_analyst,
    create_bear_researcher,
    create_bull_researcher,
    create_parallel_invest_debate,
    create_research_manager,
    create_risk_manager,
    create_risky_debator,
    create_safe_debator,
    create_neutral_debator,
    create_parallel_risk_debate,
    create_trader,
    create_msg_delete,
    Toolkit,
    AgentState,
)

from .conditional_logic import ConditionalLogic

# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    def __init__(
        self,
        quick_thinking_llm: ChatOpenAI,
        deep_thinking_llm: ChatOpenAI,
        toolkit: Toolkit,
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
        config: Dict[str, Any] = None,
        react_llm = None,
    ):
        """初始化圖設定元件。"""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.toolkit = toolkit
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.risk_manager_memory = risk_manager_memory
        self.conditional_logic = conditional_logic
        self.config = config or {}
        self.react_llm = react_llm

    def setup_graph(
        self, selected_analysts=["market", "social", "news", "fundamentals"]
    ):
        """Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): List of analyst types to include. Options are:
                - "market": Market analyst
                - "social": Social media analyst
                - "news": News analyst
                - "fundamentals": Fundamentals analyst
        """
        if len(selected_analysts) == 0:
            raise ValueError("Trading Agents Graph Setup Error: no analysts selected!")

        # 建立分析師節點（直接工具呼叫模式）
        analyst_nodes = {}
        delete_nodes = {}

        if "market" in selected_analysts:
            analyst_nodes["market"] = create_market_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["market"] = create_msg_delete()

        if "social" in selected_analysts:
            analyst_nodes["social"] = create_social_media_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["social"] = create_msg_delete()

        if "news" in selected_analysts:
            analyst_nodes["news"] = create_news_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["news"] = create_msg_delete()

        if "fundamentals" in selected_analysts:
            analyst_nodes["fundamentals"] = create_fundamentals_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["fundamentals"] = create_msg_delete()

        # 建立研究員和管理員節點
        bull_researcher_node = create_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        bear_researcher_node = create_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        research_manager_node = create_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        trader_node = create_trader(self.quick_thinking_llm, self.trader_memory)

        # 判斷是否使用並行多空辯論（僅一輪時可安全並行）
        max_debate_rounds = self.conditional_logic.max_debate_rounds
        use_parallel_debate = (max_debate_rounds == 1)
        if use_parallel_debate:
            parallel_debate_node = create_parallel_invest_debate(
                bull_researcher_node, bear_researcher_node
            )
            logger.info("多空辯論模式: 並行（看漲/看跌同時執行）")
        else:
            logger.info(f"多空辯論模式: 串行（{max_debate_rounds} 輪辯論）")

        # 建立風險分析節點
        risky_analyst = create_risky_debator(self.quick_thinking_llm)
        neutral_analyst = create_neutral_debator(self.quick_thinking_llm)
        safe_analyst = create_safe_debator(self.quick_thinking_llm)
        risk_manager_node = create_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )

        # 判斷是否使用並行風險辯論（僅一輪時可安全並行）
        max_risk_rounds = self.conditional_logic.max_risk_discuss_rounds
        use_parallel_risk = (max_risk_rounds == 1)
        if use_parallel_risk:
            parallel_risk_node = create_parallel_risk_debate(
                risky_analyst, safe_analyst, neutral_analyst
            )
            logger.info("風險辯論模式: 並行（3 位分析師同時執行）")
        else:
            logger.info(f"風險辯論模式: 串行（{max_risk_rounds} 輪辯論）")

        # 建立工作流程
        workflow = StateGraph(AgentState)

        # 加入分析師節點
        for analyst_type, node in analyst_nodes.items():
            workflow.add_node(f"{analyst_type.capitalize()} Analyst", node)
            workflow.add_node(
                f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type]
            )

        # 加入辯論節點
        if use_parallel_debate:
            # 並行模式：單一節點包裝兩位研究員
            workflow.add_node("Invest Debate", parallel_debate_node)
        else:
            # 串行模式：兩個獨立節點依序執行
            workflow.add_node("Bull Researcher", bull_researcher_node)
            workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)

        if use_parallel_risk:
            # 並行模式：單一節點包裝三位分析師
            workflow.add_node("Risk Debate", parallel_risk_node)
        else:
            # 串行模式：三個獨立節點依序執行
            workflow.add_node("Risky Analyst", risky_analyst)
            workflow.add_node("Neutral Analyst", neutral_analyst)
            workflow.add_node("Safe Analyst", safe_analyst)
        workflow.add_node("Risk Judge", risk_manager_node)

        # 定義邊：fan-out/fan-in 並行分析師節點
        # 分析師已改為直接工具呼叫，無需條件分支和工具節點迴圈
        fan_in_target = "Invest Debate" if use_parallel_debate else "Bull Researcher"
        for analyst_type in selected_analysts:
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            # START -> 所有分析師（並行 fan-out）
            workflow.add_edge(START, current_analyst)

            # 分析師 -> 訊息清理（直接連接，無條件分支）
            workflow.add_edge(current_analyst, current_clear)

            # 所有分析師完成後匯合到辯論節點（fan-in）
            workflow.add_edge(current_clear, fan_in_target)

        if use_parallel_debate:
            # 並行模式：Invest Debate（並行看漲/看跌）-> Research Manager
            workflow.add_edge("Invest Debate", "Research Manager")
        else:
            # 串行模式：Bull <-> Bear 多輪辯論 -> Research Manager
            workflow.add_conditional_edges(
                "Bull Researcher",
                self.conditional_logic.should_continue_debate,
                {
                    "Bear Researcher": "Bear Researcher",
                    "Research Manager": "Research Manager",
                },
            )
            workflow.add_conditional_edges(
                "Bear Researcher",
                self.conditional_logic.should_continue_debate,
                {
                    "Bull Researcher": "Bull Researcher",
                    "Research Manager": "Research Manager",
                },
            )
        workflow.add_edge("Research Manager", "Trader")

        if use_parallel_risk:
            # 並行模式：Trader -> Risk Debate（並行三位分析師）-> Risk Judge
            workflow.add_edge("Trader", "Risk Debate")
            workflow.add_edge("Risk Debate", "Risk Judge")
        else:
            # 串行模式：Trader -> Risky -> Safe -> Neutral -> ... -> Risk Judge
            workflow.add_edge("Trader", "Risky Analyst")
            workflow.add_conditional_edges(
                "Risky Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Safe Analyst": "Safe Analyst",
                    "Risk Judge": "Risk Judge",
                },
            )
            workflow.add_conditional_edges(
                "Safe Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Neutral Analyst": "Neutral Analyst",
                    "Risk Judge": "Risk Judge",
                },
            )
            workflow.add_conditional_edges(
                "Neutral Analyst",
                self.conditional_logic.should_continue_risk_analysis,
                {
                    "Risky Analyst": "Risky Analyst",
                    "Risk Judge": "Risk Judge",
                },
            )

        workflow.add_edge("Risk Judge", END)

        # Compile and return
        return workflow.compile()
