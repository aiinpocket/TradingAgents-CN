#!/usr/bin/env python3
"""
股票數據緩存管理器
支持本地緩存股票數據，減少API調用，提高響應速度
"""

import os
import json
import pickle
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
import hashlib

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class StockDataCache:
    """股票數據緩存管理器 - 支持美股數據緩存優化"""

    def __init__(self, cache_dir: str = None):
        """
        初始化緩存管理器

        Args:
            cache_dir: 緩存目錄路徑，默認為 tradingagents/dataflows/data_cache
        """
        if cache_dir is None:
            # 獲取當前文件所在目錄
            current_dir = Path(__file__).parent
            cache_dir = current_dir / "data_cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 創建子目錄 - 美股市場分類
        self.us_stock_dir = self.cache_dir / "us_stocks"
        self.us_news_dir = self.cache_dir / "us_news"
        self.us_fundamentals_dir = self.cache_dir / "us_fundamentals"
        self.metadata_dir = self.cache_dir / "metadata"

        # 創建所有目錄
        for dir_path in [self.us_stock_dir, self.us_news_dir,
                        self.us_fundamentals_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)

        # 緩存配置 - 美股市場TTL設定
        self.cache_config = {
            'us_stock_data': {
                'ttl_hours': 2,  # 美股數據緩存2小時（考慮到API限制）
                'max_files': 1000,
                'description': '美股歷史數據'
            },
            'us_news': {
                'ttl_hours': 6,  # 美股新聞緩存6小時
                'max_files': 500,
                'description': '美股新聞數據'
            },
            'us_fundamentals': {
                'ttl_hours': 24,  # 美股基本面數據緩存24小時
                'max_files': 200,
                'description': '美股基本面數據'
            }
        }

        # 內容長度限制配置（文件緩存默認不限制）
        self.content_length_config = {
            'max_content_length': int(os.getenv('MAX_CACHE_CONTENT_LENGTH', '50000')),  # 50K字符
            'long_text_providers': ['openai', 'google', 'anthropic'],  # 支援長文本的提供商
            'enable_length_check': os.getenv('ENABLE_CACHE_LENGTH_CHECK', 'false').lower() == 'true'  # 文件緩存默認不限制
        }

        logger.info(f"📁 緩存管理器初始化完成，緩存目錄: {self.cache_dir}")
        logger.info(f"🗄️ 數據庫緩存管理器初始化完成")
        logger.info(f"   美股數據: 已配置")

    def _determine_market_type(self, symbol: str) -> str:
        """根據股票代碼判斷市場類型（目前僅支援美股）"""
        return 'us'

    def _check_provider_availability(self) -> List[str]:
        """檢查可用的 LLM 提供商"""
        available_providers = []

        # 檢查 OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.strip():
            # 簡單的格式檢查
            if openai_key.startswith('sk-') and len(openai_key) >= 40:
                available_providers.append('openai')
        
        # 檢查Google AI
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key and google_key.strip():
            available_providers.append('google')
        
        # 檢查Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key.strip():
            available_providers.append('anthropic')
        
        return available_providers

    def should_skip_cache_for_content(self, content: str, data_type: str = "unknown") -> bool:
        """
        判斷是否因為內容超長而跳過緩存
        
        Args:
            content: 要緩存的內容
            data_type: 數據類型（用於日誌）
        
        Returns:
            bool: 是否應該跳過緩存
        """
        # 如果未啟用長度檢查，直接返回False
        if not self.content_length_config['enable_length_check']:
            return False
        
        # 檢查內容長度
        content_length = len(content)
        max_length = self.content_length_config['max_content_length']
        
        if content_length <= max_length:
            return False
        
        # 內容超長，檢查是否有可用的長文本處理提供商
        available_providers = self._check_provider_availability()
        long_text_providers = self.content_length_config['long_text_providers']
        
        # 找到可用的長文本提供商
        available_long_providers = [p for p in available_providers if p in long_text_providers]
        
        if not available_long_providers:
            logger.warning(f"⚠️ 內容過長({content_length:,}字符 > {max_length:,}字符)且無可用長文本提供商，跳過{data_type}緩存")
            logger.info(f"💡 可用提供商: {available_providers}")
            logger.info(f"💡 長文本提供商: {long_text_providers}")
            return True
        else:
            logger.info(f"✅ 內容較長({content_length:,}字符)但有可用長文本提供商({available_long_providers})，繼續緩存")
            return False
    
    def _generate_cache_key(self, data_type: str, symbol: str, **kwargs) -> str:
        """生成緩存鍵"""
        # 創建一個包含所有參數的字符串
        params_str = f"{data_type}_{symbol}"
        for key, value in sorted(kwargs.items()):
            params_str += f"_{key}_{value}"
        
        # 使用MD5生成短的唯一標識
        cache_key = hashlib.md5(params_str.encode()).hexdigest()[:12]
        return f"{symbol}_{data_type}_{cache_key}"
    
    def _get_cache_path(self, data_type: str, cache_key: str, file_format: str = "json", symbol: str = None) -> Path:
        """獲取緩存文件路徑 - 支持市場分類"""
        # 統一使用美股市場類型
        market_type = 'us'

        # 根據數據類型選擇對應的美股緩存目錄
        if data_type == "stock_data":
            base_dir = self.us_stock_dir
        elif data_type == "news":
            base_dir = self.us_news_dir
        elif data_type == "fundamentals":
            base_dir = self.us_fundamentals_dir
        else:
            base_dir = self.cache_dir

        return base_dir / f"{cache_key}.{file_format}"
    
    def _get_metadata_path(self, cache_key: str) -> Path:
        """獲取元數據文件路徑"""
        return self.metadata_dir / f"{cache_key}_meta.json"
    
    def _save_metadata(self, cache_key: str, metadata: Dict[str, Any]):
        """保存元數據"""
        metadata_path = self._get_metadata_path(cache_key)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
        metadata['cached_at'] = datetime.now().isoformat()
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _load_metadata(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """加載元數據"""
        metadata_path = self._get_metadata_path(cache_key)
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"⚠️ 加載元數據失敗: {e}")
            return None
    
    def is_cache_valid(self, cache_key: str, max_age_hours: int = None, symbol: str = None, data_type: str = None) -> bool:
        """檢查緩存是否有效 - 支持智能TTL配置"""
        metadata = self._load_metadata(cache_key)
        if not metadata:
            return False

        # 如果沒有指定TTL，根據數據類型和市場自動確定
        if max_age_hours is None:
            if symbol and data_type:
                market_type = self._determine_market_type(symbol)
                cache_type = f"{market_type}_{data_type}"
                max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)
            else:
                # 從元數據中獲取信息
                symbol = metadata.get('symbol', '')
                data_type = metadata.get('data_type', 'stock_data')
                market_type = self._determine_market_type(symbol)
                cache_type = f"{market_type}_{data_type}"
                max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)

        cached_at = datetime.fromisoformat(metadata['cached_at'])
        age = datetime.now() - cached_at

        is_valid = age.total_seconds() < max_age_hours * 3600

        if is_valid:
            market_type = self._determine_market_type(metadata.get('symbol', ''))
            cache_type = f"{market_type}_{metadata.get('data_type', 'stock_data')}"
            desc = self.cache_config.get(cache_type, {}).get('description', '數據')
            logger.info(f"✅ 緩存有效: {desc} - {metadata.get('symbol')} (剩餘 {max_age_hours - age.total_seconds()/3600:.1f}h)")

        return is_valid
    
    def save_stock_data(self, symbol: str, data: Union[pd.DataFrame, str],
                       start_date: str = None, end_date: str = None,
                       data_source: str = "unknown") -> str:
        """
        保存股票數據到緩存 - 支持美股分類儲存

        Args:
            symbol: 股票代碼
            data: 股票數據（DataFrame或字符串）
            start_date: 開始日期
            end_date: 結束日期
            data_source: 數據源（如 "tdx", "yfinance", "finnhub"）

        Returns:
            cache_key: 緩存鍵
        """
        # 檢查內容長度是否需要跳過緩存
        content_to_check = str(data)
        if self.should_skip_cache_for_content(content_to_check, "股票數據"):
            # 生成一個虛擬的緩存鍵，但不實際保存
            market_type = self._determine_market_type(symbol)
            cache_key = self._generate_cache_key("stock_data", symbol,
                                               start_date=start_date,
                                               end_date=end_date,
                                               source=data_source,
                                               market=market_type,
                                               skipped=True)
            logger.info(f"🚫 股票數據因內容過長被跳過緩存: {symbol} -> {cache_key}")
            return cache_key

        market_type = self._determine_market_type(symbol)
        cache_key = self._generate_cache_key("stock_data", symbol,
                                           start_date=start_date,
                                           end_date=end_date,
                                           source=data_source,
                                           market=market_type)

        # 保存數據
        if isinstance(data, pd.DataFrame):
            cache_path = self._get_cache_path("stock_data", cache_key, "csv", symbol)
            cache_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
            data.to_csv(cache_path, index=True)
        else:
            cache_path = self._get_cache_path("stock_data", cache_key, "txt", symbol)
            cache_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(str(data))

        # 保存元數據
        metadata = {
            'symbol': symbol,
            'data_type': 'stock_data',
            'market_type': market_type,
            'start_date': start_date,
            'end_date': end_date,
            'data_source': data_source,
            'file_path': str(cache_path),
            'file_format': 'csv' if isinstance(data, pd.DataFrame) else 'txt',
            'content_length': len(content_to_check)
        }
        self._save_metadata(cache_key, metadata)

        # 獲取描述信息
        cache_type = f"{market_type}_stock_data"
        desc = self.cache_config.get(cache_type, {}).get('description', '股票數據')
        logger.info(f"💾 {desc}已緩存: {symbol} ({data_source}) -> {cache_key}")
        return cache_key
    
    def load_stock_data(self, cache_key: str) -> Optional[Union[pd.DataFrame, str]]:
        """從緩存加載股票數據"""
        metadata = self._load_metadata(cache_key)
        if not metadata:
            return None
        
        cache_path = Path(metadata['file_path'])
        if not cache_path.exists():
            return None
        
        try:
            if metadata['file_format'] == 'csv':
                return pd.read_csv(cache_path, index_col=0)
            else:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            logger.error(f"⚠️ 加載緩存數據失敗: {e}")
            return None
    
    def find_cached_stock_data(self, symbol: str, start_date: str = None,
                              end_date: str = None, data_source: str = None,
                              max_age_hours: int = None) -> Optional[str]:
        """
        查找匹配的緩存數據 - 支持智能市場分類查找

        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            data_source: 數據源
            max_age_hours: 最大緩存時間（小時），None時使用智能配置

        Returns:
            cache_key: 如果找到有效緩存則返回緩存鍵，否則返回None
        """
        market_type = self._determine_market_type(symbol)

        # 如果沒有指定TTL，使用智能配置
        if max_age_hours is None:
            cache_type = f"{market_type}_stock_data"
            max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)

        # 生成查找鍵
        search_key = self._generate_cache_key("stock_data", symbol,
                                            start_date=start_date,
                                            end_date=end_date,
                                            source=data_source,
                                            market=market_type)

        # 檢查精確匹配
        if self.is_cache_valid(search_key, max_age_hours, symbol, 'stock_data'):
            desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '數據')
            logger.info(f"🎯 找到精確匹配的{desc}: {symbol} -> {search_key}")
            return search_key

        # 如果沒有精確匹配，查找部分匹配（相同股票代碼的其他緩存）
        for metadata_file in self.metadata_dir.glob(f"*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                if (metadata.get('symbol') == symbol and
                    metadata.get('data_type') == 'stock_data' and
                    metadata.get('market_type') == market_type and
                    (data_source is None or metadata.get('data_source') == data_source)):

                    cache_key = metadata_file.stem.replace('_meta', '')
                    if self.is_cache_valid(cache_key, max_age_hours, symbol, 'stock_data'):
                        desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '數據')
                        logger.info(f"📋 找到部分匹配的{desc}: {symbol} -> {cache_key}")
                        return cache_key
            except Exception:
                continue

        desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '數據')
        logger.error(f"❌ 未找到有效的{desc}緩存: {symbol}")
        return None
    
    def save_news_data(self, symbol: str, news_data: str, 
                      start_date: str = None, end_date: str = None,
                      data_source: str = "unknown") -> str:
        """保存新聞數據到緩存"""
        # 檢查內容長度是否需要跳過緩存
        if self.should_skip_cache_for_content(news_data, "新聞數據"):
            # 生成一個虛擬的緩存鍵，但不實際保存
            cache_key = self._generate_cache_key("news", symbol,
                                               start_date=start_date,
                                               end_date=end_date,
                                               source=data_source,
                                               skipped=True)
            logger.info(f"🚫 新聞數據因內容過長被跳過緩存: {symbol} -> {cache_key}")
            return cache_key

        cache_key = self._generate_cache_key("news", symbol,
                                           start_date=start_date,
                                           end_date=end_date,
                                           source=data_source)
        
        cache_path = self._get_cache_path("news", cache_key, "txt")
        cache_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(news_data)
        
        metadata = {
            'symbol': symbol,
            'data_type': 'news',
            'start_date': start_date,
            'end_date': end_date,
            'data_source': data_source,
            'file_path': str(cache_path),
            'file_format': 'txt',
            'content_length': len(news_data)
        }
        self._save_metadata(cache_key, metadata)
        
        logger.info(f"📰 新聞數據已緩存: {symbol} ({data_source}) -> {cache_key}")
        return cache_key
    
    def save_fundamentals_data(self, symbol: str, fundamentals_data: str,
                              data_source: str = "unknown") -> str:
        """保存基本面數據到緩存"""
        # 檢查內容長度是否需要跳過緩存
        if self.should_skip_cache_for_content(fundamentals_data, "基本面數據"):
            # 生成一個虛擬的緩存鍵，但不實際保存
            market_type = self._determine_market_type(symbol)
            cache_key = self._generate_cache_key("fundamentals", symbol,
                                               source=data_source,
                                               market=market_type,
                                               date=datetime.now().strftime("%Y-%m-%d"),
                                               skipped=True)
            logger.info(f"🚫 基本面數據因內容過長被跳過緩存: {symbol} -> {cache_key}")
            return cache_key

        market_type = self._determine_market_type(symbol)
        cache_key = self._generate_cache_key("fundamentals", symbol,
                                           source=data_source,
                                           market=market_type,
                                           date=datetime.now().strftime("%Y-%m-%d"))
        
        cache_path = self._get_cache_path("fundamentals", cache_key, "txt", symbol)
        cache_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(fundamentals_data)
        
        metadata = {
            'symbol': symbol,
            'data_type': 'fundamentals',
            'data_source': data_source,
            'market_type': market_type,
            'file_path': str(cache_path),
            'file_format': 'txt',
            'content_length': len(fundamentals_data)
        }
        self._save_metadata(cache_key, metadata)
        
        desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面數據')
        logger.info(f"💼 {desc}已緩存: {symbol} ({data_source}) -> {cache_key}")
        return cache_key
    
    def load_fundamentals_data(self, cache_key: str) -> Optional[str]:
        """從緩存加載基本面數據"""
        metadata = self._load_metadata(cache_key)
        if not metadata:
            return None
        
        cache_path = Path(metadata['file_path'])
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"⚠️ 加載基本面緩存數據失敗: {e}")
            return None
    
    def find_cached_fundamentals_data(self, symbol: str, data_source: str = None,
                                    max_age_hours: int = None) -> Optional[str]:
        """
        查找匹配的基本面緩存數據
        
        Args:
            symbol: 股票代碼
            data_source: 數據源（如 "openai", "finnhub"）
            max_age_hours: 最大緩存時間（小時），None時使用智能配置
        
        Returns:
            cache_key: 如果找到有效緩存則返回緩存鍵，否則返回None
        """
        market_type = self._determine_market_type(symbol)
        
        # 如果沒有指定TTL，使用智能配置
        if max_age_hours is None:
            cache_type = f"{market_type}_fundamentals"
            max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)
        
        # 查找匹配的緩存
        for metadata_file in self.metadata_dir.glob(f"*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                if (metadata.get('symbol') == symbol and
                    metadata.get('data_type') == 'fundamentals' and
                    metadata.get('market_type') == market_type and
                    (data_source is None or metadata.get('data_source') == data_source)):
                    
                    cache_key = metadata_file.stem.replace('_meta', '')
                    if self.is_cache_valid(cache_key, max_age_hours, symbol, 'fundamentals'):
                        desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面數據')
                        logger.info(f"🎯 找到匹配的{desc}緩存: {symbol} ({data_source}) -> {cache_key}")
                        return cache_key
            except Exception:
                continue
        
        desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面數據')
        logger.error(f"❌ 未找到有效的{desc}緩存: {symbol} ({data_source})")
        return None
    
    def clear_old_cache(self, max_age_days: int = 7):
        """清理過期緩存"""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        cleared_count = 0
        
        for metadata_file in self.metadata_dir.glob("*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                cached_at = datetime.fromisoformat(metadata['cached_at'])
                if cached_at < cutoff_time:
                    # 刪除數據文件
                    data_file = Path(metadata['file_path'])
                    if data_file.exists():
                        data_file.unlink()
                    
                    # 刪除元數據文件
                    metadata_file.unlink()
                    cleared_count += 1
                    
            except Exception as e:
                logger.warning(f"⚠️ 清理緩存時出錯: {e}")
        
        logger.info(f"🧹 已清理 {cleared_count} 個過期緩存文件")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取緩存統計信息"""
        stats = {
            'total_files': 0,
            'stock_data_count': 0,
            'news_count': 0,
            'fundamentals_count': 0,
            'total_size_mb': 0,
            'skipped_count': 0  # 新增：跳過的緩存數量
        }
        
        for metadata_file in self.metadata_dir.glob("*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                data_type = metadata.get('data_type', 'unknown')
                if data_type == 'stock_data':
                    stats['stock_data_count'] += 1
                elif data_type == 'news':
                    stats['news_count'] += 1
                elif data_type == 'fundamentals':
                    stats['fundamentals_count'] += 1
                
                # 檢查是否為跳過的緩存（沒有實際文件）
                data_file = Path(metadata.get('file_path', ''))
                if not data_file.exists():
                    stats['skipped_count'] += 1
                else:
                    # 計算文件大小
                    stats['total_size_mb'] += data_file.stat().st_size / (1024 * 1024)
                
                stats['total_files'] += 1
                
            except Exception:
                continue
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats

    def get_content_length_config_status(self) -> Dict[str, Any]:
        """獲取內容長度配置狀態"""
        available_providers = self._check_provider_availability()
        long_text_providers = self.content_length_config['long_text_providers']
        available_long_providers = [p for p in available_providers if p in long_text_providers]
        
        return {
            'enabled': self.content_length_config['enable_length_check'],
            'max_content_length': self.content_length_config['max_content_length'],
            'max_content_length_formatted': f"{self.content_length_config['max_content_length']:,}字符",
            'long_text_providers': long_text_providers,
            'available_providers': available_providers,
            'available_long_providers': available_long_providers,
            'has_long_text_support': len(available_long_providers) > 0,
            'will_skip_long_content': self.content_length_config['enable_length_check'] and len(available_long_providers) == 0
        }


# 全局緩存實例
_cache_instance = None

def get_cache() -> StockDataCache:
    """獲取全局緩存實例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = StockDataCache()
    return _cache_instance
