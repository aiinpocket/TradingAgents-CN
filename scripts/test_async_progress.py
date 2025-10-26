#!/usr/bin/env python3
"""
測試異步進度跟蹤功能
"""

import sys
import os
import time
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.utils.async_progress_tracker import AsyncProgressTracker, get_progress_by_id

def simulate_analysis(tracker: AsyncProgressTracker):
    """模擬分析過程"""
    print("🚀 開始模擬分析...")
    
    # 模擬分析過程 - 包含完整的步骤消息
    test_messages = [
        ("🚀 開始股票分析...", 1),                                    # 步骤1: 數據驗證
        ("[進度] 🔍 驗證股票代碼並預獲取數據...", 2),                    # 步骤1: 數據驗證
        ("[進度] ✅ 數據準备完成: 五粮液 (A股)", 1),                    # 步骤1完成
        ("[進度] 檢查環境變量配置...", 2),                             # 步骤2: 環境準备
        ("[進度] 環境變量驗證通過", 1),                               # 步骤2完成
        ("[進度] 💰 預估分析成本: ¥0.0200", 2),                      # 步骤3: 成本預估
        ("[進度] 配置分析參數...", 1),                               # 步骤4: 參數配置
        ("[進度] 📁 創建必要的目錄...", 1),                           # 步骤4繼续
        ("[進度] 🔧 初始化分析引擎...", 2),                           # 步骤5: 引擎初始化
        ("[進度] 📊 開始分析 000858 股票，這可能需要几分鐘時間...", 1),    # 步骤5完成
        ("📊 [模塊開始] market_analyst - 股票: 000858", 3),          # 步骤6: 市場分析師
        ("📊 [市場分析師] 工具調用: ['get_stock_market_data_unified']", 15),
        ("📊 [模塊完成] market_analyst - ✅ 成功 - 股票: 000858, 耗時: 41.73s", 2),
        ("📊 [模塊開始] fundamentals_analyst - 股票: 000858", 3),    # 步骤7: 基本面分析師
        ("📊 [基本面分析師] 工具調用: ['get_stock_fundamentals_unified']", 20),
        ("📊 [模塊完成] fundamentals_analyst - ✅ 成功 - 股票: 000858, 耗時: 35.21s", 2),
        ("📊 [模塊開始] graph_signal_processing - 股票: 000858", 2), # 步骤8: 結果整理
        ("📊 [模塊完成] graph_signal_processing - ✅ 成功 - 股票: 000858, 耗時: 2.20s", 1),
        ("✅ 分析完成", 1)                                          # 最终完成
    ]
    
    for i, (message, delay) in enumerate(test_messages):
        print(f"\n--- 步骤 {i+1} ---")
        print(f"📝 消息: {message}")
        
        tracker.update_progress(message)
        
        # 模擬處理時間
        time.sleep(delay)
    
    # 標記完成
    tracker.mark_completed("🎉 分析成功完成！")
    print("\n✅ 模擬分析完成")

def monitor_progress(analysis_id: str, max_duration: int = 120):
    """監控進度"""
    print(f"📊 開始監控進度: {analysis_id}")
    start_time = time.time()
    
    while time.time() - start_time < max_duration:
        progress_data = get_progress_by_id(analysis_id)
        
        if not progress_data:
            print("❌ 無法獲取進度數據")
            break
        
        status = progress_data.get('status', 'running')
        current_step = progress_data.get('current_step', 0)
        total_steps = progress_data.get('total_steps', 8)
        progress_percentage = progress_data.get('progress_percentage', 0.0)
        step_name = progress_data.get('current_step_name', '未知')
        last_message = progress_data.get('last_message', '')
        elapsed_time = progress_data.get('elapsed_time', 0)
        remaining_time = progress_data.get('remaining_time', 0)
        
        print(f"\r📊 [{status}] 步骤 {current_step + 1}/{total_steps} ({progress_percentage:.1f}%) - {step_name} | "
              f"已用時: {elapsed_time:.1f}s, 剩余: {remaining_time:.1f}s | {last_message[:50]}...", end="")
        
        if status in ['completed', 'failed']:
            print(f"\n🎯 分析{status}: {last_message}")
            break
        
        time.sleep(1)
    
    print(f"\n📊 監控結束: {analysis_id}")

def test_async_progress():
    """測試異步進度跟蹤"""
    print("🧪 測試異步進度跟蹤...")
    
    # 創建跟蹤器
    analysis_id = "test_analysis_12345"
    tracker = AsyncProgressTracker(
        analysis_id=analysis_id,
        analysts=['market', 'fundamentals'],
        research_depth=2,
        llm_provider='dashscope'
    )
    
    print(f"📊 創建跟蹤器: {analysis_id}")
    print(f"⏱️ 預估总時長: {tracker.estimated_duration:.1f}秒")
    
    # 在後台線程運行分析模擬
    analysis_thread = threading.Thread(target=simulate_analysis, args=(tracker,))
    analysis_thread.daemon = True
    analysis_thread.start()
    
    # 在主線程監控進度
    monitor_progress(analysis_id)
    
    # 等待分析線程完成
    analysis_thread.join(timeout=10)
    
    # 最终狀態
    final_progress = get_progress_by_id(analysis_id)
    if final_progress:
        print(f"\n🎯 最终狀態:")
        print(f"   狀態: {final_progress.get('status', 'unknown')}")
        print(f"   進度: {final_progress.get('progress_percentage', 0):.1f}%")
        print(f"   总耗時: {final_progress.get('elapsed_time', 0):.1f}秒")
        print(f"   最後消息: {final_progress.get('last_message', 'N/A')}")

if __name__ == "__main__":
    test_async_progress()
