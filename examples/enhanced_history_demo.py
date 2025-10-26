#!/usr/bin/env python3
"""
增强分析歷史功能演示腳本
展示如何使用新的歷史分析功能
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import json

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def demo_load_analysis_results():
    """演示加載分析結果"""
    print("🔍 演示：加載分析結果")
    print("-" * 30)
    
    try:
        from web.components.analysis_results import load_analysis_results
        
        # 加載最近的分析結果
        results = load_analysis_results(limit=5)
        
        print(f"📊 找到 {len(results)} 個分析結果")
        
        for i, result in enumerate(results, 1):
            print(f"\n{i}. 股票: {result.get('stock_symbol', 'unknown')}")
            print(f"   時間: {datetime.fromtimestamp(result.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M')}")
            print(f"   狀態: {'✅ 完成' if result.get('status') == 'completed' else '❌ 失败'}")
            print(f"   分析師: {', '.join(result.get('analysts', []))}")
            
            # 顯示摘要（如果有）
            summary = result.get('summary', '')
            if summary:
                preview = summary[:100] + "..." if len(summary) > 100 else summary
                print(f"   摘要: {preview}")
        
        return results
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        return []


def demo_text_similarity():
    """演示文本相似度計算"""
    print("\n🔍 演示：文本相似度計算")
    print("-" * 30)
    
    try:
        from web.components.analysis_results import calculate_text_similarity
        
        # 測試文本
        texts = [
            "招商銀行基本面良好，建议买入",
            "招商銀行財務狀况優秀，推薦購买",
            "平安銀行技術指標顯示下跌趋势",
            "中國平安保險業務增長强劲"
        ]
        
        print("📝 測試文本:")
        for i, text in enumerate(texts, 1):
            print(f"   {i}. {text}")
        
        print("\n📊 相似度矩阵:")
        print("     ", end="")
        for i in range(len(texts)):
            print(f"  {i+1:>6}", end="")
        print()
        
        for i, text1 in enumerate(texts):
            print(f"  {i+1}. ", end="")
            for j, text2 in enumerate(texts):
                similarity = calculate_text_similarity(text1, text2)
                print(f"  {similarity:>6.2f}", end="")
            print()
        
        print("\n💡 解讀:")
        print("   - 1.00 表示完全相同")
        print("   - 0.50+ 表示較高相似度")
        print("   - 0.30- 表示較低相似度")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


def demo_report_content_extraction():
    """演示報告內容提取"""
    print("\n🔍 演示：報告內容提取")
    print("-" * 30)
    
    try:
        from web.components.analysis_results import get_report_content
        
        # 模擬不同來源的分析結果
        test_cases = [
            {
                'name': '文件系統數據',
                'result': {
                    'source': 'file_system',
                    'reports': {
                        'final_trade_decision': '# 最终交易決策\n\n建议买入，目標價位 50 元',
                        'fundamentals_report': '# 基本面分析\n\n公司財務狀况良好'
                    }
                }
            },
            {
                'name': '數據庫數據',
                'result': {
                    'full_data': {
                        'final_trade_decision': '建议持有，等待更好時機',
                        'market_report': '技術指標顯示震荡趋势'
                    }
                }
            },
            {
                'name': '直接數據',
                'result': {
                    'final_trade_decision': '建议卖出，風險較高',
                    'news_report': '近期负面新聞較多'
                }
            }
        ]
        
        for case in test_cases:
            print(f"\n📋 {case['name']}:")
            result = case['result']
            
            # 嘗試提取不同類型的報告
            report_types = ['final_trade_decision', 'fundamentals_report', 'market_report', 'news_report']
            
            for report_type in report_types:
                content = get_report_content(result, report_type)
                if content:
                    preview = content[:50] + "..." if len(content) > 50 else content
                    print(f"   ✅ {report_type}: {preview}")
                else:
                    print(f"   ❌ {report_type}: 無內容")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


def demo_stock_grouping():
    """演示股票分組功能"""
    print("\n🔍 演示：股票分組分析")
    print("-" * 30)
    
    try:
        from web.components.analysis_results import load_analysis_results
        
        # 加載分析結果
        results = load_analysis_results(limit=50)
        
        if not results:
            print("❌ 没有找到分析結果")
            return
        
        # 按股票代碼分組
        stock_groups = {}
        for result in results:
            stock_symbol = result.get('stock_symbol', 'unknown')
            if stock_symbol not in stock_groups:
                stock_groups[stock_symbol] = []
            stock_groups[stock_symbol].append(result)
        
        print(f"📊 共找到 {len(stock_groups)} 只股票的分析記錄")
        
        # 顯示每只股票的分析次數
        stock_counts = [(stock, len(analyses)) for stock, analyses in stock_groups.items()]
        stock_counts.sort(key=lambda x: x[1], reverse=True)
        
        print("\n📈 股票分析頻率排行:")
        for i, (stock, count) in enumerate(stock_counts[:10], 1):
            print(f"   {i:>2}. {stock}: {count} 次分析")
        
        # 找出有多次分析的股票
        multi_analysis_stocks = {k: v for k, v in stock_groups.items() if len(v) >= 2}
        
        if multi_analysis_stocks:
            print(f"\n🔄 有多次分析記錄的股票 ({len(multi_analysis_stocks)} 只):")
            for stock, analyses in multi_analysis_stocks.items():
                print(f"   📊 {stock}: {len(analyses)} 次分析")
                
                # 顯示時間範围
                timestamps = [a.get('timestamp', 0) for a in analyses]
                if timestamps:
                    earliest = datetime.fromtimestamp(min(timestamps))
                    latest = datetime.fromtimestamp(max(timestamps))
                    print(f"      ⏰ 時間範围: {earliest.strftime('%m-%d')} 到 {latest.strftime('%m-%d')}")
        else:
            print("\n💡 提示: 没有找到有多次分析記錄的股票")
            print("   建议對同一股票進行多次分析以體驗趋势對比功能")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")


def create_demo_data():
    """創建演示數據"""
    print("\n🔍 演示：創建演示數據")
    print("-" * 30)
    
    try:
        # 創建演示數據目錄
        demo_stocks = ['DEMO001', 'DEMO002']
        base_dir = project_root / "data" / "analysis_results" / "detailed"
        
        for stock in demo_stocks:
            for days_ago in [0, 1, 3, 7]:
                date_str = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                reports_dir = base_dir / stock / date_str / "reports"
                reports_dir.mkdir(parents=True, exist_ok=True)
                
                # 創建不同的報告內容
                reports = {
                    'final_trade_decision.md': f'# {stock} 交易決策 ({date_str})\n\n{"买入" if days_ago % 2 == 0 else "持有"}建议',
                    'fundamentals_report.md': f'# {stock} 基本面分析\n\n基本面評分: {85 - days_ago * 2}/100',
                    'market_report.md': f'# {stock} 技術分析\n\n技術指標顯示{"上涨" if days_ago < 3 else "震荡"}趋势'
                }
                
                for filename, content in reports.items():
                    report_file = reports_dir / filename
                    with open(report_file, 'w', encoding='utf-8') as f:
                        f.write(content)
        
        print(f"✅ 已為 {len(demo_stocks)} 只演示股票創建歷史數據")
        print("   現在可以在Web界面中體驗同股票歷史對比功能")
        
    except Exception as e:
        print(f"❌ 創建演示數據失败: {e}")


def main():
    """主演示函數"""
    print("🚀 增强分析歷史功能演示")
    print("=" * 50)
    
    demos = [
        ("加載分析結果", demo_load_analysis_results),
        ("文本相似度計算", demo_text_similarity),
        ("報告內容提取", demo_report_content_extraction),
        ("股票分組分析", demo_stock_grouping),
        ("創建演示數據", create_demo_data)
    ]
    
    for demo_name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"❌ {demo_name} 演示失败: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print("\n💡 下一步:")
    print("   1. 啟動Web應用: python start_web.py")
    print("   2. 訪問 '📈 分析結果' 页面")
    print("   3. 體驗新的對比和統計功能")


if __name__ == "__main__":
    main()
