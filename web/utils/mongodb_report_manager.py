#!/usr/bin/env python3
"""
MongoDB報告管理器
用於保存和讀取分析報告到MongoDB資料庫
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 日誌模組
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger('web')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logger.warning("pymongo未安裝，MongoDB功能不可用")


import threading

# 模組級別的共享 MongoClient 單例（PyMongo MongoClient 內建連接池，執行緒安全）
_shared_client: Optional["MongoClient"] = None
_shared_client_lock = threading.Lock()


def _get_shared_client():
    """取得共享的 MongoClient 單例，避免每次建立新連接"""
    global _shared_client
    if _shared_client is not None:
        return _shared_client

    with _shared_client_lock:
        # 雙重檢查鎖定
        if _shared_client is not None:
            return _shared_client

        if not MONGODB_AVAILABLE:
            return None

        try:
            from dotenv import load_dotenv
            load_dotenv()

            mongodb_host = os.getenv("MONGODB_HOST", "localhost")
            mongodb_port = int(os.getenv("MONGODB_PORT", "27017"))
            mongodb_username = os.getenv("MONGODB_USERNAME", "")
            mongodb_password = os.getenv("MONGODB_PASSWORD", "")
            mongodb_auth_source = os.getenv("MONGODB_AUTH_SOURCE", "admin")

            connect_kwargs = {
                "host": mongodb_host,
                "port": mongodb_port,
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000,
                "maxPoolSize": 10,
                "minPoolSize": 1,
            }

            if mongodb_username and mongodb_password:
                connect_kwargs.update({
                    "username": mongodb_username,
                    "password": mongodb_password,
                    "authSource": mongodb_auth_source,
                })

            client = MongoClient(**connect_kwargs)
            client.admin.command("ping")
            _shared_client = client
            logger.info(f"MongoDB 共享連接池建立成功: {mongodb_host}:{mongodb_port}")
            return _shared_client

        except Exception as e:
            logger.error(f"MongoDB 共享連接池建立失敗: {e}")
            return None


class MongoDBReportManager:
    """MongoDB 報告管理器（使用共享連接池單例）"""

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False

        if MONGODB_AVAILABLE:
            self._connect()

    def _connect(self):
        """透過共享連接池連接到 MongoDB"""
        try:
            client = _get_shared_client()
            if client is None:
                self.connected = False
                return

            self.client = client
            mongodb_database = os.getenv("MONGODB_DATABASE", "tradingagents")
            self.db = self.client[mongodb_database]
            self.collection = self.db["analysis_reports"]

            # 索引只需建立一次（idempotent），共享連接池首次呼叫時建立
            self._create_indexes()

            self.connected = True

        except Exception as e:
            logger.error(f"MongoDB 連接失敗: {e}")
            self.connected = False
    
    def _create_indexes(self):
        """建立索引以提高查詢性能（含 TTL 自動清理）"""
        try:
            # 建立複合索引
            self.collection.create_index([
                ("stock_symbol", 1),
                ("analysis_date", -1),
                ("timestamp", -1)
            ])

            # 建立單欄位索引
            self.collection.create_index("analysis_id")
            self.collection.create_index("status")

            # TTL 索引：30 天後自動刪除過期報告，避免資料無限膨脹
            self.collection.create_index(
                "timestamp",
                expireAfterSeconds=30 * 24 * 3600
            )

            logger.info("MongoDB索引建立成功")

        except Exception as e:
            logger.error(f"MongoDB索引建立失敗: {e}")
    
    def save_analysis_report(self, stock_symbol: str, analysis_results: Dict[str, Any],
                           reports: Dict[str, str],
                           analysis_date: str = None,
                           formatted_result: Dict[str, Any] = None) -> bool:
        """保存分析報告到MongoDB

        Args:
            stock_symbol: 股票代碼
            analysis_results: 原始分析結果
            reports: 報告內容
            analysis_date: 分析日期（YYYY-MM-DD），預設為今天
            formatted_result: 前端可用的格式化結果（用於快取命中時直接返回）
        """
        if not self.connected:
            logger.warning("MongoDB未連接，跳過保存")
            return False

        try:
            timestamp = datetime.now()
            analysis_id = f"{stock_symbol}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

            # 使用傳入的分析日期，而非當前日期
            report_date = analysis_date if analysis_date else timestamp.strftime('%Y-%m-%d')

            document = {
                "analysis_id": analysis_id,
                "stock_symbol": stock_symbol,
                "analysis_date": report_date,
                "timestamp": timestamp,
                "status": "completed",
                "source": "mongodb",

                # 分析結果摘要
                "summary": analysis_results.get("summary", ""),
                "analysts": analysis_results.get("analysts", []),
                "research_depth": analysis_results.get("research_depth", 1),

                # 報告內容
                "reports": reports,

                # 前端格式化結果（快取用）
                "formatted_result": formatted_result,

                # 中繼資料
                "created_at": timestamp,
                "updated_at": timestamp
            }

            result = self.collection.insert_one(document)

            if result.inserted_id:
                logger.info(f"分析報告已保存到MongoDB: {analysis_id}")
                return True
            else:
                logger.error("MongoDB插入失敗")
                return False

        except Exception as e:
            logger.error(f"保存分析報告到MongoDB失敗: {e}")
            return False

    def get_latest_report(self, stock_symbol: str, analysis_date: str,
                         max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """查詢最近的分析報告作為快取

        Args:
            stock_symbol: 股票代碼
            analysis_date: 分析日期（YYYY-MM-DD）
            max_age_hours: 最大快取有效期（小時）

        Returns:
            最近一筆符合條件的報告，或 None
        """
        if not self.connected:
            return None

        # 深度防禦：確保查詢參數為純字串，防止 NoSQL 操作符注入
        if not isinstance(stock_symbol, str) or not isinstance(analysis_date, str):
            return None

        try:
            cutoff = datetime.now() - timedelta(hours=max_age_hours)
            doc = self.collection.find_one(
                {
                    "stock_symbol": stock_symbol,
                    "analysis_date": analysis_date,
                    "status": "completed",
                    "formatted_result": {"$exists": True, "$ne": None},
                    "timestamp": {"$gte": cutoff},
                },
                sort=[("timestamp", -1)],
            )
            if doc:
                logger.info(f"MongoDB 快取命中: {stock_symbol} @ {analysis_date}")
            return doc
        except Exception as e:
            logger.error(f"查詢 MongoDB 快取失敗: {e}")
            return None
    
    def get_analysis_reports(self, limit: int = 100, stock_symbol: str = None,
                           start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """從MongoDB取得分析報告"""
        if not self.connected:
            return []
        
        try:
            # 構建查詢條件
            query = {}
            
            if stock_symbol:
                query["stock_symbol"] = stock_symbol
            
            if start_date or end_date:
                date_query = {}
                if start_date:
                    date_query["$gte"] = start_date
                if end_date:
                    date_query["$lte"] = end_date
                query["analysis_date"] = date_query
            
            # 查詢資料
            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
            
            results = []
            for doc in cursor:
                # 處理timestamp欄位，相容不同的資料類型
                timestamp_value = doc.get("timestamp")
                if hasattr(timestamp_value, 'timestamp'):
                    # datetime物件
                    timestamp = timestamp_value.timestamp()
                elif isinstance(timestamp_value, (int, float)):
                    # 已經是時間戳
                    timestamp = float(timestamp_value)
                else:
                    # 其他情況，使用當前時間
                    timestamp = datetime.now().timestamp()
                
                # 轉換為Web應用期望的格式
                result = {
                    "analysis_id": doc["analysis_id"],
                    "timestamp": timestamp,
                    "stock_symbol": doc["stock_symbol"],
                    "analysts": doc.get("analysts", []),
                    "research_depth": doc.get("research_depth", 0),
                    "status": doc.get("status", "completed"),
                    "summary": doc.get("summary", ""),
                    "performance": {},
                    "tags": [],
                    "is_favorite": False,
                    "reports": doc.get("reports", {}),
                    "source": "mongodb"
                }
                results.append(result)
            
            logger.info(f"從MongoDB取得到 {len(results)} 個分析報告")
            return results
            
        except Exception as e:
            logger.error(f"從MongoDB取得分析報告失敗: {e}")
            return []
    
    def get_report_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """根據ID取得單個分析報告"""
        if not self.connected:
            return None

        # 深度防禦：確保查詢參數為純字串，防止 NoSQL 操作符注入
        if not isinstance(analysis_id, str):
            return None

        try:
            doc = self.collection.find_one({"analysis_id": analysis_id})
            
            if doc:
                # 轉換為Web應用期望的格式
                result = {
                    "analysis_id": doc["analysis_id"],
                    "timestamp": doc["timestamp"].timestamp(),
                    "stock_symbol": doc["stock_symbol"],
                    "analysts": doc.get("analysts", []),
                    "research_depth": doc.get("research_depth", 0),
                    "status": doc.get("status", "completed"),
                    "summary": doc.get("summary", ""),
                    "performance": {},
                    "tags": [],
                    "is_favorite": False,
                    "reports": doc.get("reports", {}),
                    "source": "mongodb"
                }
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"從MongoDB取得報告失敗: {e}")
            return None
    
    def delete_report(self, analysis_id: str) -> bool:
        """刪除分析報告"""
        if not self.connected:
            return False
        
        try:
            result = self.collection.delete_one({"analysis_id": analysis_id})
            
            if result.deleted_count > 0:
                logger.info(f"已刪除分析報告: {analysis_id}")
                return True
            else:
                logger.warning(f"未找到要刪除的報告: {analysis_id}")
                return False
                
        except Exception as e:
            logger.error(f"刪除分析報告失敗: {e}")
            return False

    def get_all_reports(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """取得所有分析報告"""
        if not self.connected:
            return []

        try:
            # 取得所有報告，按時間戳降序排列
            cursor = self.collection.find().sort("timestamp", -1).limit(limit)
            reports = list(cursor)

            # 轉換ObjectId為字串
            for report in reports:
                if '_id' in report:
                    report['_id'] = str(report['_id'])

            logger.info(f"從MongoDB取得了 {len(reports)} 個分析報告")
            return reports

        except Exception as e:
            logger.error(f"從MongoDB取得所有報告失敗: {e}")
            return []

    def fix_inconsistent_reports(self) -> bool:
        """修復不一致的報告資料結構"""
        if not self.connected:
            logger.warning("MongoDB未連接，跳過修復")
            return False

        try:
            # 查找缺少reports欄位或reports欄位為空的檔案
            query = {
                "$or": [
                    {"reports": {"$exists": False}},
                    {"reports": {}},
                    {"reports": None}
                ]
            }

            cursor = self.collection.find(query)
            inconsistent_docs = list(cursor)

            if not inconsistent_docs:
                logger.info("所有報告資料結構一致，無需修復")
                return True

            logger.info(f"發現 {len(inconsistent_docs)} 個不一致的報告，開始修復...")

            fixed_count = 0
            for doc in inconsistent_docs:
                try:
                    # 為缺少reports欄位的檔案新增空的reports欄位
                    update_data = {
                        "$set": {
                            "reports": {},
                            "updated_at": datetime.now()
                        }
                    }

                    result = self.collection.update_one(
                        {"_id": doc["_id"]},
                        update_data
                    )

                    if result.modified_count > 0:
                        fixed_count += 1
                        logger.info(f"修復報告: {doc.get('analysis_id', 'unknown')}")

                except Exception as e:
                    logger.error(f"修復報告失敗 {doc.get('analysis_id', 'unknown')}: {e}")

            logger.info(f"修復完成，共修復 {fixed_count} 個報告")
            return True

        except Exception as e:
            logger.error(f"修復不一致報告失敗: {e}")
            return False

    def save_report(self, report_data: Dict[str, Any]) -> bool:
        """保存報告資料（通用方法）"""
        if not self.connected:
            logger.warning("MongoDB未連接，跳過保存")
            return False

        try:
            # 確保有必要的欄位
            if 'analysis_id' not in report_data:
                logger.error("報告資料缺少analysis_id欄位")
                return False

            # 新增保存時間戳
            report_data['saved_at'] = datetime.now()

            # 使用upsert操作，如果存在則更新，不存在則插入
            result = self.collection.replace_one(
                {"analysis_id": report_data['analysis_id']},
                report_data,
                upsert=True
            )

            if result.upserted_id or result.modified_count > 0:
                logger.info(f"報告保存成功: {report_data['analysis_id']}")
                return True
            else:
                logger.warning(f"報告保存無變化: {report_data['analysis_id']}")
                return True

        except Exception as e:
            logger.error(f"保存報告到MongoDB失敗: {e}")
            return False


# 建立全局實例
mongodb_report_manager = MongoDBReportManager()
