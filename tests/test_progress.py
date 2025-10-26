#!/usr/bin/env python3
"""
測試進度顯示功能
"""

import time
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_progress_callback():
    """測試進度回調功能"""
    
    def mock_progress_callback(message, step=None, total_steps=None):
        """模擬進度回調"""
        print(f"[進度] {message}")
        if step is not None and total_steps is not None:
            percentage = (step / total_steps) * 100
            print(f"  步骤: {step}/{total_steps} ({percentage:.1f}%)")
        print()
    
    # 模擬分析過程
    steps = [
        "開始股票分析...",
        "檢查環境變量配置...",
        "環境變量驗證通過",
        "配置分析參數...",
        "創建必要的目錄...",
        "初始化分析引擎...",
        "開始分析 AAPL 股票，這可能需要几分鐘時間...",
        "分析完成，正在整理結果...",
        "✅ 分析成功完成！"
    ]
    
    print("🧪 測試進度回調功能")
    print("=" * 50)
    
    for i, step in enumerate(steps):
        mock_progress_callback(step, i, len(steps))
        time.sleep(0.5)  # 模擬處理時間
    
    print("✅ 進度回調測試完成！")

def test_progress_tracker():
    """測試進度跟蹤器"""
    try:
        from web.utils.progress_tracker import AnalysisProgressTracker
        
        print("🧪 測試進度跟蹤器")
        print("=" * 50)
        
        def mock_callback(message, current_step, total_steps, progress, elapsed_time):
            print(f"[跟蹤器] {message}")
            print(f"  步骤: {current_step + 1}/{total_steps}")
            print(f"  進度: {progress:.1%}")
            print(f"  用時: {elapsed_time:.1f}秒")
            print()
        
        tracker = AnalysisProgressTracker(callback=mock_callback)
        
        # 模擬分析步骤
        steps = [
            "開始股票分析...",
            "檢查環境變量配置...",
            "配置分析參數...",
            "創建必要的目錄...",
            "初始化分析引擎...",
            "獲取股票數據...",
            "進行技術分析...",
            "分析完成，正在整理結果...",
            "✅ 分析成功完成！"
        ]
        
        for step in steps:
            tracker.update(step)
            time.sleep(0.3)
        
        print("✅ 進度跟蹤器測試完成！")
        return True
        
    except Exception as e:
        print(f"❌ 進度跟蹤器測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 進度顯示功能測試")
    print("=" * 60)
    
    # 測試基本進度回調
    test_progress_callback()
    print()
    
    # 測試進度跟蹤器
    test_progress_tracker()
    
    print("\n🎉 所有測試完成！")

if __name__ == "__main__":
    main()
