#!/usr/bin/env python3
"""
配置管理器
管理API密鑰、模型配置、費率設定等
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from dotenv import load_dotenv

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('config')

try:
    from .mongodb_storage import MongoDBStorage
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoDBStorage = None


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str  # 供應商：openai, anthropic
    model_name: str  # 模型名稱
    api_key: str  # API密鑰
    base_url: Optional[str] = None  # 自訂 API 位址
    max_tokens: int = 4000  # 最大token數
    temperature: float = 0.7  # 溫度參數
    enabled: bool = True  # 是否啟用


@dataclass
class PricingConfig:
    """定價配置"""
    provider: str  # 供應商
    model_name: str  # 模型名稱
    input_price_per_1k: float  # 輸入token價格（每1000個token）
    output_price_per_1k: float  # 輸出token價格（每1000個token）
    currency: str = "USD"  # 貨幣單位


@dataclass
class UsageRecord:
    """使用記錄"""
    timestamp: str  # 時間戳
    provider: str  # 供應商
    model_name: str  # 模型名稱
    input_tokens: int  # 輸入token數
    output_tokens: int  # 輸出token數
    cost: float  # 成本
    session_id: str  # 會話ID
    analysis_type: str  # 分析類型


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)

        self.models_file = self.config_dir / "models.json"
        self.pricing_file = self.config_dir / "pricing.json"
        self.usage_file = self.config_dir / "usage.json"
        self.settings_file = self.config_dir / "settings.json"

        # 載入.env 檔案（保持向後相容）
        self._load_env_file()

        # 初始化MongoDB儲存（如果可用）
        self.mongodb_storage = None
        self._init_mongodb_storage()

        self._init_default_configs()

    def _load_env_file(self):
        """載入.env 檔案（保持向後相容）"""
        # 嘗試從專案根目錄載入.env 檔案
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / ".env"

        if env_file.exists():
            load_dotenv(env_file, override=True)

    def _get_env_api_key(self, provider: str) -> str:
        """從環境變數取得API密鑰"""
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }

        env_key = env_key_map.get(provider.lower())
        if env_key:
            api_key = os.getenv(env_key, "")
            # 對OpenAI密鑰進行格式驗證（始終啟用）
            if provider.lower() == "openai" and api_key:
                if not self.validate_openai_api_key_format(api_key):
                    logger.warning(f"OpenAI API密鑰格式不正確，將被忽略: {api_key[:10]}...")
                    return ""
            return api_key
        return ""
    
    def validate_openai_api_key_format(self, api_key: str) -> bool:
        """
        驗證OpenAI API密鑰格式
        
        OpenAI API密鑰格式規則：
        1. 以 'sk-' 開頭
        2. 總長度通常為51個字元
        3. 包含字母、數字和可能的特殊字元
        
        Args:
            api_key: 要驗證的API密鑰
            
        Returns:
            bool: 格式是否正確
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # 檢查是否以 'sk-' 開頭
        if not api_key.startswith('sk-'):
            return False
        
        # 檢查長度（OpenAI密鑰通常為51個字元）
        if len(api_key) != 51:
            return False
        
        # 檢查格式：sk- 後面應該是48個字元的字母數字組合
        pattern = r'^sk-[A-Za-z0-9]{48}$'
        if not re.match(pattern, api_key):
            return False
        
        return True
    
    def _init_mongodb_storage(self):
        """初始化MongoDB儲存"""
        if not MONGODB_AVAILABLE:
            return

        # 檢查是否啟用MongoDB儲存
        use_mongodb = os.getenv("USE_MONGODB_STORAGE", "false").lower() == "true"
        if not use_mongodb:
            return
        
        try:
            connection_string = os.getenv("MONGODB_CONNECTION_STRING")
            database_name = os.getenv("MONGODB_DATABASE_NAME", "tradingagents")
            
            self.mongodb_storage = MongoDBStorage(
                connection_string=connection_string,
                database_name=database_name
            )
            
            if self.mongodb_storage.is_connected():
                logger.info("MongoDB儲存已啟用")
            else:
                self.mongodb_storage = None
                logger.warning("MongoDB連接失敗，將使用JSON 檔案儲存")

        except Exception as e:
            logger.error(f"MongoDB初始化失敗: {e}", exc_info=True)
            self.mongodb_storage = None

    def _init_default_configs(self):
        """初始化預設配置"""
        # 預設模型配置
        if not self.models_file.exists():
            default_models = [
                ModelConfig(
                    provider="openai",
                    model_name="gpt-3.5-turbo",
                    api_key="",
                    max_tokens=4000,
                    temperature=0.7,
                    enabled=True
                ),
                ModelConfig(
                    provider="openai",
                    model_name="gpt-4",
                    api_key="",
                    max_tokens=8000,
                    temperature=0.7,
                    enabled=False
                ),
                ModelConfig(
                    provider="anthropic",
                    model_name="claude-sonnet-4-6",
                    api_key="",
                    max_tokens=4000,
                    temperature=0.7,
                    enabled=False
                )
            ]
            self.save_models(default_models)
        
        # 預設定價配置
        if not self.pricing_file.exists():
            default_pricing = [
                # OpenAI定價 (美元，每千token) - 2025年最新價格
                # GPT-5系列 (2025年8月發布)
                PricingConfig("openai", "gpt-5", 0.00125, 0.01, "USD"),
                PricingConfig("openai", "gpt-5-mini", 0.00025, 0.002, "USD"),
                PricingConfig("openai", "gpt-5-nano", 0.00005, 0.0004, "USD"),

                # o系列推理模型
                PricingConfig("openai", "o1", 0.015, 0.06, "USD"),
                PricingConfig("openai", "o1-mini", 0.003, 0.012, "USD"),
                PricingConfig("openai", "o1-preview", 0.015, 0.06, "USD"),

                # GPT-4系列
                PricingConfig("openai", "gpt-4o", 0.0025, 0.01, "USD"),
                PricingConfig("openai", "gpt-4o-mini", 0.00015, 0.0006, "USD"),
                PricingConfig("openai", "gpt-4-turbo", 0.01, 0.03, "USD"),
                PricingConfig("openai", "gpt-4", 0.03, 0.06, "USD"),
                PricingConfig("openai", "gpt-3.5-turbo", 0.0005, 0.0015, "USD"),

                # Anthropic Claude定價 (美元，每千token)
                # Claude 4系列 (2025年最新)
                PricingConfig("anthropic", "claude-opus-4.1", 0.015, 0.075, "USD"),
                PricingConfig("anthropic", "claude-sonnet-4.5", 0.003, 0.015, "USD"),
                PricingConfig("anthropic", "claude-haiku-4.5", 0.001, 0.005, "USD"),
                PricingConfig("anthropic", "claude-opus-4", 0.015, 0.075, "USD"),
                PricingConfig("anthropic", "claude-sonnet-4", 0.003, 0.015, "USD"),
                PricingConfig("anthropic", "claude-haiku-4", 0.001, 0.005, "USD"),

                # Claude 3系列
                PricingConfig("anthropic", "claude-3-opus-20240229", 0.015, 0.075, "USD"),
                PricingConfig("anthropic", "claude-3-sonnet-20240229", 0.003, 0.015, "USD"),
                PricingConfig("anthropic", "claude-3-haiku-20240307", 0.00025, 0.00125, "USD"),
                PricingConfig("anthropic", "claude-3-5-sonnet-20241022", 0.003, 0.015, "USD"),
            ]
            self.save_pricing(default_pricing)
        
        # 預設設定
        if not self.settings_file.exists():
            # 匯入預設資料目錄配置
            import os
            default_data_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data")
            
            default_settings = {
                "default_provider": "openai",
                "default_model": "gpt-4o-mini",
                "enable_cost_tracking": True,
                "cost_alert_threshold": 100.0,
                "currency_preference": "USD",
                "auto_save_usage": True,
                "max_usage_records": 10000,
                "data_dir": default_data_dir,
                "cache_dir": os.path.join(default_data_dir, "cache"),
                "results_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "results"),
                "auto_create_dirs": True,
                "openai_enabled": True,
            }
            self.save_settings(default_settings)
    
    def load_models(self) -> List[ModelConfig]:
        """載入模型配置，優先使用.env中的API密鑰"""
        try:
            with open(self.models_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                models = [ModelConfig(**item) for item in data]

                # 取得設定
                settings = self.load_settings()
                openai_enabled = settings.get("openai_enabled", False)

                # 合併.env中的API密鑰（優先級更高）
                for model in models:
                    env_api_key = self._get_env_api_key(model.provider)
                    if env_api_key:
                        model.api_key = env_api_key
                        # 如果.env中有API密鑰，自動啟用該模型
                        if not model.enabled:
                            model.enabled = True
                    
                    # 特殊處理OpenAI模型
                    if model.provider.lower() == "openai":
                        # 檢查OpenAI是否在配置中啟用
                        if not openai_enabled:
                            model.enabled = False
                            logger.info(f"OpenAI模型已禁用: {model.model_name}")
                        # 如果有API密鑰但格式不正確，禁用模型（驗證始終啟用）
                        elif model.api_key and not self.validate_openai_api_key_format(model.api_key):
                            model.enabled = False
                            logger.warning(f"OpenAI模型因密鑰格式不正確而禁用: {model.model_name}")

                return models
        except Exception as e:
            logger.error(f"載入模型配置失敗: {e}")
            return []
    
    def save_models(self, models: List[ModelConfig]):
        """保存模型配置"""
        try:
            data = [asdict(model) for model in models]
            with open(self.models_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存模型配置失敗: {e}")
    
    def load_pricing(self) -> List[PricingConfig]:
        """載入定價配置"""
        try:
            with open(self.pricing_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [PricingConfig(**item) for item in data]
        except Exception as e:
            logger.error(f"載入定價配置失敗: {e}")
            return []
    
    def save_pricing(self, pricing: List[PricingConfig]):
        """保存定價配置"""
        try:
            data = [asdict(price) for price in pricing]
            with open(self.pricing_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存定價配置失敗: {e}")
    
    def load_usage_records(self) -> List[UsageRecord]:
        """載入使用記錄"""
        try:
            if not self.usage_file.exists():
                return []
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [UsageRecord(**item) for item in data]
        except Exception as e:
            logger.error(f"載入使用記錄失敗: {e}")
            return []
    
    def save_usage_records(self, records: List[UsageRecord]):
        """保存使用記錄"""
        try:
            data = [asdict(record) for record in records]
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存使用記錄失敗: {e}")
    
    def add_usage_record(self, provider: str, model_name: str, input_tokens: int,
                        output_tokens: int, session_id: str, analysis_type: str = "stock_analysis"):
        """新增使用記錄"""
        # 計算成本
        cost = self.calculate_cost(provider, model_name, input_tokens, output_tokens)
        
        record = UsageRecord(
            timestamp=datetime.now().isoformat(),
            provider=provider,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            session_id=session_id,
            analysis_type=analysis_type
        )
        
        # 優先使用MongoDB儲存
        if self.mongodb_storage and self.mongodb_storage.is_connected():
            success = self.mongodb_storage.save_usage_record(record)
            if success:
                return record
            else:
                logger.error("MongoDB保存失敗，回退到JSON 檔案儲存")

        # 回退到JSON 檔案儲存
        records = self.load_usage_records()
        records.append(record)
        
        # 限制記錄數量
        settings = self.load_settings()
        max_records = settings.get("max_usage_records", 10000)
        if len(records) > max_records:
            records = records[-max_records:]
        
        self.save_usage_records(records)
        return record
    
    def calculate_cost(self, provider: str, model_name: str, input_tokens: int, output_tokens: int) -> float:
        """計算使用成本"""
        pricing_configs = self.load_pricing()

        for pricing in pricing_configs:
            if pricing.provider == provider and pricing.model_name == model_name:
                input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
                output_cost = (output_tokens / 1000) * pricing.output_price_per_1k
                total_cost = input_cost + output_cost
                return round(total_cost, 6)

        # 只在找不到配置時輸出除錯資訊
        logger.warning(f"[calculate_cost] 未找到匹配的定價配置: {provider}/{model_name}")
        logger.debug("[calculate_cost] 可用的配置:")
        for pricing in pricing_configs:
            logger.debug(f"[calculate_cost]   - {pricing.provider}/{pricing.model_name}")

        return 0.0
    
    def load_settings(self) -> Dict[str, Any]:
        """載入設定，合併.env中的配置"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                # 如果設定檔案不存在，建立預設設定
                settings = {
                    "default_provider": "openai",
                    "default_model": "gpt-4o-mini",
                    "enable_cost_tracking": True,
                    "cost_alert_threshold": 100.0,
                    "currency_preference": "USD",
                    "auto_save_usage": True,
                    "max_usage_records": 10000,
                    "data_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data"),
                    "cache_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data", "cache"),
                    "results_dir": os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "results"),
                    "auto_create_dirs": True,
                    "openai_enabled": True,
                }
                self.save_settings(settings)
        except Exception as e:
            logger.error(f"載入設定失敗: {e}")
            settings = {}

        # 合併.env中的其他配置
        env_settings = {
            "finnhub_api_key": os.getenv("FINNHUB_API_KEY", ""),
            "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", ""),
            "log_level": os.getenv("TRADINGAGENTS_LOG_LEVEL", "INFO"),
            "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", ""),  # 資料目錄環境變數
            "cache_dir": os.getenv("TRADINGAGENTS_CACHE_DIR", ""),  # 快取目錄環境變數
        }

        # 新增OpenAI相關配置
        openai_enabled_env = os.getenv("OPENAI_ENABLED", "").lower()
        if openai_enabled_env in ["true", "false"]:
            env_settings["openai_enabled"] = openai_enabled_env == "true"

        # 只有當環境變數存在且不為空時才覆蓋
        for key, value in env_settings.items():
            # 對於布爾值，直接使用
            if isinstance(value, bool):
                settings[key] = value
            # 對於字串，只有非空時才覆蓋
            elif value != "" and value is not None:
                settings[key] = value

        return settings

    def get_env_config_status(self) -> Dict[str, Any]:
        """取得.env配置狀態"""
        return {
            "env_file_exists": (Path(__file__).parent.parent.parent / ".env").exists(),
            "api_keys": {
                "openai": bool(os.getenv("OPENAI_API_KEY")),
                "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                "finnhub": bool(os.getenv("FINNHUB_API_KEY")),
            },
            "other_configs": {
                "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
                "log_level": os.getenv("TRADINGAGENTS_LOG_LEVEL", "INFO"),
            }
        }

    def save_settings(self, settings: Dict[str, Any]):
        """保存設定"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存設定失敗: {e}")
    
    def get_enabled_models(self) -> List[ModelConfig]:
        """取得啟用的模型"""
        models = self.load_models()
        return [model for model in models if model.enabled and model.api_key]
    
    def get_model_by_name(self, provider: str, model_name: str) -> Optional[ModelConfig]:
        """根據名稱取得模型配置"""
        models = self.load_models()
        for model in models:
            if model.provider == provider and model.model_name == model_name:
                return model
        return None
    
    def get_usage_statistics(self, days: int = 30) -> Dict[str, Any]:
        """取得使用統計"""
        # 優先使用MongoDB取得統計
        if self.mongodb_storage and self.mongodb_storage.is_connected():
            try:
                # 從MongoDB取得基礎統計
                stats = self.mongodb_storage.get_usage_statistics(days)
                # 取得供應商統計
                provider_stats = self.mongodb_storage.get_provider_statistics(days)
                
                if stats:
                    stats["provider_stats"] = provider_stats
                    stats["records_count"] = stats.get("total_requests", 0)
                    return stats
            except Exception as e:
                logger.error(f"MongoDB統計取得失敗，回退到JSON 檔案: {e}")
        
        # 回退到JSON 檔案統計
        records = self.load_usage_records()
        
        # 過濾最近N天的記錄
        from datetime import datetime, timedelta

        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_records = []
        for record in records:
            try:
                record_date = datetime.fromisoformat(record.timestamp)
                if record_date >= cutoff_date:
                    recent_records.append(record)
            except Exception as e:
                continue
        
        # 統計資料
        total_cost = sum(record.cost for record in recent_records)
        total_input_tokens = sum(record.input_tokens for record in recent_records)
        total_output_tokens = sum(record.output_tokens for record in recent_records)
        
        # 按供應商統計
        provider_stats = {}
        for record in recent_records:
            if record.provider not in provider_stats:
                provider_stats[record.provider] = {
                    "cost": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "requests": 0
                }
            provider_stats[record.provider]["cost"] += record.cost
            provider_stats[record.provider]["input_tokens"] += record.input_tokens
            provider_stats[record.provider]["output_tokens"] += record.output_tokens
            provider_stats[record.provider]["requests"] += 1
        
        return {
            "period_days": days,
            "total_cost": round(total_cost, 4),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_requests": len(recent_records),
            "provider_stats": provider_stats,
            "records_count": len(recent_records)
        }
    
    def get_data_dir(self) -> str:
        """取得資料目錄路徑"""
        settings = self.load_settings()
        data_dir = settings.get("data_dir")
        if not data_dir:
            # 如果沒有配置，使用預設路徑
            data_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data")
        return data_dir

    def set_data_dir(self, data_dir: str):
        """設定資料目錄路徑"""
        settings = self.load_settings()
        settings["data_dir"] = data_dir
        # 同時更新快取目錄
        settings["cache_dir"] = os.path.join(data_dir, "cache")
        self.save_settings(settings)
        
        # 如果啟用自動建立目錄，則建立目錄
        if settings.get("auto_create_dirs", True):
            self.ensure_directories_exist()

    def ensure_directories_exist(self):
        """確保必要的目錄存在"""
        settings = self.load_settings()
        
        directories = [
            settings.get("data_dir"),
            settings.get("cache_dir"),
            settings.get("results_dir"),
            os.path.join(settings.get("data_dir", ""), "finnhub_data"),
            os.path.join(settings.get("data_dir", ""), "finnhub_data", "news_data"),
            os.path.join(settings.get("data_dir", ""), "finnhub_data", "insider_sentiment"),
            os.path.join(settings.get("data_dir", ""), "finnhub_data", "insider_transactions")
        ]
        
        for directory in directories:
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                    logger.info(f"建立目錄: {directory}")
                except Exception as e:
                    logger.error(f"建立目錄失敗 {directory}: {e}")
    
    def set_openai_enabled(self, enabled: bool):
        """設定OpenAI模型啟用狀態"""
        settings = self.load_settings()
        settings["openai_enabled"] = enabled
        self.save_settings(settings)
        logger.info(f"OpenAI模型啟用狀態已設定為: {enabled}")
    
    def is_openai_enabled(self) -> bool:
        """檢查OpenAI模型是否啟用"""
        settings = self.load_settings()
        return settings.get("openai_enabled", False)
    
    def get_openai_config_status(self) -> Dict[str, Any]:
        """取得OpenAI配置狀態"""
        openai_key = os.getenv("OPENAI_API_KEY", "")
        key_valid = self.validate_openai_api_key_format(openai_key) if openai_key else False
        
        return {
            "api_key_present": bool(openai_key),
            "api_key_valid_format": key_valid,
            "enabled": self.is_openai_enabled(),
            "models_available": self.is_openai_enabled() and key_valid,
            "api_key_preview": f"{openai_key[:10]}..." if openai_key else "未配置"
        }


class TokenTracker:
    """Token使用追蹤器"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def track_usage(self, provider: str, model_name: str, input_tokens: int,
                   output_tokens: int, session_id: str = None, analysis_type: str = "stock_analysis"):
        """追蹤Token使用"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 檢查是否啟用成本追蹤
        settings = self.config_manager.load_settings()
        cost_tracking_enabled = settings.get("enable_cost_tracking", True)

        if not cost_tracking_enabled:
            return None

        # 新增使用記錄
        record = self.config_manager.add_usage_record(
            provider=provider,
            model_name=model_name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            session_id=session_id,
            analysis_type=analysis_type
        )

        # 檢查成本警告
        if record:
            self._check_cost_alert(record.cost)

        return record

    def _check_cost_alert(self, current_cost: float):
        """檢查成本警告"""
        settings = self.config_manager.load_settings()
        threshold = settings.get("cost_alert_threshold", 100.0)

        # 取得今日總成本
        today_stats = self.config_manager.get_usage_statistics(1)
        total_today = today_stats["total_cost"]

        if total_today >= threshold:
            logger.warning(f"成本警告: 今日成本已達到 ${total_today:.4f}，超過門檻 ${threshold}",
                          extra={'cost': total_today, 'threshold': threshold, 'event_type': 'cost_alert'})

    def get_session_cost(self, session_id: str) -> float:
        """取得會話成本"""
        records = self.config_manager.load_usage_records()
        session_cost = sum(record.cost for record in records if record.session_id == session_id)
        return session_cost

    def estimate_cost(self, provider: str, model_name: str, estimated_input_tokens: int,
                     estimated_output_tokens: int) -> float:
        """估算成本"""
        return self.config_manager.calculate_cost(
            provider, model_name, estimated_input_tokens, estimated_output_tokens
        )



# 全局配置管理器實例 - 使用專案根目錄的配置
def _get_project_config_dir():
    """取得專案根目錄的配置目錄"""
    # 從當前檔案位置推斷專案根目錄
    current_file = Path(__file__)  # tradingagents/config/config_manager.py
    project_root = current_file.parent.parent.parent  # 向上三級到專案根目錄
    return str(project_root / "config")

config_manager = ConfigManager(_get_project_config_dir())
token_tracker = TokenTracker(config_manager)
