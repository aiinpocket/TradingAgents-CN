#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MongoDB數據驗證腳本
驗證A股股票基础信息是否正確同步到MongoDB
"""

import os
from typing import Dict, Any, List
from datetime import datetime

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    print("❌ pymongo未安裝，請運行: pip install pymongo")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv未安裝，将使用系統環境變量")

def get_mongodb_config() -> Dict[str, Any]:
    """獲取MongoDB配置"""
    return {
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', 27018)),
        'username': os.getenv('MONGODB_USERNAME'),
        'password': os.getenv('MONGODB_PASSWORD'),
        'database': os.getenv('MONGODB_DATABASE', 'tradingagents'),
        'auth_source': os.getenv('MONGODB_AUTH_SOURCE', 'admin')
    }

def connect_mongodb():
    """連接MongoDB"""
    if not MONGODB_AVAILABLE:
        return None, None
    
    config = get_mongodb_config()
    
    try:
        # 構建連接字符串
        if config.get('username') and config.get('password'):
            connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['auth_source']}"
        else:
            connection_string = f"mongodb://{config['host']}:{config['port']}/"
        
        # 創建客戶端
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000
        )
        
        # 測試連接
        client.admin.command('ping')
        
        # 選擇數據庫
        db = client[config['database']]
        
        print(f"✅ MongoDB連接成功: {config['host']}:{config['port']}")
        return client, db
        
    except Exception as e:
        print(f"❌ MongoDB連接失败: {e}")
        return None, None

def verify_stock_data(db):
    """驗證股票數據"""
    if db is None:
        return
    
    collection = db['stock_basic_info']
    
    print("\n" + "="*60)
    print("📊 MongoDB中的A股基础信息驗證")
    print("="*60)
    
    # 1. 总記錄數
    total_count = collection.count_documents({})
    print(f"📈 总記錄數: {total_count:,}")
    
    # 2. 按市場統計
    print("\n🏢 市場分布:")
    market_pipeline = [
        {'$group': {
            '_id': '$sse',
            'count': {'$sum': 1}
        }},
        {'$sort': {'count': -1}}
    ]
    
    for market in collection.aggregate(market_pipeline):
        market_name = '上海' if market['_id'] == 'sh' else '深圳'
        print(f"  {market_name}市場 ({market['_id']}): {market['count']:,} 條")
    
    # 3. 按分類統計
    print("\n📊 分類分布:")
    category_pipeline = [
        {'$group': {
            '_id': '$sec',
            'count': {'$sum': 1}
        }},
        {'$sort': {'count': -1}}
    ]
    
    for category in collection.aggregate(category_pipeline):
        category_name = {
            'stock_cn': '股票',
            'etf_cn': 'ETF基金',
            'index_cn': '指數',
            'bond_cn': '债券'
        }.get(category['_id'], category['_id'])
        print(f"  {category_name}: {category['count']:,} 條")
    
    # 4. 數據樣本
    print("\n📋 數據樣本 (前10條):")
    samples = collection.find({}).limit(10)
    
    for i, stock in enumerate(samples, 1):
        market_name = '上海' if stock['sse'] == 'sh' else '深圳'
        print(f"  {i:2d}. {stock['code']} - {stock['name']} ({market_name})")
    
    # 5. 最近更新時間
    latest = collection.find_one({}, sort=[('updated_at', -1)])
    if latest and 'updated_at' in latest:
        print(f"\n🕒 最近更新時間: {latest['updated_at']}")
    
    # 6. 數據完整性檢查
    print("\n🔍 數據完整性檢查:")
    
    # 檢查必需字段
    required_fields = ['code', 'name', 'sse']
    for field in required_fields:
        missing_count = collection.count_documents({field: {'$exists': False}})
        null_count = collection.count_documents({field: None})
        empty_count = collection.count_documents({field: ''})
        
        if missing_count + null_count + empty_count == 0:
            print(f"  ✅ {field}: 完整")
        else:
            print(f"  ⚠️ {field}: 缺失{missing_count}, 空值{null_count}, 空字符串{empty_count}")
    
    # 7. 查詢示例
    print("\n🔍 查詢示例:")
    
    # 查找平安相關股票
    ping_an_stocks = list(collection.find(
        {'name': {'$regex': '平安', '$options': 'i'}}
    ).limit(5))
    
    if ping_an_stocks:
        print("  平安相關股票:")
        for stock in ping_an_stocks:
            market_name = '上海' if stock['sse'] == 'sh' else '深圳'
            print(f"    {stock['code']} - {stock['name']} ({market_name})")
    
    # 查找ETF
    etf_count = collection.count_documents({'sec': 'etf_cn'})
    print(f"  ETF基金总數: {etf_count:,}")
    
    # 查找指數
    index_count = collection.count_documents({'sec': 'index_cn'})
    print(f"  指數总數: {index_count:,}")

def main():
    """主函數"""
    print("🔍 正在驗證MongoDB中的A股基础信息...")
    
    # 連接MongoDB
    client, db = connect_mongodb()
    
    if client is None or db is None:
        print("❌ 無法連接到MongoDB，驗證失败")
        return
    
    try:
        # 驗證數據
        verify_stock_data(db)
        
        print("\n✅ 數據驗證完成")
        
    except Exception as e:
        print(f"❌ 驗證過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 關闭連接
        if client:
            client.close()
            print("🔒 MongoDB連接已關闭")

if __name__ == "__main__":
    main()