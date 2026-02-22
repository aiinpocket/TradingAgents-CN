#!/usr/bin/env python3
"""
快取管理頁面
使用者可以查看、管理和清理股票資料快取
"""

import json
from datetime import datetime, timedelta

import streamlit as st

try:
    from tradingagents.dataflows.cache_manager import get_cache
    from tradingagents.dataflows.optimized_us_data import get_optimized_us_data_provider
    CACHE_AVAILABLE = True
    OPTIMIZED_PROVIDERS_AVAILABLE = True
except ImportError as e:
    CACHE_AVAILABLE = False
    OPTIMIZED_PROVIDERS_AVAILABLE = False
    st.error(f"快取管理器不可用: {e}")

def main():
    """快取管理主函式，由 app.py 路由呼叫"""
    st.title("股票資料快取管理")
    st.markdown("---")
    
    if not CACHE_AVAILABLE:
        st.error("快取管理器不可用，請檢查系統配置")
        return
    
    # 取得快取實例
    cache = get_cache()
    
    # 側邊欄操作
    with st.sidebar:
        st.header("快取操作")
        
        # 重新整理按鈕
        if st.button("重新整理統計", type="primary"):
            st.rerun()
        
        st.markdown("---")
        
        # 清理操作
        st.subheader("清理快取")
        
        max_age_days = st.slider(
            "清理多少天前的快取",
            min_value=1,
            max_value=30,
            value=7,
            help="刪除指定天數之前的快取檔案"
        )
        
        if st.button("清理過期快取", type="secondary"):
            with st.spinner("正在清理過期快取..."):
                cache.clear_old_cache(max_age_days)
            st.success(f"已清理 {max_age_days} 天前的快取")
            st.rerun()
    
    # 主要內容區域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("快取統計")
        
        # 取得快取統計
        try:
            stats = cache.get_cache_stats()
            
            # 顯示統計資訊
            metric_col1, metric_col2 = st.columns(2)
            
            with metric_col1:
                st.metric(
                    label="總檔案數",
                    value=stats['total_files'],
                    help="快取中的總檔案數量"
                )
                
                st.metric(
                    label="股票資料",
                    value=f"{stats['stock_data_count']}個",
                    help="快取的股票資料檔案數量"
                )
            
            with metric_col2:
                st.metric(
                    label="總大小",
                    value=f"{stats['total_size_mb']} MB",
                    help="快取檔案佔用的磁碟空間"
                )
                
                st.metric(
                    label="新聞資料",
                    value=f"{stats['news_count']}個",
                    help="快取的新聞資料檔案數量"
                )
            
            # 基本面資料
            st.metric(
                label="基本面資料",
                value=f"{stats['fundamentals_count']}個",
                help="快取的基本面資料檔案數量"
            )
            
        except Exception as e:
            st.error(f"取得快取統計失敗: {e}")

    with col2:
        st.subheader("快取配置")

        # 顯示快取配置資訊
        if hasattr(cache, 'cache_config'):
            st.markdown("**美股資料快取配置**")
            us_configs = {k: v for k, v in cache.cache_config.items() if k.startswith('us_')}
            for config_name, config_data in us_configs.items():
                st.info(f"""
                **{config_data.get('description', config_name)}**
                - TTL: {config_data.get('ttl_hours', 'N/A')} 小時
                - 最大檔案數: {config_data.get('max_files', 'N/A')}
                """)
        else:
            st.warning("快取配置資訊不可用")

    # 快取測試功能
    st.markdown("---")
    st.subheader("快取測試")

    if OPTIMIZED_PROVIDERS_AVAILABLE:
        test_col1, test_col2 = st.columns(2)

        with test_col1:
            st.markdown("**測試美股資料快取**")
            us_symbol = st.text_input("美股代碼", value="AAPL", key="us_test")
            if st.button("測試美股快取", key="test_us"):
                if us_symbol:
                    with st.spinner(f"測試 {us_symbol} 快取..."):
                        try:
                            provider = get_optimized_us_data_provider()
                            result = provider.get_stock_data(
                                symbol=us_symbol,
                                start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                                end_date=datetime.now().strftime('%Y-%m-%d')
                            )
                            st.success("美股快取測試成功")
                            with st.expander("查看結果"):
                                st.text(result[:500] + "..." if len(result) > 500 else result)
                        except Exception as e:
                            st.error(f"美股快取測試失敗: {e}")

        with test_col2:
            st.markdown("**測試說明**")
            st.info("目前僅支援美股資料測試。請在左側輸入美股代碼進行測試。")
    else:
        st.warning("優化資料提供器不可用，無法進行快取測試")

    # 原有的快取詳情部分
    with col2:
        st.subheader("快取配置")
        st.caption("股票資料 6h / 新聞 24h / 基本面 24h")
        
        # 快取目錄資訊
        cache_dir = cache.cache_dir
        st.markdown(f"**快取目錄：**`{cache_dir}`")
        
        # 子目錄資訊
        st.markdown("**子目錄結構：**")
        st.code(f"""
 {cache_dir.name}/
├──  stock_data/     # 股票資料快取
├──  news_data/      # 新聞資料快取
├──  fundamentals/   # 基本面資料快取
└──  metadata/       # 中繼資料檔
        """)
    
    st.markdown("---")
    
    # 快取詳情
    st.subheader("快取詳情")
    
    # 選擇查看的資料類型
    data_type = st.selectbox(
        "選擇資料類型",
        ["stock_data", "news", "fundamentals"],
        format_func=lambda x: {
            "stock_data": "股票資料",
            "news": "新聞資料", 
            "fundamentals": "基本面資料"
        }[x]
    )
    
    # 顯示快取檔案列表
    try:
        metadata_files = list(cache.metadata_dir.glob("*_meta.json"))
        
        if metadata_files:
            cache_items = []
            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    if metadata.get('data_type') == data_type:
                        cached_at = datetime.fromisoformat(metadata['cached_at'])
                        cache_items.append({
                            'symbol': metadata.get('symbol', 'N/A'),
                            'data_source': metadata.get('data_source', 'N/A'),
                            'cached_at': cached_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'start_date': metadata.get('start_date', 'N/A'),
                            'end_date': metadata.get('end_date', 'N/A'),
                            'file_path': metadata.get('file_path', 'N/A')
                        })
                except Exception as e:
                    continue
            
            if cache_items:
                # 按快取時間排序
                cache_items.sort(key=lambda x: x['cached_at'], reverse=True)
                
                # 顯示表格
                import pandas as pd
                df = pd.DataFrame(cache_items)
                
                st.dataframe(
                    df,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "symbol": st.column_config.TextColumn("股票代碼", width="small"),
                        "data_source": st.column_config.TextColumn("資料來源", width="small"),
                        "cached_at": st.column_config.TextColumn("快取時間", width="medium"),
                        "start_date": st.column_config.TextColumn("開始日期", width="small"),
                        "end_date": st.column_config.TextColumn("結束日期", width="small"),
                        "file_path": st.column_config.TextColumn("檔案路徑", width="large")
                    }
                )
                
                st.info(f"找到 {len(cache_items)} 個 {data_type} 類型的快取檔案")
            else:
                st.info(f"暫無 {data_type} 類型的快取檔案")
        else:
            st.info("暫無快取檔案")
            
    except Exception as e:
        st.error(f"讀取快取詳情失敗: {e}")
    
    st.markdown("---")
    st.caption("TradingAgents - 快取管理")

if __name__ == "__main__":
    main()
