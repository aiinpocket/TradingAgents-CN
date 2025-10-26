"""
新聞過濾集成模塊
将新聞過濾器集成到現有的新聞獲取流程中
"""

import pandas as pd
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

def integrate_news_filtering(original_get_stock_news_em):
    """
    裝饰器：為get_stock_news_em函數添加新聞過濾功能
    
    Args:
        original_get_stock_news_em: 原始的get_stock_news_em函數
        
    Returns:
        包裝後的函數，具有新聞過濾功能
    """
    def filtered_get_stock_news_em(symbol: str, enable_filter: bool = True, min_score: float = 30, 
                                  use_semantic: bool = False, use_local_model: bool = False) -> pd.DataFrame:
        """
        增强版get_stock_news_em，集成新聞過濾功能
        
        Args:
            symbol: 股票代碼
            enable_filter: 是否啟用新聞過濾
            min_score: 最低相關性評分阈值
            use_semantic: 是否使用語義相似度過濾
            use_local_model: 是否使用本地分類模型
            
        Returns:
            pd.DataFrame: 過濾後的新聞數據
        """
        logger.info(f"[新聞過濾集成] 開始獲取 {symbol} 的新聞，過濾開關: {enable_filter}")
        
        # 調用原始函數獲取新聞
        start_time = datetime.now()
        try:
            news_df = original_get_stock_news_em(symbol)
            fetch_time = (datetime.now() - start_time).total_seconds()
            
            if news_df.empty:
                logger.warning(f"[新聞過濾集成] 原始函數未獲取到 {symbol} 的新聞數據")
                return news_df
            
            logger.info(f"[新聞過濾集成] 原始新聞獲取成功: {len(news_df)}條，耗時: {fetch_time:.2f}秒")
            
            # 如果不啟用過濾，直接返回原始數據
            if not enable_filter:
                logger.info(f"[新聞過濾集成] 過濾功能已禁用，返回原始新聞數據")
                return news_df
            
            # 啟用新聞過濾
            filter_start_time = datetime.now()
            
            try:
                # 導入過濾器
                from tradingagents.utils.enhanced_news_filter import create_enhanced_news_filter
                
                # 創建過濾器
                news_filter = create_enhanced_news_filter(
                    symbol, 
                    use_semantic=use_semantic, 
                    use_local_model=use_local_model
                )
                
                # 執行過濾
                filtered_df = news_filter.filter_news_enhanced(news_df, min_score=min_score)
                
                filter_time = (datetime.now() - filter_start_time).total_seconds()
                
                # 記錄過濾統計
                original_count = len(news_df)
                filtered_count = len(filtered_df)
                filter_rate = (original_count - filtered_count) / original_count * 100 if original_count > 0 else 0
                
                logger.info(f"[新聞過濾集成] 新聞過濾完成:")
                logger.info(f"  - 原始新聞: {original_count}條")
                logger.info(f"  - 過濾後新聞: {filtered_count}條")
                logger.info(f"  - 過濾率: {filter_rate:.1f}%")
                logger.info(f"  - 過濾耗時: {filter_time:.2f}秒")
                
                if not filtered_df.empty:
                    avg_score = filtered_df['final_score'].mean()
                    max_score = filtered_df['final_score'].max()
                    logger.info(f"  - 平均評分: {avg_score:.1f}")
                    logger.info(f"  - 最高評分: {max_score:.1f}")
                
                return filtered_df
                
            except Exception as filter_error:
                logger.error(f"[新聞過濾集成] 新聞過濾失败: {filter_error}")
                logger.error(f"[新聞過濾集成] 返回原始新聞數據作為备用")
                return news_df
                
        except Exception as fetch_error:
            logger.error(f"[新聞過濾集成] 原始新聞獲取失败: {fetch_error}")
            return pd.DataFrame()  # 返回空DataFrame
    
    return filtered_get_stock_news_em


def patch_akshare_utils():
    """
    為akshare_utils模塊的get_stock_news_em函數添加過濾功能
    """
    try:
        from tradingagents.dataflows import akshare_utils
        
        # 保存原始函數
        if not hasattr(akshare_utils, '_original_get_stock_news_em'):
            akshare_utils._original_get_stock_news_em = akshare_utils.get_stock_news_em
            
            # 應用過濾裝饰器
            akshare_utils.get_stock_news_em = integrate_news_filtering(
                akshare_utils._original_get_stock_news_em
            )
            
            logger.info("[新聞過濾集成] ✅ 成功為akshare_utils.get_stock_news_em添加過濾功能")
        else:
            logger.info("[新聞過濾集成] akshare_utils.get_stock_news_em已經被增强")
            
    except Exception as e:
        logger.error(f"[新聞過濾集成] 無法增强akshare_utils.get_stock_news_em: {e}")


def create_filtered_realtime_news_function():
    """
    創建增强版的實時新聞獲取函數
    """
    def get_filtered_realtime_stock_news(ticker: str, curr_date: str, hours_back: int = 6, 
                                       enable_filter: bool = True, min_score: float = 30) -> str:
        """
        增强版實時新聞獲取函數，集成新聞過濾
        
        Args:
            ticker: 股票代碼
            curr_date: 當前日期
            hours_back: 回溯小時數
            enable_filter: 是否啟用新聞過濾
            min_score: 最低相關性評分阈值
            
        Returns:
            str: 格式化的新聞報告
        """
        logger.info(f"[增强實時新聞] 開始獲取 {ticker} 的過濾新聞")
        
        try:
            # 導入原始函數
            from tradingagents.dataflows.realtime_news_utils import get_realtime_stock_news
            
            # 調用原始函數獲取新聞
            original_report = get_realtime_stock_news(ticker, curr_date, hours_back)
            
            if not enable_filter:
                logger.info(f"[增强實時新聞] 過濾功能已禁用，返回原始報告")
                return original_report
            
            # 如果啟用過濾且是A股，嘗試重新獲取並過濾
            if any(suffix in ticker for suffix in ['.SH', '.SZ', '.SS', '.XSHE', '.XSHG']) or \
               (not '.' in ticker and ticker.isdigit()):
                
                logger.info(f"[增强實時新聞] 檢測到A股代碼，嘗試使用過濾版东方財富新聞")
                
                try:
                    from tradingagents.dataflows.akshare_utils import get_stock_news_em
                    
                    # 清理股票代碼
                    clean_ticker = ticker.replace('.SH', '').replace('.SZ', '').replace('.SS', '')\
                                    .replace('.XSHE', '').replace('.XSHG', '')
                    
                    # 先獲取原始新聞
                    original_news_df = get_stock_news_em(clean_ticker)
                     
                    if enable_filter and not original_news_df.empty:
                         # 應用新聞過濾
                         from tradingagents.utils.news_filter import create_news_filter
                         news_filter = create_news_filter(clean_ticker)
                         filtered_news_df = news_filter.filter_news(original_news_df, min_score=min_score)
                         
                         # 記錄過濾統計
                         filter_stats = news_filter.get_filter_statistics(original_news_df, filtered_news_df)
                         logger.info(f"[新聞過濾集成] 新聞過濾完成:")
                         logger.info(f"  - 原始新聞: {len(original_news_df)}條")
                         logger.info(f"  - 過濾後新聞: {len(filtered_news_df)}條")
                         logger.info(f"  - 過濾率: {filter_stats['filter_rate']:.1f}%")
                    else:
                         filtered_news_df = original_news_df
                    
                    if not filtered_news_df.empty:
                        # 構建過濾後的報告
                        news_count = len(filtered_news_df)
                        
                        report = f"# {ticker} 過濾新聞報告\n\n"
                        report += f"📅 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        report += f"📊 過濾後新聞总數: {news_count}條\n"
                        report += f"🔍 過濾阈值: {min_score}分\n\n"
                        
                        # 添加過濾統計信息
                        if 'final_score' in filtered_news_df.columns:
                            avg_score = filtered_news_df['final_score'].mean()
                            max_score = filtered_news_df['final_score'].max()
                            report += f"📈 平均相關性評分: {avg_score:.1f}分\n"
                            report += f"🏆 最高相關性評分: {max_score:.1f}分\n\n"
                        
                        # 添加新聞內容
                        for idx, (_, row) in enumerate(filtered_news_df.iterrows()):
                            report += f"### {row.get('新聞標題', '無標題')}\n"
                            report += f"📅 {row.get('發布時間', '無時間')}\n"
                            
                            if 'final_score' in row:
                                report += f"⭐ 相關性評分: {row['final_score']:.1f}分\n"
                            
                            report += f"🔗 {row.get('新聞鏈接', '無鏈接')}\n\n"
                            report += f"{row.get('新聞內容', '無內容')}\n\n"
                        
                        logger.info(f"[增强實時新聞] ✅ 成功生成過濾新聞報告，包含 {news_count} 條高质量新聞")
                        return report
                    else:
                        logger.warning(f"[增强實時新聞] 過濾後無符合條件的新聞，返回原始報告")
                        return original_report
                        
                except Exception as filter_error:
                    logger.error(f"[增强實時新聞] 新聞過濾失败: {filter_error}")
                    return original_report
            else:
                logger.info(f"[增强實時新聞] 非A股代碼，返回原始報告")
                return original_report
                
        except Exception as e:
            logger.error(f"[增强實時新聞] 增强新聞獲取失败: {e}")
            return f"❌ 新聞獲取失败: {str(e)}"
    
    return get_filtered_realtime_stock_news


# 自動應用補丁
def apply_news_filtering_patches():
    """
    自動應用新聞過濾補丁
    """
    logger.info("[新聞過濾集成] 開始應用新聞過濾補丁...")
    
    # 1. 增强akshare_utils
    patch_akshare_utils()
    
    # 2. 創建增强版實時新聞函數
    enhanced_function = create_filtered_realtime_news_function()
    
    logger.info("[新聞過濾集成] ✅ 新聞過濾補丁應用完成")
    
    return enhanced_function


if __name__ == "__main__":
    # 測試集成功能
    print("=== 測試新聞過濾集成 ===")
    
    # 應用補丁
    enhanced_news_function = apply_news_filtering_patches()
    
    # 測試增强版函數
    test_result = enhanced_news_function(
        ticker="600036",
        curr_date="2024-07-28",
        enable_filter=True,
        min_score=30
    )
    
    print(f"測試結果長度: {len(test_result)} 字符")
    print(f"測試結果預覽: {test_result[:200]}...")