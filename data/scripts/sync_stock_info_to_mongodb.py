#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票基础信息同步到MongoDB
從通達信獲取股票基础信息並同步到MongoDB數據庫
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import pandas as pd

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')

# 添加項目根目錄到路徑
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from enhanced_stock_list_fetcher import enhanced_fetch_stock_list

try:
    import pymongo
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logger.error(f"❌ pymongo未安裝，請運行: pip install pymongo")

class StockInfoSyncer:
    """A股股票信息同步器"""
    
    def __init__(self, mongodb_config: Dict[str, Any] = None):
        """
        初始化同步器
        
        Args:
            mongodb_config: MongoDB配置字典
        """
        self.mongodb_client = None
        self.mongodb_db = None
        self.collection_name = "stock_basic_info"
        
        # 使用提供的配置或從環境變量讀取
        if mongodb_config:
            self.mongodb_config = mongodb_config
        else:
            self.mongodb_config = self._load_mongodb_config_from_env()
        
        # 初始化MongoDB連接
        self._init_mongodb()
    
    def _load_mongodb_config_from_env(self) -> Dict[str, Any]:
        """從環境變量加載MongoDB配置"""
        from dotenv import load_dotenv
        load_dotenv()
        
        # 優先使用連接字符串
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        if connection_string:
            return {
                'connection_string': connection_string,
                'database': os.getenv('MONGODB_DATABASE', 'tradingagents')
            }
        
        # 使用分離的配置參數
        return {
            'host': os.getenv('MONGODB_HOST', 'localhost'),
            'port': int(os.getenv('MONGODB_PORT', 27017)),
            'username': os.getenv('MONGODB_USERNAME'),
            'password': os.getenv('MONGODB_PASSWORD'),
            'database': os.getenv('MONGODB_DATABASE', 'tradingagents'),
            'auth_source': os.getenv('MONGODB_AUTH_SOURCE', 'admin')
        }
    
    def _init_mongodb(self):
        """初始化MongoDB連接"""
        if not MONGODB_AVAILABLE:
            logger.error(f"❌ MongoDB不可用，請安裝pymongo")
            return
        
        try:
            # 構建連接字符串
            if 'connection_string' in self.mongodb_config:
                connection_string = self.mongodb_config['connection_string']
            else:
                config = self.mongodb_config
                if config.get('username') and config.get('password'):
                    connection_string = f"mongodb://{config['username']}:{config['password']}@{config['host']}:{config['port']}/{config['auth_source']}"
                else:
                    connection_string = f"mongodb://{config['host']}:{config['port']}/"
            
            # 創建客戶端
            self.mongodb_client = MongoClient(
                connection_string,
                serverSelectionTimeoutMS=5000  # 5秒超時
            )
            
            # 測試連接
            self.mongodb_client.admin.command('ping')
            
            # 選擇數據庫
            self.mongodb_db = self.mongodb_client[self.mongodb_config['database']]
            
            logger.info(f"✅ MongoDB連接成功: {self.mongodb_config.get('host', 'unknown')}")
            
            # 創建索引
            self._create_indexes()
            
        except Exception as e:
            logger.error(f"❌ MongoDB連接失败: {e}")
            self.mongodb_client = None
            self.mongodb_db = None
    
    def _create_indexes(self):
        """創建數據庫索引"""
        if self.mongodb_db is None:
            return
        
        try:
            collection = self.mongodb_db[self.collection_name]
            
            # 創建索引
            indexes = [
                ('code', 1),  # 股票代碼索引
                ('sse', 1),   # 市場索引
                ([('code', 1), ('sse', 1)], {'unique': True}),  # 複合唯一索引
                ('sec', 1),   # 股票分類索引
                ('updated_at', -1),  # 更新時間索引
                ('name', 'text')  # 股票名稱文本索引
            ]
            
            for index in indexes:
                if isinstance(index, tuple) and len(index) == 2 and isinstance(index[1], dict):
                    # 帶選項的索引
                    collection.create_index(index[0], **index[1])
                else:
                    # 普通索引
                    collection.create_index(index)
            
            logger.info(f"✅ 數據庫索引創建完成: {self.collection_name}")
            
        except Exception as e:
            logger.warning(f"⚠️ 創建索引時出現警告: {e}")
    
    def fetch_stock_data(self, stock_type: str = 'stock') -> Optional[pd.DataFrame]:
        """從通達信獲取股票數據"""
        logger.info(f"📊 正在從通達信獲取{stock_type}數據...")
        
        try:
            stock_data = enhanced_fetch_stock_list(
                type_=stock_type,
                enable_server_failover=True,
                max_retries=3
            )
            
            if stock_data is not None and not stock_data.empty:
                logger.info(f"✅ 成功獲取 {len(stock_data)} 條{stock_type}數據")
                return stock_data
            else:
                logger.error(f"❌ 未能獲取到{stock_type}數據")
                return None
                
        except Exception as e:
            logger.error(f"❌ 獲取{stock_type}數據時發生錯誤: {e}")
            return None
    
    def sync_to_mongodb(self, stock_data: pd.DataFrame) -> bool:
        """将股票數據同步到MongoDB"""
        if self.mongodb_db is None:
            logger.error(f"❌ MongoDB未連接，無法同步數據")
            return False
        
        if stock_data is None or stock_data.empty:
            logger.error(f"❌ 没有數據需要同步")
            return False
        
        try:
            collection = self.mongodb_db[self.collection_name]
            current_time = datetime.utcnow()
            
            # 準备批量操作
            bulk_operations = []
            
            for idx, row in stock_data.iterrows():
                # 構建文档
                document = {
                    'code': row['code'],
                    'name': row['name'],
                    'sse': row['sse'],
                    'market': row.get('market', '深圳' if row['sse'] == 'sz' else '上海'),
                    'sec': row.get('sec', 'unknown'),
                    'category': row.get('category', '未知'),
                    'volunit': row.get('volunit', 0),
                    'decimal_point': row.get('decimal_point', 0),
                    'pre_close': row.get('pre_close', 0.0),
                    'updated_at': current_time,
                    'sync_source': 'tdx',  # 數據來源標识
                    'data_version': '1.0'
                }
                
                # 添加創建時間（仅在插入時）
                update_doc = {
                    '$set': document,
                    '$setOnInsert': {'created_at': current_time}
                }
                
                # 使用upsert操作
                bulk_operations.append(
                    pymongo.UpdateOne(
                        {'code': row['code'], 'sse': row['sse']},
                        update_doc,
                        upsert=True
                    )
                )
            
            # 執行批量操作
            if bulk_operations:
                result = collection.bulk_write(bulk_operations)
                
                logger.info(f"📊 數據同步完成:")
                logger.info(f"  - 插入新記錄: {result.upserted_count}")
                logger.info(f"  - 更新記錄: {result.modified_count}")
                logger.info(f"  - 匹配記錄: {result.matched_count}")
                
                return True
            else:
                logger.error(f"❌ 没有數據需要同步")
                return False
                
        except Exception as e:
            logger.error(f"❌ 同步數據到MongoDB時發生錯誤: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_sync_statistics(self) -> Dict[str, Any]:
        """獲取同步統計信息"""
        if self.mongodb_db is None:
            return {}
        
        try:
            collection = self.mongodb_db[self.collection_name]
            
            # 总記錄數
            total_count = collection.count_documents({})
            
            # 按市場統計
            market_stats = list(collection.aggregate([
                {'$group': {
                    '_id': '$sse',
                    'count': {'$sum': 1}
                }}
            ]))
            
            # 按分類統計
            category_stats = list(collection.aggregate([
                {'$group': {
                    '_id': '$sec',
                    'count': {'$sum': 1}
                }}
            ]))
            
            # 最近更新時間
            latest_update = collection.find_one(
                {},
                sort=[('updated_at', -1)]
            )
            
            return {
                'total_count': total_count,
                'market_distribution': {item['_id']: item['count'] for item in market_stats},
                'category_distribution': {item['_id']: item['count'] for item in category_stats},
                'latest_update': latest_update['updated_at'] if latest_update else None
            }
            
        except Exception as e:
            logger.error(f"❌ 獲取統計信息時發生錯誤: {e}")
            return {}
    
    def query_stocks(self, 
                    code: str = None, 
                    name: str = None, 
                    market: str = None, 
                    category: str = None,
                    limit: int = 10) -> List[Dict[str, Any]]:
        """查詢股票信息"""
        if self.mongodb_db is None:
            return []
        
        try:
            collection = self.mongodb_db[self.collection_name]
            
            # 構建查詢條件
            query = {}
            if code:
                query['code'] = {'$regex': code, '$options': 'i'}
            if name:
                query['name'] = {'$regex': name, '$options': 'i'}
            if market:
                query['sse'] = market
            if category:
                query['sec'] = category
            
            # 執行查詢
            cursor = collection.find(query).limit(limit)
            results = list(cursor)
            
            # 移除MongoDB的_id字段
            for result in results:
                if '_id' in result:
                    del result['_id']
            
            return results
            
        except Exception as e:
            logger.error(f"❌ 查詢股票信息時發生錯誤: {e}")
            return []
    
    def close(self):
        """關闭數據庫連接"""
        if self.mongodb_client:
            self.mongodb_client.close()
            logger.info(f"🔒 MongoDB連接已關闭")


def main():
    """主函數"""
    logger.info(f"=")
    logger.info(f"📊 A股股票基础信息同步到MongoDB")
    logger.info(f"=")
    
    # 創建同步器
    syncer = StockInfoSyncer()
    
    if syncer.mongodb_db is None:
        logger.error(f"❌ MongoDB連接失败，請檢查配置")
        return
    
    try:
        # 同步股票數據
        logger.info(f"\n🏢 同步股票數據...")
        stock_data = syncer.fetch_stock_data('stock')
        if stock_data is not None:
            syncer.sync_to_mongodb(stock_data)
        
        # 同步指數數據
        logger.info(f"\n📊 同步指數數據...")
        index_data = syncer.fetch_stock_data('index')
        if index_data is not None:
            syncer.sync_to_mongodb(index_data)
        
        # 同步ETF數據
        logger.info(f"\n📈 同步ETF數據...")
        etf_data = syncer.fetch_stock_data('etf')
        if etf_data is not None:
            syncer.sync_to_mongodb(etf_data)
        
        # 顯示統計信息
        logger.info(f"\n📊 同步統計信息:")
        stats = syncer.get_sync_statistics()
        if stats:
            logger.info(f"  总記錄數: {stats.get('total_count', 0)}")
            
            market_dist = stats.get('market_distribution', {})
            if market_dist:
                logger.info(f"  市場分布:")
                for market, count in market_dist.items():
                    market_name = "深圳" if market == 'sz' else "上海"
                    logger.info(f"    {market_name}市場: {count} 條")
            
            category_dist = stats.get('category_distribution', {})
            if category_dist:
                logger.info(f"  分類分布:")
                for category, count in category_dist.items():
                    logger.info(f"    {category}: {count} 條")
            
            latest_update = stats.get('latest_update')
            if latest_update:
                logger.info(f"  最近更新: {latest_update}")
        
        # 示例查詢
        logger.debug(f"\n🔍 示例查詢 - 查找平安銀行:")
        results = syncer.query_stocks(name="平安", limit=5)
        for result in results:
            logger.info(f"  {result['code']} - {result['name']} ({result['market']})")
        
    except KeyboardInterrupt:
        logger.info(f"\n⏹️ 用戶中斷操作")
    except Exception as e:
        logger.error(f"\n❌ 同步過程中發生錯誤: {e}")
        import traceback

        traceback.print_exc()
    finally:
        syncer.close()
    
    logger.info(f"\n✅ 同步完成")


if __name__ == "__main__":
    main()