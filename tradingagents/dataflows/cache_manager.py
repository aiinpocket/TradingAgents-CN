#!/usr/bin/env python3
"""
股票資料快取管理器
支援本地快取股票資料，減少API呼叫，提高回應速度
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Union, List
import hashlib

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class StockDataCache:
    """股票資料快取管理器 - 支援美股資料快取優化"""

    def __init__(self, cache_dir: str = None):
        """
        初始化快取管理器

        Args:
            cache_dir: 快取目錄路徑，預設為 tradingagents/dataflows/data_cache
        """
        if cache_dir is None:
            # 取得當前檔案所在目錄
            current_dir = Path(__file__).parent
            cache_dir = current_dir / "data_cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # 建立子目錄 - 美股市場分類
        self.us_stock_dir = self.cache_dir / "us_stocks"
        self.us_news_dir = self.cache_dir / "us_news"
        self.us_fundamentals_dir = self.cache_dir / "us_fundamentals"
        self.metadata_dir = self.cache_dir / "metadata"

        # 建立所有目錄
        for dir_path in [self.us_stock_dir, self.us_news_dir,
                        self.us_fundamentals_dir, self.metadata_dir]:
            dir_path.mkdir(exist_ok=True)

        # 記憶體 metadata 索引：避免重複掃描檔案系統
        # 格式: {cache_key: metadata_dict}
        self._metadata_index: Dict[str, Dict[str, Any]] = {}
        self._metadata_index_built = False

        # 快取配置 - 美股市場TTL設定
        # 同一交易日內重複分析同一股票時，較長的 TTL 可避免重複 API 呼叫
        self.cache_config = {
            'us_stock_data': {
                'ttl_hours': 4,  # 美股資料快取4小時（覆蓋同一交易日大部分場景）
                'max_files': 1000,
                'description': '美股歷史資料'
            },
            'us_news': {
                'ttl_hours': 8,  # 美股新聞快取8小時（降低新聞 API 呼叫頻率）
                'max_files': 500,
                'description': '美股新聞資料'
            },
            'us_fundamentals': {
                'ttl_hours': 24,  # 美股基本面資料快取24小時
                'max_files': 200,
                'description': '美股基本面資料'
            }
        }

        # 內容長度限制配置（檔案快取預設不限制）
        self.content_length_config = {
            'max_content_length': int(os.getenv('MAX_CACHE_CONTENT_LENGTH', '50000')),  # 50K字元
            'long_text_providers': ['openai', 'anthropic'],  # 支援長文本的提供商
            'enable_length_check': os.getenv('ENABLE_CACHE_LENGTH_CHECK', 'false').lower() == 'true'  # 檔案快取預設不限制
        }

        logger.info(f"快取管理器初始化完成，快取目錄: {self.cache_dir}")
        logger.info("資料庫快取管理器初始化完成")
        logger.info("   美股資料: 已配置")

    def _build_metadata_index(self):
        """建構記憶體 metadata 索引，避免每次查找都掃描檔案系統"""
        if self._metadata_index_built:
            return
        try:
            for metadata_file in self.metadata_dir.glob("*_meta.json"):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    cache_key = metadata_file.stem.replace('_meta', '')
                    self._metadata_index[cache_key] = metadata
                except (json.JSONDecodeError, IOError):
                    continue
            self._metadata_index_built = True
            logger.debug(f"metadata 索引建構完成，共 {len(self._metadata_index)} 筆")
        except OSError as e:
            logger.warning(f"建構 metadata 索引失敗: {e}")

    def _index_metadata(self, cache_key: str, metadata: Dict[str, Any]):
        """將新的 metadata 加入記憶體索引"""
        self._metadata_index[cache_key] = metadata

    def _find_in_index(self, **filters) -> list:
        """從記憶體索引中查找符合條件的 cache key 清單"""
        self._build_metadata_index()
        results = []
        for cache_key, metadata in self._metadata_index.items():
            match = True
            for key, value in filters.items():
                if value is not None and metadata.get(key) != value:
                    match = False
                    break
            if match:
                results.append(cache_key)
        return results

    @staticmethod
    def _date_bucket(date_str: str, bucket_days: int = 3) -> str:
        """將日期歸入桶，降低 cache key 對日期的敏感度
        例如 bucket_days=3 時，同一個 3 天區間內的日期會產生相同的桶值"""
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # 以 epoch 天數除以 bucket_days 取整
            epoch = datetime(2020, 1, 1)
            day_offset = (dt - epoch).days
            bucket_id = day_offset // bucket_days
            return str(bucket_id)
        except (ValueError, TypeError):
            return date_str or "none"

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
        
        # 檢查Anthropic
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key.strip():
            available_providers.append('anthropic')
        
        return available_providers

    def should_skip_cache_for_content(self, content: str, data_type: str = "unknown") -> bool:
        """
        判斷是否因為內容超長而跳過快取
        
        Args:
            content: 要快取的內容
            data_type: 資料類型（用於日誌）
        
        Returns:
            bool: 是否應該跳過快取
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
            logger.warning(f"內容過長({content_length:,}字元 > {max_length:,}字元)且無可用長文本提供商，跳過{data_type}快取")
            logger.info(f"可用提供商: {available_providers}")
            logger.info(f"長文本提供商: {long_text_providers}")
            return True
        else:
            logger.info(f"內容較長({content_length:,}字元)但有可用長文本提供商({available_long_providers})，繼續快取")
            return False
    
    def _generate_cache_key(self, data_type: str, symbol: str, **kwargs) -> str:
        """生成快取鍵"""
        # 建立一個包含所有參數的字串
        params_str = f"{data_type}_{symbol}"
        for key, value in sorted(kwargs.items()):
            params_str += f"_{key}_{value}"
        
        # 使用 SHA-256 生成短的唯一標識
        cache_key = hashlib.sha256(params_str.encode()).hexdigest()[:12]
        return f"{symbol}_{data_type}_{cache_key}"
    
    def _get_cache_path(self, data_type: str, cache_key: str, file_format: str = "json", symbol: str = None) -> Path:
        """取得快取檔案路徑 - 支援市場分類"""
        # 統一使用美股市場類型
        market_type = 'us'

        # 根據資料類型選擇對應的美股快取目錄
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
        """取得中繼資料檔路徑"""
        return self.metadata_dir / f"{cache_key}_meta.json"
    
    def _save_metadata(self, cache_key: str, metadata: Dict[str, Any]):
        """保存中繼資料（同時更新記憶體索引）"""
        metadata_path = self._get_metadata_path(cache_key)
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata['cached_at'] = datetime.now().isoformat()

        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # 同步更新記憶體索引
        self._index_metadata(cache_key, metadata)
    
    def _load_metadata(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """載入中繼資料"""
        metadata_path = self._get_metadata_path(cache_key)
        if not metadata_path.exists():
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"載入中繼資料失敗: {e}")
            return None
    
    def is_cache_valid(self, cache_key: str, max_age_hours: int = None, symbol: str = None, data_type: str = None) -> bool:
        """檢查快取是否有效 - 支援智慧TTL配置"""
        metadata = self._load_metadata(cache_key)
        if not metadata:
            return False

        # 如果沒有指定TTL，根據資料類型和市場自動確定
        if max_age_hours is None:
            if symbol and data_type:
                market_type = self._determine_market_type(symbol)
                cache_type = f"{market_type}_{data_type}"
                max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)
            else:
                # 從中繼資料中取得資訊
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
            desc = self.cache_config.get(cache_type, {}).get('description', '資料')
            logger.info(f"快取有效: {desc} - {metadata.get('symbol')} (剩餘 {max_age_hours - age.total_seconds()/3600:.1f}h)")

        return is_valid
    
    def save_stock_data(self, symbol: str, data: Union[pd.DataFrame, str],
                       start_date: str = None, end_date: str = None,
                       data_source: str = "unknown") -> str:
        """
        保存股票資料到快取 - 支援美股分類儲存

        Args:
            symbol: 股票代碼
            data: 股票資料（DataFrame或字串）
            start_date: 開始日期
            end_date: 結束日期
            data_source: 資料來源（如 "tdx", "yfinance", "finnhub"）

        Returns:
            cache_key: 快取鍵
        """
        # 檢查內容長度是否需要跳過快取
        content_to_check = str(data)
        if self.should_skip_cache_for_content(content_to_check, "股票資料"):
            # 生成一個虛擬的快取鍵，但不實際保存
            market_type = self._determine_market_type(symbol)
            cache_key = self._generate_cache_key("stock_data", symbol,
                                               start_bucket=self._date_bucket(start_date),
                                               end_bucket=self._date_bucket(end_date),
                                               source=data_source,
                                               market=market_type,
                                               skipped=True)
            logger.info(f"股票資料因內容過長被跳過快取: {symbol} -> {cache_key}")
            return cache_key

        market_type = self._determine_market_type(symbol)
        # 使用日期桶降低 key 對每日日期偏移的敏感度
        cache_key = self._generate_cache_key("stock_data", symbol,
                                           start_bucket=self._date_bucket(start_date),
                                           end_bucket=self._date_bucket(end_date),
                                           source=data_source,
                                           market=market_type)

        # 保存資料
        if isinstance(data, pd.DataFrame):
            cache_path = self._get_cache_path("stock_data", cache_key, "csv", symbol)
            cache_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
            data.to_csv(cache_path, index=True)
        else:
            cache_path = self._get_cache_path("stock_data", cache_key, "txt", symbol)
            cache_path.parent.mkdir(parents=True, exist_ok=True)  # 確保目錄存在
            with open(cache_path, 'w', encoding='utf-8') as f:
                f.write(str(data))

        # 保存中繼資料
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

        # 取得描述資訊
        cache_type = f"{market_type}_stock_data"
        desc = self.cache_config.get(cache_type, {}).get('description', '股票資料')
        logger.info(f"{desc}已快取: {symbol} ({data_source}) -> {cache_key}")
        return cache_key
    
    def load_stock_data(self, cache_key: str) -> Optional[Union[pd.DataFrame, str]]:
        """從快取載入股票資料"""
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
            logger.error(f"載入快取資料失敗: {e}")
            return None
    
    def find_cached_stock_data(self, symbol: str, start_date: str = None,
                              end_date: str = None, data_source: str = None,
                              max_age_hours: int = None) -> Optional[str]:
        """
        查找匹配的快取資料 - 支援智慧市場分類查找

        Args:
            symbol: 股票代碼
            start_date: 開始日期
            end_date: 結束日期
            data_source: 資料來源
            max_age_hours: 最大快取時間（小時），None時使用智慧配置

        Returns:
            cache_key: 如果找到有效快取則返回快取鍵，否則返回None
        """
        market_type = self._determine_market_type(symbol)

        # 如果沒有指定TTL，使用智慧配置
        if max_age_hours is None:
            cache_type = f"{market_type}_stock_data"
            max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)

        # 使用日期桶生成查找鍵（與 save_stock_data 對齊）
        search_key = self._generate_cache_key("stock_data", symbol,
                                            start_bucket=self._date_bucket(start_date),
                                            end_bucket=self._date_bucket(end_date),
                                            source=data_source,
                                            market=market_type)

        # 檢查精確匹配（日期桶相同時直接命中）
        if self.is_cache_valid(search_key, max_age_hours, symbol, 'stock_data'):
            desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '資料')
            logger.info(f"找到精確匹配的{desc}: {symbol} -> {search_key}")
            return search_key

        # 如果沒有精確匹配，使用記憶體索引查找部分匹配
        candidate_keys = self._find_in_index(
            symbol=symbol,
            data_type='stock_data',
            market_type=market_type,
        )
        for cache_key in candidate_keys:
            meta = self._metadata_index.get(cache_key, {})
            if data_source is not None and meta.get('data_source') != data_source:
                continue
            if self.is_cache_valid(cache_key, max_age_hours, symbol, 'stock_data'):
                desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '資料')
                logger.info(f"找到部分匹配的{desc}: {symbol} -> {cache_key}")
                return cache_key

        desc = self.cache_config.get(f"{market_type}_stock_data", {}).get('description', '資料')
        logger.error(f"未找到有效的{desc}快取: {symbol}")
        return None

    def save_news_data(self, symbol: str, news_data: str, 
                      start_date: str = None, end_date: str = None,
                      data_source: str = "unknown") -> str:
        """保存新聞資料到快取"""
        # 檢查內容長度是否需要跳過快取
        if self.should_skip_cache_for_content(news_data, "新聞資料"):
            # 生成一個虛擬的快取鍵，但不實際保存
            cache_key = self._generate_cache_key("news", symbol,
                                               start_date=start_date,
                                               end_date=end_date,
                                               source=data_source,
                                               skipped=True)
            logger.info(f"新聞資料因內容過長被跳過快取: {symbol} -> {cache_key}")
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
        
        logger.info(f"新聞資料已快取: {symbol} ({data_source}) -> {cache_key}")
        return cache_key
    
    def save_fundamentals_data(self, symbol: str, fundamentals_data: str,
                              data_source: str = "unknown") -> str:
        """保存基本面資料到快取（key 不含日期，靠 TTL 控制新鮮度）"""
        # 檢查內容長度是否需要跳過快取
        if self.should_skip_cache_for_content(fundamentals_data, "基本面資料"):
            market_type = self._determine_market_type(symbol)
            cache_key = self._generate_cache_key("fundamentals", symbol,
                                               source=data_source,
                                               market=market_type,
                                               skipped=True)
            logger.info(f"基本面資料因內容過長被跳過快取: {symbol} -> {cache_key}")
            return cache_key

        market_type = self._determine_market_type(symbol)
        # 移除 date 參數：同一 symbol+source 共用固定 key，靠 24h TTL 控制新鮮度
        cache_key = self._generate_cache_key("fundamentals", symbol,
                                           source=data_source,
                                           market=market_type)
        
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
        
        desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面資料')
        logger.info(f"{desc}已快取: {symbol} ({data_source}) -> {cache_key}")
        return cache_key
    
    def load_fundamentals_data(self, cache_key: str) -> Optional[str]:
        """從快取載入基本面資料"""
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
            logger.error(f"載入基本面快取資料失敗: {e}")
            return None
    
    def find_cached_fundamentals_data(self, symbol: str, data_source: str = None,
                                    max_age_hours: int = None) -> Optional[str]:
        """
        查找匹配的基本面快取資料
        先嘗試精確 key 匹配（O(1)），再退化到記憶體索引掃描

        Args:
            symbol: 股票代碼
            data_source: 資料來源（如 "openai", "finnhub"）
            max_age_hours: 最大快取時間（小時），None時使用智慧配置

        Returns:
            cache_key: 如果找到有效快取則返回快取鍵，否則返回None
        """
        market_type = self._determine_market_type(symbol)

        # 如果沒有指定TTL，使用智慧配置
        if max_age_hours is None:
            cache_type = f"{market_type}_fundamentals"
            max_age_hours = self.cache_config.get(cache_type, {}).get('ttl_hours', 24)

        # 精確匹配：key 不含日期，同一 symbol+source 直接命中
        if data_source is not None:
            exact_key = self._generate_cache_key("fundamentals", symbol,
                                                source=data_source,
                                                market=market_type)
            if self.is_cache_valid(exact_key, max_age_hours, symbol, 'fundamentals'):
                desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面資料')
                logger.info(f"找到精確匹配的{desc}快取: {symbol} ({data_source}) -> {exact_key}")
                return exact_key

        # 退化到記憶體索引掃描
        candidate_keys = self._find_in_index(
            symbol=symbol,
            data_type='fundamentals',
            market_type=market_type,
        )
        for cache_key in candidate_keys:
            meta = self._metadata_index.get(cache_key, {})
            if data_source is not None and meta.get('data_source') != data_source:
                continue
            if self.is_cache_valid(cache_key, max_age_hours, symbol, 'fundamentals'):
                desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面資料')
                logger.info(f"找到匹配的{desc}快取: {symbol} ({data_source}) -> {cache_key}")
                return cache_key

        desc = self.cache_config.get(f"{market_type}_fundamentals", {}).get('description', '基本面資料')
        logger.error(f"未找到有效的{desc}快取: {symbol} ({data_source})")
        return None
    
    def clear_old_cache(self, max_age_days: int = 7):
        """清理過期快取（同步清理記憶體索引）"""
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        cleared_count = 0

        for metadata_file in self.metadata_dir.glob("*_meta.json"):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                cached_at = datetime.fromisoformat(metadata['cached_at'])
                if cached_at < cutoff_time:
                    # 刪除資料檔案
                    data_file = Path(metadata['file_path'])
                    if data_file.exists():
                        data_file.unlink()

                    # 從記憶體索引移除
                    cache_key = metadata_file.stem.replace('_meta', '')
                    self._metadata_index.pop(cache_key, None)

                    # 刪除中繼資料檔
                    metadata_file.unlink()
                    cleared_count += 1

            except Exception as e:
                logger.warning(f"清理快取時出錯: {e}")

        logger.info(f"已清理 {cleared_count} 個過期快取檔案")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """取得快取統計資訊"""
        stats = {
            'total_files': 0,
            'stock_data_count': 0,
            'news_count': 0,
            'fundamentals_count': 0,
            'total_size_mb': 0,
            'skipped_count': 0  # 新增：跳過的快取數量
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
                
                # 檢查是否為跳過的快取（沒有實際檔案）
                data_file = Path(metadata.get('file_path', ''))
                if not data_file.exists():
                    stats['skipped_count'] += 1
                else:
                    # 計算檔案大小
                    stats['total_size_mb'] += data_file.stat().st_size / (1024 * 1024)
                
                stats['total_files'] += 1
                
            except Exception as e:
                continue
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        return stats

    def get_content_length_config_status(self) -> Dict[str, Any]:
        """取得內容長度配置狀態"""
        available_providers = self._check_provider_availability()
        long_text_providers = self.content_length_config['long_text_providers']
        available_long_providers = [p for p in available_providers if p in long_text_providers]
        
        return {
            'enabled': self.content_length_config['enable_length_check'],
            'max_content_length': self.content_length_config['max_content_length'],
            'max_content_length_formatted': f"{self.content_length_config['max_content_length']:,}字元",
            'long_text_providers': long_text_providers,
            'available_providers': available_providers,
            'available_long_providers': available_long_providers,
            'has_long_text_support': len(available_long_providers) > 0,
            'will_skip_long_content': self.content_length_config['enable_length_check'] and len(available_long_providers) == 0
        }


# 全局快取實例
_cache_instance = None

def get_cache() -> StockDataCache:
    """取得全局快取實例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = StockDataCache()
    return _cache_instance
