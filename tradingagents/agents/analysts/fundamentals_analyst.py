"""
基本面分析師 - 統一工具架構版本
使用統一工具自動識別股票類型並呼叫相應資料來源
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# 匯入分析模組日誌裝飾器
from tradingagents.utils.tool_logging import log_analyst_module

# 匯入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


def _get_company_name_for_fundamentals(ticker: str, market_info: dict) -> str:
    """
    為基本面分析師取得公司名稱

    Args:
        ticker: 股票代碼
        market_info: 市場資訊字典

    Returns:
        str: 公司名稱
    """
    try:
        us_stock_names = {
            'AAPL': '蘋果公司',
            'TSLA': '特斯拉',
            'NVDA': '輝達',
            'MSFT': '微軟',
            'GOOGL': '谷歌',
            'AMZN': '亞馬遜',
            'META': 'Meta',
            'NFLX': 'Netflix'
        }

        company_name = us_stock_names.get(ticker.upper(), ticker)
        logger.debug(f"[基本面分析師] 美股名稱映射: {ticker} -> {company_name}")
        return company_name

    except Exception as e:
        logger.error(f"[基本面分析師] 取得公司名稱失敗: {e}")
        return ticker


def create_fundamentals_analyst(llm, toolkit):
    @log_analyst_module("fundamentals")
    def fundamentals_analyst_node(state):
        logger.debug("===== 基本面分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        from tradingagents.agents.utils.agent_utils import calc_start_date
        start_date = calc_start_date(current_date)

        logger.debug(f"輸入參數: ticker={ticker}, date={current_date}")
        logger.debug(f"當前狀態中的訊息數量: {len(state.get('messages', []))}")
        logger.debug(f"現有基本面報告: {state.get('fundamentals_report', 'None')}")

        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info
        logger.info(f"[基本面分析師] 正在分析股票: {ticker}")

        # 股票代碼追蹤日誌
        logger.info(f"[股票代碼追蹤] 基本面分析師接收到的股票代碼: '{ticker}' (類型: {type(ticker)})")

        market_info = get_stock_market_info(ticker)
        logger.info(f"[股票代碼追蹤] get_stock_market_info 返回的市場資訊: {market_info}")

        logger.debug(f"股票類型檢查: {ticker} -> {market_info['market_name']} ({market_info['currency_name']})")
        logger.debug(f"市場資訊: is_us={market_info['is_us']}")
        logger.debug(f"工具配置檢查: online_tools={toolkit.config['online_tools']}")

        # 取得公司名稱
        company_name = _get_company_name_for_fundamentals(ticker, market_info)
        logger.debug(f"公司名稱: {ticker} -> {company_name}")

        # 直接呼叫工具取得資料（跳過 LLM 工具決策步驟，節省一次 LLM 呼叫）
        currency_info = f"{market_info['currency_name']}（{market_info['currency_symbol']}）"

        if toolkit.config["online_tools"]:
            logger.info("[基本面分析師] 直接呼叫工具取得基本面資料和分析師共識")

            from tradingagents.agents.utils.agent_utils import invoke_tools_direct
            tools = [toolkit.get_stock_fundamentals_unified, toolkit.get_finnhub_analyst_consensus]
            tool_args = [
                {"ticker": ticker, "start_date": start_date, "end_date": current_date, "curr_date": current_date},
                {"ticker": ticker, "curr_date": current_date},
            ]
            tool_results = invoke_tools_direct(tools, tool_args, logger)

            fundamentals_data = tool_results[0]
            analyst_consensus = tool_results[1]
        else:
            logger.info("[基本面分析師] 離線模式，直接呼叫多個資料工具")
            from tradingagents.agents.utils.agent_utils import invoke_tools_direct
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
                toolkit.get_finnhub_analyst_consensus,
            ]
            tool_args = [
                {"ticker": ticker, "curr_date": current_date},
                {"ticker": ticker, "curr_date": current_date},
                {"ticker": ticker, "freq": "quarterly"},
                {"ticker": ticker, "freq": "quarterly"},
                {"ticker": ticker, "freq": "quarterly"},
                {"ticker": ticker, "curr_date": current_date},
            ]
            tool_results = invoke_tools_direct(tools, tool_args, logger)
            fundamentals_data = "\n\n".join(tool_results[:-1])
            analyst_consensus = tool_results[-1]

        # 單次 LLM 呼叫：基於已取得的工具資料生成分析報告
        from langchain_core.messages import HumanMessage

        analysis_prompt = f"""你是一位專業的股票基本面分析師。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。**

請基於以下真實資料，對{company_name}（{ticker}）進行詳細的基本面分析。
當前日期：{current_date}
所屬市場：{market_info['market_name']}
計價貨幣：{currency_info}

=== 基本面資料 ===
{fundamentals_data}

=== 華爾街分析師共識 ===
{analyst_consensus}

**分析要求：**
1. 基於上述真實資料進行分析，不要編造數據
2. 整合分析師共識資料（評級分布、目標價、EPS/營收預測）
3. 包含 PE、PB、PEG 等估值指標分析
4. 計算合理價位區間，分析當前股價是否被低估或高估
5. 投資建議使用中文（買入/持有/賣出），不允許使用英文
6. 所有價格使用{currency_info}

**輸出格式：**
## 公司基本資訊
## 財務狀況評估
## 盈利能力分析
## 估值分析
## 投資建議"""

        try:
            result = llm.invoke([HumanMessage(content=analysis_prompt)])
            report = result.content
            logger.info(f"[基本面分析師] 直接模式完成，報告長度: {len(report)}")
        except Exception as e:
            logger.error(f"[基本面分析師] LLM 分析失敗: {e}", exc_info=True)
            report = f"基本面分析失敗: {str(e)}"

        return {"fundamentals_report": report}

    return fundamentals_analyst_node
