"""
新聞過濾功能演示腳本
展示如何使用不同的新聞過濾方法來提高新聞质量
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from datetime import datetime

def demo_basic_filtering():
    """演示基础新聞過濾功能"""
    print("🔍 演示1: 基础新聞過濾功能")
    print("-" * 40)
    
    from tradingagents.utils.news_filter import create_news_filter
    
    # 創建招商銀行新聞過濾器
    filter = create_news_filter('600036')
    
    # 模擬混合质量的新聞數據
    mixed_news = pd.DataFrame([
        {
            '新聞標題': '招商銀行發布2024年第三季度財報',
            '新聞內容': '招商銀行今日發布第三季度財報，净利润同比增長8%，資產质量持续改善...'
        },
        {
            '新聞標題': '上證180ETF指數基金投資策略分析',
            '新聞內容': '上證180指數包含招商銀行等180只大盘蓝筹股，ETF基金採用被動投資策略...'
        },
        {
            '新聞標題': '招商銀行信用卡業務創新發展',
            '新聞內容': '招商銀行信用卡中心推出多項創新產品，數字化轉型成效顯著...'
        },
        {
            '新聞標題': '無標題',
            '新聞內容': '指數基金跟蹤上證180指數，權重股包括招商銀行等金融股...'
        }
    ])
    
    print(f"📊 原始新聞: {len(mixed_news)}條")
    
    # 執行過濾
    filtered_news = filter.filter_news(mixed_news, min_score=30)
    
    print(f"✅ 過濾後新聞: {len(filtered_news)}條")
    print(f"📈 過濾率: {(len(mixed_news) - len(filtered_news)) / len(mixed_news) * 100:.1f}%")
    
    print("\n🎯 高质量新聞:")
    for idx, (_, row) in enumerate(filtered_news.iterrows(), 1):
        print(f"{idx}. {row['新聞標題']} (評分: {row['relevance_score']:.1f})")
    
    return filtered_news


def demo_real_news_filtering():
    """演示真實新聞數據過濾"""
    print("\n🌐 演示2: 真實新聞數據過濾")
    print("-" * 40)
    
    from tradingagents.dataflows.akshare_utils import get_stock_news_em
    from tradingagents.utils.news_filter import create_news_filter
    
    # 獲取真實新聞
    print("📡 正在獲取招商銀行真實新聞...")
    real_news = get_stock_news_em('600036')
    
    if real_news.empty:
        print("❌ 未獲取到新聞數據")
        return None
    
    print(f"✅ 獲取到 {len(real_news)} 條新聞")
    
    # 顯示原始新聞质量
    print("\n📰 原始新聞標題示例:")
    for idx, (_, row) in enumerate(real_news.head(3).iterrows(), 1):
        title = row.get('新聞標題', '無標題')
        print(f"{idx}. {title}")
    
    # 創建過濾器
    filter = create_news_filter('600036')
    
    # 過濾新聞
    filtered_news = filter.filter_news(real_news, min_score=30)
    
    print(f"\n🔍 過濾結果:")
    print(f"  原始新聞: {len(real_news)}條")
    print(f"  過濾後新聞: {len(filtered_news)}條")
    print(f"  過濾率: {(len(real_news) - len(filtered_news)) / len(real_news) * 100:.1f}%")
    
    if not filtered_news.empty:
        avg_score = filtered_news['relevance_score'].mean()
        print(f"  平均相關性評分: {avg_score:.1f}")
        
        print("\n🎯 過濾後高质量新聞:")
        for idx, (_, row) in enumerate(filtered_news.head(5).iterrows(), 1):
            title = row.get('新聞標題', '無標題')
            score = row.get('relevance_score', 0)
            print(f"{idx}. {title} (評分: {score:.1f})")
    
    return filtered_news


def demo_enhanced_filtering():
    """演示增强新聞過濾功能"""
    print("\n⚡ 演示3: 增强新聞過濾功能")
    print("-" * 40)
    
    from tradingagents.utils.enhanced_news_filter import create_enhanced_news_filter
    
    # 創建增强過濾器（仅使用規則過濾，避免外部依賴）
    enhanced_filter = create_enhanced_news_filter(
        '600036',
        use_semantic=False,
        use_local_model=False
    )
    
    # 測試數據
    test_news = pd.DataFrame([
        {
            '新聞標題': '招商銀行董事會決议公告',
            '新聞內容': '招商銀行董事會審议通過重要決议，包括高管任免、業務發展战略等重要事項...'
        },
        {
            '新聞標題': '招商銀行与科技公司战略合作',
            '新聞內容': '招商銀行宣布与知名科技公司達成战略合作協议，共同推進金融科技創新...'
        },
        {
            '新聞標題': '銀行板塊ETF基金表現分析',
            '新聞內容': '銀行ETF基金今日上涨，成分股包括招商銀行、工商銀行等多只銀行股...'
        }
    ])
    
    print(f"📊 測試新聞: {len(test_news)}條")
    
    # 執行增强過濾
    enhanced_result = enhanced_filter.filter_news_enhanced(test_news, min_score=40)
    
    print(f"✅ 增强過濾結果: {len(enhanced_result)}條")
    
    if not enhanced_result.empty:
        print("\n🎯 增强過濾後的新聞:")
        for idx, (_, row) in enumerate(enhanced_result.iterrows(), 1):
            print(f"{idx}. {row['新聞標題']}")
            print(f"   综合評分: {row['final_score']:.1f}")
    
    return enhanced_result


def demo_integrated_filtering():
    """演示集成新聞過濾功能"""
    print("\n🔧 演示4: 集成新聞過濾功能")
    print("-" * 40)
    
    from tradingagents.utils.news_filter_integration import create_filtered_realtime_news_function
    
    # 創建增强版實時新聞函數
    enhanced_news_func = create_filtered_realtime_news_function()
    
    print("🧪 測試增强版實時新聞函數...")
    
    # 調用增强版函數
    result = enhanced_news_func(
        ticker="600036",
        curr_date=datetime.now().strftime("%Y-%m-%d"),
        enable_filter=True,
        min_score=30
    )
    
    print(f"📊 返回結果長度: {len(result)} 字符")
    
    # 檢查是否包含過濾信息
    if "過濾新聞報告" in result:
        print("✅ 檢測到過濾功能已生效")
        print("📈 新聞质量得到提升")
    else:
        print("ℹ️ 使用了原始新聞報告")
    
    # 顯示部分結果
    print("\n📄 報告預覽:")
    preview = result[:300] + "..." if len(result) > 300 else result
    print(preview)
    
    return result


def main():
    """主演示函數"""
    print("🚀 新聞過濾功能演示")
    print("=" * 50)
    print("本演示将展示如何使用不同的新聞過濾方法來提高新聞质量")
    print()
    
    try:
        # 演示1: 基础過濾
        demo_basic_filtering()
        
        # 演示2: 真實新聞過濾
        demo_real_news_filtering()
        
        # 演示3: 增强過濾
        demo_enhanced_filtering()
        
        # 演示4: 集成過濾
        demo_integrated_filtering()
        
        print("\n" + "=" * 50)
        print("🎉 演示完成！")
        print()
        print("💡 总結:")
        print("1. 基础過濾器：通過關键詞規則快速過濾低质量新聞")
        print("2. 真實數據過濾：有效解決东方財富新聞质量問題")
        print("3. 增强過濾器：支持多種過濾策略的综合評分")
        print("4. 集成功能：無缝集成到現有新聞獲取流程")
        print()
        print("🔧 使用建议:")
        print("- 對於A股新聞，建议使用基础過濾器（快速、有效）")
        print("- 對於重要分析，可以使用增强過濾器（更精確）")
        print("- 集成功能可以直接替換現有新聞獲取函數")
        
    except Exception as e:
        print(f"❌ 演示過程中出現錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()