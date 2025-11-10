#!/usr/bin/env python3
"""
MongoDB報告管理器
用於保存和讀取分析報告到MongoDB數據庫
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    logger.warning("pymongo未安裝，MongoDB功能不可用")


class MongoDBReportManager:
    """MongoDB報告管理器"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connected = False
        
        if MONGODB_AVAILABLE:
            self._connect()
    
    def _connect(self):
        """連接到MongoDB"""
        try:
            # 加載環境變量
            from dotenv import load_dotenv
            load_dotenv()

            # 從環境變量獲取MongoDB配置
            mongodb_host = os.getenv("MONGODB_HOST", "localhost")
            mongodb_port = int(os.getenv("MONGODB_PORT", "27017"))
            mongodb_username = os.getenv("MONGODB_USERNAME", "")
            mongodb_password = os.getenv("MONGODB_PASSWORD", "")
            mongodb_database = os.getenv("MONGODB_DATABASE", "tradingagents")
            mongodb_auth_source = os.getenv("MONGODB_AUTH_SOURCE", "admin")

            logger.info(f"🔧 MongoDB配置: host={mongodb_host}, port={mongodb_port}, db={mongodb_database}")
            logger.info(f"🔧 認證信息: username={mongodb_username}, auth_source={mongodb_auth_source}")

            # 構建連接參數
            connect_kwargs = {
                "host": mongodb_host,
                "port": mongodb_port,
                "serverSelectionTimeoutMS": 5000,
                "connectTimeoutMS": 5000
            }

            # 如果有用戶名和密碼，添加認證信息
            if mongodb_username and mongodb_password:
                connect_kwargs.update({
                    "username": mongodb_username,
                    "password": mongodb_password,
                    "authSource": mongodb_auth_source
                })

            # 連接MongoDB
            self.client = MongoClient(**connect_kwargs)
            
            # 測試連接
            self.client.admin.command('ping')
            
            # 選擇數據庫和集合
            self.db = self.client[mongodb_database]
            self.collection = self.db["analysis_reports"]
            
            # 創建索引
            self._create_indexes()
            
            self.connected = True
            logger.info(f"✅ MongoDB連接成功: {mongodb_database}.analysis_reports")
            
        except Exception as e:
            logger.error(f"❌ MongoDB連接失败: {e}")
            self.connected = False
    
    def _create_indexes(self):
        """創建索引以提高查詢性能"""
        try:
            # 創建複合索引
            self.collection.create_index([
                ("stock_symbol", 1),
                ("analysis_date", -1),
                ("timestamp", -1)
            ])
            
            # 創建單字段索引
            self.collection.create_index("analysis_id")
            self.collection.create_index("status")
            
            logger.info("✅ MongoDB索引創建成功")
            
        except Exception as e:
            logger.error(f"❌ MongoDB索引創建失败: {e}")
    
    def save_analysis_report(self, stock_symbol: str, analysis_results: Dict[str, Any],
                           reports: Dict[str, str]) -> bool:
        """保存分析報告到MongoDB"""
        if not self.connected:
            logger.warning("MongoDB未連接，跳過保存")
            return False

        try:
            # 生成分析ID
            timestamp = datetime.now()
            analysis_id = f"{stock_symbol}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

            # 構建文檔
            document = {
                "analysis_id": analysis_id,
                "stock_symbol": stock_symbol,
                "analysis_date": timestamp.strftime('%Y-%m-%d'),
                "timestamp": timestamp,
                "status": "completed",
                "source": "mongodb",

                # 分析結果摘要
                "summary": analysis_results.get("summary", ""),
                "analysts": analysis_results.get("analysts", []),
                "research_depth": analysis_results.get("research_depth", 1),  # 修正：從分析結果中獲取真實的研究深度

                # 報告內容
                "reports": reports,

                # 元數據
                "created_at": timestamp,
                "updated_at": timestamp
            }
            
            # 插入文檔
            result = self.collection.insert_one(document)
            
            if result.inserted_id:
                logger.info(f"✅ 分析報告已保存到MongoDB: {analysis_id}")
                return True
            else:
                logger.error("❌ MongoDB插入失败")
                return False
                
        except Exception as e:
            logger.error(f"❌ 保存分析報告到MongoDB失败: {e}")
            return False
    
    def get_analysis_reports(self, limit: int = 100, stock_symbol: str = None,
                           start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """從MongoDB獲取分析報告"""
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
            
            # 查詢數據
            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)
            
            results = []
            for doc in cursor:
                # 處理timestamp字段，兼容不同的數據類型
                timestamp_value = doc.get("timestamp")
                if hasattr(timestamp_value, 'timestamp'):
                    # datetime對象
                    timestamp = timestamp_value.timestamp()
                elif isinstance(timestamp_value, (int, float)):
                    # 已經是時間戳
                    timestamp = float(timestamp_value)
                else:
                    # 其他情況，使用當前時間
                    from datetime import datetime
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
            
            logger.info(f"✅ 從MongoDB獲取到 {len(results)} 個分析報告")
            return results
            
        except Exception as e:
            logger.error(f"❌ 從MongoDB獲取分析報告失败: {e}")
            return []
    
    def get_report_by_id(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """根據ID獲取單個分析報告"""
        if not self.connected:
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
            logger.error(f"❌ 從MongoDB獲取報告失败: {e}")
            return None
    
    def delete_report(self, analysis_id: str) -> bool:
        """刪除分析報告"""
        if not self.connected:
            return False
        
        try:
            result = self.collection.delete_one({"analysis_id": analysis_id})
            
            if result.deleted_count > 0:
                logger.info(f"✅ 已刪除分析報告: {analysis_id}")
                return True
            else:
                logger.warning(f"⚠️ 未找到要刪除的報告: {analysis_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 刪除分析報告失败: {e}")
            return False

    def get_all_reports(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """獲取所有分析報告"""
        if not self.connected:
            return []

        try:
            # 獲取所有報告，按時間戳降序排列
            cursor = self.collection.find().sort("timestamp", -1).limit(limit)
            reports = list(cursor)

            # 轉換ObjectId為字符串
            for report in reports:
                if '_id' in report:
                    report['_id'] = str(report['_id'])

            logger.info(f"✅ 從MongoDB獲取了 {len(reports)} 個分析報告")
            return reports

        except Exception as e:
            logger.error(f"❌ 從MongoDB獲取所有報告失败: {e}")
            return []

    def fix_inconsistent_reports(self) -> bool:
        """修複不一致的報告數據結構"""
        if not self.connected:
            logger.warning("MongoDB未連接，跳過修複")
            return False

        try:
            # 查找缺少reports字段或reports字段為空的文檔
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
                logger.info("✅ 所有報告數據結構一致，無需修複")
                return True

            logger.info(f"🔧 發現 {len(inconsistent_docs)} 個不一致的報告，開始修複...")

            fixed_count = 0
            for doc in inconsistent_docs:
                try:
                    # 為缺少reports字段的文檔添加空的reports字段
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
                        logger.info(f"✅ 修複報告: {doc.get('analysis_id', 'unknown')}")

                except Exception as e:
                    logger.error(f"❌ 修複報告失败 {doc.get('analysis_id', 'unknown')}: {e}")

            logger.info(f"✅ 修複完成，共修複 {fixed_count} 個報告")
            return True

        except Exception as e:
            logger.error(f"❌ 修複不一致報告失败: {e}")
            return False

    def save_report(self, report_data: Dict[str, Any]) -> bool:
        """保存報告數據（通用方法）"""
        if not self.connected:
            logger.warning("MongoDB未連接，跳過保存")
            return False

        try:
            # 確保有必要的字段
            if 'analysis_id' not in report_data:
                logger.error("報告數據缺少analysis_id字段")
                return False

            # 添加保存時間戳
            report_data['saved_at'] = datetime.now()

            # 使用upsert操作，如果存在則更新，不存在則插入
            result = self.collection.replace_one(
                {"analysis_id": report_data['analysis_id']},
                report_data,
                upsert=True
            )

            if result.upserted_id or result.modified_count > 0:
                logger.info(f"✅ 報告保存成功: {report_data['analysis_id']}")
                return True
            else:
                logger.warning(f"⚠️ 報告保存無變化: {report_data['analysis_id']}")
                return True

        except Exception as e:
            logger.error(f"❌ 保存報告到MongoDB失败: {e}")
            return False


# 創建全局實例
mongodb_report_manager = MongoDBReportManager()
