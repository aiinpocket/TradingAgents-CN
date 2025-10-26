#!/usr/bin/env python3
"""
改進的港股數據獲取工具
解決API速率限制和數據獲取問題
"""

import time
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# 導入統一日誌系統
from tradingagents.utils.logging_init import get_logger
logger = get_logger("default")


class ImprovedHKStockProvider:
    """改進的港股數據提供器"""
    
    def __init__(self):
        self.cache_file = "hk_stock_cache.json"
        self.cache_ttl = 3600 * 24  # 24小時緩存
        self.rate_limit_wait = 5  # 速率限制等待時間
        self.last_request_time = 0
        
        # 內置港股名稱映射（避免API調用）
        self.hk_stock_names = {
            # 腾讯系
            '0700.HK': '腾讯控股', '0700': '腾讯控股', '00700': '腾讯控股',
            
            # 电信運營商
            '0941.HK': '中國移動', '0941': '中國移動', '00941': '中國移動',
            '0762.HK': '中國聯通', '0762': '中國聯通', '00762': '中國聯通',
            '0728.HK': '中國电信', '0728': '中國电信', '00728': '中國电信',
            
            # 銀行
            '0939.HK': '建設銀行', '0939': '建設銀行', '00939': '建設銀行',
            '1398.HK': '工商銀行', '1398': '工商銀行', '01398': '工商銀行',
            '3988.HK': '中國銀行', '3988': '中國銀行', '03988': '中國銀行',
            '0005.HK': '汇丰控股', '0005': '汇丰控股', '00005': '汇丰控股',
            
            # 保險
            '1299.HK': '友邦保險', '1299': '友邦保險', '01299': '友邦保險',
            '2318.HK': '中國平安', '2318': '中國平安', '02318': '中國平安',
            '2628.HK': '中國人寿', '2628': '中國人寿', '02628': '中國人寿',
            
            # 石油化工
            '0857.HK': '中國石油', '0857': '中國石油', '00857': '中國石油',
            '0386.HK': '中國石化', '0386': '中國石化', '00386': '中國石化',
            
            # 地產
            '1109.HK': '華润置地', '1109': '華润置地', '01109': '華润置地',
            '1997.HK': '九龙仓置業', '1997': '九龙仓置業', '01997': '九龙仓置業',
            
            # 科技
            '9988.HK': '阿里巴巴', '9988': '阿里巴巴', '09988': '阿里巴巴',
            '3690.HK': '美团', '3690': '美团', '03690': '美团',
            '1024.HK': '快手', '1024': '快手', '01024': '快手',
            '9618.HK': '京东集团', '9618': '京东集团', '09618': '京东集团',
            
            # 消費
            '1876.HK': '百威亚太', '1876': '百威亚太', '01876': '百威亚太',
            '0291.HK': '華润啤酒', '0291': '華润啤酒', '00291': '華润啤酒',
            
            # 醫藥
            '1093.HK': '石藥集团', '1093': '石藥集团', '01093': '石藥集团',
            '0867.HK': '康師傅', '0867': '康師傅', '00867': '康師傅',
            
            # 汽車
            '2238.HK': '廣汽集团', '2238': '廣汽集团', '02238': '廣汽集团',
            '1211.HK': '比亚迪', '1211': '比亚迪', '01211': '比亚迪',
            
            # 航空
            '0753.HK': '中國國航', '0753': '中國國航', '00753': '中國國航',
            '0670.HK': '中國东航', '0670': '中國东航', '00670': '中國东航',
            
            # 鋼鐵
            '0347.HK': '鞍鋼股份', '0347': '鞍鋼股份', '00347': '鞍鋼股份',
            
            # 电力
            '0902.HK': '華能國际', '0902': '華能國际', '00902': '華能國际',
            '0991.HK': '大唐發电', '0991': '大唐發电', '00991': '大唐發电'
        }
        
        self._load_cache()
    
    def _load_cache(self):
        """加載緩存"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logger.debug(f"📊 [港股緩存] 加載緩存失败: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """保存緩存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.debug(f"📊 [港股緩存] 保存緩存失败: {e}")
    
    def _is_cache_valid(self, key: str) -> bool:
        """檢查緩存是否有效"""
        if key not in self.cache:
            return False
        
        cache_time = self.cache[key].get('timestamp', 0)
        return (time.time() - cache_time) < self.cache_ttl
    
    def _normalize_hk_symbol(self, symbol: str) -> str:
        """標準化港股代碼"""
        # 移除.HK後缀
        clean_symbol = symbol.replace('.HK', '').replace('.hk', '')
        
        # 補齊到5位數字
        if len(clean_symbol) == 4:
            clean_symbol = '0' + clean_symbol
        elif len(clean_symbol) == 3:
            clean_symbol = '00' + clean_symbol
        elif len(clean_symbol) == 2:
            clean_symbol = '000' + clean_symbol
        elif len(clean_symbol) == 1:
            clean_symbol = '0000' + clean_symbol
        
        return clean_symbol
    
    def get_company_name(self, symbol: str) -> str:
        """
        獲取港股公司名稱
        
        Args:
            symbol: 港股代碼
            
        Returns:
            str: 公司名稱
        """
        try:
            # 檢查緩存
            cache_key = f"name_{symbol}"
            if self._is_cache_valid(cache_key):
                cached_name = self.cache[cache_key]['data']
                logger.debug(f"📊 [港股緩存] 從緩存獲取公司名稱: {symbol} -> {cached_name}")
                return cached_name
            
            # 方案1：使用內置映射
            normalized_symbol = self._normalize_hk_symbol(symbol)
            
            # 嘗試多種格式匹配
            for format_symbol in [symbol, normalized_symbol, f"{normalized_symbol}.HK"]:
                if format_symbol in self.hk_stock_names:
                    company_name = self.hk_stock_names[format_symbol]
                    
                    # 緩存結果
                    self.cache[cache_key] = {
                        'data': company_name,
                        'timestamp': time.time(),
                        'source': 'builtin_mapping'
                    }
                    self._save_cache()
                    
                    logger.debug(f"📊 [港股映射] 獲取公司名稱: {symbol} -> {company_name}")
                    return company_name
            
            # 方案2：優先嘗試AKShare API獲取（有速率限制保護）
            try:
                # 速率限制保護
                current_time = time.time()
                if current_time - self.last_request_time < self.rate_limit_wait:
                    wait_time = self.rate_limit_wait - (current_time - self.last_request_time)
                    logger.debug(f"📊 [港股API] 速率限制保護，等待 {wait_time:.1f} 秒")
                    time.sleep(wait_time)

                self.last_request_time = time.time()

                # 優先嘗試AKShare獲取
                try:
                    from tradingagents.dataflows.akshare_utils import get_hk_stock_info_akshare
                    logger.debug(f"📊 [港股API] 優先使用AKShare獲取: {symbol}")

                    akshare_info = get_hk_stock_info_akshare(symbol)
                    if akshare_info and isinstance(akshare_info, dict) and 'name' in akshare_info:
                        akshare_name = akshare_info['name']
                        if not akshare_name.startswith('港股'):
                            # 緩存AKShare結果
                            self.cache[cache_key] = {
                                'data': akshare_name,
                                'timestamp': time.time(),
                                'source': 'akshare_api'
                            }
                            self._save_cache()

                            logger.debug(f"📊 [港股AKShare] 獲取公司名稱: {symbol} -> {akshare_name}")
                            return akshare_name
                except Exception as e:
                    logger.debug(f"📊 [港股AKShare] AKShare獲取失败: {e}")

                # 备用：嘗試從統一接口獲取（包含Yahoo Finance）
                from tradingagents.dataflows.interface import get_hk_stock_info_unified
                hk_info = get_hk_stock_info_unified(symbol)

                if hk_info and isinstance(hk_info, dict) and 'name' in hk_info:
                    api_name = hk_info['name']
                    if not api_name.startswith('港股'):
                        # 緩存API結果
                        self.cache[cache_key] = {
                            'data': api_name,
                            'timestamp': time.time(),
                            'source': 'unified_api'
                        }
                        self._save_cache()

                        logger.debug(f"📊 [港股統一API] 獲取公司名稱: {symbol} -> {api_name}")
                        return api_name

            except Exception as e:
                logger.debug(f"📊 [港股API] API獲取失败: {e}")
            
            # 方案3：生成友好的默認名稱
            clean_symbol = self._normalize_hk_symbol(symbol)
            default_name = f"港股{clean_symbol}"
            
            # 緩存默認結果（較短的TTL）
            self.cache[cache_key] = {
                'data': default_name,
                'timestamp': time.time() - self.cache_ttl + 3600,  # 1小時後過期
                'source': 'default'
            }
            self._save_cache()
            
            logger.debug(f"📊 [港股默認] 使用默認名稱: {symbol} -> {default_name}")
            return default_name
            
        except Exception as e:
            logger.error(f"❌ [港股] 獲取公司名稱失败: {e}")
            clean_symbol = self._normalize_hk_symbol(symbol)
            return f"港股{clean_symbol}"
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """
        獲取港股基本信息
        
        Args:
            symbol: 港股代碼
            
        Returns:
            Dict: 港股信息
        """
        try:
            company_name = self.get_company_name(symbol)
            
            return {
                'symbol': symbol,
                'name': company_name,
                'currency': 'HKD',
                'exchange': 'HKG',
                'market': '港股',
                'source': 'improved_hk_provider'
            }
            
        except Exception as e:
            logger.error(f"❌ [港股] 獲取股票信息失败: {e}")
            clean_symbol = self._normalize_hk_symbol(symbol)
            return {
                'symbol': symbol,
                'name': f'港股{clean_symbol}',
                'currency': 'HKD',
                'exchange': 'HKG',
                'market': '港股',
                'source': 'error',
                'error': str(e)
            }


# 全局實例
_improved_hk_provider = None

def get_improved_hk_provider() -> ImprovedHKStockProvider:
    """獲取改進的港股提供器實例"""
    global _improved_hk_provider
    if _improved_hk_provider is None:
        _improved_hk_provider = ImprovedHKStockProvider()
    return _improved_hk_provider


def get_hk_company_name_improved(symbol: str) -> str:
    """
    獲取港股公司名稱的改進版本
    
    Args:
        symbol: 港股代碼
        
    Returns:
        str: 公司名稱
    """
    provider = get_improved_hk_provider()
    return provider.get_company_name(symbol)


def get_hk_stock_info_improved(symbol: str) -> Dict[str, Any]:
    """
    獲取港股信息的改進版本
    
    Args:
        symbol: 港股代碼
        
    Returns:
        Dict: 港股信息
    """
    provider = get_improved_hk_provider()
    return provider.get_stock_info(symbol)
