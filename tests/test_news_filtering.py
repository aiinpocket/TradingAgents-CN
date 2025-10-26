"""
測試新聞過濾功能
驗證基於規則的過濾器和增强過濾器的效果
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import time
from datetime import datetime

def test_basic_news_filter():
    """測試基础新聞過濾器"""
    print("=== 測試基础新聞過濾器 ===")
    
    try:
        from tradingagents.utils.news_filter import create_news_filter
        
        # 創建過濾器
        filter = create_news_filter('600036')
        print(f"✅ 成功創建招商銀行(600036)新聞過濾器")
        
        # 模擬新聞數據
        test_news = pd.DataFrame([
            {
                '新聞標題': '招商銀行發布2024年第三季度業绩報告',
                '新聞內容': '招商銀行今日發布第三季度財報，净利润同比增長8%，資產质量持续改善，不良贷款率進一步下降...'
            },
            {
                '新聞標題': '上證180ETF指數基金（530280）自帶杠铃策略',
                '新聞內容': '數據顯示，上證180指數前十大權重股分別為贵州茅台、招商銀行600036、五粮液等，该ETF基金採用被動投資策略...'
            },
            {
                '新聞標題': '銀行ETF指數(512730)多只成分股上涨',
                '新聞內容': '銀行板塊今日表現强势，招商銀行、工商銀行、建設銀行等多只成分股上涨，銀行ETF基金受益明顯...'
            },
            {
                '新聞標題': '招商銀行与某科技公司簽署战略合作協议',
                '新聞內容': '招商銀行宣布与知名科技公司達成战略合作，将在數字化轉型、金融科技創新等方面深度合作，推動銀行業務升級...'
            },
            {
                '新聞標題': '無標題',
                '新聞內容': '指數基金跟蹤上證180指數，该指數包含180只大盘蓝筹股，權重股包括招商銀行等金融股...'
            }
        ])
        
        print(f"📊 測試新聞數量: {len(test_news)}條")
        
        # 執行過濾
        start_time = time.time()
        filtered_news = filter.filter_news(test_news, min_score=30)
        filter_time = time.time() - start_time
        
        print(f"⏱️ 過濾耗時: {filter_time:.3f}秒")
        print(f"📈 過濾結果: {len(test_news)}條 -> {len(filtered_news)}條")
        
        if not filtered_news.empty:
            print("\n🎯 過濾後的新聞:")
            for idx, (_, row) in enumerate(filtered_news.iterrows(), 1):
                print(f"{idx}. {row['新聞標題']} (評分: {row['relevance_score']:.1f})")
        
        # 獲取過濾統計
        stats = filter.get_filter_statistics(test_news, filtered_news)
        print(f"\n📊 過濾統計:")
        print(f"  - 過濾率: {stats['filter_rate']:.1f}%")
        print(f"  - 平均評分: {stats['avg_score']:.1f}")
        print(f"  - 最高評分: {stats['max_score']:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ 基础過濾器測試失败: {e}")
        return False


def test_enhanced_news_filter():
    """測試增强新聞過濾器"""
    print("\n=== 測試增强新聞過濾器 ===")
    
    try:
        from tradingagents.utils.enhanced_news_filter import create_enhanced_news_filter
        
        # 創建增强過濾器（不使用外部模型依賴）
        enhanced_filter = create_enhanced_news_filter(
            '600036', 
            use_semantic=False,  # 暂時不使用語義模型
            use_local_model=False  # 暂時不使用本地模型
        )
        print(f"✅ 成功創建增强新聞過濾器")
        
        # 使用相同的測試數據
        test_news = pd.DataFrame([
            {
                '新聞標題': '招商銀行發布2024年第三季度業绩報告',
                '新聞內容': '招商銀行今日發布第三季度財報，净利润同比增長8%，資產质量持续改善，不良贷款率進一步下降...'
            },
            {
                '新聞標題': '上證180ETF指數基金（530280）自帶杠铃策略',
                '新聞內容': '數據顯示，上證180指數前十大權重股分別為贵州茅台、招商銀行600036、五粮液等，该ETF基金採用被動投資策略...'
            },
            {
                '新聞標題': '招商銀行股东大會通過分红方案',
                '新聞內容': '招商銀行股东大會審议通過2024年度利润分配方案，每10股派發現金红利12元，分红率達到30%...'
            },
            {
                '新聞標題': '招商銀行信用卡業務創新發展',
                '新聞內容': '招商銀行信用卡中心推出多項創新產品，包括數字化信用卡、消費分期等，用戶體驗顯著提升...'
            }
        ])
        
        print(f"📊 測試新聞數量: {len(test_news)}條")
        
        # 執行增强過濾
        start_time = time.time()
        enhanced_filtered = enhanced_filter.filter_news_enhanced(test_news, min_score=40)
        filter_time = time.time() - start_time
        
        print(f"⏱️ 增强過濾耗時: {filter_time:.3f}秒")
        print(f"📈 增强過濾結果: {len(test_news)}條 -> {len(enhanced_filtered)}條")
        
        if not enhanced_filtered.empty:
            print("\n🎯 增强過濾後的新聞:")
            for idx, (_, row) in enumerate(enhanced_filtered.iterrows(), 1):
                print(f"{idx}. {row['新聞標題']}")
                print(f"   综合評分: {row['final_score']:.1f} (規則:{row['rule_score']:.1f}, 語義:{row['semantic_score']:.1f}, 分類:{row['classification_score']:.1f})")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强過濾器測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_real_news_filtering():
    """測試真實新聞數據過濾"""
    print("\n=== 測試真實新聞數據過濾 ===")
    
    try:
        from tradingagents.dataflows.akshare_utils import get_stock_news_em
        from tradingagents.utils.news_filter import create_news_filter
        
        print("📡 正在獲取招商銀行真實新聞數據...")
        
        # 獲取真實新聞數據
        start_time = time.time()
        real_news = get_stock_news_em('600036')
        fetch_time = time.time() - start_time
        
        if real_news.empty:
            print("❌ 未獲取到真實新聞數據")
            return False
        
        print(f"✅ 成功獲取真實新聞: {len(real_news)}條，耗時: {fetch_time:.2f}秒")
        
        # 顯示前3條新聞標題
        print("\n📰 原始新聞標題示例:")
        for idx, (_, row) in enumerate(real_news.head(3).iterrows(), 1):
            title = row.get('新聞標題', '無標題')
            print(f"{idx}. {title}")
        
        # 創建過濾器並過濾
        filter = create_news_filter('600036')
        
        start_time = time.time()
        filtered_real_news = filter.filter_news(real_news, min_score=30)
        filter_time = time.time() - start_time
        
        print(f"\n🔍 過濾結果:")
        print(f"  - 原始新聞: {len(real_news)}條")
        print(f"  - 過濾後新聞: {len(filtered_real_news)}條")
        print(f"  - 過濾率: {(len(real_news) - len(filtered_real_news)) / len(real_news) * 100:.1f}%")
        print(f"  - 過濾耗時: {filter_time:.3f}秒")
        
        if not filtered_real_news.empty:
            avg_score = filtered_real_news['relevance_score'].mean()
            max_score = filtered_real_news['relevance_score'].max()
            print(f"  - 平均評分: {avg_score:.1f}")
            print(f"  - 最高評分: {max_score:.1f}")
            
            print("\n🎯 過濾後高质量新聞標題:")
            for idx, (_, row) in enumerate(filtered_real_news.head(5).iterrows(), 1):
                title = row.get('新聞標題', '無標題')
                score = row.get('relevance_score', 0)
                print(f"{idx}. {title} (評分: {score:.1f})")
        
        return True
        
    except Exception as e:
        print(f"❌ 真實新聞過濾測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_news_filter_integration():
    """測試新聞過濾集成功能"""
    print("\n=== 測試新聞過濾集成功能 ===")
    
    try:
        from tradingagents.utils.news_filter_integration import apply_news_filtering_patches
        
        print("🔧 正在應用新聞過濾補丁...")
        enhanced_function = apply_news_filtering_patches()
        
        print("✅ 新聞過濾補丁應用成功")
        
        # 測試增强版函數
        print("🧪 測試增强版實時新聞函數...")
        
        test_result = enhanced_function(
            ticker="600036",
            curr_date=datetime.now().strftime("%Y-%m-%d"),
            enable_filter=True,
            min_score=30
        )
        
        print(f"📊 增强版函數返回結果長度: {len(test_result)} 字符")
        
        if "過濾新聞報告" in test_result:
            print("✅ 檢測到過濾功能已生效")
        else:
            print("ℹ️ 使用了原始新聞報告")
        
        return True
        
    except Exception as e:
        print(f"❌ 新聞過濾集成測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主測試函數"""
    print("🚀 開始新聞過濾功能測試")
    print("=" * 50)
    
    test_results = []
    
    # 1. 測試基础過濾器
    test_results.append(("基础新聞過濾器", test_basic_news_filter()))
    
    # 2. 測試增强過濾器
    test_results.append(("增强新聞過濾器", test_enhanced_news_filter()))
    
    # 3. 測試真實新聞過濾
    test_results.append(("真實新聞數據過濾", test_real_news_filtering()))
    
    # 4. 測試集成功能
    test_results.append(("新聞過濾集成功能", test_news_filter_integration()))
    
    # 輸出測試总結
    print("\n" + "=" * 50)
    print("📋 測試結果总結:")
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"  - {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 总體結果: {passed}/{len(test_results)} 項測試通過")
    
    if passed == len(test_results):
        print("🎉 所有測試通過！新聞過濾功能工作正常")
    else:
        print("⚠️ 部分測試失败，請檢查相關功能")


if __name__ == "__main__":
    main()