#!/usr/bin/env python3
"""
測試Web配置管理頁面
"""

import sys
from pathlib import Path

# 新增專案根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_config_page_import():
    """測試配置頁面匯入"""
    print(" 測試配置管理頁面匯入")
    print("=" * 50)
    
    try:
        from web.pages.config_management import render_config_management
        print(" 配置管理頁面匯入成功")
        return True
    except Exception as e:
        print(f" 配置管理頁面匯入失敗: {e}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

def test_config_manager_import():
    """測試配置管理器匯入"""
    print("\n 測試配置管理器匯入")
    print("=" * 50)
    
    try:
        from tradingagents.config.config_manager import config_manager, token_tracker
        print(" 配置管理器匯入成功")
        
        # 測試基本功能
        models = config_manager.load_models()
        print(f" 載入了 {len(models)} 個模型配置")
        
        pricing = config_manager.load_pricing()
        print(f" 載入了 {len(pricing)} 個定價配置")
        
        settings = config_manager.load_settings()
        print(f" 載入了 {len(settings)} 個系統設定")
        
        return True
    except Exception as e:
        print(f" 配置管理器匯入失敗: {e}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False

def test_streamlit_components():
    """測試Streamlit元件"""
    print("\n 測試Streamlit元件")
    print("=" * 50)
    
    try:
        import streamlit as st
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        
        print(" Streamlit匯入成功")
        print(" Pandas匯入成功")
        print(" Plotly匯入成功")
        
        return True
    except Exception as e:
        print(f" Streamlit元件匯入失敗: {e}")
        return False

def main():
    """主測試函式"""
    print(" Web配置管理頁面測試")
    print("=" * 60)
    
    tests = [
        ("Streamlit元件", test_streamlit_components),
        ("配置管理器", test_config_manager_import),
        ("配置頁面", test_config_page_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f" {test_name} 測試通過")
            else:
                print(f" {test_name} 測試失敗")
        except Exception as e:
            print(f" {test_name} 測試異常: {e}")
    
    print(f"\n 測試結果: {passed}/{total} 通過")
    
    if passed == total:
        print(" 所有測試通過！配置管理頁面可以正常使用")
        print("\n 使用方法:")
        print("1. 啟動Web應用: python -m streamlit run web/app.py")
        print("2. 在側邊欄選擇 ' 配置管理'")
        print("3. 配置API密鑰、模型參數和費率設定")
        print("4. 查看使用統計和成本分析")
        return True
    else:
        print(" 部分測試失敗，請檢查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
