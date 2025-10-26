#!/usr/bin/env python3
"""
簡單的異步進度跟蹤測試
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_basic_functionality():
    """測試基本功能"""
    print("🧪 測試異步進度跟蹤基本功能...")
    
    try:
        from web.utils.async_progress_tracker import AsyncProgressTracker, get_progress_by_id
        print("✅ 導入成功")
        
        # 創建跟蹤器
        analysis_id = "test_simple_123"
        tracker = AsyncProgressTracker(
            analysis_id=analysis_id,
            analysts=['market', 'fundamentals'],
            research_depth=2,
            llm_provider='dashscope'
        )
        print(f"✅ 創建跟蹤器成功: {analysis_id}")
        
        # 更新進度
        tracker.update_progress("🚀 開始股票分析...")
        print("✅ 更新進度成功")
        
        # 獲取進度
        progress = get_progress_by_id(analysis_id)
        if progress:
            print(f"✅ 獲取進度成功: {progress['progress_percentage']:.1f}%")
            print(f"   當前步骤: {progress['current_step_name']}")
            print(f"   最後消息: {progress['last_message']}")
        else:
            print("❌ 獲取進度失败")
        
        # 模擬几個步骤
        test_messages = [
            "[進度] 🔍 驗證股票代碼並預獲取數據...",
            "[進度] 檢查環境變量配置...",
            "📊 [模塊開始] market_analyst - 股票: 000858",
            "📊 [模塊完成] market_analyst - ✅ 成功 - 股票: 000858, 耗時: 41.73s",
            "✅ 分析完成"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n--- 步骤 {i+2} ---")
            tracker.update_progress(message)
            
            progress = get_progress_by_id(analysis_id)
            if progress:
                print(f"📊 步骤 {progress['current_step'] + 1}/{progress['total_steps']} ({progress['progress_percentage']:.1f}%)")
                print(f"   {progress['current_step_name']}: {message[:50]}...")
            
            time.sleep(0.5)
        
        # 最终狀態
        final_progress = get_progress_by_id(analysis_id)
        if final_progress:
            print(f"\n🎯 最终狀態:")
            print(f"   狀態: {final_progress['status']}")
            print(f"   進度: {final_progress['progress_percentage']:.1f}%")
            print(f"   总耗時: {final_progress['elapsed_time']:.1f}秒")
        
        print("\n✅ 測試完成")
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_functionality()
