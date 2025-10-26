#!/usr/bin/env python3
"""
異步進度跟蹤器
支持Redis和文件两種存储方式，前端定時轮詢獲取進度
"""

import json
import time
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import threading
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('async_progress')

def safe_serialize(obj):
    """安全序列化對象，處理不可序列化的類型"""
    # 特殊處理LangChain消息對象
    if hasattr(obj, '__class__') and 'Message' in obj.__class__.__name__:
        try:
            # 嘗試使用LangChain的序列化方法
            if hasattr(obj, 'dict'):
                return obj.dict()
            elif hasattr(obj, 'to_dict'):
                return obj.to_dict()
            else:
                # 手動提取消息內容
                return {
                    'type': obj.__class__.__name__,
                    'content': getattr(obj, 'content', str(obj)),
                    'additional_kwargs': getattr(obj, 'additional_kwargs', {}),
                    'response_metadata': getattr(obj, 'response_metadata', {})
                }
        except Exception:
            # 如果所有方法都失败，返回字符串表示
            return {
                'type': obj.__class__.__name__,
                'content': str(obj)
            }
    
    if hasattr(obj, 'dict'):
        # Pydantic對象
        try:
            return obj.dict()
        except Exception:
            return str(obj)
    elif hasattr(obj, '__dict__'):
        # 普通對象，轉換為字典
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):  # 跳過私有屬性
                try:
                    json.dumps(value)  # 測試是否可序列化
                    result[key] = value
                except (TypeError, ValueError):
                    result[key] = safe_serialize(value)  # 遞歸處理
        return result
    elif isinstance(obj, (list, tuple)):
        return [safe_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: safe_serialize(value) for key, value in obj.items()}
    else:
        try:
            json.dumps(obj)  # 測試是否可序列化
            return obj
        except (TypeError, ValueError):
            return str(obj)  # 轉換為字符串

class AsyncProgressTracker:
    """異步進度跟蹤器"""
    
    def __init__(self, analysis_id: str, analysts: List[str], research_depth: int, llm_provider: str):
        self.analysis_id = analysis_id
        self.analysts = analysts
        self.research_depth = research_depth
        self.llm_provider = llm_provider
        self.start_time = time.time()
        
        # 生成分析步骤
        self.analysis_steps = self._generate_dynamic_steps()
        self.estimated_duration = self._estimate_total_duration()
        
        # 初始化狀態
        self.current_step = 0
        self.progress_data = {
            'analysis_id': analysis_id,
            'status': 'running',
            'current_step': 0,
            'total_steps': len(self.analysis_steps),
            'progress_percentage': 0.0,
            'current_step_name': self.analysis_steps[0]['name'],
            'current_step_description': self.analysis_steps[0]['description'],
            'elapsed_time': 0.0,
            'estimated_total_time': self.estimated_duration,
            'remaining_time': self.estimated_duration,
            'last_message': '準备開始分析...',
            'last_update': time.time(),
            'start_time': self.start_time,
            'steps': self.analysis_steps
        }
        
        # 嘗試初始化Redis，失败則使用文件
        self.redis_client = None
        self.use_redis = self._init_redis()
        
        if not self.use_redis:
            # 使用文件存储
            self.progress_file = f"./data/progress_{analysis_id}.json"
            os.makedirs(os.path.dirname(self.progress_file), exist_ok=True)
        
        # 保存初始狀態
        self._save_progress()
        
        logger.info(f"📊 [異步進度] 初始化完成: {analysis_id}, 存储方式: {'Redis' if self.use_redis else '文件'}")

        # 註冊到日誌系統進行自動進度更新
        try:
            from .progress_log_handler import register_analysis_tracker
            import threading

            # 使用超時機制避免死鎖
            def register_with_timeout():
                try:
                    register_analysis_tracker(self.analysis_id, self)
                    print(f"✅ [進度集成] 跟蹤器註冊成功: {self.analysis_id}")
                except Exception as e:
                    print(f"❌ [進度集成] 跟蹤器註冊失败: {e}")

            # 在單獨線程中註冊，避免阻塞主線程
            register_thread = threading.Thread(target=register_with_timeout, daemon=True)
            register_thread.start()
            register_thread.join(timeout=2.0)  # 2秒超時

            if register_thread.is_alive():
                print(f"⚠️ [進度集成] 跟蹤器註冊超時，繼续執行: {self.analysis_id}")

        except ImportError:
            logger.debug("📊 [異步進度] 日誌集成不可用")
        except Exception as e:
            print(f"❌ [進度集成] 跟蹤器註冊異常: {e}")
    
    def _init_redis(self) -> bool:
        """初始化Redis連接"""
        try:
            # 首先檢查REDIS_ENABLED環境變量
            redis_enabled_raw = os.getenv('REDIS_ENABLED', 'false')
            redis_enabled = redis_enabled_raw.lower()
            logger.info(f"🔍 [Redis檢查] REDIS_ENABLED原值='{redis_enabled_raw}' -> 處理後='{redis_enabled}'")

            if redis_enabled != 'true':
                logger.info(f"📊 [異步進度] Redis已禁用，使用文件存储")
                return False

            import redis

            # 從環境變量獲取Redis配置
            redis_host = os.getenv('REDIS_HOST', 'localhost')
            redis_port = int(os.getenv('REDIS_PORT', 6379))
            redis_password = os.getenv('REDIS_PASSWORD', None)
            redis_db = int(os.getenv('REDIS_DB', 0))

            # 創建Redis連接
            if redis_password:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    db=redis_db,
                    decode_responses=True
                )
            else:
                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True
                )

            # 測試連接
            self.redis_client.ping()
            logger.info(f"📊 [異步進度] Redis連接成功: {redis_host}:{redis_port}")
            return True
        except Exception as e:
            logger.warning(f"📊 [異步進度] Redis連接失败，使用文件存储: {e}")
            return False
    
    def _generate_dynamic_steps(self) -> List[Dict]:
        """根據分析師數量和研究深度動態生成分析步骤"""
        steps = [
            {"name": "📋 準备階段", "description": "驗證股票代碼，檢查數據源可用性", "weight": 0.05},
            {"name": "🔧 環境檢查", "description": "檢查API密鑰配置，確保數據獲取正常", "weight": 0.02},
            {"name": "💰 成本估算", "description": "根據分析深度預估API調用成本", "weight": 0.01},
            {"name": "⚙️ 參數設置", "description": "配置分析參數和AI模型選擇", "weight": 0.02},
            {"name": "🚀 啟動引擎", "description": "初始化AI分析引擎，準备開始分析", "weight": 0.05},
        ]

        # 為每個分析師添加專門的步骤
        analyst_base_weight = 0.6 / len(self.analysts)  # 60%的時間用於分析師工作
        for analyst in self.analysts:
            analyst_info = self._get_analyst_step_info(analyst)
            steps.append({
                "name": analyst_info["name"],
                "description": analyst_info["description"],
                "weight": analyst_base_weight
            })

        # 根據研究深度添加後续步骤
        if self.research_depth >= 2:
            # 標準和深度分析包含研究員辩論
            steps.extend([
                {"name": "📈 多头觀點", "description": "從乐觀角度分析投資機會和上涨潜力", "weight": 0.06},
                {"name": "📉 空头觀點", "description": "從谨慎角度分析投資風險和下跌可能", "weight": 0.06},
                {"name": "🤝 觀點整合", "description": "综合多空觀點，形成平衡的投資建议", "weight": 0.05},
            ])

        # 所有深度都包含交易決策
        steps.append({"name": "💡 投資建议", "description": "基於分析結果制定具體的买卖建议", "weight": 0.06})

        if self.research_depth >= 3:
            # 深度分析包含詳細風險評估
            steps.extend([
                {"name": "🔥 激進策略", "description": "評估高風險高收益的投資策略", "weight": 0.03},
                {"name": "🛡️ 保守策略", "description": "評估低風險穩健的投資策略", "weight": 0.03},
                {"name": "⚖️ 平衡策略", "description": "評估風險收益平衡的投資策略", "weight": 0.03},
                {"name": "🎯 風險控制", "description": "制定風險控制措施和止損策略", "weight": 0.04},
            ])
        else:
            # 快速和標準分析的簡化風險評估
            steps.append({"name": "⚠️ 風險提示", "description": "识別主要投資風險並提供風險提示", "weight": 0.05})

        # 最後的整理步骤
        steps.append({"name": "📊 生成報告", "description": "整理所有分析結果，生成最终投資報告", "weight": 0.04})

        # 重新平衡權重，確保总和為1.0
        total_weight = sum(step["weight"] for step in steps)
        for step in steps:
            step["weight"] = step["weight"] / total_weight

        return steps
    
    def _get_analyst_display_name(self, analyst: str) -> str:
        """獲取分析師顯示名稱（保留兼容性）"""
        name_map = {
            'market': '市場分析師',
            'fundamentals': '基本面分析師',
            'technical': '技術分析師',
            'sentiment': '情绪分析師',
            'risk': '風險分析師'
        }
        return name_map.get(analyst, f'{analyst}分析師')

    def _get_analyst_step_info(self, analyst: str) -> Dict[str, str]:
        """獲取分析師步骤信息（名稱和描述）"""
        analyst_info = {
            'market': {
                "name": "📊 市場分析",
                "description": "分析股價走势、成交量、市場熱度等市場表現"
            },
            'fundamentals': {
                "name": "💼 基本面分析",
                "description": "分析公司財務狀况、盈利能力、成長性等基本面"
            },
            'technical': {
                "name": "📈 技術分析",
                "description": "分析K線圖形、技術指標、支撑阻力等技術面"
            },
            'sentiment': {
                "name": "💭 情绪分析",
                "description": "分析市場情绪、投資者心理、舆論倾向等"
            },
            'news': {
                "name": "📰 新聞分析",
                "description": "分析相關新聞、公告、行業動態對股價的影響"
            },
            'social_media': {
                "name": "🌐 社交媒體",
                "description": "分析社交媒體討論、網絡熱度、散戶情绪等"
            },
            'risk': {
                "name": "⚠️ 風險分析",
                "description": "识別投資風險、評估風險等級、制定風控措施"
            }
        }

        return analyst_info.get(analyst, {
            "name": f"🔍 {analyst}分析",
            "description": f"進行{analyst}相關的專業分析"
        })
    
    def _estimate_total_duration(self) -> float:
        """根據分析師數量、研究深度、模型類型預估总時長（秒）"""
        # 基础時間（秒）- 環境準备、配置等
        base_time = 60
        
        # 每個分析師的實际耗時（基於真實測試數據）
        analyst_base_time = {
            1: 120,  # 快速分析：每個分析師約2分鐘
            2: 180,  # 基础分析：每個分析師約3分鐘  
            3: 240   # 標準分析：每個分析師約4分鐘
        }.get(self.research_depth, 180)
        
        analyst_time = len(self.analysts) * analyst_base_time
        
        # 模型速度影響（基於實际測試）
        model_multiplier = {
            'dashscope': 1.0,  # 阿里百炼速度適中
            'deepseek': 0.7,   # DeepSeek較快
            'google': 1.3      # Google較慢
        }.get(self.llm_provider, 1.0)
        
        # 研究深度額外影響（工具調用複雜度）
        depth_multiplier = {
            1: 0.8,  # 快速分析，較少工具調用
            2: 1.0,  # 基础分析，標準工具調用
            3: 1.3   # 標準分析，更多工具調用和推理
        }.get(self.research_depth, 1.0)
        
        total_time = (base_time + analyst_time) * model_multiplier * depth_multiplier
        return total_time
    
    def update_progress(self, message: str, step: Optional[int] = None):
        """更新進度狀態"""
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # 自動檢測步骤
        if step is None:
            step = self._detect_step_from_message(message)

        # 更新步骤（防止倒退）
        if step is not None and step >= self.current_step:
            self.current_step = step
            logger.debug(f"📊 [異步進度] 步骤推進到 {self.current_step + 1}/{len(self.analysis_steps)}")

        # 如果是完成消息，確保進度為100%
        if "分析完成" in message or "分析成功" in message or "✅ 分析完成" in message:
            self.current_step = len(self.analysis_steps) - 1
            logger.info(f"📊 [異步進度] 分析完成，設置為最终步骤")

        # 計算進度
        progress_percentage = self._calculate_weighted_progress() * 100
        remaining_time = self._estimate_remaining_time(progress_percentage / 100, elapsed_time)

        # 更新進度數據
        current_step_info = self.analysis_steps[self.current_step] if self.current_step < len(self.analysis_steps) else self.analysis_steps[-1]

        # 特殊處理工具調用消息，更新步骤描述但不改變步骤
        step_description = current_step_info['description']
        if "工具調用" in message:
            # 提取工具名稱並更新描述
            if "get_stock_market_data_unified" in message:
                step_description = "正在獲取市場數據和技術指標..."
            elif "get_stock_fundamentals_unified" in message:
                step_description = "正在獲取基本面數據和財務指標..."
            elif "get_china_stock_data" in message:
                step_description = "正在獲取A股市場數據..."
            elif "get_china_fundamentals" in message:
                step_description = "正在獲取A股基本面數據..."
            else:
                step_description = "正在調用分析工具..."
        elif "模塊開始" in message:
            step_description = f"開始{current_step_info['name']}..."
        elif "模塊完成" in message:
            step_description = f"{current_step_info['name']}已完成"

        self.progress_data.update({
            'current_step': self.current_step,
            'progress_percentage': progress_percentage,
            'current_step_name': current_step_info['name'],
            'current_step_description': step_description,
            'elapsed_time': elapsed_time,
            'remaining_time': remaining_time,
            'last_message': message,
            'last_update': current_time,
            'status': 'completed' if progress_percentage >= 100 else 'running'
        })

        # 保存到存储
        self._save_progress()

        # 詳細的更新日誌
        step_name = current_step_info.get('name', '未知')
        logger.info(f"📊 [進度更新] {self.analysis_id}: {message[:50]}...")
        logger.debug(f"📊 [進度詳情] 步骤{self.current_step + 1}/{len(self.analysis_steps)} ({step_name}), 進度{progress_percentage:.1f}%, 耗時{elapsed_time:.1f}s")
    
    def _detect_step_from_message(self, message: str) -> Optional[int]:
        """根據消息內容智能檢測當前步骤"""
        message_lower = message.lower()

        # 開始分析階段 - 只匹配最初的開始消息
        if "🚀 開始股票分析" in message:
            return 0
        # 數據驗證階段
        elif "驗證" in message or "預獲取" in message or "數據準备" in message:
            return 0
        # 環境準备階段
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
        # 模塊開始日誌 - 只在第一次開始時推進步骤
        elif "模塊開始" in message:
            # 從日誌中提取分析師類型，匹配新的步骤名稱
            if "market_analyst" in message or "market" in message:
                return self._find_step_by_keyword(["市場分析", "市場"])
            elif "fundamentals_analyst" in message or "fundamentals" in message:
                return self._find_step_by_keyword(["基本面分析", "基本面"])
            elif "technical_analyst" in message or "technical" in message:
                return self._find_step_by_keyword(["技術分析", "技術"])
            elif "sentiment_analyst" in message or "sentiment" in message:
                return self._find_step_by_keyword(["情绪分析", "情绪"])
            elif "news_analyst" in message or "news" in message:
                return self._find_step_by_keyword(["新聞分析", "新聞"])
            elif "social_media_analyst" in message or "social" in message:
                return self._find_step_by_keyword(["社交媒體", "社交"])
            elif "risk_analyst" in message or "risk" in message:
                return self._find_step_by_keyword(["風險分析", "風險"])
            elif "bull_researcher" in message or "bull" in message:
                return self._find_step_by_keyword(["多头觀點", "多头", "看涨"])
            elif "bear_researcher" in message or "bear" in message:
                return self._find_step_by_keyword(["空头觀點", "空头", "看跌"])
            elif "research_manager" in message:
                return self._find_step_by_keyword(["觀點整合", "整合"])
            elif "trader" in message:
                return self._find_step_by_keyword(["投資建议", "建议"])
            elif "risk_manager" in message:
                return self._find_step_by_keyword(["風險控制", "控制"])
            elif "graph_signal_processing" in message or "signal" in message:
                return self._find_step_by_keyword(["生成報告", "報告"])
        # 工具調用日誌 - 不推進步骤，只更新描述
        elif "工具調用" in message:
            # 保持當前步骤，不推進
            return None
        # 模塊完成日誌 - 推進到下一步
        elif "模塊完成" in message:
            # 模塊完成時，從當前步骤推進到下一步
            # 不再依賴模塊名稱，而是基於當前進度推進
            next_step = min(self.current_step + 1, len(self.analysis_steps) - 1)
            logger.debug(f"📊 [步骤推進] 模塊完成，從步骤{self.current_step}推進到步骤{next_step}")
            return next_step

        return None

    def _find_step_by_keyword(self, keywords) -> Optional[int]:
        """根據關键詞查找步骤索引"""
        if isinstance(keywords, str):
            keywords = [keywords]

        for i, step in enumerate(self.analysis_steps):
            for keyword in keywords:
                if keyword in step["name"]:
                    return i
        return None

    def _get_next_step(self, keyword: str) -> Optional[int]:
        """獲取指定步骤的下一步"""
        current_step_index = self._find_step_by_keyword(keyword)
        if current_step_index is not None:
            return min(current_step_index + 1, len(self.analysis_steps) - 1)
        return None

    def _calculate_weighted_progress(self) -> float:
        """根據步骤權重計算進度"""
        if self.current_step >= len(self.analysis_steps):
            return 1.0

        # 如果是最後一步，返回100%
        if self.current_step == len(self.analysis_steps) - 1:
            return 1.0

        completed_weight = sum(step["weight"] for step in self.analysis_steps[:self.current_step])
        total_weight = sum(step["weight"] for step in self.analysis_steps)

        return min(completed_weight / total_weight, 1.0)
    
    def _estimate_remaining_time(self, progress: float, elapsed_time: float) -> float:
        """基於总預估時間計算剩余時間"""
        # 如果進度已完成，剩余時間為0
        if progress >= 1.0:
            return 0.0

        # 使用簡單而準確的方法：总預估時間 - 已花費時間
        remaining = max(self.estimated_duration - elapsed_time, 0)

        # 如果已經超過預估時間，根據當前進度動態調整
        if remaining <= 0 and progress > 0:
            # 基於當前進度重新估算总時間，然後計算剩余
            estimated_total = elapsed_time / progress
            remaining = max(estimated_total - elapsed_time, 0)

        return remaining
    
    def _save_progress(self):
        """保存進度到存储"""
        try:
            current_step_name = self.progress_data.get('current_step_name', '未知')
            progress_pct = self.progress_data.get('progress_percentage', 0)
            status = self.progress_data.get('status', 'running')

            if self.use_redis:
                # 保存到Redis（安全序列化）
                key = f"progress:{self.analysis_id}"
                safe_data = safe_serialize(self.progress_data)
                data_json = json.dumps(safe_data, ensure_ascii=False)
                self.redis_client.setex(key, 3600, data_json)  # 1小時過期

                logger.info(f"📊 [Redis寫入] {self.analysis_id} -> {status} | {current_step_name} | {progress_pct:.1f}%")
                logger.debug(f"📊 [Redis詳情] 键: {key}, 數據大小: {len(data_json)} 字節")
            else:
                # 保存到文件（安全序列化）
                safe_data = safe_serialize(self.progress_data)
                with open(self.progress_file, 'w', encoding='utf-8') as f:
                    json.dump(safe_data, f, ensure_ascii=False, indent=2)

                logger.info(f"📊 [文件寫入] {self.analysis_id} -> {status} | {current_step_name} | {progress_pct:.1f}%")
                logger.debug(f"📊 [文件詳情] 路徑: {self.progress_file}")

        except Exception as e:
            logger.error(f"📊 [異步進度] 保存失败: {e}")
            # 嘗試备用存储方式
            try:
                if self.use_redis:
                    # Redis失败，嘗試文件存储
                    logger.warning(f"📊 [異步進度] Redis保存失败，嘗試文件存储")
                    backup_file = f"./data/progress_{self.analysis_id}.json"
                    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
                    safe_data = safe_serialize(self.progress_data)
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(safe_data, f, ensure_ascii=False, indent=2)
                    logger.info(f"📊 [备用存储] 文件保存成功: {backup_file}")
                else:
                    # 文件存储失败，嘗試簡化數據
                    logger.warning(f"📊 [異步進度] 文件保存失败，嘗試簡化數據")
                    simplified_data = {
                        'analysis_id': self.analysis_id,
                        'status': self.progress_data.get('status', 'unknown'),
                        'progress_percentage': self.progress_data.get('progress_percentage', 0),
                        'last_message': str(self.progress_data.get('last_message', '')),
                        'last_update': self.progress_data.get('last_update', time.time())
                    }
                    backup_file = f"./data/progress_{self.analysis_id}.json"
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(simplified_data, f, ensure_ascii=False, indent=2)
                    logger.info(f"📊 [备用存储] 簡化數據保存成功: {backup_file}")
            except Exception as backup_e:
                logger.error(f"📊 [異步進度] 备用存储也失败: {backup_e}")
    
    def get_progress(self) -> Dict[str, Any]:
        """獲取當前進度"""
        return self.progress_data.copy()
    
    def mark_completed(self, message: str = "分析完成", results: Any = None):
        """標記分析完成"""
        self.update_progress(message)
        self.progress_data['status'] = 'completed'
        self.progress_data['progress_percentage'] = 100.0
        self.progress_data['remaining_time'] = 0.0

        # 保存分析結果（安全序列化）
        if results is not None:
            try:
                self.progress_data['raw_results'] = safe_serialize(results)
                logger.info(f"📊 [異步進度] 保存分析結果: {self.analysis_id}")
            except Exception as e:
                logger.warning(f"📊 [異步進度] 結果序列化失败: {e}")
                self.progress_data['raw_results'] = str(results)  # 最後的fallback

        self._save_progress()
        logger.info(f"📊 [異步進度] 分析完成: {self.analysis_id}")

        # 從日誌系統註銷
        try:
            from .progress_log_handler import unregister_analysis_tracker
            unregister_analysis_tracker(self.analysis_id)
        except ImportError:
            pass
    
    def mark_failed(self, error_message: str):
        """標記分析失败"""
        self.progress_data['status'] = 'failed'
        self.progress_data['last_message'] = f"分析失败: {error_message}"
        self.progress_data['last_update'] = time.time()
        self._save_progress()
        logger.error(f"📊 [異步進度] 分析失败: {self.analysis_id}, 錯誤: {error_message}")

        # 從日誌系統註銷
        try:
            from .progress_log_handler import unregister_analysis_tracker
            unregister_analysis_tracker(self.analysis_id)
        except ImportError:
            pass

def get_progress_by_id(analysis_id: str) -> Optional[Dict[str, Any]]:
    """根據分析ID獲取進度"""
    try:
        # 檢查REDIS_ENABLED環境變量
        redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'

        # 如果Redis啟用，先嘗試Redis
        if redis_enabled:
            try:
                import redis

                # 從環境變量獲取Redis配置
                redis_host = os.getenv('REDIS_HOST', 'localhost')
                redis_port = int(os.getenv('REDIS_PORT', 6379))
                redis_password = os.getenv('REDIS_PASSWORD', None)
                redis_db = int(os.getenv('REDIS_DB', 0))

                # 創建Redis連接
                if redis_password:
                    redis_client = redis.Redis(
                        host=redis_host,
                        port=redis_port,
                        password=redis_password,
                        db=redis_db,
                        decode_responses=True
                    )
                else:
                    redis_client = redis.Redis(
                        host=redis_host,
                        port=redis_port,
                        db=redis_db,
                        decode_responses=True
                    )

                key = f"progress:{analysis_id}"
                data = redis_client.get(key)
                if data:
                    return json.loads(data)
            except Exception as e:
                logger.debug(f"📊 [異步進度] Redis讀取失败: {e}")

        # 嘗試文件
        progress_file = f"./data/progress_{analysis_id}.json"
        if os.path.exists(progress_file):
            with open(progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return None
    except Exception as e:
        logger.error(f"📊 [異步進度] 獲取進度失败: {analysis_id}, 錯誤: {e}")
        return None

def format_time(seconds: float) -> str:
    """格式化時間顯示"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}分鐘"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}小時"


def get_latest_analysis_id() -> Optional[str]:
    """獲取最新的分析ID"""
    try:
        # 檢查REDIS_ENABLED環境變量
        redis_enabled = os.getenv('REDIS_ENABLED', 'false').lower() == 'true'

        # 如果Redis啟用，先嘗試從Redis獲取
        if redis_enabled:
            try:
                import redis

                # 從環境變量獲取Redis配置
                redis_host = os.getenv('REDIS_HOST', 'localhost')
                redis_port = int(os.getenv('REDIS_PORT', 6379))
                redis_password = os.getenv('REDIS_PASSWORD', None)
                redis_db = int(os.getenv('REDIS_DB', 0))

                # 創建Redis連接
                if redis_password:
                    redis_client = redis.Redis(
                        host=redis_host,
                        port=redis_port,
                        password=redis_password,
                        db=redis_db,
                        decode_responses=True
                    )
                else:
                    redis_client = redis.Redis(
                        host=redis_host,
                        port=redis_port,
                        db=redis_db,
                        decode_responses=True
                    )

                # 獲取所有progress键
                keys = redis_client.keys("progress:*")
                if not keys:
                    return None

                # 獲取每個键的數據，找到最新的
                latest_time = 0
                latest_id = None

                for key in keys:
                    try:
                        data = redis_client.get(key)
                        if data:
                            progress_data = json.loads(data)
                            last_update = progress_data.get('last_update', 0)
                            if last_update > latest_time:
                                latest_time = last_update
                                # 從键名中提取analysis_id (去掉"progress:"前缀)
                                latest_id = key.replace('progress:', '')
                    except Exception:
                        continue

                if latest_id:
                    logger.info(f"📊 [恢複分析] 找到最新分析ID: {latest_id}")
                    return latest_id

            except Exception as e:
                logger.debug(f"📊 [恢複分析] Redis查找失败: {e}")

        # 如果Redis失败或未啟用，嘗試從文件查找
        data_dir = Path("data")
        if data_dir.exists():
            progress_files = list(data_dir.glob("progress_*.json"))
            if progress_files:
                # 按修改時間排序，獲取最新的
                latest_file = max(progress_files, key=lambda f: f.stat().st_mtime)
                # 從文件名提取analysis_id
                filename = latest_file.name
                if filename.startswith("progress_") and filename.endswith(".json"):
                    analysis_id = filename[9:-5]  # 去掉前缀和後缀
                    logger.debug(f"📊 [恢複分析] 從文件找到最新分析ID: {analysis_id}")
                    return analysis_id

        return None
    except Exception as e:
        logger.error(f"📊 [恢複分析] 獲取最新分析ID失败: {e}")
        return None
