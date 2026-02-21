"""
智能進度跟蹤器
根據分析師數量、研究深度動態計算進度和時間預估
"""

import time
from typing import Optional, Callable, Dict, List
import streamlit as st

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('progress')

class SmartAnalysisProgressTracker:
    """智能分析進度跟蹤器"""

    def __init__(self, analysts: List[str], research_depth: int, llm_provider: str, callback: Optional[Callable] = None):
        self.callback = callback
        self.analysts = analysts
        self.research_depth = research_depth
        self.llm_provider = llm_provider
        self.steps = []
        self.current_step = 0
        self.start_time = time.time()

        # 根據分析師數量和研究深度動態生成步驟
        self.analysis_steps = self._generate_dynamic_steps()
        self.estimated_duration = self._estimate_total_duration()

    def _generate_dynamic_steps(self) -> List[Dict]:
        """根據分析師數量動態生成分析步驟"""
        steps = [
            {"name": "數據驗證", "description": "驗證股票代碼並預獲取數據", "weight": 0.05},
            {"name": "環境準備", "description": "檢查API密鑰和環境配置", "weight": 0.02},
            {"name": "成本預估", "description": "預估分析成本", "weight": 0.01},
            {"name": "參數配置", "description": "配置分析參數和模型", "weight": 0.02},
            {"name": "引擎初始化", "description": "初始化AI分析引擎", "weight": 0.05},
        ]

        # 為每個分析師添加專門的步驟
        analyst_weight = 0.8 / len(self.analysts)  # 80%的時間用於分析師工作
        for analyst in self.analysts:
            analyst_name = self._get_analyst_display_name(analyst)
            steps.append({
                "name": f"{analyst_name}分析",
                "description": f"{analyst_name}正在進行專業分析",
                "weight": analyst_weight
            })

        # 最後的整理步驟
        steps.append({"name": "結果整理", "description": "整理分析結果和生成報告", "weight": 0.05})

        return steps

    def _get_analyst_display_name(self, analyst: str) -> str:
        """獲取分析師顯示名稱"""
        name_map = {
            'market': '市場分析師',
            'fundamentals': '基本面分析師',
            'technical': '技術分析師',
            'sentiment': '情緒分析師',
            'risk': '風險分析師'
        }
        return name_map.get(analyst, analyst)

    def _estimate_total_duration(self) -> float:
        """根據分析師數量、研究深度、模型類型預估總時長（秒）"""
        # 基礎時間（秒）- 環境準備、配置等
        base_time = 60

        # 每個分析師的實際耗時（基於真實測試數據）
        analyst_base_time = {
            1: 120,  # 快速分析：每個分析師約2分鐘
            2: 180,  # 基礎分析：每個分析師約3分鐘
            3: 240   # 標準分析：每個分析師約4分鐘
        }.get(self.research_depth, 180)

        analyst_time = len(self.analysts) * analyst_base_time

        # 模型速度影響（基於實際測試）
        model_multiplier = {
            'openai': 0.8,
            'google': 1.3,
            'anthropic': 1.0,
            'openrouter': 1.1,
            'ollama': 1.5,
            'custom_openai': 1.0
        }.get(self.llm_provider, 1.0)

        # 研究深度額外影響（工具調用複雜度）
        depth_multiplier = {
            1: 0.8,  # 快速分析，較少工具調用
            2: 1.0,  # 基礎分析，標準工具調用
            3: 1.3   # 標準分析，更多工具調用和推理
        }.get(self.research_depth, 1.0)

        total_time = (base_time + analyst_time) * model_multiplier * depth_multiplier
        return total_time
    
    def update(self, message: str, step: Optional[int] = None, total_steps: Optional[int] = None):
        """更新進度"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # 記錄步驟
        self.steps.append({
            'message': message,
            'timestamp': current_time,
            'elapsed': elapsed_time
        })

        # 根據訊息內容自動判斷當前步驟
        if step is None:
            step = self._detect_step_from_message(message)

        if step is not None:
            # 特殊處理：如果檢測到"模塊完成"，推進到下一步
            if "模塊完成" in message and step == self.current_step:
                # 分析師完成，推進到下一步
                next_step = min(step + 1, len(self.analysis_steps) - 1)
                self.current_step = next_step
                logger.info(f"📊 [進度更新] 分析師完成，推進到步驟 {self.current_step + 1}/{len(self.analysis_steps)}")
            # 防止步驟倒退：只有當檢測到的步驟大於等於當前步驟時才更新
            elif step >= self.current_step:
                self.current_step = step
                logger.debug(f"📊 [進度更新] 步驟推進到 {self.current_step + 1}/{len(self.analysis_steps)}")
            else:
                logger.debug(f"📊 [進度更新] 忽略倒退步驟：檢測到步驟{step + 1}，當前步驟{self.current_step + 1}")

        # 如果是完成訊息，確保進度為100%
        if "分析完成" in message or "分析成功" in message or "✅ 分析完成" in message:
            self.current_step = len(self.analysis_steps) - 1
            logger.info(f"📊 [進度更新] 分析完成，設置為最終步驟 {self.current_step + 1}/{len(self.analysis_steps)}")

        # 調用回調函數
        if self.callback:
            progress = self._calculate_weighted_progress()
            remaining_time = self._estimate_remaining_time(progress, elapsed_time)
            self.callback(message, self.current_step, len(self.analysis_steps), progress, elapsed_time, remaining_time)

    def _calculate_weighted_progress(self) -> float:
        """根據步驟權重計算進度"""
        if self.current_step >= len(self.analysis_steps):
            return 1.0

        # 如果是最後一步，返回100%
        if self.current_step == len(self.analysis_steps) - 1:
            return 1.0

        completed_weight = sum(step["weight"] for step in self.analysis_steps[:self.current_step])
        total_weight = sum(step["weight"] for step in self.analysis_steps)

        return min(completed_weight / total_weight, 1.0)

    def _estimate_remaining_time(self, progress: float, elapsed_time: float) -> float:
        """智能預估剩餘時間"""
        if progress <= 0:
            return self.estimated_duration

        # 如果進度超過20%，使用實際進度來預估
        if progress > 0.2:
            estimated_total = elapsed_time / progress
            return max(estimated_total - elapsed_time, 0)
        else:
            # 前期使用預估時間
            return max(self.estimated_duration - elapsed_time, 0)
    
    def _detect_step_from_message(self, message: str) -> Optional[int]:
        """根據訊息內容智能檢測當前步驟"""
        message_lower = message.lower()

        # 開始分析階段 - 只匹配最初的開始訊息
        if "🚀 開始股票分析" in message:
            return 0
        # 數據驗證階段
        elif "驗證" in message or "預獲取" in message or "數據準備" in message:
            return 0
        # 環境準備階段
        elif "環境" in message or "api" in message_lower or "密鑰" in message:
            return 1
        # 成本預估階段
        elif "成本" in message or "預估" in message:
            return 2
        # 參數配置階段
        elif "配置" in message or "參數" in message:
            return 3
        # 引擎初始化階段
        elif "初始化" in message or "引擎" in message:
            return 4
        # 分析師工作階段 - 根據分析師名稱和工具調用匹配
        elif any(analyst_name in message for analyst_name in ["市場分析師", "基本面分析師", "技術分析師", "情緒分析師", "風險分析師"]):
            # 找到對應的分析師步驟
            for i, step in enumerate(self.analysis_steps):
                if "分析師" in step["name"]:
                    # 檢查訊息中是否包含對應的分析師類型
                    if "市場" in message and "市場" in step["name"]:
                        return i
                    elif "基本面" in message and "基本面" in step["name"]:
                        return i
                    elif "技術" in message and "技術" in step["name"]:
                        return i
                    elif "情緒" in message and "情緒" in step["name"]:
                        return i
                    elif "風險" in message and "風險" in step["name"]:
                        return i
        # 工具調用階段 - 檢測分析師正在使用工具
        elif "工具調用" in message or "正在調用" in message or "tool" in message.lower():
            # 如果當前步驟是分析師步驟，保持當前步驟
            if self.current_step < len(self.analysis_steps) and "分析師" in self.analysis_steps[self.current_step]["name"]:
                return self.current_step
        # 模塊開始/完成日誌
        elif "模塊開始" in message or "模塊完成" in message:
            # 從日誌中提取分析師類型
            if "market_analyst" in message or "market" in message or "市場" in message:
                for i, step in enumerate(self.analysis_steps):
                    if "市場" in step["name"]:
                        return i
            elif "fundamentals_analyst" in message or "fundamentals" in message or "基本面" in message:
                for i, step in enumerate(self.analysis_steps):
                    if "基本面" in step["name"]:
                        return i
            elif "technical_analyst" in message or "technical" in message or "技術" in message:
                for i, step in enumerate(self.analysis_steps):
                    if "技術" in step["name"]:
                        return i
            elif "sentiment_analyst" in message or "sentiment" in message or "情緒" in message:
                for i, step in enumerate(self.analysis_steps):
                    if "情緒" in step["name"]:
                        return i
            elif "risk_analyst" in message or "risk" in message or "風險" in message:
                for i, step in enumerate(self.analysis_steps):
                    if "風險" in step["name"]:
                        return i
            elif "graph_signal_processing" in message or "signal" in message or "信號" in message:
                for i, step in enumerate(self.analysis_steps):
                    if "信號" in step["name"] or "整理" in step["name"]:
                        return i
        # 結果整理階段
        elif "整理" in message or "結果" in message:
            return len(self.analysis_steps) - 1
        # 完成階段
        elif "完成" in message or "成功" in message:
            return len(self.analysis_steps) - 1

        return None
    
    def get_current_step_info(self) -> Dict:
        """獲取當前步驟信息"""
        if self.current_step < len(self.analysis_steps):
            return self.analysis_steps[self.current_step]
        return {"name": "完成", "description": "分析已完成", "weight": 0}

    def get_progress_percentage(self) -> float:
        """獲取進度百分比"""
        return self._calculate_weighted_progress() * 100

    def get_elapsed_time(self) -> float:
        """獲取已用時間"""
        return time.time() - self.start_time

    def get_estimated_total_time(self) -> float:
        """獲取預估總時間"""
        return self.estimated_duration

    def format_time(self, seconds: float) -> str:
        """格式化時間顯示"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分鐘"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小時"

class SmartStreamlitProgressDisplay:
    """智能Streamlit進度顯示組件"""

    def __init__(self, container):
        self.container = container
        self.progress_bar = None
        self.status_text = None
        self.step_info = None
        self.time_info = None
        self.setup_display()

    def setup_display(self):
        """設置顯示組件"""
        with self.container:
            st.markdown("### 📊 分析進度")
            self.progress_bar = st.progress(0)
            self.status_text = st.empty()
            self.step_info = st.empty()
            self.time_info = st.empty()

    def update(self, message: str, current_step: int, total_steps: int, progress: float, elapsed_time: float, remaining_time: float):
        """更新顯示"""
        # 更新進度條
        self.progress_bar.progress(progress)

        # 更新狀態文本
        self.status_text.markdown(f"**當前狀態:** 📋 {message}")

        # 更新步驟信息
        step_text = f"**進度:** 第 {current_step + 1} 步，共 {total_steps} 步 ({progress:.1%})"
        self.step_info.markdown(step_text)

        # 更新時間信息
        time_text = f"**已用時間:** {self._format_time(elapsed_time)}"
        if remaining_time > 0:
            time_text += f" | **預計剩餘:** {self._format_time(remaining_time)}"

        self.time_info.markdown(time_text)
    
    def _format_time(self, seconds: float) -> str:
        """格式化時間顯示"""
        if seconds < 60:
            return f"{seconds:.1f}秒"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}分鐘"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}小時"
    
    def clear(self):
        """清除顯示"""
        self.container.empty()

def create_smart_progress_callback(display: SmartStreamlitProgressDisplay, analysts: List[str], research_depth: int, llm_provider: str) -> Callable:
    """創建智能進度回調函數"""
    tracker = SmartAnalysisProgressTracker(analysts, research_depth, llm_provider)

    def callback(message: str, step: Optional[int] = None, total_steps: Optional[int] = None):
        # 如果明確指定了步驟和總步驟，使用舊的固定模式（兼容性）
        if step is not None and total_steps is not None and total_steps == 10:
            # 兼容舊的10步模式，使用智能時間預估
            progress = step / max(total_steps - 1, 1) if total_steps > 1 else 1.0
            progress = min(progress, 1.0)
            elapsed_time = tracker.get_elapsed_time()
            remaining_time = tracker._estimate_remaining_time(progress, elapsed_time)
            display.update(message, step, total_steps, progress, elapsed_time, remaining_time)
        else:
            # 使用新的智能跟蹤模式
            tracker.update(message, step, total_steps)
            current_step = tracker.current_step
            total_steps_count = len(tracker.analysis_steps)
            progress = tracker.get_progress_percentage() / 100
            elapsed_time = tracker.get_elapsed_time()
            remaining_time = tracker._estimate_remaining_time(progress, elapsed_time)
            display.update(message, current_step, total_steps_count, progress, elapsed_time, remaining_time)

    return callback

# 向後兼容的函數
def create_progress_callback(display, analysts=None, research_depth=2, llm_provider="openai") -> Callable:
    """創建進度回調函數（向後兼容）"""
    if hasattr(display, '__class__') and 'Smart' in display.__class__.__name__:
        return create_smart_progress_callback(display, analysts or ['market', 'fundamentals'], research_depth, llm_provider)
    else:
        # 舊版本兼容
        tracker = SmartAnalysisProgressTracker(analysts or ['market', 'fundamentals'], research_depth, llm_provider)

        def callback(message: str, step: Optional[int] = None, total_steps: Optional[int] = None):
            if step is not None and total_steps is not None:
                progress = step / max(total_steps - 1, 1) if total_steps > 1 else 1.0
                progress = min(progress, 1.0)
                elapsed_time = tracker.get_elapsed_time()
                display.update(message, step, total_steps, progress, elapsed_time)
            else:
                tracker.update(message, step, total_steps)
                current_step = tracker.current_step
                total_steps_count = len(tracker.analysis_steps)
                progress = tracker.get_progress_percentage() / 100
                elapsed_time = tracker.get_elapsed_time()
                display.update(message, current_step, total_steps_count, progress, elapsed_time)

        return callback
