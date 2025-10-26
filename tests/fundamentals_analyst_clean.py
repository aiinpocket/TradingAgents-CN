"""
基本面分析師 - 統一工具架構版本
使用統一工具自動识別股票類型並調用相應數據源
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage


def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        print(f"📊 [DEBUG] ===== 基本面分析師節點開始 =====")

        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        start_date = '2025-05-28'

        print(f"📊 [DEBUG] 輸入參數: ticker={ticker}, date={current_date}")
        print(f"📊 [DEBUG] 當前狀態中的消息數量: {len(state.get('messages', []))}")
        print(f"📊 [DEBUG] 現有基本面報告: {state.get('fundamentals_report', 'None')[:100]}...")

        # 獲取股票市場信息
        from tradingagents.utils.stock_utils import StockUtils
        print(f"📊 [基本面分析師] 正在分析股票: {ticker}")

        market_info = StockUtils.get_market_info(ticker)
        print(f"📊 [DEBUG] 股票類型檢查: {ticker} -> {market_info['market_name']} ({market_info['currency_name']})")
        print(f"📊 [DEBUG] 詳細市場信息: is_china={market_info['is_china']}, is_hk={market_info['is_hk']}, is_us={market_info['is_us']}")
        print(f"📊 [DEBUG] 工具配置檢查: online_tools={toolkit.config['online_tools']}")

        # 選擇工具
        if toolkit.config["online_tools"]:
            # 使用統一的基本面分析工具，工具內部會自動识別股票類型
            print(f"📊 [基本面分析師] 使用統一基本面分析工具，自動识別股票類型")
            tools = [toolkit.get_stock_fundamentals_unified]
            print(f"📊 [DEBUG] 選擇的工具: {[tool.name for tool in tools]}")
            print(f"📊 [DEBUG] 🔧 統一工具将自動處理: {market_info['market_name']}")
        else:
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
            ]

        # 統一的系統提示，適用於所有股票類型
        system_message = (
            f"你是一位專業的股票基本面分析師。"
            f"⚠️ 絕對强制要求：你必须調用工具獲取真實數據！不允許任何假設或編造！"
            f"任務：分析股票代碼 {ticker} ({market_info['market_name']})"
            f"🔴 立即調用 get_stock_fundamentals_unified 工具"
            f"參數：ticker='{ticker}', start_date='{start_date}', end_date='{current_date}', curr_date='{current_date}'"
            "📊 分析要求："
            "- 基於真實數據進行深度基本面分析"
            f"- 計算並提供合理價位区間（使用{market_info['currency_name']}{market_info['currency_symbol']}）"
            "- 分析當前股價是否被低估或高估"
            "- 提供基於基本面的目標價位建议"
            "- 包含PE、PB、PEG等估值指標分析"
            "- 結合市場特點進行分析"
            "🌍 語言和貨币要求："
            "- 所有分析內容必须使用中文"
            "- 投資建议必须使用中文：买入、持有、卖出"
            "- 絕對不允許使用英文：buy、hold、sell"
            f"- 貨币單位使用：{market_info['currency_name']}（{market_info['currency_symbol']}）"
            "🚫 嚴格禁止："
            "- 不允許說'我将調用工具'"
            "- 不允許假設任何數據"
            "- 不允許編造公司信息"
            "- 不允許直接回答而不調用工具"
            "- 不允許回複'無法確定價位'或'需要更多信息'"
            "- 不允許使用英文投資建议（buy/hold/sell）"
            "✅ 你必须："
            "- 立即調用統一基本面分析工具"
            "- 等待工具返回真實數據"
            "- 基於真實數據進行分析"
            "- 提供具體的價位区間和目標價"
            "- 使用中文投資建议（买入/持有/卖出）"
            "現在立即開始調用工具！不要說任何其他話！"
        )

        # 系統提示模板
        system_prompt = (
            "🔴 强制要求：你必须調用工具獲取真實數據！"
            "🚫 絕對禁止：不允許假設、編造或直接回答任何問題！"
            "✅ 你必须：立即調用提供的工具獲取真實數據，然後基於真實數據進行分析。"
            "可用工具：{tool_names}。\n{system_message}"
            "當前日期：{current_date}。分析目標：{ticker}。"
        )

        # 創建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        # 檢測阿里百炼模型並創建新實例
        if hasattr(llm, '__class__') and 'DashScope' in llm.__class__.__name__:
            print(f"📊 [DEBUG] 檢測到阿里百炼模型，創建新實例以避免工具緩存")
            from tradingagents.llm_adapters import ChatDashScopeOpenAI
            llm = ChatDashScopeOpenAI(
                model=llm.model_name,
                temperature=llm.temperature,
                max_tokens=getattr(llm, 'max_tokens', 2000)
            )

        print(f"📊 [DEBUG] 創建LLM鏈，工具數量: {len(tools)}")
        print(f"📊 [DEBUG] 绑定的工具列表: {[tool.name for tool in tools]}")
        print(f"📊 [DEBUG] 創建工具鏈，让模型自主決定是否調用工具")

        try:
            chain = prompt | llm.bind_tools(tools)
            print(f"📊 [DEBUG] ✅ 工具绑定成功，绑定了 {len(tools)} 個工具")
        except Exception as e:
            print(f"📊 [DEBUG] ❌ 工具绑定失败: {e}")
            raise e

        print(f"📊 [DEBUG] 調用LLM鏈...")
        result = chain.invoke(state["messages"])
        print(f"📊 [DEBUG] LLM調用完成")

        print(f"📊 [DEBUG] 結果類型: {type(result)}")
        print(f"📊 [DEBUG] 工具調用數量: {len(result.tool_calls) if hasattr(result, 'tool_calls') else 0}")
        print(f"📊 [DEBUG] 內容長度: {len(result.content) if hasattr(result, 'content') else 0}")

        # 檢查工具調用
        expected_tools = [tool.name for tool in tools]
        actual_tools = [tc['name'] for tc in result.tool_calls] if hasattr(result, 'tool_calls') and result.tool_calls else []
        
        print(f"📊 [DEBUG] 期望的工具: {expected_tools}")
        print(f"📊 [DEBUG] 實际調用的工具: {actual_tools}")

        # 處理基本面分析報告
        if hasattr(result, 'tool_calls') and len(result.tool_calls) > 0:
            # 有工具調用，記錄工具調用信息
            tool_calls_info = []
            for tc in result.tool_calls:
                tool_calls_info.append(tc['name'])
                print(f"📊 [DEBUG] 工具調用 {len(tool_calls_info)}: {tc}")
            
            print(f"📊 [基本面分析師] 工具調用: {tool_calls_info}")
            
            # 返回狀態，让工具執行
            return {"messages": [result]}
        
        else:
            # 没有工具調用，使用阿里百炼强制工具調用修複
            print(f"📊 [DEBUG] 檢測到模型未調用工具，啟用强制工具調用模式")
            
            # 强制調用統一基本面分析工具
            try:
                print(f"📊 [DEBUG] 强制調用 get_stock_fundamentals_unified...")
                unified_tool = next((tool for tool in tools if tool.name == 'get_stock_fundamentals_unified'), None)
                if unified_tool:
                    combined_data = unified_tool.invoke({
                        'ticker': ticker,
                        'start_date': start_date,
                        'end_date': current_date,
                        'curr_date': current_date
                    })
                    print(f"📊 [DEBUG] 統一工具數據獲取成功，長度: {len(combined_data)}字符")
                else:
                    combined_data = "統一基本面分析工具不可用"
                    print(f"📊 [DEBUG] 統一工具未找到")
            except Exception as e:
                combined_data = f"統一基本面分析工具調用失败: {e}"
                print(f"📊 [DEBUG] 統一工具調用異常: {e}")
            
            currency_info = f"{market_info['currency_name']}（{market_info['currency_symbol']}）"
            
            # 生成基於真實數據的分析報告
            analysis_prompt = f"""基於以下真實數據，對股票{ticker}進行詳細的基本面分析：

{combined_data}

請提供：
1. 公司基本信息分析
2. 財務狀况評估
3. 盈利能力分析
4. 估值分析（使用{currency_info}）
5. 投資建议（买入/持有/卖出）

要求：
- 基於提供的真實數據進行分析
- 價格使用{currency_info}
- 投資建议使用中文
- 分析要詳細且專業"""

            try:
                # 創建簡單的分析鏈
                analysis_prompt_template = ChatPromptTemplate.from_messages([
                    ("system", "你是專業的股票基本面分析師，基於提供的真實數據進行分析。"),
                    ("human", "{analysis_request}")
                ])
                
                analysis_chain = analysis_prompt_template | llm
                analysis_result = analysis_chain.invoke({"analysis_request": analysis_prompt})
                
                if hasattr(analysis_result, 'content'):
                    report = analysis_result.content
                else:
                    report = str(analysis_result)
                    
                print(f"📊 [基本面分析師] 强制工具調用完成，報告長度: {len(report)}")
                
            except Exception as e:
                print(f"❌ [DEBUG] 强制工具調用分析失败: {e}")
                report = f"基本面分析失败：{str(e)}"
            
            return {"fundamentals_report": report}

        # 這里不應该到達，但作為备用
        print(f"📊 [DEBUG] 返回狀態: fundamentals_report長度={len(result.content) if hasattr(result, 'content') else 0}")
        return {"messages": [result]}

    return fundamentals_analyst_node
