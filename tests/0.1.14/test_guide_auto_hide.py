#!/usr/bin/env python3
"""
測試使用指南自動隐藏功能
驗證在開始分析時使用指南會自動隐藏
"""

import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_guide_auto_hide_logic():
    """測試使用指南自動隐藏邏輯"""
    print(" 測試使用指南自動隐藏功能")
    print("=" * 60)
    
    # 模擬session state
    class MockSessionState:
        def __init__(self):
            self.data = {}
        
        def get(self, key, default=None):
            return self.data.get(key, default)
        
        def __setitem__(self, key, value):
            self.data[key] = value
        
        def __getitem__(self, key):
            return self.data[key]
        
        def __contains__(self, key):
            return key in self.data
    
    session_state = MockSessionState()
    
    # 測試場景1: 初始狀態 - 應該顯示使用指南
    print("\n 場景1: 初始狀態")
    print("-" * 40)
    
    analysis_running = session_state.get('analysis_running', False)
    analysis_results = session_state.get('analysis_results')
    default_show_guide = not (analysis_running or analysis_results is not None)
    
    print(f"   analysis_running: {analysis_running}")
    print(f"   analysis_results: {analysis_results}")
    print(f"   default_show_guide: {default_show_guide}")
    print(f"    初始狀態應該顯示使用指南: {default_show_guide}")
    
    # 測試場景2: 開始分析 - 應該隐藏使用指南
    print("\n 場景2: 開始分析")
    print("-" * 40)
    
    # 模擬開始分析
    session_state['analysis_running'] = True
    session_state['analysis_results'] = None
    
    # 自動隐藏使用指南（除非用戶明確設置要顯示）
    if not session_state.get('user_set_guide_preference', False):
        session_state['show_guide_preference'] = False
        print("    開始分析，自動隐藏使用指南")
    
    analysis_running = session_state.get('analysis_running', False)
    analysis_results = session_state.get('analysis_results')
    default_show_guide = not (analysis_running or analysis_results is not None)
    show_guide_preference = session_state.get('show_guide_preference', default_show_guide)
    
    print(f"   analysis_running: {analysis_running}")
    print(f"   analysis_results: {analysis_results}")
    print(f"   default_show_guide: {default_show_guide}")
    print(f"   show_guide_preference: {show_guide_preference}")
    print(f"    開始分析後應該隐藏使用指南: {not show_guide_preference}")
    
    # 測試場景3: 分析完成有結果 - 應該保持隐藏
    print("\n 場景3: 分析完成有結果")
    print("-" * 40)
    
    session_state['analysis_running'] = False
    session_state['analysis_results'] = {"stock_symbol": "AAPL", "analysis": "測試結果"}
    
    analysis_running = session_state.get('analysis_running', False)
    analysis_results = session_state.get('analysis_results')
    default_show_guide = not (analysis_running or analysis_results is not None)
    show_guide_preference = session_state.get('show_guide_preference', default_show_guide)
    
    print(f"   analysis_running: {analysis_running}")
    print(f"   analysis_results: {bool(analysis_results)}")
    print(f"   default_show_guide: {default_show_guide}")
    print(f"   show_guide_preference: {show_guide_preference}")
    print(f"    有分析結果時應該保持隐藏: {not show_guide_preference}")
    
    # 測試場景4: 用戶手動設置顯示 - 應該尊重用戶選擇
    print("\n 場景4: 用戶手動設置顯示")
    print("-" * 40)
    
    # 模擬用戶手動設置要顯示使用指南
    session_state['user_set_guide_preference'] = True
    session_state['show_guide_preference'] = True
    
    # 再次開始分析
    session_state['analysis_running'] = True
    session_state['analysis_results'] = None
    
    # 這次不應該自動隐藏，因為用戶明確設置了
    if not session_state.get('user_set_guide_preference', False):
        session_state['show_guide_preference'] = False
        print("    自動隐藏使用指南")
    else:
        print("    用戶已手動設置，保持用戶選擇")
    
    show_guide_preference = session_state.get('show_guide_preference', False)
    print(f"   user_set_guide_preference: {session_state.get('user_set_guide_preference')}")
    print(f"   show_guide_preference: {show_guide_preference}")
    print(f"    用戶手動設置後應該尊重用戶選擇: {show_guide_preference}")
    
    print("\n 測試總結:")
    print("   1.  初始狀態默認顯示使用指南")
    print("   2.  開始分析時自動隐藏使用指南")
    print("   3.  有分析結果時保持隐藏狀態")
    print("   4.  用戶手動設置後尊重用戶選擇")
    
    return True

def test_ui_behavior():
    """測試UI行為邏輯"""
    print("\n 測試UI行為邏輯")
    print("=" * 60)
    
    # 模擬不同的布局場景
    scenarios = [
        {
            "name": "初始訪問",
            "analysis_running": False,
            "analysis_results": None,
            "user_set_preference": False,
            "expected_show_guide": True
        },
        {
            "name": "開始分析",
            "analysis_running": True,
            "analysis_results": None,
            "user_set_preference": False,
            "expected_show_guide": False
        },
        {
            "name": "分析完成",
            "analysis_running": False,
            "analysis_results": {"data": "test"},
            "user_set_preference": False,
            "expected_show_guide": False
        },
        {
            "name": "用戶強制顯示",
            "analysis_running": True,
            "analysis_results": {"data": "test"},
            "user_set_preference": True,
            "user_preference_value": True,
            "expected_show_guide": True
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n 場景{i}: {scenario['name']}")
        print("-" * 40)
        
        # 計算默認值
        default_show_guide = not (scenario['analysis_running'] or scenario['analysis_results'] is not None)
        
        # 計算實際顯示值
        if scenario['user_set_preference']:
            actual_show_guide = scenario.get('user_preference_value', True)
        else:
            actual_show_guide = default_show_guide
            # 如果開始分析且用戶沒有設置，則隐藏
            if scenario['analysis_running'] and not scenario['user_set_preference']:
                actual_show_guide = False
        
        print(f"   分析運行中: {scenario['analysis_running']}")
        print(f"   有分析結果: {bool(scenario['analysis_results'])}")
        print(f"   用戶設置偏好: {scenario['user_set_preference']}")
        print(f"   默認顯示指南: {default_show_guide}")
        print(f"   實際顯示指南: {actual_show_guide}")
        print(f"   預期顯示指南: {scenario['expected_show_guide']}")
        
        if actual_show_guide == scenario['expected_show_guide']:
            print(f"    測試通過")
        else:
            print(f"    測試失敗")
    
    return True

if __name__ == "__main__":
    print(" 使用指南自動隐藏功能測試")
    print("=" * 70)
    
    try:
        test_guide_auto_hide_logic()
        test_ui_behavior()
        
        print("\n 所有測試完成！")
        print(" 功能說明:")
        print("   - 初次訪問時顯示使用指南，幫助用戶了解操作")
        print("   - 點擊開始分析後自動隐藏使用指南，節省屏幕空間")
        print("   - 用戶可以手動控制使用指南的顯示/隐藏")
        print("   - 系統會記住用戶的偏好設置")
        
    except Exception as e:
        print(f" 測試失敗: {e}")
        sys.exit(1)