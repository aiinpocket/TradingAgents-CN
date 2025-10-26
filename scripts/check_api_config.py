#!/usr/bin/env python3
"""
API配置檢查工具
檢查各種API密鑰的配置狀態和可用性
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_env_file():
    """檢查.env文件是否存在"""
    env_file = project_root / ".env"
    if env_file.exists():
        print("✅ .env文件存在")
        load_dotenv(env_file)
        return True
    else:
        print("❌ .env文件不存在")
        print("💡 請複制.env_example為.env並配置API密鑰")
        return False

def check_dashscope_config():
    """檢查DashScope配置"""
    print("\n🔍 檢查DashScope配置...")
    
    api_key = os.getenv('DASHSCOPE_API_KEY')
    if not api_key:
        print("❌ DASHSCOPE_API_KEY未配置")
        print("💡 影響: 記忆功能将被禁用，但系統可以正常運行")
        return False
    
    print(f"✅ DASHSCOPE_API_KEY已配置: {api_key[:12]}...{api_key[-4:]}")
    
    # 測試API可用性
    try:
        import dashscope
        from dashscope import TextEmbedding
        
        dashscope.api_key = api_key
        
        response = TextEmbedding.call(
            model="text-embedding-v3",
            input="測試文本"
        )
        
        if response.status_code == 200:
            print("✅ DashScope API測試成功")
            return True
        else:
            print(f"❌ DashScope API測試失败: {response.code} - {response.message}")
            return False
            
    except ImportError:
        print("⚠️ dashscope包未安裝，無法測試API")
        return False
    except Exception as e:
        print(f"❌ DashScope API測試異常: {e}")
        return False

def check_other_apis():
    """檢查其他API配置"""
    print("\n🔍 檢查其他API配置...")
    
    apis = {
        'OPENAI_API_KEY': 'OpenAI API',
        'GOOGLE_API_KEY': 'Google AI API', 
        'DEEPSEEK_API_KEY': 'DeepSeek API',
        'TUSHARE_TOKEN': 'Tushare數據源',
        'FINNHUB_API_KEY': 'FinnHub數據源'
    }
    
    configured_apis = []
    missing_apis = []
    
    for env_var, name in apis.items():
        value = os.getenv(env_var)
        if value:
            print(f"✅ {name}: 已配置")
            configured_apis.append(name)
        else:
            print(f"❌ {name}: 未配置")
            missing_apis.append(name)
    
    return configured_apis, missing_apis

def check_memory_functionality():
    """檢查記忆功能是否可用"""
    print("\n🧠 檢查記忆功能...")
    
    try:
        from tradingagents.agents.utils.memory import FinancialSituationMemory
        from tradingagents.default_config import DEFAULT_CONFIG
        
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "dashscope"
        
        memory = FinancialSituationMemory("test_memory", config)
        
        # 測試embedding
        embedding = memory.get_embedding("測試文本")
        
        if all(x == 0.0 for x in embedding):
            print("⚠️ 記忆功能已禁用（返回空向量）")
            print("💡 原因: DashScope API密鑰未配置或無效")
            return False
        else:
            print(f"✅ 記忆功能正常（向量維度: {len(embedding)}）")
            return True
            
    except Exception as e:
        print(f"❌ 記忆功能測試失败: {e}")
        return False

def provide_recommendations(dashscope_ok, configured_apis, missing_apis):
    """提供配置建议"""
    print("\n💡 配置建议:")
    print("=" * 50)
    
    if not dashscope_ok:
        print("🔴 DashScope配置問題:")
        print("   - 記忆功能将被禁用")
        print("   - 看涨/看跌研究員無法使用歷史經驗")
        print("   - 系統仍可正常進行股票分析")
        print("   - 建议配置DASHSCOPE_API_KEY以獲得完整功能")
        print()
    
    if 'Tushare數據源' not in configured_apis:
        print("🟡 Tushare未配置:")
        print("   - A股數據将使用AKShare备用源")
        print("   - 建议配置TUSHARE_TOKEN以獲得更好的數據质量")
        print()
    
    if len(configured_apis) == 0:
        print("🔴 嚴重警告:")
        print("   - 没有配置任何API密鑰")
        print("   - 系統可能無法正常工作")
        print("   - 請至少配置一個LLM API密鑰")
        print()
    
    print("📋 最小配置建议:")
    print("   1. 配置至少一個LLM API密鑰（DASHSCOPE_API_KEY推薦）")
    print("   2. 配置TUSHARE_TOKEN以獲得A股數據")
    print("   3. 其他API密鑰可選配置")
    print()
    
    print("🚀 完整配置建议:")
    print("   - DASHSCOPE_API_KEY: 阿里百炼（推薦，中文優化）")
    print("   - TUSHARE_TOKEN: A股專業數據")
    print("   - OPENAI_API_KEY: 备用LLM")
    print("   - FINNHUB_API_KEY: 美股數據")

def main():
    """主函數"""
    print("🔍 TradingAgents API配置檢查工具")
    print("=" * 60)
    
    # 檢查.env文件
    if not check_env_file():
        return
    
    # 檢查DashScope
    dashscope_ok = check_dashscope_config()
    
    # 檢查其他API
    configured_apis, missing_apis = check_other_apis()
    
    # 檢查記忆功能
    memory_ok = check_memory_functionality()
    
    # 总結
    print("\n📊 配置总結:")
    print("=" * 30)
    print(f"DashScope API: {'✅ 正常' if dashscope_ok else '❌ 異常'}")
    print(f"記忆功能: {'✅ 可用' if memory_ok else '❌ 禁用'}")
    print(f"已配置API: {len(configured_apis)}個")
    print(f"缺失API: {len(missing_apis)}個")
    
    # 提供建议
    provide_recommendations(dashscope_ok, configured_apis, missing_apis)
    
    # 系統狀態評估
    if dashscope_ok and len(configured_apis) >= 2:
        print("\n🎉 系統配置良好，可以正常使用所有功能！")
    elif len(configured_apis) >= 1:
        print("\n⚠️ 系統可以基本運行，但建议完善配置以獲得更好體驗。")
    else:
        print("\n🚨 系統配置不足，可能無法正常工作，請配置必要的API密鑰。")

if __name__ == "__main__":
    main()
