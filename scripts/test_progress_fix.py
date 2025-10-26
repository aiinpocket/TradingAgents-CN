#!/usr/bin/env python3
"""
測試修複後的進度跟蹤功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.utils.progress_tracker import SmartAnalysisProgressTracker

def test_progress_tracker():
    """測試進度跟蹤器"""
    print("🧪 測試進度跟蹤器...")
    
    # 創建跟蹤器
    tracker = SmartAnalysisProgressTracker(
        analysts=['market', 'fundamentals'],
        research_depth=2,
        llm_provider='dashscope'
    )
    
    print(f"📊 初始狀態: 步骤 {tracker.current_step + 1}/{len(tracker.analysis_steps)}")
    print(f"⏱️ 預估总時長: {tracker.format_time(tracker.estimated_duration)}")
    
    # 模擬分析過程 - 包含完整的步骤消息
    test_messages = [
        "🚀 開始股票分析...",                                    # 步骤1: 數據驗證
        "[進度] 🔍 驗證股票代碼並預獲取數據...",                    # 步骤1: 數據驗證
        "[進度] ✅ 數據準备完成: 五粮液 (A股)",                    # 步骤1完成
        "[進度] 檢查環境變量配置...",                             # 步骤2: 環境準备
        "[進度] 環境變量驗證通過",                               # 步骤2完成
        "[進度] 💰 預估分析成本: ¥0.0200",                      # 步骤3: 成本預估
        "[進度] 配置分析參數...",                               # 步骤4: 參數配置
        "[進度] 📁 創建必要的目錄...",                           # 步骤4繼续
        "[進度] 🔧 初始化分析引擎...",                           # 步骤5: 引擎初始化
        "[進度] 📊 開始分析 000858 股票，這可能需要几分鐘時間...",    # 步骤5完成
        "📊 [模塊開始] market_analyst - 股票: 000858",          # 步骤6: 市場分析師
        "📊 [市場分析師] 工具調用: ['get_stock_market_data_unified']",
        "📊 [模塊完成] market_analyst - ✅ 成功 - 股票: 000858, 耗時: 41.73s",
        "📊 [模塊開始] fundamentals_analyst - 股票: 000858",    # 步骤7: 基本面分析師
        "📊 [基本面分析師] 工具調用: ['get_stock_fundamentals_unified']",
        "📊 [模塊完成] fundamentals_analyst - ✅ 成功 - 股票: 000858, 耗時: 35.21s",
        "📊 [模塊開始] graph_signal_processing - 股票: 000858", # 步骤8: 結果整理
        "📊 [模塊完成] graph_signal_processing - ✅ 成功 - 股票: 000858, 耗時: 2.20s",
        "✅ 分析完成"                                          # 最终完成
    ]
    
    for i, message in enumerate(test_messages):
        print(f"\n--- 消息 {i+1} ---")
        print(f"📝 消息: {message}")
        
        tracker.update(message)
        
        step_info = tracker.get_current_step_info()
        progress = tracker.get_progress_percentage()
        elapsed = tracker.get_elapsed_time()
        
        print(f"📊 當前步骤: {tracker.current_step + 1}/{len(tracker.analysis_steps)} - {step_info['name']}")
        print(f"📈 進度: {progress:.1f}%")
        print(f"⏱️ 已用時間: {tracker.format_time(elapsed)}")
        
        # 模擬時間間隔
        import time
        time.sleep(0.5)

if __name__ == "__main__":
    test_progress_tracker()
