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
from tradingagents.dataflows.config import set_config

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
            # 強制使用 Chat Completions API，避免 Responses API 回傳
            # ResponseFunctionWebSearch 等 LangGraph ToolNode 無法處理的物件
            openai_kwargs = {
                "model": self.config["deep_think_llm"],
                "use_responses_api": False,
            }
            if backend_url:
                openai_kwargs["base_url"] = backend_url
            self.deep_thinking_llm = ChatOpenAI(**openai_kwargs)

            openai_kwargs_quick = {
                "model": self.config["quick_think_llm"],
                "use_responses_api": False,
            }
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
            # 使用單例ChromaDB管理器，避免並發建立衝突
            self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
            self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
            self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
            self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
            self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)
        else:
            # 建立空的記憶物件
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
                    # FinnHub 技術訊號（分析師 bind_tools 有用到）
                    self.toolkit.get_finnhub_technical_signals,
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
                    # FinnHub 情緒量化資料
                    self.toolkit.get_finnhub_sentiment_data,
                ]
            ),
            "news": ToolNode(
                [
                    # 新聞來源
                    self.toolkit.get_global_news_openai,
                    self.toolkit.get_google_news,
                    self.toolkit.get_finnhub_news,
                    # FinnHub 情緒量化資料
                    self.toolkit.get_finnhub_sentiment_data,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # 統一工具
                    self.toolkit.get_stock_fundamentals_unified,
                    # 華爾街分析師共識資料（分析師 bind_tools 有用到）
                    self.toolkit.get_finnhub_analyst_consensus,
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
        import re

        # 驗證股票代碼格式，防止路徑穿越攻擊
        if not company_name or not re.match(r"^[A-Za-z]{1,5}$", str(company_name).strip()):
            raise ValueError(f"無效的股票代碼: {company_name}")

        # 驗證日期格式
        if not trade_date or not re.match(r"^\d{4}-\d{2}-\d{2}$", str(trade_date).strip()):
            raise ValueError(f"無效的日期格式: {trade_date}")

        # 新增詳細的接收日誌
        logger.debug("===== TradingAgentsGraph.propagate 接收參數 =====")
        logger.debug(f"接收到的company_name: '{company_name}' (類型: {type(company_name)})")
        logger.debug(f"接收到的trade_date: '{trade_date}' (類型: {type(trade_date)})")

        self.ticker = company_name.upper().strip()
        logger.debug(f"設定self.ticker: '{self.ticker}'")

        # Initialize state
        logger.debug(f"建立初始狀態，傳遞參數: company_name='{company_name}', trade_date='{trade_date}'")
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

            if not trace:
                raise RuntimeError("Debug 模式未收到任何回應，請檢查 graph 設定")
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
        try:
            invest_debate = final_state.get("investment_debate_state", {})
            risk_debate = final_state.get("risk_debate_state", {})
            self.log_states_dict[str(trade_date)] = {
                "company_of_interest": final_state.get("company_of_interest", ""),
                "trade_date": final_state.get("trade_date", ""),
                "market_report": final_state.get("market_report", ""),
                "sentiment_report": final_state.get("sentiment_report", ""),
                "news_report": final_state.get("news_report", ""),
                "fundamentals_report": final_state.get("fundamentals_report", ""),
                "investment_debate_state": {
                    "bull_history": invest_debate.get("bull_history", ""),
                    "bear_history": invest_debate.get("bear_history", ""),
                    "history": invest_debate.get("history", ""),
                    "current_response": invest_debate.get("current_response", ""),
                    "judge_decision": invest_debate.get("judge_decision", ""),
                },
                "trader_investment_decision": final_state.get("trader_investment_plan", ""),
                "risk_debate_state": {
                    "risky_history": risk_debate.get("risky_history", ""),
                    "safe_history": risk_debate.get("safe_history", ""),
                    "neutral_history": risk_debate.get("neutral_history", ""),
                    "history": risk_debate.get("history", ""),
                    "judge_decision": risk_debate.get("judge_decision", ""),
                },
                "investment_plan": final_state.get("investment_plan", ""),
                "final_trade_decision": final_state.get("final_trade_decision", ""),
            }
        except Exception as e:
            logger.error(f"記錄狀態時發生錯誤: {e}")
            return

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
        if not self.curr_state:
            logger.warning("尚無分析狀態，跳過反思")
            return

        memories = [
            ("bull_researcher", self.bull_memory, self.reflector.reflect_bull_researcher),
            ("bear_researcher", self.bear_memory, self.reflector.reflect_bear_researcher),
            ("trader", self.trader_memory, self.reflector.reflect_trader),
            ("invest_judge", self.invest_judge_memory, self.reflector.reflect_invest_judge),
            ("risk_manager", self.risk_manager_memory, self.reflector.reflect_risk_manager),
        ]
        for name, memory, reflect_fn in memories:
            if memory is None:
                logger.debug(f"{name} 記憶系統未啟用，跳過反思")
                continue
            try:
                reflect_fn(self.curr_state, returns_losses, memory)
            except Exception as e:
                logger.error(f"{name} 反思時發生錯誤: {e}")

    def process_signal(self, full_signal, stock_symbol=None):
        """Process a signal to extract the core decision."""
        return self.signal_processor.process_signal(full_signal, stock_symbol)
