#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finnhub示例數據下載腳本

這個腳本用於創建示例的Finnhub數據文件，以便測試新聞數據功能。
在沒有真實API密鑰或數據的情況下，可以使用此腳本創建測試數據。
"""

import os
import json
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.dataflows.config import get_config, set_config

def create_sample_news_data(ticker, data_dir, days=7):
    """
    創建示例新聞數據
    
    Args:
        ticker (str): 股票代碼
        data_dir (str): 數據目錄
        days (int): 生成多少天的數據
    """
    # 創建目錄結構
    news_dir = os.path.join(data_dir, "finnhub_data", "news_data")
    os.makedirs(news_dir, exist_ok=True)
    
    # 生成示例新聞數據
    sample_news = {
        "AAPL": [
            "蘋果公司發布新款iPhone，銷量預期強勁",
            "蘋果在人工智能領域取得重大突破",
            "蘋果股價創歷史新高，投資者信心增強",
            "蘋果宣布新的環保計劃，致力於碳中和",
            "蘋果服務業務收入持續增長"
        ],
        "TSLA": [
            "特斯拉交付量超預期，股價大漲",
            "特斯拉自動駕駛技術獲得新突破",
            "特斯拉在中國市場表現強勁",
            "特斯拉能源業務快速增長",
            "馬斯克宣布特斯拉新工廠計劃"
        ],
        "MSFT": [
            "微軟云業務Azure收入大幅增長",
            "微軟AI助手Copilot用戶數量激增",
            "微軟與OpenAI合作深化",
            "微軟Office 365訂閱用戶創新高",
            "微軟遊戲業務表現亮眼"
        ],
        "GOOGL": [
            "谷歌搜索廣告收入穩定增長",
            "谷歌云計算業務競爭力提升",
            "谷歌AI模型Gemini性能優異",
            "YouTube廣告收入超預期",
            "谷歌在量子計算領域取得進展"
        ],
        "AMZN": [
            "亞馬遜AWS云服務市場份額擴大",
            "亞馬遜Prime會員數量持續增長",
            "亞馬遜物流網絡進一步優化",
            "亞馬遜廣告業務快速發展",
            "亞馬遜在AI領域投資加大"
        ]
    }
    
    # 為指定股票生成數據
    if ticker not in sample_news:
        # 如果不在預定義列表中，使用通用模板
        headlines = [
            f"{ticker}公司業績超預期，股價上漲",
            f"{ticker}宣布重大戰略調整",
            f"{ticker}在行業中地位穩固",
            f"{ticker}管理層對未來前景樂觀",
            f"{ticker}獲得分析師買入評級"
        ]
    else:
        headlines = sample_news[ticker]
    
    # 生成日期數據
    data = {}
    current_date = datetime.now()
    
    for i in range(days):
        date = current_date - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # 每天生成1-3條新聞
        num_news = random.randint(1, 3)
        daily_news = []
        
        for j in range(num_news):
            headline_idx = (i + j) % len(headlines)
            headline = headlines[headline_idx]
            
            news_item = {
                "headline": headline,
                "summary": f"根據最新報道，{headline}。這一訊息對投資者來說具有重要意義，可能會影響股票的短期和長期表現。分析師認為這一發展符合公司的戰略方向。",
                "source": "財經新聞",
                "url": f"https://example.com/news/{ticker.lower()}-{date_str}-{j+1}",
                "datetime": int(date.timestamp())
            }
            daily_news.append(news_item)
        
        data[date_str] = daily_news
    
    # 保存數據文件
    file_path = os.path.join(news_dir, f"{ticker}_data_formatted.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f" 創建示例新聞數據: {file_path}")
    logger.info(f"   包含 {len(data)} 天的數據，共 {sum(len(news) for news in data.values())} 條新聞")
    
    return file_path

def create_sample_insider_data(ticker, data_dir, data_type):
    """
    創建示例內部人數據
    
    Args:
        ticker (str): 股票代碼
        data_dir (str): 數據目錄
        data_type (str): 數據類型 (insider_senti 或 insider_trans)
    """
    # 創建目錄結構
    insider_dir = os.path.join(data_dir, "finnhub_data", data_type)
    os.makedirs(insider_dir, exist_ok=True)
    
    data = {}
    current_date = datetime.now()
    
    if data_type == "insider_senti":
        # 內部人情緒數據
        for i in range(3):  # 生成3個月的數據
            date = current_date - timedelta(days=30*i)
            date_str = date.strftime("%Y-%m-%d")
            
            sentiment_data = [{
                "year": date.year,
                "month": date.month,
                "change": round(random.uniform(-1000000, 1000000), 2),
                "mspr": round(random.uniform(0, 1), 4)
            }]
            
            data[date_str] = sentiment_data
    
    elif data_type == "insider_trans":
        # 內部人交易數據
        executives = ["CEO John Smith", "CFO Jane Doe", "CTO Mike Johnson"]
        
        for i in range(7):  # 生成7天的數據
            date = current_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            if random.random() > 0.7:  # 30%概率有交易
                transaction_data = [{
                    "filingDate": date_str,
                    "name": random.choice(executives),
                    "change": random.randint(-10000, 10000),
                    "share": random.randint(1000, 50000),
                    "transactionPrice": round(random.uniform(100, 300), 2),
                    "transactionCode": random.choice(["S", "P", "A"]),
                    "transactionDate": date_str
                }]
                data[date_str] = transaction_data
    
    # 保存數據文件
    file_path = os.path.join(insider_dir, f"{ticker}_data_formatted.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f" 創建示例{data_type}數據: {file_path}")
    return file_path

def main():
    """
    主函數
    """
    logger.info(f"Finnhub示例數據下載腳本")
    logger.info(f"=")
    
    # 獲取配置
    config = get_config()
    data_dir = config.get('data_dir')
    
    if not data_dir:
        logger.error(f" 數據目錄未配置")
        return
    
    logger.info(f"數據目錄: {data_dir}")
    
    # 確保數據目錄存在
    os.makedirs(data_dir, exist_ok=True)
    
    # 常用股票代碼
    tickers = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"]
    
    logger.info(f"\n創建示例數據...")
    
    # 為每個股票創建新聞數據
    for ticker in tickers:
        create_sample_news_data(ticker, data_dir, days=7)
        create_sample_insider_data(ticker, data_dir, "insider_senti")
        create_sample_insider_data(ticker, data_dir, "insider_trans")
    
    logger.info(f"\n=== 數據創建完成 ===")
    logger.info(f"數據位置: {data_dir}")
    logger.info(f"包含以下股票的示例數據:")
    for ticker in tickers:
        logger.info(f"  - {ticker}: 新聞、內部人情緒、內部人交易")
    
    logger.info(f"\n現在您可以測試Finnhub新聞功能了！")
    
    # 測試數據獲取
    logger.info(f"\n=== 測試數據獲取 ===")
    try:
        from tradingagents.dataflows.interface import get_finnhub_news

        
        result = get_finnhub_news(
            ticker="AAPL",
            curr_date=datetime.now().strftime("%Y-%m-%d"),
            look_back_days=3
        )
        
        if result and "無法獲取" not in result:
            logger.info(f" 新聞數據獲取成功！")
            logger.info(f"示例內容: {result[:200]}...")
        else:
            logger.error(f" 新聞數據獲取失敗，請檢查配置")
            logger.info(f"返回結果: {result}")
    
    except Exception as e:
        logger.error(f" 測試失敗: {e}")

if __name__ == "__main__":
    main()