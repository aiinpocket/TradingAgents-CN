#!/usr/bin/env python3
"""
緩存管理页面
用戶可以查看、管理和清理股票數據緩存
"""

import streamlit as st
import sys
import os
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 導入UI工具函數
sys.path.append(str(Path(__file__).parent.parent))
from utils.ui_utils import apply_hide_deploy_button_css

try:
    from tradingagents.dataflows.cache_manager import get_cache
    from tradingagents.dataflows.optimized_us_data import get_optimized_us_data_provider
    from tradingagents.dataflows.optimized_china_data import get_optimized_china_data_provider
    CACHE_AVAILABLE = True
    OPTIMIZED_PROVIDERS_AVAILABLE = True
except ImportError as e:
    CACHE_AVAILABLE = False
    OPTIMIZED_PROVIDERS_AVAILABLE = False
    st.error(f"緩存管理器不可用: {e}")

def main():
    st.set_page_config(
        page_title="緩存管理 - TradingAgents",
        page_icon="💾",
        layout="wide"
    )
    
    # 應用隱藏Deploy按钮的CSS樣式
    apply_hide_deploy_button_css()
    
    st.title("💾 股票數據緩存管理")
    st.markdown("---")
    
    if not CACHE_AVAILABLE:
        st.error("❌ 緩存管理器不可用，請檢查系統配置")
        return
    
    # 獲取緩存實例
    cache = get_cache()
    
    # 侧邊栏操作
    with st.sidebar:
        st.header("🛠️ 緩存操作")
        
        # 刷新按钮
        if st.button("🔄 刷新統計", type="primary"):
            st.rerun()
        
        st.markdown("---")
        
        # 清理操作
        st.subheader("🧹 清理緩存")
        
        max_age_days = st.slider(
            "清理多少天前的緩存",
            min_value=1,
            max_value=30,
            value=7,
            help="刪除指定天數之前的緩存文件"
        )
        
        if st.button("🗑️ 清理過期緩存", type="secondary"):
            with st.spinner("正在清理過期緩存..."):
                cache.clear_old_cache(max_age_days)
            st.success(f"✅ 已清理 {max_age_days} 天前的緩存")
            st.rerun()
    
    # 主要內容區域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📊 緩存統計")
        
        # 獲取緩存統計
        try:
            stats = cache.get_cache_stats()
            
            # 顯示統計信息
            metric_col1, metric_col2 = st.columns(2)
            
            with metric_col1:
                st.metric(
                    label="总文件數",
                    value=stats['total_files'],
                    help="緩存中的总文件數量"
                )
                
                st.metric(
                    label="股票數據",
                    value=f"{stats['stock_data_count']}個",
                    help="緩存的股票數據文件數量"
                )
            
            with metric_col2:
                st.metric(
                    label="总大小",
                    value=f"{stats['total_size_mb']} MB",
                    help="緩存文件占用的磁盘空間"
                )
                
                st.metric(
                    label="新聞數據",
                    value=f"{stats['news_count']}個",
                    help="緩存的新聞數據文件數量"
                )
            
            # 基本面數據
            st.metric(
                label="基本面數據",
                value=f"{stats['fundamentals_count']}個",
                help="緩存的基本面數據文件數量"
            )
            
        except Exception as e:
            st.error(f"獲取緩存統計失败: {e}")

    with col2:
        st.subheader("⚙️ 緩存配置")

        # 顯示緩存配置信息
        if hasattr(cache, 'cache_config'):
            config_tabs = st.tabs(["美股配置", "A股配置"])

            with config_tabs[0]:
                st.markdown("**美股數據緩存配置**")
                us_configs = {k: v for k, v in cache.cache_config.items() if k.startswith('us_')}
                for config_name, config_data in us_configs.items():
                    st.info(f"""
                    **{config_data.get('description', config_name)}**
                    - TTL: {config_data.get('ttl_hours', 'N/A')} 小時
                    - 最大文件數: {config_data.get('max_files', 'N/A')}
                    """)

            with config_tabs[1]:
                st.markdown("**A股數據緩存配置**")
                china_configs = {k: v for k, v in cache.cache_config.items() if k.startswith('china_')}
                for config_name, config_data in china_configs.items():
                    st.info(f"""
                    **{config_data.get('description', config_name)}**
                    - TTL: {config_data.get('ttl_hours', 'N/A')} 小時
                    - 最大文件數: {config_data.get('max_files', 'N/A')}
                    """)
        else:
            st.warning("緩存配置信息不可用")

    # 緩存測試功能
    st.markdown("---")
    st.subheader("🧪 緩存測試")

    if OPTIMIZED_PROVIDERS_AVAILABLE:
        test_col1, test_col2 = st.columns(2)

        with test_col1:
            st.markdown("**測試美股數據緩存**")
            us_symbol = st.text_input("美股代碼", value="AAPL", key="us_test")
            if st.button("測試美股緩存", key="test_us"):
                if us_symbol:
                    with st.spinner(f"測試 {us_symbol} 緩存..."):
                        try:
                            from datetime import datetime, timedelta
                            provider = get_optimized_us_data_provider()
                            result = provider.get_stock_data(
                                symbol=us_symbol,
                                start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                                end_date=datetime.now().strftime('%Y-%m-%d')
                            )
                            st.success("✅ 美股緩存測試成功")
                            with st.expander("查看結果"):
                                st.text(result[:500] + "..." if len(result) > 500 else result)
                        except Exception as e:
                            st.error(f"❌ 美股緩存測試失败: {e}")

        with test_col2:
            st.markdown("**測試A股數據緩存**")
            china_symbol = st.text_input("A股代碼", value="000001", key="china_test")
            if st.button("測試A股緩存", key="test_china"):
                if china_symbol:
                    with st.spinner(f"測試 {china_symbol} 緩存..."):
                        try:
                            from datetime import datetime, timedelta
                            provider = get_optimized_china_data_provider()
                            result = provider.get_stock_data(
                                symbol=china_symbol,
                                start_date=(datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                                end_date=datetime.now().strftime('%Y-%m-%d')
                            )
                            st.success("✅ A股緩存測試成功")
                            with st.expander("查看結果"):
                                st.text(result[:500] + "..." if len(result) > 500 else result)
                        except Exception as e:
                            st.error(f"❌ A股緩存測試失败: {e}")
    else:
        st.warning("優化數據提供器不可用，無法進行緩存測試")

    # 原有的緩存詳情部分
    with col2:
        st.subheader("⚙️ 緩存配置")
        
        # 緩存設置
        st.info("""
        **緩存機制說明：**
        
        🔹 **股票數據緩存**：6小時有效期
        - 减少API調用次數
        - 提高數據獲取速度
        - 支持離線分析
        
        🔹 **新聞數據緩存**：24小時有效期
        - 避免重複獲取相同新聞
        - 節省API配額
        
        🔹 **基本面數據緩存**：24小時有效期
        - 减少基本面分析API調用
        - 提高分析響應速度
        """)
        
        # 緩存目錄信息
        cache_dir = cache.cache_dir
        st.markdown(f"**緩存目錄：** `{cache_dir}`")
        
        # 子目錄信息
        st.markdown("**子目錄結構：**")
        st.code(f"""
📁 {cache_dir.name}/
├── 📁 stock_data/     # 股票數據緩存
├── 📁 news_data/      # 新聞數據緩存
├── 📁 fundamentals/   # 基本面數據緩存
└── 📁 metadata/       # 元數據文件
        """)
    
    st.markdown("---")
    
    # 緩存詳情
    st.subheader("📋 緩存詳情")
    
    # 選擇查看的數據類型
    data_type = st.selectbox(
        "選擇數據類型",
        ["stock_data", "news", "fundamentals"],
        format_func=lambda x: {
            "stock_data": "📈 股票數據",
            "news": "📰 新聞數據", 
            "fundamentals": "💼 基本面數據"
        }[x]
    )
    
    # 顯示緩存文件列表
    try:
        metadata_files = list(cache.metadata_dir.glob("*_meta.json"))
        
        if metadata_files:
            import json
            from datetime import datetime
            
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
                except Exception:
                    continue
            
            if cache_items:
                # 按緩存時間排序
                cache_items.sort(key=lambda x: x['cached_at'], reverse=True)
                
                # 顯示表格
                import pandas as pd
                df = pd.DataFrame(cache_items)
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "symbol": st.column_config.TextColumn("股票代碼", width="small"),
                        "data_source": st.column_config.TextColumn("數據源", width="small"),
                        "cached_at": st.column_config.TextColumn("緩存時間", width="medium"),
                        "start_date": st.column_config.TextColumn("開始日期", width="small"),
                        "end_date": st.column_config.TextColumn("結束日期", width="small"),
                        "file_path": st.column_config.TextColumn("文件路徑", width="large")
                    }
                )
                
                st.info(f"📊 找到 {len(cache_items)} 個 {data_type} 類型的緩存文件")
            else:
                st.info(f"📭 暂無 {data_type} 類型的緩存文件")
        else:
            st.info("📭 暂無緩存文件")
            
    except Exception as e:
        st.error(f"讀取緩存詳情失败: {e}")
    
    # 页腳信息
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        💾 緩存管理系統 | TradingAgents v0.1.2 | 
        <a href='https://github.com/your-repo/TradingAgents' target='_blank'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
