#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finnhub數據下載腳本

這個腳本用於從Finnhub API下載新聞數據、內部人情緒數據和內部人交易數據。
支持批量下載和增量更新。

使用方法:
    python scripts/download_finnhub_data.py --data-type news --symbols AAPL,TSLA,MSFT
    python scripts/download_finnhub_data.py --all
    python scripts/download_finnhub_data.py --force-refresh
"""

import os
import sys
import json
import argparse
import requests
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 導入項目模塊
try:
    from tradingagents.utils.logging_manager import get_logger
    from tradingagents.config.config_manager import config_manager
    logger = get_logger('finnhub_downloader')
except ImportError as e:
    print(f"❌ 導入模塊失敗: {e}")
    print("請確保在項目根目錄運行此腳本")
    sys.exit(1)

class FinnhubDataDownloader:
    """Finnhub數據下載器"""
    
    def __init__(self, api_key: str = None, data_dir: str = None):
        """
        初始化下載器
        
        Args:
            api_key: Finnhub API密鑰
            data_dir: 數據存儲目錄
        """
        # 獲取API密鑰
        self.api_key = api_key or os.getenv('FINNHUB_API_KEY')
        if not self.api_key:
            raise ValueError("❌ 未找到Finnhub API密鑰，請設置FINNHUB_API_KEY環境變量")
        
        # 獲取數據目錄
        if data_dir:
            self.data_dir = data_dir
        else:
            # 優先使用環境變量，然後是項目根目錄
            env_data_dir = os.getenv('TRADINGAGENTS_DATA_DIR')
            if env_data_dir:
                self.data_dir = env_data_dir
            else:
                # 使用項目根目錄下的data目錄
                self.data_dir = str(project_root / "data")

            logger.info(f"🔍 數據目錄來源: {'環境變量' if env_data_dir else '項目根目錄'}")
        
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        
        logger.info(f"📁 數據目錄: {self.data_dir}")
        logger.info(f"🔑 API密鑰: {self.api_key[:8]}...")
    
    def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        發送API請求
        
        Args:
            endpoint: API端點
            params: 請求參數
            
        Returns:
            API響應數據
        """
        params['token'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            # 檢查API限制
            if response.status_code == 429:
                logger.warning("⚠️ API調用頻率限制，等待60秒...")
                time.sleep(60)
                return self._make_request(endpoint, params)
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API請求失敗: {e}")
            return {}
    
    def download_news_data(self, symbols: List[str], days: int = 7, force_refresh: bool = False):
        """
        下載新聞數據
        
        Args:
            symbols: 股票代碼列表
            days: 下載多少天的數據
            force_refresh: 是否強制刷新
        """
        logger.info(f"📰 開始下載新聞數據，股票: {symbols}, 天數: {days}")
        
        # 創建目錄
        news_dir = Path(self.data_dir) / "finnhub_data" / "news_data"
        news_dir.mkdir(parents=True, exist_ok=True)
        
        # 計算日期範圍
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for symbol in symbols:
            logger.info(f"📰 下載 {symbol} 的新聞數據...")
            
            # 檢查文件是否存在且有效
            file_path = news_dir / f"{symbol}_data_formatted.json"
            if file_path.exists() and not force_refresh:
                # 檢查文件是否有內容
                try:
                    file_size = file_path.stat().st_size
                    if file_size > 10:  # 文件大小大於10字節才認為有效
                        logger.info(f"📄 {symbol} 數據文件已存在且有效 (大小: {file_size} 字節)，跳過下載")
                        continue
                    else:
                        logger.warning(f"⚠️ {symbol} 數據文件存在但為空 (大小: {file_size} 字節)，重新下載")
                except Exception as e:
                    logger.warning(f"⚠️ 檢查 {symbol} 文件狀態失敗: {e}，重新下載")

            logger.info(f"📥 開始下載 {symbol} 的新聞數據...")
            
            # 下載新聞數據
            params = {
                'symbol': symbol,
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d')
            }
            
            news_data = self._make_request('company-news', params)

            logger.info(f"🔍 API響應類型: {type(news_data)}, 長度: {len(news_data) if isinstance(news_data, list) else 'N/A'}")

            if news_data and isinstance(news_data, list) and len(news_data) > 0:
                # 格式化數據
                formatted_data = []
                for item in news_data:
                    formatted_item = {
                        'datetime': item.get('datetime', 0),
                        'headline': item.get('headline', ''),
                        'summary': item.get('summary', ''),
                        'url': item.get('url', ''),
                        'source': item.get('source', ''),
                        'category': item.get('category', ''),
                        'sentiment': item.get('sentiment', {})
                    }
                    formatted_data.append(formatted_item)

                # 保存數據
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(formatted_data, f, ensure_ascii=False, indent=2)

                    # 驗證文件保存
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        logger.info(f"✅ {symbol} 新聞數據已保存: {len(formatted_data)} 條, 文件大小: {file_size} 字節")
                    else:
                        logger.error(f"❌ {symbol} 文件保存失敗，文件不存在")

                except Exception as e:
                    logger.error(f"❌ {symbol} 文件保存異常: {e}")

            elif news_data and isinstance(news_data, dict):
                logger.warning(f"⚠️ {symbol} API返回字典而非列表: {news_data}")
            else:
                logger.warning(f"⚠️ {symbol} 新聞數據下載失敗或為空")
            
            # 避免API限制
            time.sleep(1)
    
    def download_insider_sentiment(self, symbols: List[str], force_refresh: bool = False):
        """
        下載內部人情緒數據
        
        Args:
            symbols: 股票代碼列表
            force_refresh: 是否強制刷新
        """
        logger.info(f"💭 開始下載內部人情緒數據，股票: {symbols}")
        
        # 創建目錄
        sentiment_dir = Path(self.data_dir) / "finnhub_data" / "insider_senti"
        sentiment_dir.mkdir(parents=True, exist_ok=True)
        
        for symbol in symbols:
            logger.info(f"💭 下載 {symbol} 的內部人情緒數據...")
            
            # 檢查文件是否存在
            file_path = sentiment_dir / f"{symbol}_data_formatted.json"
            if file_path.exists() and not force_refresh:
                logger.info(f"📄 {symbol} 情緒數據文件已存在，跳過下載")
                continue
            
            # 下載情緒數據
            params = {'symbol': symbol}
            sentiment_data = self._make_request('stock/insider-sentiment', params)
            
            if sentiment_data and 'data' in sentiment_data:
                # 保存數據
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(sentiment_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✅ {symbol} 內部人情緒數據已保存")
            else:
                logger.warning(f"⚠️ {symbol} 內部人情緒數據下載失敗")
            
            # 避免API限制
            time.sleep(1)
    
    def download_insider_transactions(self, symbols: List[str], force_refresh: bool = False):
        """
        下載內部人交易數據
        
        Args:
            symbols: 股票代碼列表
            force_refresh: 是否強制刷新
        """
        logger.info(f"💰 開始下載內部人交易數據，股票: {symbols}")
        
        # 創建目錄
        trans_dir = Path(self.data_dir) / "finnhub_data" / "insider_trans"
        trans_dir.mkdir(parents=True, exist_ok=True)
        
        for symbol in symbols:
            logger.info(f"💰 下載 {symbol} 的內部人交易數據...")
            
            # 檢查文件是否存在
            file_path = trans_dir / f"{symbol}_data_formatted.json"
            if file_path.exists() and not force_refresh:
                logger.info(f"📄 {symbol} 交易數據文件已存在，跳過下載")
                continue
            
            # 下載交易數據
            params = {'symbol': symbol}
            trans_data = self._make_request('stock/insider-transactions', params)
            
            if trans_data and 'data' in trans_data:
                # 保存數據
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(trans_data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"✅ {symbol} 內部人交易數據已保存")
            else:
                logger.warning(f"⚠️ {symbol} 內部人交易數據下載失敗")
            
            # 避免API限制
            time.sleep(1)

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description='Finnhub數據下載腳本')
    
    parser.add_argument('--data-type', 
                       choices=['news', 'sentiment', 'transactions', 'all'],
                       default='all',
                       help='要下載的數據類型')
    
    parser.add_argument('--symbols',
                       type=str,
                       default='AAPL,TSLA,MSFT,GOOGL,AMZN',
                       help='股票代碼，用逗號分隔')
    
    parser.add_argument('--days',
                       type=int,
                       default=7,
                       help='下載多少天的新聞數據')
    
    parser.add_argument('--force-refresh',
                       action='store_true',
                       help='強制刷新已存在的數據')
    
    parser.add_argument('--all',
                       action='store_true',
                       help='下載所有類型的數據')
    
    parser.add_argument('--api-key',
                       type=str,
                       help='Finnhub API密鑰')
    
    parser.add_argument('--data-dir',
                       type=str,
                       help='數據存儲目錄')
    
    args = parser.parse_args()
    
    # 解析股票代碼
    symbols = [s.strip().upper() for s in args.symbols.split(',')]
    
    try:
        # 創建下載器
        downloader = FinnhubDataDownloader(
            api_key=args.api_key,
            data_dir=args.data_dir
        )
        
        # 確定要下載的數據類型
        if args.all:
            data_types = ['news', 'sentiment', 'transactions']
        else:
            data_types = [args.data_type] if args.data_type != 'all' else ['news', 'sentiment', 'transactions']
        
        logger.info(f"🚀 開始下載Finnhub數據")
        logger.info(f"📊 股票代碼: {symbols}")
        logger.info(f"📋 數據類型: {data_types}")
        logger.info(f"🔄 強制刷新: {args.force_refresh}")
        
        # 下載數據
        for data_type in data_types:
            if data_type == 'news':
                downloader.download_news_data(symbols, args.days, args.force_refresh)
            elif data_type == 'sentiment':
                downloader.download_insider_sentiment(symbols, args.force_refresh)
            elif data_type == 'transactions':
                downloader.download_insider_transactions(symbols, args.force_refresh)
        
        logger.info("🎉 數據下載完成！")
        
    except Exception as e:
        logger.error(f"❌ 下載失敗: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
