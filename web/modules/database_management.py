#!/usr/bin/env python3
"""
數據庫緩存管理頁面
MongoDB + Redis 緩存管理和監控
"""

import streamlit as st
import sys
import os
from pathlib import Path
import json
from datetime import datetime, timedelta

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 導入UI工具函數
sys.path.append(str(Path(__file__).parent.parent))
from utils.ui_utils import apply_hide_deploy_button_css

try:
    from tradingagents.config.database_manager import get_database_manager
    DB_MANAGER_AVAILABLE = True
except ImportError as e:
    DB_MANAGER_AVAILABLE = False
    st.error(f"數據庫管理器不可用: {e}")

def main():
    st.set_page_config(
        page_title="數據庫管理 - TradingAgents",
        page_icon="",
        layout="wide"
    )
    
    # 應用隱藏Deploy按鈕的CSS樣式
    apply_hide_deploy_button_css()
    
    st.title("MongoDB + Redis 數據庫管理")
    st.markdown("---")
    
    if not DB_MANAGER_AVAILABLE:
        st.error("數據庫管理器不可用")
        st.info("""
        請按以下步驟設置數據庫環境：
        
        1. 安裝依賴包：
        ```bash
        pip install -r requirements_db.txt
        ```
        
        2. 設置數據庫：
        ```bash
        python scripts/setup_databases.py
        ```
        
        3. 測試連接：
        ```bash
        python scripts/setup_databases.py --test
        ```
        """)
        return
    
    # 獲取數據庫管理器實例
    db_manager = get_database_manager()
    
    # 側邊欄操作
    with st.sidebar:
        st.header("數據庫操作")
        
        # 連接狀態
        st.subheader("連接狀態")
        mongodb_status = "已連接" if db_manager.is_mongodb_available() else "未連接"
        redis_status = "已連接" if db_manager.is_redis_available() else "未連接"
        
        st.write(f"**MongoDB**: {mongodb_status}")
        st.write(f"**Redis**: {redis_status}")
        
        st.markdown("---")
        
        # 刷新按鈕
        if st.button("刷新統計", type="primary"):
            st.rerun()
        
        st.markdown("---")
        
        # 清理操作
        st.subheader("清理數據")
        
        max_age_days = st.slider(
            "清理多少天前的數據",
            min_value=1,
            max_value=30,
            value=7,
            help="刪除指定天數之前的緩存數據"
        )
        
        if st.button("清理過期數據", type="secondary"):
            with st.spinner("正在清理過期數據..."):
                # 使用database_manager的緩存清理功能
                pattern = f"*:{max_age_days}d:*"  # 簡化的清理模式
                cleared_count = db_manager.cache_clear_pattern(pattern)
            st.success(f"已清理 {cleared_count} 條過期記錄")
            st.rerun()
    
    # 主要內容區域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("MongoDB 統計")
        
        try:
            stats = db_manager.get_cache_stats()
            
            if db_manager.is_mongodb_available():
                # 獲取MongoDB集合統計
                collections_info = {
                    "stock_data": "股票數據",
                    "analysis_results": "分析結果",
                    "user_sessions": "用戶會話",
                    "configurations": "配置信息"
                }

                total_records = 0
                st.markdown("**集合詳情：**")

                mongodb_client = db_manager.get_mongodb_client()
                if mongodb_client is not None:
                    mongodb_db = mongodb_client[db_manager.mongodb_config["database"]]
                    for collection_name, display_name in collections_info.items():
                        try:
                            collection = mongodb_db[collection_name]
                            count = collection.count_documents({})
                            total_records += count
                            st.write(f"**{display_name}**: {count:,} 條記錄")
                        except Exception as e:
                            st.write(f"**{display_name}**: 獲取失敗 ({e})")
                
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("總記錄數", f"{total_records:,}")
                with metric_col2:
                    st.metric("Redis緩存", stats.get('redis_keys', 0))
            else:
                st.error("MongoDB 未連接")
                
        except Exception as e:
            st.error(f"獲取MongoDB統計失敗: {e}")
    
    with col2:
        st.subheader("Redis 統計")
        
        try:
            stats = db_manager.get_cache_stats()
            
            if db_manager.is_redis_available():
                metric_col1, metric_col2 = st.columns(2)
                with metric_col1:
                    st.metric("緩存鍵數量", stats.get("redis_keys", 0))
                with metric_col2:
                    st.metric("內存使用", stats.get("redis_memory", "N/A"))
                
                st.info("""
                **Redis 緩存策略：**

                - **股票數據**：6小時自動過期
                - **分析結果**：24小時自動過期
                - **用戶會話**：1小時自動過期

                Redis 主要用於熱點數據的快速訪問，
                過期後會自動從 MongoDB 重新加載。
                """)
            else:
                st.error("Redis 未連接")
                
        except Exception as e:
            st.error(f"獲取Redis統計失敗: {e}")
    
    st.markdown("---")
    
    # 數據庫配置信息
    st.subheader("數據庫配置")
    
    config_col1, config_col2 = st.columns([1, 1])
    
    with config_col1:
        st.markdown("**MongoDB 配置：**")
        # 從數據庫管理器獲取實際配置
        mongodb_config = db_manager.mongodb_config
        mongodb_host = mongodb_config.get('host', 'localhost')
        mongodb_port = mongodb_config.get('port', 27017)
        mongodb_db_name = mongodb_config.get('database', 'tradingagents')
        st.code(f"""
    主機: {mongodb_host}:{mongodb_port}
    數據庫: {mongodb_db_name}
    狀態: {mongodb_status}
    啟用: {mongodb_config.get('enabled', False)}
        """)

        if db_manager.is_mongodb_available():
            st.markdown("**集合結構：**")
            st.code("""
    tradingagents/
    ├── stock_data        # 股票歷史數據
    ├── analysis_results  # 分析結果
    ├── user_sessions     # 用戶會話
    └── configurations    # 系統配置
                """)
    
    with config_col2:
        st.markdown("**Redis 配置：**")
        # 從數據庫管理器獲取實際配置
        redis_config = db_manager.redis_config
        redis_host = redis_config.get('host', 'localhost')
        redis_port = redis_config.get('port', 6379)
        redis_db = redis_config.get('db', 0)
        st.code(f"""
    主機: {redis_host}:{redis_port}
    數據庫: {redis_db}
    狀態: {redis_status}
    啟用: {redis_config.get('enabled', False)}
                """)
        
        if db_manager.is_redis_available():
            st.markdown("**緩存鍵格式：**")
            st.code("""
    stock:SYMBOL:HASH     # 股票數據緩存
    analysis:SYMBOL:HASH  # 分析結果緩存  
    session:USER:HASH     # 用戶會話緩存
                """)
    
    st.markdown("---")
    
    # 性能對比
    st.subheader("性能優勢")
    
    perf_col1, perf_col2, perf_col3 = st.columns(3)
    
    with perf_col1:
        st.metric(
            label="Redis 緩存速度",
            value="< 1ms",
            delta="比API快 1000+ 倍",
            help="Redis內存緩存的超快訪問速度"
        )
    
    with perf_col2:
        st.metric(
            label="MongoDB 查詢速度", 
            value="< 10ms",
            delta="比API快 100+ 倍",
            help="MongoDB索引優化的查詢速度"
        )
    
    with perf_col3:
        st.metric(
            label="儲存容量",
            value="無限制",
            delta="vs API 配額限制",
            help="本地儲存不受API調用次數限制"
        )
    
    # 架構說明
    st.markdown("---")
    st.subheader("緩存架構")
    
    st.info("""
    **三層緩存架構：**
    
    1. **Redis (L1緩存)** - 內存緩存，毫秒級訪問
       - 儲存最熱點的數據
       - 自動過期管理
       - 高並發支持
    
    2. **MongoDB (L2緩存)** - 持久化儲存，秒級訪問  
       - 儲存所有歷史數據
       - 支持複雜查詢
       - 數據持久化保證
    
    3. **API (L3數據源)** - 外部數據源，分鐘級訪問
       - FinnHub API (美股數據)
       - Yahoo Finance API (市場數據)
       - Google News (新聞數據)
    
    **數據流向：** API → MongoDB → Redis → 應用程序
    """)
    
    # 頁腳資訊
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        數據庫緩存管理系統 | TradingAgents v0.1.2 |
        <a href='https://github.com/your-repo/TradingAgents' target='_blank'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
