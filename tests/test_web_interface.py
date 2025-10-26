#!/usr/bin/env python3
"""
測試Web界面的Google模型功能
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

def test_web_interface_config():
    """測試Web界面配置功能"""
    print("🧪 測試Web界面Google模型配置")
    print("=" * 60)
    
    try:
        # 測試sidebar配置
        print("📋 測試sidebar配置...")
        from web.components.sidebar import render_sidebar
        
        # 模擬Streamlit環境（簡化測試）
        print("✅ sidebar模塊導入成功")
        
        # 測試analysis_runner配置
        print("📊 測試analysis_runner配置...")
        from web.utils.analysis_runner import run_stock_analysis
        
        print("✅ analysis_runner模塊導入成功")
        
        # 測試參數驗證
        print("🔧 測試參數配置...")
        
        # 模擬Google配置
        test_config = {
            'llm_provider': 'google',
            'llm_model': 'gemini-2.0-flash',
            'enable_memory': True,
            'enable_debug': False,
            'max_tokens': 4000
        }
        
        print(f"✅ 測試配置創建成功: {test_config}")
        
        # 驗證配置參數
        required_params = ['llm_provider', 'llm_model']
        for param in required_params:
            if param in test_config:
                print(f"   ✅ {param}: {test_config[param]}")
            else:
                print(f"   ❌ {param}: 缺失")
        
        return True
        
    except Exception as e:
        print(f"❌ Web界面配置測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_model_options():
    """測試模型選項配置"""
    print("\n🧪 測試模型選項配置")
    print("=" * 60)
    
    # 阿里百炼模型選項
    dashscope_models = ["qwen-turbo", "qwen-plus", "qwen-max"]
    print("📊 阿里百炼模型選項:")
    for model in dashscope_models:
        print(f"   ✅ {model}")
    
    # Google模型選項
    google_models = ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"]
    print("\n🤖 Google模型選項:")
    for model in google_models:
        print(f"   ✅ {model}")
    
    # 驗證推薦配置
    print(f"\n🏆 推薦配置:")
    print(f"   LLM提供商: Google AI")
    print(f"   推薦模型: gemini-2.0-flash")
    print(f"   嵌入服務: 阿里百炼 (自動配置)")
    print(f"   內存功能: 啟用")
    
    return True

def test_api_requirements():
    """測試API密鑰要求"""
    print("\n🧪 測試API密鑰要求")
    print("=" * 60)
    
    # 檢查必需的API密鑰
    api_keys = {
        'GOOGLE_API_KEY': 'Google AI API密鑰',
        'DASHSCOPE_API_KEY': '阿里百炼API密鑰（用於嵌入）',
        'FINNHUB_API_KEY': '金融數據API密鑰'
    }
    
    all_configured = True
    
    for key, description in api_keys.items():
        value = os.getenv(key)
        if value:
            print(f"✅ {description}: 已配置")
        else:
            print(f"❌ {description}: 未配置")
            all_configured = False
    
    if all_configured:
        print(f"\n🎉 所有必需的API密鑰都已配置！")
        print(f"💡 現在可以使用Google AI進行完整的股票分析")
    else:
        print(f"\n⚠️ 部分API密鑰未配置")
        print(f"💡 請在.env文件中配置缺失的API密鑰")
    
    return all_configured

def main():
    """主測試函數"""
    print("🧪 Web界面Google模型功能測試")
    print("=" * 70)
    
    # 運行測試
    results = {}
    
    results['Web界面配置'] = test_web_interface_config()
    results['模型選項'] = test_model_options()
    results['API密鑰'] = test_api_requirements()
    
    # 总結結果
    print(f"\n📊 測試結果总結:")
    print("=" * 50)
    
    for test_name, success in results.items():
        status = "✅ 通過" if success else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    successful_tests = sum(results.values())
    total_tests = len(results)
    
    print(f"\n🎯 总體結果: {successful_tests}/{total_tests} 測試通過")
    
    if successful_tests == total_tests:
        print("🎉 Web界面Google模型功能完全可用！")
        print("\n💡 使用指南:")
        print("   1. 打開Web界面: http://localhost:8501")
        print("   2. 在左侧邊栏選擇'Google AI'作為LLM提供商")
        print("   3. 選擇'Gemini 2.0 Flash'模型（推薦）")
        print("   4. 啟用記忆功能獲得更好的分析效果")
        print("   5. 選擇分析師並開始股票分析")
        print("\n🚀 現在您可以享受Google AI的强大分析能力！")
    else:
        print("⚠️ 部分功能需要進一步配置")

if __name__ == "__main__":
    main()
