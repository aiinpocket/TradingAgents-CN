#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版股票列表獲取示例
演示如何使用從tdx_servers_config.json配置文件中獲取數據服務器參數
"""

from enhanced_stock_list_fetcher import enhanced_fetch_stock_list
import pandas as pd
import json

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('default')


def demo_stock_list_fetcher():
    """演示增强版股票列表獲取功能"""
    logger.info(f"=== 增强版股票列表獲取演示 ===")
    logger.info(f"\n功能特點:")
    logger.info(f"1. 從tdx_servers_config.json自動加載服務器配置")
    logger.info(f"2. 支持服務器故障轉移")
    logger.info(f"3. 獲取完整的股票、指數、ETF信息")
    logger.info(f"4. 自動數據清洗和去重")
    
    # 演示不同類型的數據獲取
    data_types = {
        'stock': '股票',
        'index': '指數', 
        'etf': 'ETF基金',
        'all': '全部數據'
    }
    
    for type_key, type_name in data_types.items():
        logger.info(f"\n=== 獲取{type_name}數據 ===")
        
        try:
            # 調用增强版股票列表獲取函數
            result = enhanced_fetch_stock_list(
                type_=type_key,
                enable_server_failover=True,  # 啟用服務器故障轉移
                max_retries=2  # 每個服務器最多重試2次
            )
            
            if result is not None and not result.empty:
                logger.info(f"✅ 成功獲取 {len(result)} 條{type_name}數據")
                
                # 轉換為DataFrame便於查看
                df = pd.DataFrame(result)
                logger.info(f"\n數據列: {list(df.columns)}")
                
                # 顯示前5條數據
                logger.info(f"\n前5條{type_name}數據:")
                print(df.head().to_string(index=False))
                
                # 顯示統計信息
                if 'sse' in df.columns:
                    market_counts = df['sse'].value_counts()
                    logger.info(f"\n市場分布:")
                    for market, count in market_counts.items():
                        market_name = '上海' if market == 1 else '深圳'
                        logger.info(f"  {market_name}市場: {count} 只")
                        
            else:
                logger.error(f"❌ 未能獲取到{type_name}數據")
                
        except Exception as e:
            logger.error(f"❌ 獲取{type_name}數據時發生錯誤: {str(e)}")
            
        # 只演示第一種類型，避免過多網絡請求
        logger.warning(f"\n註意: 為避免過多網絡請求，此演示只獲取股票數據")
        logger.info(f"實际使用時可以獲取所有類型的數據")
        break

def show_usage_examples():
    """顯示使用示例"""
    logger.info(f"\n=== 使用示例 ===")
    
    examples = [
        {
            'title': '獲取所有股票數據',
            'code': '''result = enhanced_fetch_stock_list(type_='stock')'''
        },
        {
            'title': '獲取所有指數數據',
            'code': '''result = enhanced_fetch_stock_list(type_='index')'''
        },
        {
            'title': '獲取ETF數據',
            'code': '''result = enhanced_fetch_stock_list(type_='etf')'''
        },
        {
            'title': '獲取全部數據（股票+指數+ETF）',
            'code': '''result = enhanced_fetch_stock_list(type_='all')'''
        },
        {
            'title': '啟用服務器故障轉移',
            'code': '''result = enhanced_fetch_stock_list(
    type_='stock',
    enable_server_failover=True,
    max_retries=3
)'''
        },
        {
            'title': '指定服務器IP和端口',
            'code': '''result = enhanced_fetch_stock_list(
    type_='stock',
    ip='115.238.56.198',
    port=7709
)'''
        }
    ]
    
    for i, example in enumerate(examples, 1):
        logger.info(f"\n{i}. {example['title']}:")
        logger.info(f"```python\n{example['code']}\n```")

if __name__ == "__main__":
    # 顯示使用示例
    show_usage_examples()
    
    # 演示功能（註釋掉以避免實际網絡請求）
    logger.info(f"\n")
    logger.info(f"如需測試實际功能，請取消下面代碼的註釋:")
    logger.info(f"# demo_stock_list_fetcher()")
    
    # 取消註釋下面這行來運行實际演示
    demo_stock_list_fetcher()