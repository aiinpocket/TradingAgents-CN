#!/usr/bin/env python3
"""
測試智能進度跟蹤器
"""

import sys
import os
import time

# 添加項目根目錄到路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'web'))

from web.utils.progress_tracker import SmartAnalysisProgressTracker

def test_progress_tracker():
    """測試智能進度跟蹤器"""
    print("🧪 測試智能進度跟蹤器")
    print("=" * 50)
    
    # 測試不同配置的進度跟蹤器
    test_configs = [
        {
            "name": "快速分析 - 2個分析師",
            "analysts": ["market", "fundamentals"],
            "research_depth": 1,
            "llm_provider": "dashscope"
        },
        {
            "name": "標準分析 - 3個分析師", 
            "analysts": ["market", "fundamentals", "technical"],
            "research_depth": 3,
            "llm_provider": "deepseek"
        },
        {
            "name": "深度分析 - 5個分析師",
            "analysts": ["market", "fundamentals", "technical", "sentiment", "risk"],
            "research_depth": 3,
            "llm_provider": "google"
        }
    ]
    
    for config in test_configs:
        print(f"\n📊 {config['name']}")
        print("-" * 30)
        
        tracker = SmartAnalysisProgressTracker(
            config["analysts"],
            config["research_depth"], 
            config["llm_provider"]
        )
        
        print(f"分析師: {config['analysts']}")
        print(f"研究深度: {config['research_depth']}")
        print(f"LLM提供商: {config['llm_provider']}")
        print(f"預估总時長: {tracker.format_time(tracker.estimated_duration)}")
        print(f"总步骤數: {len(tracker.analysis_steps)}")
        
        print("\n步骤詳情:")
        for i, step in enumerate(tracker.analysis_steps):
            print(f"  {i+1}. {step['name']} - {step['description']} (權重: {step['weight']:.2f})")
        
        print("\n模擬進度更新:")

        # 根據配置生成對應的測試消息
        test_messages = [
            "🔍 驗證股票代碼並預獲取數據...",
            "檢查環境變量配置...",
            "💰 預估分析成本: ¥0.0200",
            "配置分析參數...",
            "🔧 初始化分析引擎...",
        ]

        # 為每個分析師添加消息
        for analyst in config["analysts"]:
            analyst_name = tracker._get_analyst_display_name(analyst)
            test_messages.append(f"📊 {analyst_name}正在分析...")

        test_messages.extend([
            "📋 分析完成，正在整理結果...",
            "✅ 分析成功完成！"
        ])

        for msg in test_messages:
            tracker.update(msg)
            progress = tracker.get_progress_percentage()
            elapsed = tracker.get_elapsed_time()
            remaining = tracker._estimate_remaining_time(progress/100, elapsed)

            print(f"    {msg}")
            print(f"      進度: {progress:.1f}% | 已用: {tracker.format_time(elapsed)} | 剩余: {tracker.format_time(remaining)}")

            time.sleep(0.1)  # 模擬時間流逝

def test_time_estimation():
    """測試時間預估準確性"""
    print("\n\n⏱️ 測試時間預估準確性")
    print("=" * 50)
    
    # 不同配置的預估時間
    configs = [
        (["market"], 1, "dashscope"),
        (["market", "fundamentals"], 1, "dashscope"),
        (["market", "fundamentals"], 2, "dashscope"),
        (["market", "fundamentals"], 3, "dashscope"),
        (["market", "fundamentals", "technical"], 3, "deepseek"),
        (["market", "fundamentals", "technical", "sentiment", "risk"], 3, "google"),
    ]
    
    print("配置 | 分析師數 | 深度 | 提供商 | 預估時間")
    print("-" * 60)
    
    for i, (analysts, depth, provider) in enumerate(configs, 1):
        tracker = SmartAnalysisProgressTracker(analysts, depth, provider)
        estimated = tracker.estimated_duration
        print(f"{i:2d}   | {len(analysts):6d}   | {depth:2d}   | {provider:8s} | {tracker.format_time(estimated)}")

if __name__ == "__main__":
    test_progress_tracker()
    test_time_estimation()
    print("\n✅ 測試完成！")
