# TradingAgents/graph/trading_graph.py

import os
from pathlib import Path
import json
from typing import Dict, Any

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from langgraph.prebuilt import ToolNode

from tradingagents.agents.utils.agent_utils import Toolkit
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')
from tradingagents.dataflows.interface import set_config

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class TradingAgentsGraph:
    """Main class that orchestrates the trading agents framework."""

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """Initialize the trading agents graph and components.

        Args:
            selected_analysts: List of analyst types to include
            debug: Whether to run in debug mode
            config: Configuration dictionary. If None, uses default config
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG

        # Update the interface's config
        set_config(self.config)

        # Create necessary directories
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # 初始化 LLM（僅支援 OpenAI 和 Anthropic）
        provider = self.config["llm_provider"].lower()
        backend_url = self.config.get("backend_url", "")

        if provider == "openai":
            # OpenAI 支援自訂 base_url（用於相容 API 代理等場景）
            openai_kwargs = {"model": self.config["deep_think_llm"]}
            if backend_url:
                openai_kwargs["base_url"] = backend_url
            self.deep_thinking_llm = ChatOpenAI(**openai_kwargs)

            openai_kwargs_quick = {"model": self.config["quick_think_llm"]}
            if backend_url:
                openai_kwargs_quick["base_url"] = backend_url
            self.quick_thinking_llm = ChatOpenAI(**openai_kwargs_quick)

        elif provider == "anthropic":
            # Anthropic 使用獨立的 API 端點，不傳入 OpenAI 的 base_url
            anthropic_kwargs = {"model": self.config["deep_think_llm"]}
            anthropic_base = self.config.get("anthropic_base_url", "")
            if anthropic_base:
                anthropic_kwargs["base_url"] = anthropic_base
            self.deep_thinking_llm = ChatAnthropic(**anthropic_kwargs)

            anthropic_kwargs_quick = {"model": self.config["quick_think_llm"]}
            if anthropic_base:
                anthropic_kwargs_quick["base_url"] = anthropic_base
            self.quick_thinking_llm = ChatAnthropic(**anthropic_kwargs_quick)

        else:
            raise ValueError(f"不支援的 LLM 提供商: {self.config['llm_provider']}。僅支援 openai 和 anthropic。")
        
        self.toolkit = Toolkit(config=self.config)

        # Initialize memories (如果啟用)
        memory_enabled = self.config.get("memory_enabled", True)
        if memory_enabled:
            # 使用單例ChromaDB管理器，避免並發創建衝突
            self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
            self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
            self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
            self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
            self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)
        else:
            # 創建空的內存對象
            self.bull_memory = None
            self.bear_memory = None
            self.trader_memory = None
            self.invest_judge_memory = None
            self.risk_manager_memory = None

        # Create tool nodes
        self.tool_nodes = self._create_tool_nodes()

        # Initialize components
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
            self.config,
            getattr(self, 'react_llm', None),
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # State tracking
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # date to full state dict

        # Set up the graph
        self.graph = self.graph_setup.setup_graph(selected_analysts)

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """Create tool nodes for different data sources."""
        return {
            "market": ToolNode(
                [
                    # 統一工具
                    self.toolkit.get_stock_market_data_unified,
                    # online tools
                    self.toolkit.get_YFin_data_online,
                    self.toolkit.get_stockstats_indicators_report_online,
                    # offline tools
                    self.toolkit.get_YFin_data,
                    self.toolkit.get_stockstats_indicators_report,
                ]
            ),
            "social": ToolNode(
                [
                    # 新聞情緒工具
                    self.toolkit.get_stock_news_openai,
                    # FinnHub 情緒量化數據
                    self.toolkit.get_finnhub_sentiment_data,
                ]
            ),
            "news": ToolNode(
                [
                    # 新聞來源
                    self.toolkit.get_global_news_openai,
                    self.toolkit.get_google_news,
                    self.toolkit.get_finnhub_news,
                    # FinnHub 情緒量化數據
                    self.toolkit.get_finnhub_sentiment_data,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # 統一工具
                    self.toolkit.get_stock_fundamentals_unified,
                    # offline tools
                    self.toolkit.get_finnhub_company_insider_sentiment,
                    self.toolkit.get_finnhub_company_insider_transactions,
                    self.toolkit.get_simfin_balance_sheet,
                    self.toolkit.get_simfin_cashflow,
                    self.toolkit.get_simfin_income_stmt,
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """Run the trading agents graph for a company on a specific date."""

        # 添加詳細的接收日誌
        logger.debug("===== TradingAgentsGraph.propagate 接收參數 =====")
        logger.debug(f"接收到的company_name: '{company_name}' (類型: {type(company_name)})")
        logger.debug(f"接收到的trade_date: '{trade_date}' (類型: {type(trade_date)})")

        self.ticker = company_name
        logger.debug(f"設置self.ticker: '{self.ticker}'")

        # Initialize state
        logger.debug(f"創建初始狀態，傳遞參數: company_name='{company_name}', trade_date='{trade_date}'")
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        logger.debug(f"初始狀態中的company_of_interest: '{init_agent_state.get('company_of_interest', 'NOT_FOUND')}'")
        logger.debug(f"初始狀態中的trade_date: '{init_agent_state.get('trade_date', 'NOT_FOUND')}'")
        args = self.propagator.get_graph_args()

        if self.debug:
            # Debug mode with tracing
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if chunk["messages"]:
                    last_msg = chunk["messages"][-1]
                    msg_content = getattr(last_msg, 'content', str(last_msg))
                    logger.debug(f"[Debug] {msg_content[:200]}")
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # Standard mode without tracing
            final_state = self.graph.invoke(init_agent_state, **args)

        # Store current state for reflection
        self.curr_state = final_state

        # Log state
        self._log_state(trade_date, final_state)

        # Return decision and processed signal
        return final_state, self.process_signal(final_state["final_trade_decision"], company_name)

    def _log_state(self, trade_date, final_state):
        """Log the final state to a JSON file."""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """Reflect on decisions and update memory based on returns."""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal, stock_symbol=None):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal, stock_symbol)
