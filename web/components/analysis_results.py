"""
分析結果管理組件
提供股票分析歷史結果的查看和管理功能
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import os
from pathlib import Path
import hashlib
import logging

# MongoDB相關導入
try:
    from web.utils.mongodb_report_manager import MongoDBReportManager
    MONGODB_AVAILABLE = True
    print("✅ MongoDB模塊導入成功")
except ImportError as e:
    MONGODB_AVAILABLE = False
    print(f"❌ MongoDB模塊導入失败: {e}")

# 設置日誌
logger = logging.getLogger(__name__)

def safe_timestamp_to_datetime(timestamp_value):
    """安全地将時間戳轉換為datetime對象"""
    if isinstance(timestamp_value, datetime):
        # 如果已經是datetime對象（來自MongoDB）
        return timestamp_value
    elif isinstance(timestamp_value, (int, float)):
        # 如果是時間戳數字（來自文件系統）
        try:
            return datetime.fromtimestamp(timestamp_value)
        except (ValueError, OSError):
            # 時間戳無效，使用當前時間
            return datetime.now()
    else:
        # 其他情況，使用當前時間
        return datetime.now()

def get_analysis_results_dir():
    """獲取分析結果目錄"""
    results_dir = Path(__file__).parent.parent / "data" / "analysis_results"
    results_dir.mkdir(parents=True, exist_ok=True)
    return results_dir

def get_favorites_file():
    """獲取收藏文件路徑"""
    return get_analysis_results_dir() / "favorites.json"

def get_tags_file():
    """獲取標簽文件路徑"""
    return get_analysis_results_dir() / "tags.json"

def load_favorites():
    """加載收藏列表"""
    favorites_file = get_favorites_file()
    if favorites_file.exists():
        try:
            with open(favorites_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_favorites(favorites):
    """保存收藏列表"""
    favorites_file = get_favorites_file()
    try:
        with open(favorites_file, 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_tags():
    """加載標簽數據"""
    tags_file = get_tags_file()
    if tags_file.exists():
        try:
            with open(tags_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_tags(tags):
    """保存標簽數據"""
    tags_file = get_tags_file()
    try:
        with open(tags_file, 'w', encoding='utf-8') as f:
            json.dump(tags, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def add_tag_to_analysis(analysis_id, tag):
    """為分析結果添加標簽"""
    tags = load_tags()
    if analysis_id not in tags:
        tags[analysis_id] = []
    if tag not in tags[analysis_id]:
        tags[analysis_id].append(tag)
        save_tags(tags)

def remove_tag_from_analysis(analysis_id, tag):
    """從分析結果移除標簽"""
    tags = load_tags()
    if analysis_id in tags and tag in tags[analysis_id]:
        tags[analysis_id].remove(tag)
        if not tags[analysis_id]:  # 如果没有標簽了，刪除该條目
            del tags[analysis_id]
        save_tags(tags)

def get_analysis_tags(analysis_id):
    """獲取分析結果的標簽"""
    tags = load_tags()
    return tags.get(analysis_id, [])

def load_analysis_results(start_date=None, end_date=None, stock_symbol=None, analyst_type=None,
                         limit=100, search_text=None, tags_filter=None, favorites_only=False):
    """加載分析結果 - 優先從MongoDB加載"""
    all_results = []
    favorites = load_favorites() if favorites_only else []
    tags_data = load_tags()
    mongodb_loaded = False

    # 優先從MongoDB加載數據
    if MONGODB_AVAILABLE:
        try:
            print("🔍 [數據加載] 從MongoDB加載分析結果")
            mongodb_manager = MongoDBReportManager()
            mongodb_results = mongodb_manager.get_all_reports()
            print(f"🔍 [數據加載] MongoDB返回 {len(mongodb_results)} 個結果")

            for mongo_result in mongodb_results:
                # 轉換MongoDB結果格式
                result = {
                    'analysis_id': mongo_result.get('analysis_id', ''),
                    'timestamp': mongo_result.get('timestamp', 0),
                    'stock_symbol': mongo_result.get('stock_symbol', ''),
                    'analysts': mongo_result.get('analysts', []),
                    'research_depth': mongo_result.get('research_depth', 1),
                    'status': mongo_result.get('status', 'completed'),
                    'summary': mongo_result.get('summary', ''),
                    'performance': mongo_result.get('performance', {}),
                    'tags': tags_data.get(mongo_result.get('analysis_id', ''), []),
                    'is_favorite': mongo_result.get('analysis_id', '') in favorites,
                    'reports': mongo_result.get('reports', {}),
                    'source': 'mongodb'  # 標記數據來源
                }
                all_results.append(result)

            mongodb_loaded = True
            print(f"✅ 從MongoDB加載了 {len(mongodb_results)} 個分析結果")

        except Exception as e:
            print(f"❌ MongoDB加載失败: {e}")
            logger.error(f"MongoDB加載失败: {e}")
            mongodb_loaded = False
    else:
        print("⚠️ MongoDB不可用，将使用文件系統數據")

    # 只有在MongoDB加載失败或不可用時才從文件系統加載
    if not mongodb_loaded:
        print("🔄 [備用數據源] 從文件系統加載分析結果")

        # 首先嘗試從Web界面的保存位置讀取
        web_results_dir = get_analysis_results_dir()
        for result_file in web_results_dir.glob("*.json"):
            if result_file.name in ['favorites.json', 'tags.json']:
                continue

            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    result = json.load(f)

                    # 添加標簽信息
                    result['tags'] = tags_data.get(result.get('analysis_id', ''), [])
                    result['is_favorite'] = result.get('analysis_id', '') in favorites
                    result['source'] = 'file_system'  # 標記數據來源

                    all_results.append(result)
            except Exception as e:
                st.warning(f"讀取分析結果文件 {result_file.name} 失败: {e}")

        # 然後從實际的分析結果保存位置讀取
        project_results_dir = Path(__file__).parent.parent.parent / "data" / "analysis_results" / "detailed"

        if project_results_dir.exists():
            # 遍歷股票代碼目錄
            for stock_dir in project_results_dir.iterdir():
                if not stock_dir.is_dir():
                    continue

                stock_code = stock_dir.name

                # 遍歷日期目錄
                for date_dir in stock_dir.iterdir():
                    if not date_dir.is_dir():
                        continue

                    date_str = date_dir.name
                    reports_dir = date_dir / "reports"

                    if not reports_dir.exists():
                        continue

                    # 讀取所有報告文件
                    reports = {}
                    summary_content = ""

                    for report_file in reports_dir.glob("*.md"):
                        try:
                            with open(report_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                report_name = report_file.stem
                                reports[report_name] = content

                                # 如果是最終決策報告，提取摘要
                                if report_name == "final_trade_decision":
                                    # 提取前200個字符作為摘要
                                    summary_content = content[:200].replace('#', '').replace('*', '').strip()
                                    if len(content) > 200:
                                        summary_content += "..."

                        except Exception as e:
                            continue

                    if reports:
                        # 解析日期
                        try:
                            analysis_date = datetime.strptime(date_str, '%Y-%m-%d')
                            timestamp = analysis_date.timestamp()
                        except:
                            timestamp = datetime.now().timestamp()

                        # 創建分析結果條目
                        analysis_id = f"{stock_code}_{date_str}_{int(timestamp)}"

                        # 嘗試從元數據文件中讀取真實的研究深度和分析師信息
                        research_depth = 1
                        analysts = ['market', 'fundamentals', 'trader']  # 默認值

                        metadata_file = date_dir / "analysis_metadata.json"
                        if metadata_file.exists():
                            try:
                                with open(metadata_file, 'r', encoding='utf-8') as f:
                                    metadata = json.load(f)
                                    research_depth = metadata.get('research_depth', 1)
                                    analysts = metadata.get('analysts', analysts)
                            except Exception as e:
                                # 如果讀取元數據失败，使用推斷邏輯
                                if len(reports) >= 5:
                                    research_depth = 3
                                elif len(reports) >= 3:
                                    research_depth = 2
                        else:
                            # 如果没有元數據文件，使用推斷邏輯
                            if len(reports) >= 5:
                                research_depth = 3
                            elif len(reports) >= 3:
                                research_depth = 2

                        result = {
                            'analysis_id': analysis_id,
                            'timestamp': timestamp,
                            'stock_symbol': stock_code,
                            'analysts': analysts,
                            'research_depth': research_depth,
                            'status': 'completed',
                            'summary': summary_content,
                            'performance': {},
                            'tags': tags_data.get(analysis_id, []),
                            'is_favorite': analysis_id in favorites,
                            'reports': reports,  # 保存所有報告內容
                            'source': 'file_system'  # 標記數據來源
                        }

                        all_results.append(result)

        print(f"🔄 [備用數據源] 從文件系統加載了 {len(all_results)} 個分析結果")
    
    # 過濾結果
    filtered_results = []
    for result in all_results:
        # 收藏過濾
        if favorites_only and not result.get('is_favorite', False):
            continue
            
        # 時間過濾
        if start_date or end_date:
            result_time = safe_timestamp_to_datetime(result.get('timestamp', 0))
            if start_date and result_time.date() < start_date:
                continue
            if end_date and result_time.date() > end_date:
                continue
        
        # 股票代碼過濾
        if stock_symbol and stock_symbol.upper() not in result.get('stock_symbol', '').upper():
            continue
        
        # 分析師類型過濾
        if analyst_type and analyst_type not in result.get('analysts', []):
            continue
            
        # 文本搜索過濾
        if search_text:
            search_text = search_text.lower()
            searchable_text = f"{result.get('stock_symbol', '')} {result.get('summary', '')} {' '.join(result.get('analysts', []))}".lower()
            if search_text not in searchable_text:
                continue
                
        # 標簽過濾
        if tags_filter:
            result_tags = result.get('tags', [])
            if not any(tag in result_tags for tag in tags_filter):
                continue
        
        filtered_results.append(result)
    
    # 按時間倒序排列 - 使用安全的時間戳轉換函數確保類型一致
    filtered_results.sort(key=lambda x: safe_timestamp_to_datetime(x.get('timestamp', 0)), reverse=True)
    
    # 限制數量
    return filtered_results[:limit]

def render_analysis_results():
    """渲染分析結果管理界面"""
    
    # 檢查權限
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from utils.auth_manager import auth_manager
        
        if not auth_manager or not auth_manager.check_permission("analysis"):
            st.error("❌ 您没有權限訪問分析結果")
            st.info("💡 提示：分析結果功能需要 'analysis' 權限")
            return
    except Exception as e:
        st.error(f"❌ 權限檢查失败: {e}")
        return
    
    st.title("📊 分析結果歷史記錄")
    
    # 侧邊栏過濾選項
    with st.sidebar:
        st.header("🔍 搜索与過濾")
        
        # 文本搜索
        search_text = st.text_input("🔍 關键詞搜索", placeholder="搜索股票代碼、摘要內容...")
        
        # 收藏過濾
        favorites_only = st.checkbox("⭐ 仅顯示收藏")
        
        # 日期範围選擇
        date_range = st.selectbox(
            "📅 時間範围",
            ["最近1天", "最近3天", "最近7天", "最近30天", "自定義"],
            index=2
        )
        
        if date_range == "自定義":
            start_date = st.date_input("開始日期", datetime.now() - timedelta(days=7))
            end_date = st.date_input("結束日期", datetime.now())
        else:
            days_map = {"最近1天": 1, "最近3天": 3, "最近7天": 7, "最近30天": 30}
            days = days_map[date_range]
            end_date = datetime.now().date()
            start_date = (datetime.now() - timedelta(days=days)).date()
        
        # 股票代碼過濾
        stock_filter = st.text_input("📈 股票代碼", placeholder="如: 000001, AAPL")
        
        # 分析師類型過濾
        analyst_filter = st.selectbox(
            "👥 分析師類型",
            ["全部", "market_analyst", "social_media_analyst", "news_analyst", "fundamental_analyst"],
            help="註意：社交媒體分析師仅適用於美股和港股，A股分析中不包含此類型"
        )
        
        if analyst_filter == "全部":
            analyst_filter = None
            
        # 標簽過濾
        all_tags = set()
        tags_data = load_tags()
        for tag_list in tags_data.values():
            all_tags.update(tag_list)
        
        if all_tags:
            selected_tags = st.multiselect("🏷️ 標簽過濾", sorted(all_tags))
        else:
            selected_tags = []
    
    # 加載分析結果
    results = load_analysis_results(
        start_date=start_date,
        end_date=end_date,
        stock_symbol=stock_filter if stock_filter else None,
        analyst_type=analyst_filter,
        limit=200,
        search_text=search_text if search_text else None,
        tags_filter=selected_tags if selected_tags else None,
        favorites_only=favorites_only
    )
    
    if not results:
        st.warning("📭 未找到符合條件的分析結果")
        return
    
    # 顯示統計概覽
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 总分析數", len(results))
    
    with col2:
        unique_stocks = len(set(result.get('stock_symbol', 'unknown') for result in results))
        st.metric("📈 分析股票", unique_stocks)
    
    with col3:
        successful_analyses = sum(1 for result in results if result.get('status') == 'completed')
        success_rate = (successful_analyses / len(results) * 100) if results else 0
        st.metric("✅ 成功率", f"{success_rate:.1f}%")
    
    with col4:
        favorites_count = sum(1 for result in results if result.get('is_favorite', False))
        st.metric("⭐ 收藏數", favorites_count)
    
    # 保留需要的功能按钮，移除不需要的功能
    tab1, tab2, tab3 = st.tabs([
        "📋 結果列表", "📈 統計圖表", "📊 詳細分析"
    ])
    
    with tab1:
        render_results_list(results)
    
    with tab2:
        render_results_charts(results)
    
    with tab3:
        render_detailed_analysis(results)

def render_results_list(results: List[Dict[str, Any]]):
    """渲染分析結果列表"""
    
    st.subheader("📋 分析結果列表")
    
    # 排序選項
    col1, col2 = st.columns([2, 1])
    with col1:
        sort_by = st.selectbox("排序方式", ["時間倒序", "時間正序", "股票代碼", "成功率"])
    with col2:
        view_mode = st.selectbox("顯示模式", ["卡片視圖", "表格視圖"])
    
    # 排序結果
    if sort_by == "時間正序":
        results.sort(key=lambda x: safe_timestamp_to_datetime(x.get('timestamp', 0)))
    elif sort_by == "股票代碼":
        results.sort(key=lambda x: x.get('stock_symbol', ''))
    elif sort_by == "成功率":
        results.sort(key=lambda x: 1 if x.get('status') == 'completed' else 0, reverse=True)
    
    if view_mode == "表格視圖":
        render_results_table(results)
    else:
        render_results_cards(results)

def render_results_table(results: List[Dict[str, Any]]):
    """渲染表格視圖"""
    
    # 準备表格數據
    table_data = []
    for result in results:
        table_data.append({
            '時間': safe_timestamp_to_datetime(result.get('timestamp', 0)).strftime('%m-%d %H:%M'),
            '股票': result.get('stock_symbol', 'unknown'),
            '分析師': ', '.join(result.get('analysts', [])[:2]) + ('...' if len(result.get('analysts', [])) > 2 else ''),
            '狀態': '✅' if result.get('status') == 'completed' else '❌',
            '收藏': '⭐' if result.get('is_favorite', False) else '',
            '標簽': ', '.join(result.get('tags', [])[:2]) + ('...' if len(result.get('tags', [])) > 2 else ''),
            '摘要': (result.get('summary', '')[:50] + '...') if len(result.get('summary', '')) > 50 else result.get('summary', '')
        })
    
    if table_data:
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)

def render_results_cards(results: List[Dict[str, Any]]):
    """渲染卡片視圖"""
    
    # 分页設置
    page_size = st.selectbox("每页顯示", [5, 10, 20, 50], index=1)
    total_pages = (len(results) + page_size - 1) // page_size
    
    if total_pages > 1:
        page = st.number_input("页碼", min_value=1, max_value=total_pages, value=1) - 1
    else:
        page = 0
    
    # 獲取當前页數據
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, len(results))
    page_results = results[start_idx:end_idx]
    
    # 顯示結果卡片
    for i, result in enumerate(page_results):
        analysis_id = result.get('analysis_id', '')
        
        with st.container():
            # 卡片頭部
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"### 📊 {result.get('stock_symbol', 'unknown')}")
                st.caption(f"🕐 {safe_timestamp_to_datetime(result.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            with col2:
                # 收藏按钮
                is_favorite = result.get('is_favorite', False)
                if st.button("⭐" if is_favorite else "☆", key=f"fav_{start_idx + i}"):
                    toggle_favorite(analysis_id)
                    st.rerun()
            
            with col3:
                # 查看詳情按钮
                result_id = result.get('_id') or result.get('analysis_id') or f"result_{start_idx + i}"
                current_expanded = st.session_state.get('expanded_result_id') == result_id
                button_text = "🔼 收起" if current_expanded else "👁️ 詳情"

                if st.button(button_text, key=f"view_{start_idx + i}"):
                    if current_expanded:
                        # 如果當前已展開，則收起
                        st.session_state['expanded_result_id'] = None
                    else:
                        # 展開當前結果的詳情
                        st.session_state['expanded_result_id'] = result_id
                        st.session_state['selected_result_for_detail'] = result
                    st.rerun()
            
            with col4:
                # 狀態顯示
                status_icon = "✅" if result.get('status') == 'completed' else "❌"
                st.markdown(f"**狀態**: {status_icon}")
            
            # 卡片內容
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**分析師**: {', '.join(result.get('analysts', []))}")
                st.write(f"**研究深度**: {result.get('research_depth', 'unknown')}")

                # 顯示分析摘要
                if result.get('summary'):
                    summary = result['summary'][:150] + "..." if len(result['summary']) > 150 else result['summary']
                    st.write(f"**摘要**: {summary}")
            
            with col2:
                # 顯示標簽
                tags = result.get('tags', [])
                if tags:
                    st.write("**標簽**:")
                    for tag in tags[:3]:  # 最多顯示3個標簽
                        st.markdown(f"`{tag}`")
                    if len(tags) > 3:
                        st.caption(f"还有 {len(tags) - 3} 個標簽...")

            # 顯示折叠詳情
            result_id = result.get('_id') or result.get('analysis_id') or f"result_{start_idx + i}"
            if st.session_state.get('expanded_result_id') == result_id:
                show_expanded_detail(result)

            st.divider()
    
    # 顯示分页信息
    if total_pages > 1:
        st.info(f"第 {page + 1} 页，共 {total_pages} 页，总計 {len(results)} 條記錄")
    
    # 註意：詳情現在以折叠方式顯示在每個結果下方

# 弹窗功能已移除，詳情現在以折叠方式顯示

def toggle_favorite(analysis_id):
    """切換收藏狀態"""
    favorites = load_favorites()
    if analysis_id in favorites:
        favorites.remove(analysis_id)
    else:
        favorites.append(analysis_id)
    save_favorites(favorites)

def render_results_comparison(results: List[Dict[str, Any]]):
    """渲染結果對比功能"""
    
    st.subheader("🔄 分析結果對比")
    
    if len(results) < 2:
        st.warning("至少需要2個分析結果才能進行對比")
        return
    
    # 選擇要對比的結果
    col1, col2 = st.columns(2)
    
    result_options = []
    for i, result in enumerate(results[:20]):  # 限制選項數量
        option = f"{result.get('stock_symbol', 'unknown')} - {safe_timestamp_to_datetime(result.get('timestamp', 0)).strftime('%m-%d %H:%M')}"
        result_options.append((option, i))
    
    with col1:
        st.write("**選擇結果A**")
        selected_a = st.selectbox("結果A", result_options, format_func=lambda x: x[0], key="compare_a")
        result_a = results[selected_a[1]]
    
    with col2:
        st.write("**選擇結果B**")
        selected_b = st.selectbox("結果B", result_options, format_func=lambda x: x[0], key="compare_b")
        result_b = results[selected_b[1]]
    
    if selected_a[1] == selected_b[1]:
        st.warning("請選擇不同的分析結果進行對比")
        return
    
    # 對比顯示
    st.markdown("---")
    
    # 基本信息對比
    st.subheader("📋 基本信息對比")
    
    comparison_data = {
        '項目': ['股票代碼', '分析時間', '分析師', '研究深度', '狀態'],
        '結果A': [
            result_a.get('stock_symbol', 'unknown'),
            safe_timestamp_to_datetime(result_a.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M'),
            ', '.join(result_a.get('analysts', [])),
            str(result_a.get('research_depth', 'unknown')),
            '完成' if result_a.get('status') == 'completed' else '失败'
        ],
        '結果B': [
            result_b.get('stock_symbol', 'unknown'),
            safe_timestamp_to_datetime(result_b.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M'),
            ', '.join(result_b.get('analysts', [])),
            str(result_b.get('research_depth', 'unknown')),
            '完成' if result_b.get('status') == 'completed' else '失败'
        ]
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # 摘要對比
    if result_a.get('summary') or result_b.get('summary'):
        st.subheader("📝 分析摘要對比")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**結果A摘要**")
            st.text_area("", value=result_a.get('summary', '暂無摘要'), height=200, key="summary_a", disabled=True)
        
        with col2:
            st.write("**結果B摘要**")
            st.text_area("", value=result_b.get('summary', '暂無摘要'), height=200, key="summary_b", disabled=True)
    
    # 性能對比
    perf_a = result_a.get('performance', {})
    perf_b = result_b.get('performance', {})
    
    if perf_a or perf_b:
        st.subheader("⚡ 性能指標對比")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**結果A性能**")
            if perf_a:
                st.json(perf_a)
            else:
                st.info("暂無性能數據")
        
        with col2:
            st.write("**結果B性能**")
            if perf_b:
                st.json(perf_b)
            else:
                st.info("暂無性能數據")

def render_results_charts(results: List[Dict[str, Any]]):
    """渲染分析結果統計圖表"""
    
    st.subheader("📈 統計圖表")
    
    # 按股票統計
    st.subheader("📊 按股票統計")
    stock_counts = {}
    for result in results:
        stock = result.get('stock_symbol', 'unknown')
        stock_counts[stock] = stock_counts.get(stock, 0) + 1
    
    if stock_counts:
        # 只顯示前10個最常分析的股票
        top_stocks = sorted(stock_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        stocks = [item[0] for item in top_stocks]
        counts = [item[1] for item in top_stocks]
        
        fig_bar = px.bar(
            x=stocks,
            y=counts,
            title="最常分析的股票 (前10名)",
            labels={'x': '股票代碼', 'y': '分析次數'},
            color=counts,
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # 按時間統計
    st.subheader("📅 每日分析趋势")
    daily_results = {}
    for result in results:
        date_str = safe_timestamp_to_datetime(result.get('timestamp', 0)).strftime('%Y-%m-%d')
        daily_results[date_str] = daily_results.get(date_str, 0) + 1
    
    if daily_results:
        dates = sorted(daily_results.keys())
        counts = [daily_results[date] for date in dates]
        
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=dates,
            y=counts,
            mode='lines+markers',
            name='每日分析數',
            line=dict(color='#2E8B57', width=3),
            marker=dict(size=8, color='#FF6B6B'),
            fill='tonexty'
        ))
        fig_line.update_layout(
            title="每日分析趋势",
            xaxis_title="日期",
            yaxis_title="分析數量",
            hovermode='x unified'
        )
        st.plotly_chart(fig_line, use_container_width=True)
    
    # 按分析師類型統計
    st.subheader("👥 分析師使用分布")
    analyst_counts = {}
    for result in results:
        analysts = result.get('analysts', [])
        for analyst in analysts:
            analyst_counts[analyst] = analyst_counts.get(analyst, 0) + 1
    
    if analyst_counts:
        fig_pie = px.pie(
            values=list(analyst_counts.values()),
            names=list(analyst_counts.keys()),
            title="分析師使用分布",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # 成功率統計
    st.subheader("✅ 分析成功率統計")
    success_data = {'成功': 0, '失败': 0}
    for result in results:
        if result.get('status') == 'completed':
            success_data['成功'] += 1
        else:
            success_data['失败'] += 1
    
    if success_data['成功'] + success_data['失败'] > 0:
        fig_success = px.pie(
            values=list(success_data.values()),
            names=list(success_data.keys()),
            title="分析成功率",
            color_discrete_map={'成功': '#4CAF50', '失败': '#F44336'}
        )
        st.plotly_chart(fig_success, use_container_width=True)
    
    # 標簽使用統計
    tags_data = load_tags()
    if tags_data:
        st.subheader("🏷️ 標簽使用統計")
        tag_counts = {}
        for tag_list in tags_data.values():
            for tag in tag_list:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        if tag_counts:
            # 只顯示前10個最常用的標簽
            top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            tags = [item[0] for item in top_tags]
            counts = [item[1] for item in top_tags]
            
            fig_tags = px.bar(
                x=tags,
                y=counts,
                title="最常用標簽 (前10名)",
                labels={'x': '標簽', 'y': '使用次數'},
                color=counts,
                color_continuous_scale='plasma'
            )
            fig_tags.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_tags, use_container_width=True)

def render_tags_management(results: List[Dict[str, Any]]):
    """渲染標簽管理功能"""
    
    st.subheader("🏷️ 標簽管理")
    
    # 獲取所有標簽
    all_tags = set()
    tags_data = load_tags()
    for tag_list in tags_data.values():
        all_tags.update(tag_list)
    
    # 標簽統計
    if all_tags:
        st.write("**現有標簽統計**")
        tag_counts = {}
        for tag_list in tags_data.values():
            for tag in tag_list:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # 顯示標簽云
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # 創建標簽云可視化
            if tag_counts:
                fig = px.bar(
                    x=list(tag_counts.keys()),
                    y=list(tag_counts.values()),
                    title="標簽使用頻率",
                    labels={'x': '標簽', 'y': '使用次數'}
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.write("**標簽列表**")
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
                st.write(f"• {tag} ({count})")
    
    # 批量標簽操作
    st.markdown("---")
    st.write("**批量標簽操作**")
    
    # 選擇要操作的結果
    if results:
        selected_results = st.multiselect(
            "選擇分析結果",
            options=range(len(results)),
            format_func=lambda i: f"{results[i].get('stock_symbol', 'unknown')} - {safe_timestamp_to_datetime(results[i].get('timestamp', 0)).strftime('%m-%d %H:%M')}",
            max_selections=10
        )
        
        if selected_results:
            col1, col2 = st.columns(2)
            
            with col1:
                # 添加標簽
                new_tag = st.text_input("新標簽名稱", placeholder="輸入標簽名稱")
                if st.button("➕ 添加標簽") and new_tag:
                    for idx in selected_results:
                        analysis_id = results[idx].get('analysis_id', '')
                        if analysis_id:
                            add_tag_to_analysis(analysis_id, new_tag)
                    st.success(f"已為 {len(selected_results)} 個結果添加標簽: {new_tag}")
                    st.rerun()
            
            with col2:
                # 移除標簽
                if all_tags:
                    remove_tag = st.selectbox("選擇要移除的標簽", sorted(all_tags))
                    if st.button("➖ 移除標簽") and remove_tag:
                        for idx in selected_results:
                            analysis_id = results[idx].get('analysis_id', '')
                            if analysis_id:
                                remove_tag_from_analysis(analysis_id, remove_tag)
                        st.success(f"已從 {len(selected_results)} 個結果移除標簽: {remove_tag}")
                        st.rerun()

def render_results_export(results: List[Dict[str, Any]]):
    """渲染分析結果導出功能"""
    
    st.subheader("📤 導出分析結果")
    
    if not results:
        st.warning("没有可導出的分析結果")
        return
    
    # 導出選項
    export_type = st.selectbox("選擇導出內容", ["摘要信息", "完整數據"])
    export_format = st.selectbox("選擇導出格式", ["CSV", "JSON", "Excel"])
    
    if st.button("📥 導出結果"):
        try:
            if export_type == "摘要信息":
                # 導出摘要信息
                summary_data = []
                for result in results:
                    summary_data.append({
                        '分析時間': safe_timestamp_to_datetime(result.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S'),
                        '股票代碼': result.get('stock_symbol', 'unknown'),
                        '分析師': ', '.join(result.get('analysts', [])),
                        '研究深度': result.get('research_depth', 'unknown'),
                        '狀態': result.get('status', 'unknown'),
                        '摘要': result.get('summary', '')[:100] + '...' if len(result.get('summary', '')) > 100 else result.get('summary', '')
                    })
                
                if export_format == "CSV":
                    df = pd.DataFrame(summary_data)
                    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                    
                    st.download_button(
                        label="下載 CSV 文件",
                        data=csv_data,
                        file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                elif export_format == "JSON":
                    json_data = json.dumps(summary_data, ensure_ascii=False, indent=2)
                    
                    st.download_button(
                        label="下載 JSON 文件",
                        data=json_data,
                        file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                
                elif export_format == "Excel":
                    df = pd.DataFrame(summary_data)
                    
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='分析摘要')
                    
                    excel_data = output.getvalue()
                    
                    st.download_button(
                        label="下載 Excel 文件",
                        data=excel_data,
                        file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            
            else:  # 完整數據
                if export_format == "JSON":
                    json_data = json.dumps(results, ensure_ascii=False, indent=2)
                    
                    st.download_button(
                        label="下載完整數據 JSON 文件",
                        data=json_data,
                        file_name=f"analysis_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
                else:
                    st.warning("完整數據只支持 JSON 格式導出")
            
            st.success(f"✅ {export_format} 文件準备完成，請點擊下載按钮")
            
        except Exception as e:
            st.error(f"❌ 導出失败: {e}")

def render_results_comparison(results: List[Dict[str, Any]]):
    """渲染分析結果對比"""
    
    st.subheader("🔍 分析結果對比")
    
    if len(results) < 2:
        st.info("至少需要2個分析結果才能進行對比")
        return
    
    # 選擇要對比的分析結果
    st.write("**選擇要對比的分析結果：**")
    
    col1, col2 = st.columns(2)
    
    # 準备選項
    result_options = []
    for i, result in enumerate(results[:20]):  # 限制前20個
        option = f"{result.get('stock_symbol', 'unknown')} - {safe_timestamp_to_datetime(result.get('timestamp', 0)).strftime('%m-%d %H:%M')}"
        result_options.append((option, i))
    
    with col1:
        st.write("**分析結果 A**")
        selected_a = st.selectbox(
            "選擇第一個分析結果", 
            result_options, 
            format_func=lambda x: x[0],
            key="compare_a"
        )
        result_a = results[selected_a[1]]
    
    with col2:
        st.write("**分析結果 B**")
        selected_b = st.selectbox(
            "選擇第二個分析結果", 
            result_options, 
            format_func=lambda x: x[0],
            key="compare_b"
        )
        result_b = results[selected_b[1]]
    
    if selected_a[1] == selected_b[1]:
        st.warning("請選擇不同的分析結果進行對比")
        return
    
    # 基本信息對比
    st.subheader("📊 基本信息對比")
    
    comparison_data = {
        "項目": ["股票代碼", "分析時間", "分析師數量", "研究深度", "狀態", "標簽數量"],
        "分析結果 A": [
            result_a.get('stock_symbol', 'unknown'),
            safe_timestamp_to_datetime(result_a.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M'),
            len(result_a.get('analysts', [])),
            result_a.get('research_depth', 'unknown'),
            "✅ 完成" if result_a.get('status') == 'completed' else "❌ 失败",
            len(result_a.get('tags', []))
        ],
        "分析結果 B": [
            result_b.get('stock_symbol', 'unknown'),
            safe_timestamp_to_datetime(result_b.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M'),
            len(result_b.get('analysts', [])),
            result_b.get('research_depth', 'unknown'),
            "✅ 完成" if result_b.get('status') == 'completed' else "❌ 失败",
            len(result_b.get('tags', []))
        ]
    }
    
    import pandas as pd
    df_comparison = pd.DataFrame(comparison_data)
    st.dataframe(df_comparison, use_container_width=True)
    
    # 性能指標對比
    perf_a = result_a.get('performance', {})
    perf_b = result_b.get('performance', {})
    
    if perf_a or perf_b:
        st.subheader("⚡ 性能指標對比")
        
        # 合並所有性能指標键
        all_perf_keys = set(perf_a.keys()) | set(perf_b.keys())
        
        if all_perf_keys:
            perf_comparison = {
                "指標": list(all_perf_keys),
                "分析結果 A": [perf_a.get(key, "N/A") for key in all_perf_keys],
                "分析結果 B": [perf_b.get(key, "N/A") for key in all_perf_keys]
            }
            
            df_perf = pd.DataFrame(perf_comparison)
            st.dataframe(df_perf, use_container_width=True)
    
    # 標簽對比
    tags_a = set(result_a.get('tags', []))
    tags_b = set(result_b.get('tags', []))
    
    if tags_a or tags_b:
        st.subheader("🏷️ 標簽對比")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**共同標簽**")
            common_tags = tags_a & tags_b
            if common_tags:
                for tag in common_tags:
                    st.markdown(f"✅ `{tag}`")
            else:
                st.write("無共同標簽")
        
        with col2:
            st.write("**仅在結果A中**")
            only_a = tags_a - tags_b
            if only_a:
                for tag in only_a:
                    st.markdown(f"🔵 `{tag}`")
            else:
                st.write("無獨有標簽")
        
        with col3:
            st.write("**仅在結果B中**")
            only_b = tags_b - tags_a
            if only_b:
                for tag in only_b:
                    st.markdown(f"🔴 `{tag}`")
            else:
                st.write("無獨有標簽")
    
    # 摘要對比
    summary_a = result_a.get('summary', '')
    summary_b = result_b.get('summary', '')
    
    if summary_a or summary_b:
        st.subheader("📝 分析摘要對比")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**分析結果 A 摘要**")
            if summary_a:
                st.markdown(summary_a)
            else:
                st.write("無摘要")
        
        with col2:
            st.write("**分析結果 B 摘要**")
            if summary_b:
                st.markdown(summary_b)
            else:
                st.write("無摘要")
    
    # 詳細內容對比
    st.subheader("📊 詳細內容對比")
    
    # 定義要對比的關键字段
    comparison_fields = [
        ('market_report', '📈 市場技術分析'),
        ('fundamentals_report', '💰 基本面分析'),
        ('sentiment_report', '💭 市場情绪分析'),
        ('news_report', '📰 新聞事件分析'),
        ('risk_assessment', '⚠️ 風險評估'),
        ('investment_plan', '📋 投資建議'),
        ('final_trade_decision', '🎯 最終交易決策')
    ]
    
    # 創建對比標簽页
    available_fields = []
    for field_key, field_name in comparison_fields:
        if (field_key in result_a and result_a[field_key]) or (field_key in result_b and result_b[field_key]):
            available_fields.append((field_key, field_name))
    
    if available_fields:
        tabs = st.tabs([field_name for _, field_name in available_fields])
        
        for i, (tab, (field_key, field_name)) in enumerate(zip(tabs, available_fields)):
            with tab:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**分析結果 A**")
                    content_a = result_a.get(field_key, '')
                    if content_a:
                        if isinstance(content_a, str):
                            st.markdown(content_a)
                        else:
                            st.write(content_a)
                    else:
                        st.write("無此項分析")
                
                with col2:
                    st.write("**分析結果 B**")
                    content_b = result_b.get(field_key, '')
                    if content_b:
                        if isinstance(content_b, str):
                            st.markdown(content_b)
                        else:
                            st.write(content_b)
                    else:
                        st.write("無此項分析")

def render_detailed_analysis(results: List[Dict[str, Any]]):
    """渲染詳細分析"""
    
    st.subheader("📊 詳細分析")
    
    if not results:
        st.info("没有可分析的數據")
        return
    
    # 選擇要查看的分析結果
    result_options = []
    for i, result in enumerate(results[:50]):  # 顯示前50個
        option = f"{result.get('stock_symbol', 'unknown')} - {safe_timestamp_to_datetime(result.get('timestamp', 0)).strftime('%m-%d %H:%M')}"
        result_options.append((option, i))
    
    if result_options:
        selected_option = st.selectbox(
            "選擇分析結果", 
            result_options, 
            format_func=lambda x: x[0]
        )
        selected_result = results[selected_option[1]]
        
        # 顯示基本信息
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("股票代碼", selected_result.get('stock_symbol', 'unknown'))
            st.metric("分析師數量", len(selected_result.get('analysts', [])))
        
        with col2:
            analysis_time = safe_timestamp_to_datetime(selected_result.get('timestamp', 0))
            st.metric("分析時間", analysis_time.strftime('%m-%d %H:%M'))
            status = "✅ 完成" if selected_result.get('status') == 'completed' else "❌ 失败"
            st.metric("狀態", status)
        
        with col3:
            st.metric("研究深度", selected_result.get('research_depth', 'unknown'))
            tags = selected_result.get('tags', [])
            st.metric("標簽數量", len(tags))
        
        # 顯示標簽
        if tags:
            st.write("**標簽**:")
            tag_cols = st.columns(min(len(tags), 5))
            for i, tag in enumerate(tags):
                with tag_cols[i % 5]:
                    st.markdown(f"`{tag}`")
        
        # 顯示分析摘要
        if selected_result.get('summary'):
            st.subheader("📝 分析摘要")
            st.markdown(selected_result['summary'])
        
        # 顯示性能指標
        performance = selected_result.get('performance', {})
        if performance:
            st.subheader("⚡ 性能指標")
            perf_cols = st.columns(len(performance))
            for i, (key, value) in enumerate(performance.items()):
                with perf_cols[i]:
                    st.metric(key.replace('_', ' ').title(), f"{value:.2f}" if isinstance(value, (int, float)) else str(value))
        
        # 顯示完整分析結果
        if st.checkbox("顯示完整分析結果"):
            render_detailed_analysis_content(selected_result)

def render_detailed_analysis_content(selected_result):
    """渲染詳細分析結果內容"""
    st.subheader("📊 完整分析數據")

    # 檢查是否有報告數據（支持文件系統和MongoDB）
    if 'reports' in selected_result and selected_result['reports']:
        # 顯示文件系統中的報告
        reports = selected_result['reports']
        
        if not reports:
            st.warning("该分析結果没有可用的報告內容")
            return
        
        # 調試信息：顯示所有可用的報告
        print(f"🔍 [弹窗調試] 數據來源: {selected_result.get('source', '未知')}")
        print(f"🔍 [弹窗調試] 可用報告數量: {len(reports)}")
        print(f"🔍 [弹窗調試] 報告類型: {list(reports.keys())}")

        # 創建標簽页顯示不同的報告
        report_tabs = list(reports.keys())

        # 為報告名稱添加中文標題和圖標
        report_display_names = {
            'final_trade_decision': '🎯 最終交易決策',
            'fundamentals_report': '💰 基本面分析',
            'technical_report': '📈 技術面分析',
            'market_sentiment_report': '💭 市場情绪分析',
            'risk_assessment_report': '⚠️ 風險評估',
            'price_target_report': '🎯 目標價格分析',
            'summary_report': '📋 分析摘要',
            'news_analysis_report': '📰 新聞分析',
            'social_media_report': '📱 社交媒體分析'
        }
        
        # 創建顯示名稱列表
        tab_names = []
        for report_key in report_tabs:
            display_name = report_display_names.get(report_key, f"📄 {report_key.replace('_', ' ').title()}")
            tab_names.append(display_name)
            print(f"🔍 [弹窗調試] 添加標簽: {display_name}")

        print(f"🔍 [弹窗調試] 总標簽數: {len(tab_names)}")
        
        if len(tab_names) == 1:
            # 只有一個報告，直接顯示
            st.markdown(f"### {tab_names[0]}")
            st.markdown("---")
            st.markdown(reports[report_tabs[0]])
        else:
            # 多個報告，使用標簽页
            tabs = st.tabs(tab_names)
            
            for i, (tab, report_key) in enumerate(zip(tabs, report_tabs)):
                with tab:
                    st.markdown(reports[report_key])
        
        return
    
    # 添加自定義CSS樣式美化標簽页
    st.markdown("""
    <style>
    /* 標簽页容器樣式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* 單個標簽页樣式 */
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 8px 16px;
        background-color: #ffffff;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        color: #495057;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    /* 標簽页悬停效果 */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e3f2fd;
        border-color: #2196f3;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(33,150,243,0.2);
    }

    /* 選中的標簽页樣式 */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-color: #667eea !important;
        box-shadow: 0 4px 12px rgba(102,126,234,0.3) !important;
        transform: translateY(-2px);
    }

    /* 標簽页內容區域 */
    .stTabs [data-baseweb="tab-panel"] {
        padding: 20px;
        background-color: #ffffff;
        border-radius: 10px;
        border: 1px solid #e1e5e9;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    /* 標簽页文字樣式 */
    .stTabs [data-baseweb="tab"] p {
        margin: 0;
        font-size: 14px;
        font-weight: 600;
    }

    /* 選中標簽页的文字樣式 */
    .stTabs [aria-selected="true"] p {
        color: white !important;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 定義分析模塊
    analysis_modules = [
        {
            'key': 'market_report',
            'title': '📈 市場技術分析',
            'icon': '📈',
            'description': '技術指標、價格趋势、支撑阻力位分析'
        },
        {
            'key': 'fundamentals_report',
            'title': '💰 基本面分析',
            'icon': '💰',
            'description': '財務數據、估值水平、盈利能力分析'
        },
        {
            'key': 'sentiment_report',
            'title': '💭 市場情绪分析',
            'icon': '💭',
            'description': '投資者情绪、社交媒體情绪指標'
        },
        {
            'key': 'news_report',
            'title': '📰 新聞事件分析',
            'icon': '📰',
            'description': '相關新聞事件、市場動態影響分析'
        },
        {
            'key': 'risk_assessment',
            'title': '⚠️ 風險評估',
            'icon': '⚠️',
            'description': '風險因素识別、風險等級評估'
        },
        {
            'key': 'investment_plan',
            'title': '📋 投資建議',
            'icon': '📋',
            'description': '具體投資策略、仓位管理建議'
        },
        {
            'key': 'investment_debate_state',
            'title': '🔬 研究团隊決策',
            'icon': '🔬',
            'description': '多头/空头研究員辩論分析，研究經理綜合決策'
        },
        {
            'key': 'trader_investment_plan',
            'title': '💼 交易团隊計劃',
            'icon': '💼',
            'description': '專業交易員制定的具體交易執行計劃'
        },
        {
            'key': 'risk_debate_state',
            'title': '⚖️ 風險管理团隊',
            'icon': '⚖️',
            'description': '激進/保守/中性分析師風險評估，投資組合經理最終決策'
        },
        {
            'key': 'final_trade_decision',
            'title': '🎯 最終交易決策',
            'icon': '🎯',
            'description': '綜合所有团隊分析後的最終投資決策'
        }
    ]
    
    # 過濾出有數據的模塊
    available_modules = []
    for module in analysis_modules:
        if module['key'] in selected_result and selected_result[module['key']]:
            # 檢查字典類型的數據是否有實际內容
            if isinstance(selected_result[module['key']], dict):
                # 對於字典，檢查是否有非空的值
                has_content = any(v for v in selected_result[module['key']].values() if v)
                if has_content:
                    available_modules.append(module)
            else:
                # 對於字符串或其他類型，直接添加
                available_modules.append(module)

    if not available_modules:
        # 如果没有預定義模塊的數據，顯示所有可用的分析數據
        st.info("📊 顯示完整分析報告數據")
        
        # 排除一些基础字段，只顯示分析相關的數據
        excluded_keys = {'analysis_id', 'timestamp', 'stock_symbol', 'analysts', 
                        'research_depth', 'status', 'summary', 'performance', 
                        'is_favorite', 'tags', 'full_data'}
        
        # 獲取所有分析相關的數據
        analysis_data = {}
        for key, value in selected_result.items():
            if key not in excluded_keys and value:
                analysis_data[key] = value
        
        # 如果有full_data字段，優先使用它
        if 'full_data' in selected_result and selected_result['full_data']:
            full_data = selected_result['full_data']
            if isinstance(full_data, dict):
                for key, value in full_data.items():
                    if key not in excluded_keys and value:
                        analysis_data[key] = value
        
        if analysis_data:
            # 創建動態標簽页顯示所有分析數據
            tab_names = []
            tab_data = []
            
            for key, value in analysis_data.items():
                # 格式化標簽页名稱
                tab_name = key.replace('_', ' ').title()
                if 'report' in key.lower():
                    tab_name = f"📊 {tab_name}"
                elif 'analysis' in key.lower():
                    tab_name = f"🔍 {tab_name}"
                elif 'decision' in key.lower():
                    tab_name = f"🎯 {tab_name}"
                elif 'plan' in key.lower():
                    tab_name = f"📋 {tab_name}"
                else:
                    tab_name = f"📄 {tab_name}"
                
                tab_names.append(tab_name)
                tab_data.append((key, value))
            
            # 創建標簽页
            tabs = st.tabs(tab_names)
            
            for i, (tab, (key, value)) in enumerate(zip(tabs, tab_data)):
                with tab:
                    st.markdown(f"## {tab_names[i]}")
                    st.markdown("---")
                    
                    # 根據數據類型顯示內容
                    if isinstance(value, str):
                        # 如果是長文本，使用markdown顯示
                        if len(value) > 100:
                            st.markdown(value)
                        else:
                            st.write(value)
                    elif isinstance(value, dict):
                        # 字典類型，遞歸顯示
                        for sub_key, sub_value in value.items():
                            if sub_value:
                                st.subheader(sub_key.replace('_', ' ').title())
                                if isinstance(sub_value, str):
                                    st.markdown(sub_value)
                                else:
                                    st.write(sub_value)
                    elif isinstance(value, list):
                        # 列表類型
                        for idx, item in enumerate(value):
                            st.subheader(f"項目 {idx + 1}")
                            if isinstance(item, str):
                                st.markdown(item)
                            else:
                                st.write(item)
                    else:
                        # 其他類型直接顯示
                        st.write(value)
        else:
            # 如果真的没有任何分析數據，顯示原始JSON
            st.warning("📊 该分析結果暂無詳細報告數據")
            with st.expander("查看原始數據"):
                st.json(selected_result)
        return

    # 只為有數據的模塊創建標簽页
    tabs = st.tabs([module['title'] for module in available_modules])

    for i, (tab, module) in enumerate(zip(tabs, available_modules)):
        with tab:
            # 在內容區域顯示圖標和描述
            st.markdown(f"## {module['icon']} {module['title']}")
            st.markdown(f"*{module['description']}*")
            st.markdown("---")

            # 格式化顯示內容
            content = selected_result[module['key']]
            if isinstance(content, str):
                st.markdown(content)
            elif isinstance(content, dict):
                # 特殊處理团隊決策報告的字典結構
                if module['key'] == 'investment_debate_state':
                    render_investment_debate_content(content)
                elif module['key'] == 'risk_debate_state':
                    render_risk_debate_content(content)
                else:
                    # 普通字典格式化顯示
                    for key, value in content.items():
                        if value:  # 只顯示非空值
                            st.subheader(key.replace('_', ' ').title())
                            if isinstance(value, str):
                                st.markdown(value)
                            else:
                                st.write(value)
            else:
                st.write(content)

def render_investment_debate_content(content):
    """渲染投資辩論內容"""
    if 'bull_analyst_report' in content and content['bull_analyst_report']:
        st.subheader("🐂 多头分析師觀點")
        st.markdown(content['bull_analyst_report'])
    
    if 'bear_analyst_report' in content and content['bear_analyst_report']:
        st.subheader("🐻 空头分析師觀點")
        st.markdown(content['bear_analyst_report'])
    
    if 'research_manager_decision' in content and content['research_manager_decision']:
        st.subheader("👨‍💼 研究經理決策")
        st.markdown(content['research_manager_decision'])

def render_risk_debate_content(content):
    """渲染風險辩論內容"""
    if 'aggressive_analyst_report' in content and content['aggressive_analyst_report']:
        st.subheader("🔥 激進分析師觀點")
        st.markdown(content['aggressive_analyst_report'])
    
    if 'conservative_analyst_report' in content and content['conservative_analyst_report']:
        st.subheader("🛡️ 保守分析師觀點")
        st.markdown(content['conservative_analyst_report'])
    
    if 'neutral_analyst_report' in content and content['neutral_analyst_report']:
        st.subheader("⚖️ 中性分析師觀點")
        st.markdown(content['neutral_analyst_report'])
    
    if 'portfolio_manager_decision' in content and content['portfolio_manager_decision']:
        st.subheader("👨‍💼 投資組合經理決策")
        st.markdown(content['portfolio_manager_decision'])

def save_analysis_result(analysis_id: str, stock_symbol: str, analysts: List[str],
                        research_depth: int, result_data: Dict, status: str = "completed"):
    """保存分析結果"""
    try:
        from web.utils.async_progress_tracker import safe_serialize

        # 創建結果條目，使用安全序列化
        result_entry = {
            'analysis_id': analysis_id,
            'timestamp': datetime.now().timestamp(),
            'stock_symbol': stock_symbol,
            'analysts': analysts,
            'research_depth': research_depth,
            'status': status,
            'summary': safe_serialize(result_data.get('summary', '')),
            'performance': safe_serialize(result_data.get('performance', {})),
            'full_data': safe_serialize(result_data)
        }

        # 1. 保存到文件系統（保持兼容性）
        results_dir = get_analysis_results_dir()
        result_file = results_dir / f"analysis_{analysis_id}.json"

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_entry, f, ensure_ascii=False, indent=2)

        # 2. 保存到MongoDB（如果可用）
        if MONGODB_AVAILABLE:
            try:
                print(f"💾 [MongoDB保存] 開始保存分析結果: {analysis_id}")
                mongodb_manager = MongoDBReportManager()

                # 使用標準的save_analysis_report方法，確保數據結構一致
                analysis_results = {
                    'stock_symbol': result_entry.get('stock_symbol', ''),
                    'analysts': result_entry.get('analysts', []),
                    'research_depth': result_entry.get('research_depth', 1),
                    'summary': result_entry.get('summary', '')
                }

                # 嘗試從文件系統讀取報告內容
                reports = {}
                try:
                    # 構建報告目錄路徑
                    from pathlib import Path
                    import os

                    # 獲取當前日期
                    current_date = datetime.now().strftime('%Y-%m-%d')

                    # 構建報告路徑
                    project_root = Path(__file__).parent.parent.parent
                    reports_dir = project_root / "data" / "analysis_results" / stock_symbol / current_date / "reports"

                    # 確保路徑在Windows上正確顯示（避免雙反斜杠）
                    reports_dir_str = os.path.normpath(str(reports_dir))
                    print(f"🔍 [MongoDB保存] 查找報告目錄: {reports_dir_str}")

                    if reports_dir.exists():
                        # 讀取所有報告文件
                        for report_file in reports_dir.glob("*.md"):
                            try:
                                with open(report_file, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    report_name = report_file.stem
                                    reports[report_name] = content
                                    print(f"✅ [MongoDB保存] 讀取報告: {report_name} ({len(content)} 字符)")
                            except Exception as e:
                                print(f"⚠️ [MongoDB保存] 讀取報告文件失败 {report_file}: {e}")

                        print(f"📊 [MongoDB保存] 共讀取 {len(reports)} 個報告文件")
                    else:
                        print(f"⚠️ [MongoDB保存] 報告目錄不存在: {reports_dir_str}")

                except Exception as e:
                    print(f"⚠️ [MongoDB保存] 讀取報告文件異常: {e}")
                    reports = {}

                # 使用標準保存方法，確保字段結構一致
                success = mongodb_manager.save_analysis_report(
                    stock_symbol=result_entry.get('stock_symbol', ''),
                    analysis_results=analysis_results,
                    reports=reports
                )

                if success:
                    print(f"✅ [MongoDB保存] 分析結果已保存到MongoDB: {analysis_id} (包含 {len(reports)} 個報告)")
                else:
                    print(f"❌ [MongoDB保存] 保存失败: {analysis_id}")

            except Exception as e:
                print(f"❌ [MongoDB保存] 保存異常: {e}")
                logger.error(f"MongoDB保存異常: {e}")

        return True

    except Exception as e:
        print(f"❌ [保存分析結果] 保存失败: {e}")
        logger.error(f"保存分析結果異常: {e}")
        return False

def show_expanded_detail(result):
    """顯示展開的詳情內容"""

    # 創建詳情容器
    with st.container():
        st.markdown("---")
        st.markdown("### 📊 詳細分析報告")

        # 檢查是否有報告數據
        if 'reports' not in result or not result['reports']:
            # 如果没有reports字段，檢查是否有其他分析數據
            if result.get('summary'):
                st.subheader("📝 分析摘要")
                st.markdown(result['summary'])

            # 檢查是否有full_data中的報告
            if 'full_data' in result and result['full_data']:
                full_data = result['full_data']
                if isinstance(full_data, dict):
                    # 顯示full_data中的分析內容
                    analysis_fields = [
                        ('market_report', '📈 市場分析'),
                        ('fundamentals_report', '💰 基本面分析'),
                        ('sentiment_report', '💭 情感分析'),
                        ('news_report', '📰 新聞分析'),
                        ('risk_assessment', '⚠️ 風險評估'),
                        ('investment_plan', '📋 投資建議'),
                        ('final_trade_decision', '🎯 最終決策')
                    ]

                    available_reports = []
                    for field_key, field_name in analysis_fields:
                        if field_key in full_data and full_data[field_key]:
                            available_reports.append((field_key, field_name, full_data[field_key]))

                    if available_reports:
                        # 創建標簽页顯示分析內容
                        tab_names = [name for _, name, _ in available_reports]
                        tabs = st.tabs(tab_names)

                        for i, (tab, (field_key, field_name, content)) in enumerate(zip(tabs, available_reports)):
                            with tab:
                                if isinstance(content, str):
                                    st.markdown(content)
                                elif isinstance(content, dict):
                                    for key, value in content.items():
                                        if value:
                                            st.subheader(key.replace('_', ' ').title())
                                            st.markdown(str(value))
                                else:
                                    st.write(content)
                    else:
                        st.info("暂無詳細分析報告")
                else:
                    st.info("暂無詳細分析報告")
            else:
                st.info("暂無詳細分析報告")
            return

        # 獲取報告數據
        reports = result['reports']

        # 為報告名稱添加中文標題和圖標
        report_display_names = {
            'final_trade_decision': '🎯 最終交易決策',
            'fundamentals_report': '💰 基本面分析',
            'technical_report': '📈 技術面分析',
            'market_sentiment_report': '💭 市場情绪分析',
            'risk_assessment_report': '⚠️ 風險評估',
            'price_target_report': '🎯 目標價格分析',
            'summary_report': '📋 分析摘要',
            'news_analysis_report': '📰 新聞分析',
            'news_report': '📰 新聞分析',
            'market_report': '📈 市場分析',
            'social_media_report': '📱 社交媒體分析',
            'bull_state': '🐂 多头觀點',
            'bear_state': '🐻 空头觀點',
            'trader_state': '💼 交易員分析',
            'invest_judge_state': '⚖️ 投資判斷',
            'research_team_state': '🔬 研究团隊觀點',
            'risk_debate_state': '⚠️ 風險管理討論',
            'research_team_decision': '🔬 研究团隊決策',
            'risk_management_decision': '🛡️ 風險管理決策',
            'investment_plan': '📋 投資計劃',
            'trader_investment_plan': '💼 交易員投資計劃',
            'investment_debate_state': '💬 投資討論狀態'
        }

        # 創建標簽页顯示不同的報告
        report_tabs = list(reports.keys())
        tab_names = []
        for report_key in report_tabs:
            display_name = report_display_names.get(report_key, f"📄 {report_key.replace('_', ' ').title()}")
            tab_names.append(display_name)

        if len(tab_names) == 1:
            # 只有一個報告，直接顯示內容（不添加額外標題，避免重複）
            report_content = reports[report_tabs[0]]
            # 如果報告內容已經包含標題，直接顯示；否則添加標題
            if not report_content.strip().startswith('#'):
                st.markdown(f"### {tab_names[0]}")
                st.markdown("---")
            st.markdown(report_content)
        else:
            # 多個報告，使用標簽页
            tabs = st.tabs(tab_names)

            for i, (tab, report_key) in enumerate(zip(tabs, report_tabs)):
                with tab:
                    st.markdown(reports[report_key])

        st.markdown("---")