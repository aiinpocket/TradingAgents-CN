# TradingAgents/graph/signal_processing.py

from langchain_openai import ChatOpenAI

# 導入統一日誌系統和圖處理模塊日誌裝飾器
from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_graph_module
logger = get_logger("graph.signal_processing")


class SignalProcessor:
    """Processes trading signals to extract actionable decisions."""

    def __init__(self, quick_thinking_llm: ChatOpenAI):
        """Initialize with an LLM for processing."""
        self.quick_thinking_llm = quick_thinking_llm

    @log_graph_module("signal_processing")
    def process_signal(self, full_signal: str, stock_symbol: str = None) -> dict:
        """
        Process a full trading signal to extract structured decision information.

        Args:
            full_signal: Complete trading signal text
            stock_symbol: Stock symbol to determine currency type

        Returns:
            Dictionary containing extracted decision information
        """

        # 驗證輸入參數
        if not full_signal or not isinstance(full_signal, str) or len(full_signal.strip()) == 0:
            logger.error(f" [SignalProcessor] 輸入信號為空或無效: {repr(full_signal)}")
            return {
                'action': '持有',
                'target_price': None,
                'confidence': 0.5,
                'risk_score': 0.5,
                'reasoning': '輸入信號無效，默認持有建議'
            }

        # 清理和驗證信號內容
        full_signal = full_signal.strip()
        if len(full_signal) == 0:
            logger.error(" [SignalProcessor] 信號內容為空")
            return {
                'action': '持有',
                'target_price': None,
                'confidence': 0.5,
                'risk_score': 0.5,
                'reasoning': '信號內容為空，默認持有建議'
            }

        # 取得股票市場資訊（僅支援美股）
        from tradingagents.utils.stock_utils import get_stock_market_info

        market_info = get_stock_market_info(stock_symbol)
        currency = market_info['currency_name']
        currency_symbol = market_info['currency_symbol']

        logger.info(f"[SignalProcessor] 處理信號: 股票={stock_symbol}, 市場={market_info['market_name']}, 貨幣={currency}",
                   extra={'stock_symbol': stock_symbol, 'market': market_info['market_name'], 'currency': currency})

        messages = [
            (
                "system",
                f"""您是一位專業的金融分析助手，負責從交易員的分析報告中提取結構化的投資決策信息。

請從提供的分析報告中提取以下信息，並以JSON格式返回：

{{
    "action": "買入/持有/賣出",
    "target_price": 數字({currency}價格，**必須提供具體數值，不能為null**),
    "confidence": 數字(0-1之間，如果沒有明確提及則為0.7),
    "risk_score": 數字(0-1之間，如果沒有明確提及則為0.5),
    "reasoning": "決策的主要理由摘要"
}}

請確保：
1. action字段必須是"買入"、"持有"或"賣出"之一（絕對不允許使用英文buy/hold/sell）
2. target_price必須是具體的數字,target_price應該是合理的{currency}價格數字（使用{currency_symbol}符號）
3. confidence和risk_score應該在0-1之間
4. reasoning應該是簡潔的中文摘要
5. 所有內容必須使用中文，不允許任何英文投資建議

特別註意：
- 股票代碼 {stock_symbol or '未知'} 是{market_info['market_name']}，使用{currency}計價
- 目標價格必須與股票的交易貨幣一致（{currency_symbol}）

如果某些信息在報告中沒有明確提及，請使用合理的默認值。""",
            ),
            ("human", full_signal),
        ]

        # 驗證messages內容
        if not messages or len(messages) == 0:
            logger.error(" [SignalProcessor] messages為空")
            return self._get_default_decision()
        
        # 驗證human訊息內容
        human_content = messages[1][1] if len(messages) > 1 else ""
        if not human_content or len(human_content.strip()) == 0:
            logger.error(" [SignalProcessor] human訊息內容為空")
            return self._get_default_decision()

        logger.debug(f"[SignalProcessor] 準備調用LLM，訊息數量: {len(messages)}, 信號長度: {len(full_signal)}")

        try:
            response = self.quick_thinking_llm.invoke(messages).content
            logger.debug(f"[SignalProcessor] LLM響應: {response[:200]}...")

            # 嘗試解析JSON響應
            import json
            import re

            # 提取JSON部分
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_text = json_match.group()
                logger.debug(f"[SignalProcessor] 提取的JSON: {json_text}")
                decision_data = json.loads(json_text)

                # 驗證和標準化數據
                action = decision_data.get('action', '持有')
                if action not in ['買入', '持有', '賣出']:
                    # 嘗試映射英文和其他變體
                    action_map = {
                        'buy': '買入', 'hold': '持有', 'sell': '賣出',
                        'BUY': '買入', 'HOLD': '持有', 'SELL': '賣出',
                        '購買': '買入', '保持': '持有', '出售': '賣出',
                        'purchase': '買入', 'keep': '持有', 'dispose': '賣出'
                    }
                    action = action_map.get(action, '持有')
                    if action != decision_data.get('action', '持有'):
                        logger.debug(f"[SignalProcessor] 投資建議映射: {decision_data.get('action')} -> {action}")

                # 處理目標價格，確保正確提取
                target_price = decision_data.get('target_price')
                if target_price is None or target_price == "null" or target_price == "":
                    # 如果JSON中沒有目標價格，嘗試從reasoning和完整文本中提取
                    reasoning = decision_data.get('reasoning', '')
                    full_text = f"{reasoning} {full_signal}"  # 擴大搜索範圍
                    
                    # 增強的價格匹配模式
                    price_patterns = [
                        r'目標價[位格]?[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',  # 目標價位: 45.50
                        r'目標[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',         # 目標: 45.50
                        r'價格[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',         # 價格: 45.50
                        r'價位[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',         # 價位: 45.50
                        r'合理[價位格]?[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)', # 合理價位: 45.50
                        r'估值[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',         # 估值: 45.50
                        r'[¥\$](\d+(?:\.\d+)?)',                      # ¥45.50 或 $190
                        r'(\d+(?:\.\d+)?)元',                         # 45.50元
                        r'(\d+(?:\.\d+)?)美元',                       # 190美元
                        r'建議[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',        # 建議: 45.50
                        r'預期[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',        # 預期: 45.50
                        r'看[到至]\s*[¥\$]?(\d+(?:\.\d+)?)',          # 看到45.50
                        r'上漲[到至]\s*[¥\$]?(\d+(?:\.\d+)?)',        # 上漲到45.50
                        r'(\d+(?:\.\d+)?)\s*[¥\$]',                  # 45.50¥
                    ]
                    
                    for pattern in price_patterns:
                        price_match = re.search(pattern, full_text, re.IGNORECASE)
                        if price_match:
                            try:
                                target_price = float(price_match.group(1))
                                logger.debug(f"[SignalProcessor] 從文本中提取到目標價格: {target_price} (模式: {pattern})")
                                break
                            except (ValueError, IndexError):
                                continue

                    # 如果仍然沒有找到價格，嘗試智能推算
                    if target_price is None or target_price == "null" or target_price == "":
                        target_price = self._smart_price_estimation(full_text, action)
                        if target_price:
                            logger.debug(f"[SignalProcessor] 智能推算目標價格: {target_price}")
                        else:
                            target_price = None
                            logger.warning("[SignalProcessor] 未能提取到目標價格，設置為None")
                else:
                    # 確保價格是數值類型
                    try:
                        if isinstance(target_price, str):
                            # 清理字符串格式的價格
                            clean_price = target_price.replace('$', '').replace('¥', '').replace('￥', '').replace('元', '').replace('美元', '').strip()
                            target_price = float(clean_price) if clean_price and clean_price.lower() not in ['none', 'null', ''] else None
                        elif isinstance(target_price, (int, float)):
                            target_price = float(target_price)
                        logger.debug(f"[SignalProcessor] 處理後的目標價格: {target_price}")
                    except (ValueError, TypeError):
                        target_price = None
                        logger.warning("[SignalProcessor] 價格轉換失敗，設置為None")

                result = {
                    'action': action,
                    'target_price': target_price,
                    'confidence': float(decision_data.get('confidence', 0.7)),
                    'risk_score': float(decision_data.get('risk_score', 0.5)),
                    'reasoning': decision_data.get('reasoning', '基於綜合分析的投資建議')
                }
                logger.info(f"[SignalProcessor] 處理結果: {result}",
                           extra={'action': result['action'], 'target_price': result['target_price'],
                                 'confidence': result['confidence'], 'stock_symbol': stock_symbol})
                return result
            else:
                # 如果無法解析JSON，使用簡單的文本提取
                return self._extract_simple_decision(response)

        except Exception as e:
            logger.error(f"信號處理錯誤: {e}", exc_info=True, extra={'stock_symbol': stock_symbol})
            # 回退到簡單提取
            return self._extract_simple_decision(full_signal)

    def _smart_price_estimation(self, text: str, action: str) -> float:
        """智能價格推算方法（僅支援美股）"""
        import re
        
        # 嘗試從文本中提取當前價格和漲跌幅信息
        current_price = None
        percentage_change = None
        
        # 提取當前價格
        current_price_patterns = [
            r'當前價[格位]?[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',
            r'現價[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',
            r'股價[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',
            r'價格[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',
        ]
        
        for pattern in current_price_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    current_price = float(match.group(1))
                    break
                except ValueError:
                    continue
        
        # 提取漲跌幅信息
        percentage_patterns = [
            r'上漲\s*(\d+(?:\.\d+)?)%',
            r'漲幅\s*(\d+(?:\.\d+)?)%',
            r'增長\s*(\d+(?:\.\d+)?)%',
            r'(\d+(?:\.\d+)?)%\s*的?上漲',
        ]
        
        for pattern in percentage_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    percentage_change = float(match.group(1)) / 100
                    break
                except ValueError:
                    continue
        
        # 基於動作和信息推算目標價
        if current_price and percentage_change:
            if action == '買入':
                return round(current_price * (1 + percentage_change), 2)
            elif action == '賣出':
                return round(current_price * (1 - percentage_change), 2)
        
        # 如果有當前價格但沒有漲跌幅，使用預設估算（美股）
        if current_price:
            if action == '買入':
                # 買入建議預設12%漲幅
                return round(current_price * 1.12, 2)
            elif action == '賣出':
                # 賣出建議預設8%跌幅
                return round(current_price * 0.92, 2)
            else:  # 持有
                # 持有建議使用當前價格
                return current_price
        
        return None

    def _extract_simple_decision(self, text: str) -> dict:
        """簡單的決策提取方法作為備用"""
        import re

        # 提取動作
        action = '持有'  # 默認
        if re.search(r'買入|BUY', text, re.IGNORECASE):
            action = '買入'
        elif re.search(r'賣出|SELL', text, re.IGNORECASE):
            action = '賣出'
        elif re.search(r'持有|HOLD', text, re.IGNORECASE):
            action = '持有'

        # 嘗試提取目標價格（使用增強的模式）
        target_price = None
        price_patterns = [
            r'目標價[位格]?[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',  # 目標價位: 45.50
            r'\*\*目標價[位格]?\*\*[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',  # **目標價位**: 45.50
            r'目標[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',         # 目標: 45.50
            r'價格[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)',         # 價格: 45.50
            r'[¥\$](\d+(?:\.\d+)?)',                      # ¥45.50 或 $190
            r'(\d+(?:\.\d+)?)元',                         # 45.50元
        ]

        for pattern in price_patterns:
            price_match = re.search(pattern, text)
            if price_match:
                try:
                    target_price = float(price_match.group(1))
                    break
                except ValueError:
                    continue

        # 如果沒有找到價格，嘗試智能推算（僅美股）
        if target_price is None:
            target_price = self._smart_price_estimation(text, action)

        return {
            'action': action,
            'target_price': target_price,
            'confidence': 0.7,
            'risk_score': 0.5,
            'reasoning': '基於綜合分析的投資建議'
        }

    def _get_default_decision(self) -> dict:
        """返回默認的投資決策"""
        return {
            'action': '持有',
            'target_price': None,
            'confidence': 0.5,
            'risk_score': 0.5,
            'reasoning': '輸入數據無效，默認持有建議'
        }
