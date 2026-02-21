from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# 匯入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')


# 建立自訂配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-4o"
config["quick_think_llm"] = "gpt-4o-mini"
config["max_debate_rounds"] = 1
config["online_tools"] = True

# 使用自訂配置初始化
ta = TradingAgentsGraph(debug=False, config=config)

# 執行分析
_, decision = ta.propagate("NVDA", "2024-05-10")
logger.info(f"交易決策: {decision}")

# 反思與記憶（參數為持倉收益）
# ta.reflect_and_remember(1000)
