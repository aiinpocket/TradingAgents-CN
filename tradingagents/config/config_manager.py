#!/usr/bin/env python3
"""
配置管理器
管理API密鑰、模型配置、費率設置等
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from dotenv import load_dotenv

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')

try:
    from .mongodb_storage import MongoDBStorage
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    MongoDBStorage = None


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str  # 供應商：openai, google, anthropic, etc.
    model_name: str  # 模型名稱
    api_key: str  # API密鑰
    base_url: Optional[str] = None  # 自定義API地址
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
    currency: str = "CNY"  # 貨币單位


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

        # 加載.env文件（保持向後兼容）
        self._load_env_file()

        # 初始化MongoDB存储（如果可用）
        self.mongodb_storage = None
        self._init_mongodb_storage()

        self._init_default_configs()

    def _load_env_file(self):
        """加載.env文件（保持向後兼容）"""
        # 嘗試從項目根目錄加載.env文件
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / ".env"

        if env_file.exists():
            load_dotenv(env_file, override=True)

    def _get_env_api_key(self, provider: str) -> str:
        """從環境變量獲取API密鑰"""
        env_key_map = {
            "openai": "OPENAI_API_KEY",
            "google": "GOOGLE_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }

        env_key = env_key_map.get(provider.lower())
        if env_key:
            api_key = os.getenv(env_key, "")
            # 對OpenAI密鑰進行格式驗證（始终啟用）
            if provider.lower() == "openai" and api_key:
                if not self.validate_openai_api_key_format(api_key):
                    logger.warning(f"⚠️ OpenAI API密鑰格式不正確，将被忽略: {api_key[:10]}...")
                    return ""
            return api_key
        return ""
    
    def validate_openai_api_key_format(self, api_key: str) -> bool:
        """
        驗證OpenAI API密鑰格式
        
        OpenAI API密鑰格式規則：
        1. 以 'sk-' 開头
        2. 总長度通常為51個字符
        3. 包含字母、數字和可能的特殊字符
        
        Args:
            api_key: 要驗證的API密鑰
            
        Returns:
            bool: 格式是否正確
        """
        if not api_key or not isinstance(api_key, str):
            return False
        
        # 檢查是否以 'sk-' 開头
        if not api_key.startswith('sk-'):
            return False
        
        # 檢查長度（OpenAI密鑰通常為51個字符）
        if len(api_key) != 51:
            return False
        
        # 檢查格式：sk- 後面應该是48個字符的字母數字組合
        pattern = r'^sk-[A-Za-z0-9]{48}$'
        if not re.match(pattern, api_key):
            return False
        
        return True
    
    def _init_mongodb_storage(self):
        """初始化MongoDB存储"""
        if not MONGODB_AVAILABLE:
            return
        
        # 檢查是否啟用MongoDB存储
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
                logger.info("✅ MongoDB存储已啟用")
            else:
                self.mongodb_storage = None
                logger.warning("⚠️ MongoDB連接失败，将使用JSON文件存储")

        except Exception as e:
            logger.error(f"❌ MongoDB初始化失败: {e}", exc_info=True)
            self.mongodb_storage = None

    def _init_default_configs(self):
        """初始化默認配置"""
        # 默認模型配置
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
                    provider="google",
                    model_name="gemini-2.5-pro",
                    api_key="",
                    max_tokens=4000,
                    temperature=0.7,
                    enabled=False
                )
            ]
            self.save_models(default_models)
        
        # 默認定價配置
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

                # Google定價 (美元，每千token)
                # Gemini 2.5系列 (2025年最新)
                PricingConfig("google", "gemini-2.5-pro", 0.00125, 0.01, "USD"),
                PricingConfig("google", "gemini-2.5-pro-002", 0.00125, 0.01, "USD"),
                PricingConfig("google", "gemini-2.5-flash", 0.0003, 0.0025, "USD"),
                PricingConfig("google", "gemini-2.5-flash-002", 0.0003, 0.0025, "USD"),
                PricingConfig("google", "gemini-2.5-flash-preview-05-20", 0.0003, 0.0025, "USD"),
                PricingConfig("google", "gemini-2.5-flash-lite", 0.0001, 0.0004, "USD"),
                PricingConfig("google", "gemini-2.5-flash-lite-preview-06-17", 0.0001, 0.0004, "USD"),

                # Gemini 2.0系列
                PricingConfig("google", "gemini-2.0-flash", 0.00025, 0.0005, "USD"),
                PricingConfig("google", "gemini-2.0-flash-lite", 0.0001, 0.0004, "USD"),
                PricingConfig("google", "gemini-2.0-pro-experimental", 0.00125, 0.01, "USD"),

                # Gemini 1.5系列
                PricingConfig("google", "gemini-1.5-pro", 0.00025, 0.0005, "USD"),
                PricingConfig("google", "gemini-1.5-flash", 0.00025, 0.0005, "USD"),
                PricingConfig("google", "gemini-pro", 0.00025, 0.0005, "USD"),
                PricingConfig("google", "gemini-pro-vision", 0.00025, 0.0005, "USD"),

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
        
        # 默認設置
        if not self.settings_file.exists():
            # 導入默認數據目錄配置
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
        """加載模型配置，優先使用.env中的API密鑰"""
        try:
            with open(self.models_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                models = [ModelConfig(**item) for item in data]

                # 獲取設置
                settings = self.load_settings()
                openai_enabled = settings.get("openai_enabled", False)

                # 合並.env中的API密鑰（優先級更高）
                for model in models:
                    env_api_key = self._get_env_api_key(model.provider)
                    if env_api_key:
                        model.api_key = env_api_key
                        # 如果.env中有API密鑰，自動啟用该模型
                        if not model.enabled:
                            model.enabled = True
                    
                    # 特殊處理OpenAI模型
                    if model.provider.lower() == "openai":
                        # 檢查OpenAI是否在配置中啟用
                        if not openai_enabled:
                            model.enabled = False
                            logger.info(f"🔒 OpenAI模型已禁用: {model.model_name}")
                        # 如果有API密鑰但格式不正確，禁用模型（驗證始终啟用）
                        elif model.api_key and not self.validate_openai_api_key_format(model.api_key):
                            model.enabled = False
                            logger.warning(f"⚠️ OpenAI模型因密鑰格式不正確而禁用: {model.model_name}")

                return models
        except Exception as e:
            logger.error(f"加載模型配置失败: {e}")
            return []
    
    def save_models(self, models: List[ModelConfig]):
        """保存模型配置"""
        try:
            data = [asdict(model) for model in models]
            with open(self.models_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存模型配置失败: {e}")
    
    def load_pricing(self) -> List[PricingConfig]:
        """加載定價配置"""
        try:
            with open(self.pricing_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [PricingConfig(**item) for item in data]
        except Exception as e:
            logger.error(f"加載定價配置失败: {e}")
            return []
    
    def save_pricing(self, pricing: List[PricingConfig]):
        """保存定價配置"""
        try:
            data = [asdict(price) for price in pricing]
            with open(self.pricing_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存定價配置失败: {e}")
    
    def load_usage_records(self) -> List[UsageRecord]:
        """加載使用記錄"""
        try:
            if not self.usage_file.exists():
                return []
            with open(self.usage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [UsageRecord(**item) for item in data]
        except Exception as e:
            logger.error(f"加載使用記錄失败: {e}")
            return []
    
    def save_usage_records(self, records: List[UsageRecord]):
        """保存使用記錄"""
        try:
            data = [asdict(record) for record in records]
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存使用記錄失败: {e}")
    
    def add_usage_record(self, provider: str, model_name: str, input_tokens: int,
                        output_tokens: int, session_id: str, analysis_type: str = "stock_analysis"):
        """添加使用記錄"""
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
        
        # 優先使用MongoDB存储
        if self.mongodb_storage and self.mongodb_storage.is_connected():
            success = self.mongodb_storage.save_usage_record(record)
            if success:
                return record
            else:
                logger.error(f"⚠️ MongoDB保存失败，回退到JSON文件存储")
        
        # 回退到JSON文件存储
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

        # 只在找不到配置時輸出調試信息
        logger.warning(f"⚠️ [calculate_cost] 未找到匹配的定價配置: {provider}/{model_name}")
        logger.debug(f"⚠️ [calculate_cost] 可用的配置:")
        for pricing in pricing_configs:
            logger.debug(f"⚠️ [calculate_cost]   - {pricing.provider}/{pricing.model_name}")

        return 0.0
    
    def load_settings(self) -> Dict[str, Any]:
        """加載設置，合並.env中的配置"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                # 如果設置文件不存在，創建默認設置
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
            logger.error(f"加載設置失败: {e}")
            settings = {}

        # 合並.env中的其他配置
        env_settings = {
            "finnhub_api_key": os.getenv("FINNHUB_API_KEY", ""),
            "reddit_client_id": os.getenv("REDDIT_CLIENT_ID", ""),
            "reddit_client_secret": os.getenv("REDDIT_CLIENT_SECRET", ""),
            "reddit_user_agent": os.getenv("REDDIT_USER_AGENT", ""),
            "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", ""),
            "log_level": os.getenv("TRADINGAGENTS_LOG_LEVEL", "INFO"),
            "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", ""),  # 數據目錄環境變量
            "cache_dir": os.getenv("TRADINGAGENTS_CACHE_DIR", ""),  # 緩存目錄環境變量
        }

        # 添加OpenAI相關配置
        openai_enabled_env = os.getenv("OPENAI_ENABLED", "").lower()
        if openai_enabled_env in ["true", "false"]:
            env_settings["openai_enabled"] = openai_enabled_env == "true"

        # 只有當環境變量存在且不為空時才覆蓋
        for key, value in env_settings.items():
            # 對於布爾值，直接使用
            if isinstance(value, bool):
                settings[key] = value
            # 對於字符串，只有非空時才覆蓋
            elif value != "" and value is not None:
                settings[key] = value

        return settings

    def get_env_config_status(self) -> Dict[str, Any]:
        """獲取.env配置狀態"""
        return {
            "env_file_exists": (Path(__file__).parent.parent.parent / ".env").exists(),
            "api_keys": {
                "openai": bool(os.getenv("OPENAI_API_KEY")),
                "google": bool(os.getenv("GOOGLE_API_KEY")),
                "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
                "finnhub": bool(os.getenv("FINNHUB_API_KEY")),
            },
            "other_configs": {
                "reddit_configured": bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")),
                "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
                "log_level": os.getenv("TRADINGAGENTS_LOG_LEVEL", "INFO"),
            }
        }

    def save_settings(self, settings: Dict[str, Any]):
        """保存設置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存設置失败: {e}")
    
    def get_enabled_models(self) -> List[ModelConfig]:
        """獲取啟用的模型"""
        models = self.load_models()
        return [model for model in models if model.enabled and model.api_key]
    
    def get_model_by_name(self, provider: str, model_name: str) -> Optional[ModelConfig]:
        """根據名稱獲取模型配置"""
        models = self.load_models()
        for model in models:
            if model.provider == provider and model.model_name == model_name:
                return model
        return None
    
    def get_usage_statistics(self, days: int = 30) -> Dict[str, Any]:
        """獲取使用統計"""
        # 優先使用MongoDB獲取統計
        if self.mongodb_storage and self.mongodb_storage.is_connected():
            try:
                # 從MongoDB獲取基础統計
                stats = self.mongodb_storage.get_usage_statistics(days)
                # 獲取供應商統計
                provider_stats = self.mongodb_storage.get_provider_statistics(days)
                
                if stats:
                    stats["provider_stats"] = provider_stats
                    stats["records_count"] = stats.get("total_requests", 0)
                    return stats
            except Exception as e:
                logger.error(f"⚠️ MongoDB統計獲取失败，回退到JSON文件: {e}")
        
        # 回退到JSON文件統計
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
            except:
                continue
        
        # 統計數據
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
        """獲取數據目錄路徑"""
        settings = self.load_settings()
        data_dir = settings.get("data_dir")
        if not data_dir:
            # 如果沒有配置，使用默認路徑
            data_dir = os.path.join(os.path.expanduser("~"), "Documents", "TradingAgents", "data")
        return data_dir

    def set_data_dir(self, data_dir: str):
        """設置數據目錄路徑"""
        settings = self.load_settings()
        settings["data_dir"] = data_dir
        # 同時更新緩存目錄
        settings["cache_dir"] = os.path.join(data_dir, "cache")
        self.save_settings(settings)
        
        # 如果啟用自動創建目錄，則創建目錄
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
                    logger.info(f"✅ 創建目錄: {directory}")
                except Exception as e:
                    logger.error(f"❌ 創建目錄失败 {directory}: {e}")
    
    def set_openai_enabled(self, enabled: bool):
        """設置OpenAI模型啟用狀態"""
        settings = self.load_settings()
        settings["openai_enabled"] = enabled
        self.save_settings(settings)
        logger.info(f"🔧 OpenAI模型啟用狀態已設置為: {enabled}")
    
    def is_openai_enabled(self) -> bool:
        """檢查OpenAI模型是否啟用"""
        settings = self.load_settings()
        return settings.get("openai_enabled", False)
    
    def get_openai_config_status(self) -> Dict[str, Any]:
        """獲取OpenAI配置狀態"""
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
    """Token使用跟蹤器"""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def track_usage(self, provider: str, model_name: str, input_tokens: int,
                   output_tokens: int, session_id: str = None, analysis_type: str = "stock_analysis"):
        """跟蹤Token使用"""
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 檢查是否啟用成本跟蹤
        settings = self.config_manager.load_settings()
        cost_tracking_enabled = settings.get("enable_cost_tracking", True)

        if not cost_tracking_enabled:
            return None

        # 添加使用記錄
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

        # 獲取今日总成本
        today_stats = self.config_manager.get_usage_statistics(1)
        total_today = today_stats["total_cost"]

        if total_today >= threshold:
            logger.warning(f"⚠️ 成本警告: 今日成本已達到 ¥{total_today:.4f}，超過阈值 ¥{threshold}",
                          extra={'cost': total_today, 'threshold': threshold, 'event_type': 'cost_alert'})

    def get_session_cost(self, session_id: str) -> float:
        """獲取會話成本"""
        records = self.config_manager.load_usage_records()
        session_cost = sum(record.cost for record in records if record.session_id == session_id)
        return session_cost

    def estimate_cost(self, provider: str, model_name: str, estimated_input_tokens: int,
                     estimated_output_tokens: int) -> float:
        """估算成本"""
        return self.config_manager.calculate_cost(
            provider, model_name, estimated_input_tokens, estimated_output_tokens
        )




# 全局配置管理器實例 - 使用項目根目錄的配置
def _get_project_config_dir():
    """獲取項目根目錄的配置目錄"""
    # 從當前文件位置推斷項目根目錄
    current_file = Path(__file__)  # tradingagents/config/config_manager.py
    project_root = current_file.parent.parent.parent  # 向上三級到項目根目錄
    return str(project_root / "config")

config_manager = ConfigManager(_get_project_config_dir())
token_tracker = TokenTracker(config_manager)
