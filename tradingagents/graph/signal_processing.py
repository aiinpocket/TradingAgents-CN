# TradingAgents/graph/signal_processing.py
# 從風險管理委員會的最終決策文本中提取結構化交易訊號
# 使用純正則提取（不依賴 LLM），節省 1-3 秒延遲和 token 成本

import json
import re

from tradingagents.utils.logging_init import get_logger
from tradingagents.utils.tool_logging import log_graph_module

logger = get_logger("graph.signal_processing")

# 投資建議映射表（各種變體 -> 標準中文）
_ACTION_MAP = {
    'buy': '買入', 'hold': '持有', 'sell': '賣出',
    'BUY': '買入', 'HOLD': '持有', 'SELL': '賣出',
    '購買': '買入', '保持': '持有', '出售': '賣出',
    'purchase': '買入', 'keep': '持有', 'dispose': '賣出',
}

# 預編譯價格提取正則
_PRICE_PATTERNS = [
    re.compile(r'目標價[位格]?[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)'),
    re.compile(r'目標[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)'),
    re.compile(r'價格[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)'),
    re.compile(r'價位[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)'),
    re.compile(r'合理[價位格]?[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)'),
    re.compile(r'估值[：:]?\s*[¥\$]?(\d+(?:\.\d+)?)'),
    re.compile(r'[¥\$](\d+(?:\.\d+)?)'),
    re.compile(r'(\d+(?:\.\d+)?)美元'),
    re.compile(r'看[到至]\s*[¥\$]?(\d+(?:\.\d+)?)'),
    re.compile(r'上漲[到至]\s*[¥\$]?(\d+(?:\.\d+)?)'),
]

# 投資建議偵測正則
_ACTION_BUY_RE = re.compile(r'買入|BUY', re.IGNORECASE)
_ACTION_SELL_RE = re.compile(r'賣出|SELL', re.IGNORECASE)
_ACTION_HOLD_RE = re.compile(r'持有|HOLD', re.IGNORECASE)

# JSON 區塊偵測正則（Risk Judge 報告中可能包含結構化輸出）
_JSON_BLOCK_RE = re.compile(r'\{[^{}]*"action"[^{}]*\}', re.DOTALL)


class SignalProcessor:
    """從風險管理委員會的決策文本中提取結構化交易訊號（純正則，不使用 LLM）。"""

    def __init__(self, quick_thinking_llm=None):
        """保留 LLM 參數以維持向後相容，但不再使用。"""
        pass

    @log_graph_module("signal_processing")
    def process_signal(self, full_signal: str, stock_symbol: str = None) -> dict:
        """從決策文本中提取結構化交易訊號。純正則提取，不呼叫 LLM。"""

        # 驗證輸入
        if not full_signal or not isinstance(full_signal, str) or not full_signal.strip():
            logger.error(f"[SignalProcessor] 輸入訊號為空或無效: {repr(full_signal)}")
            return self._get_default_decision()

        text = full_signal.strip()
        logger.info(
            f"[SignalProcessor] 處理訊號: 股票={stock_symbol}, 文本長度={len(text)}",
            extra={"stock_symbol": stock_symbol},
        )

        # 策略 1：嘗試從文本中提取 JSON 區塊（某些 LLM 會在報告中嵌入結構化輸出）
        result = self._try_extract_json(text)
        if result:
            logger.info(
                f"[SignalProcessor] JSON 提取成功: action={result['action']}",
                extra={"action": result["action"], "stock_symbol": stock_symbol},
            )
            return result

        # 策略 2：純正則提取
        result = self._extract_simple_decision(text)
        logger.info(
            f"[SignalProcessor] 正則提取結果: {result}",
            extra={"action": result["action"], "target_price": result["target_price"], "stock_symbol": stock_symbol},
        )
        return result

    def _try_extract_json(self, text: str) -> dict | None:
        """嘗試從文本中提取 JSON 區塊並解析為決策字典。"""
        match = _JSON_BLOCK_RE.search(text)
        if not match:
            return None
        try:
            data = json.loads(match.group())
        except json.JSONDecodeError:
            return None

        action = data.get("action", "持有")
        if action not in ("買入", "持有", "賣出"):
            action = _ACTION_MAP.get(action, "持有")

        target_price = self._parse_price(data.get("target_price"))
        if target_price is None:
            target_price = self._extract_price_from_text(text)

        return {
            "action": action,
            "target_price": target_price,
            "confidence": self._clamp(data.get("confidence", 0.7)),
            "risk_score": self._clamp(data.get("risk_score", 0.5)),
            "reasoning": data.get("reasoning", "基於綜合分析的投資建議"),
        }

    def _extract_simple_decision(self, text: str) -> dict:
        """純正則提取決策（主要路徑，不使用 LLM）。"""
        # 提取投資建議
        if _ACTION_BUY_RE.search(text):
            action = "買入"
        elif _ACTION_SELL_RE.search(text):
            action = "賣出"
        else:
            action = "持有"

        # 提取目標價格
        target_price = self._extract_price_from_text(text)

        # 提取推理摘要（取建議後的第一段非空行，最多 100 字）
        reasoning = "基於綜合分析的投資建議"
        reason_match = re.search(
            r'(?:理由|原因|依據|建議|摘要|結論)[：:]\s*(.{10,100})',
            text,
        )
        if reason_match:
            reasoning = reason_match.group(1).strip()

        return {
            "action": action,
            "target_price": target_price,
            "confidence": 0.7,
            "risk_score": 0.5,
            "reasoning": reasoning,
        }

    # -- 內部工具方法 --

    @staticmethod
    def _extract_price_from_text(text: str) -> float | None:
        """從文本中用正則提取目標價格。"""
        for pattern in _PRICE_PATTERNS:
            m = pattern.search(text)
            if m:
                try:
                    return float(m.group(1))
                except (ValueError, IndexError):
                    continue
        return None

    @staticmethod
    def _parse_price(value) -> float | None:
        """將各種格式的價格值轉為 float。"""
        if value is None or value == "null" or value == "":
            return None
        try:
            if isinstance(value, str):
                cleaned = value.replace("$", "").replace("¥", "").replace("美元", "").strip()
                return float(cleaned) if cleaned and cleaned.lower() not in ("none", "null", "") else None
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _clamp(value, lo=0.0, hi=1.0, default=0.5) -> float:
        """將數值限制在 [lo, hi] 範圍。"""
        try:
            v = float(value)
            return max(lo, min(hi, v))
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _get_default_decision() -> dict:
        """返回預設的投資決策。"""
        return {
            "action": "持有",
            "target_price": None,
            "confidence": 0.5,
            "risk_score": 0.5,
            "reasoning": "輸入資料無效，預設持有建議",
        }
