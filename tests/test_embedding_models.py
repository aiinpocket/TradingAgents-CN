#!/usr/bin/env python3
"""
測試不同嵌入模型的使用場景
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

def test_embedding_selection():
    """測試不同配置下的嵌入模型選擇"""
    print("🧪 測試嵌入模型選擇逻辑")
    print("=" * 60)
    
    from tradingagents.agents.utils.memory import FinancialSituationMemory
    from tradingagents.default_config import DEFAULT_CONFIG
    
    # 測試場景1: 阿里百炼
    print("📊 場景1: 阿里百炼配置")
    config1 = DEFAULT_CONFIG.copy()
    config1["llm_provider"] = "dashscope"
    config1["backend_url"] = "https://dashscope.aliyuncs.com/api/v1"
    
    try:
        memory1 = FinancialSituationMemory("test_dashscope", config1)
        print(f"✅ 嵌入模型: {memory1.embedding}")
        print(f"   LLM提供商: {memory1.llm_provider}")
        print(f"   客戶端: {type(memory1.client)}")
    except Exception as e:
        print(f"❌ 阿里百炼配置失败: {e}")
    
    print()
    
    # 測試場景2: 本地Ollama
    print("📊 場景2: 本地Ollama配置")
    config2 = DEFAULT_CONFIG.copy()
    config2["llm_provider"] = "ollama"
    config2["backend_url"] = "http://localhost:11434/v1"
    
    try:
        memory2 = FinancialSituationMemory("test_ollama", config2)
        print(f"✅ 嵌入模型: {memory2.embedding}")
        print(f"   LLM提供商: {memory2.llm_provider}")
        print(f"   客戶端: {type(memory2.client)}")
        print(f"   後端URL: {config2['backend_url']}")
    except Exception as e:
        print(f"❌ 本地Ollama配置失败: {e}")
    
    print()
    
    # 測試場景3: Google AI (問題場景)
    print("📊 場景3: Google AI配置 (問題場景)")
    config3 = DEFAULT_CONFIG.copy()
    config3["llm_provider"] = "google"
    config3["backend_url"] = "https://api.openai.com/v1"  # 默認还是OpenAI URL
    
    try:
        memory3 = FinancialSituationMemory("test_google", config3)
        print(f"⚠️ 嵌入模型: {memory3.embedding}")
        print(f"   LLM提供商: {memory3.llm_provider}")
        print(f"   客戶端: {type(memory3.client)}")
        print(f"   問題: Google AI没有專門的嵌入配置，默認使用OpenAI")
    except Exception as e:
        print(f"❌ Google AI配置失败: {e}")
    
    print()
    
    # 測試場景4: OpenAI
    print("📊 場景4: OpenAI配置")
    config4 = DEFAULT_CONFIG.copy()
    config4["llm_provider"] = "openai"
    config4["backend_url"] = "https://api.openai.com/v1"
    
    try:
        memory4 = FinancialSituationMemory("test_openai", config4)
        print(f"✅ 嵌入模型: {memory4.embedding}")
        print(f"   LLM提供商: {memory4.llm_provider}")
        print(f"   客戶端: {type(memory4.client)}")
    except Exception as e:
        print(f"❌ OpenAI配置失败: {e}")

def test_embedding_functionality():
    """測試嵌入功能是否正常工作"""
    print("\n🧪 測試嵌入功能")
    print("=" * 60)
    
    from tradingagents.agents.utils.memory import FinancialSituationMemory
    from tradingagents.default_config import DEFAULT_CONFIG
    
    # 測試阿里百炼嵌入
    dashscope_key = os.getenv('DASHSCOPE_API_KEY')
    if dashscope_key:
        print("📊 測試阿里百炼嵌入功能")
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "dashscope"
        
        try:
            memory = FinancialSituationMemory("test_embedding", config)
            embedding = memory.get_embedding("苹果公司股票分析")
            print(f"✅ 阿里百炼嵌入成功")
            print(f"   嵌入維度: {len(embedding)}")
            print(f"   嵌入預覽: {embedding[:5]}...")
        except Exception as e:
            print(f"❌ 阿里百炼嵌入失败: {e}")
    else:
        print("⚠️ 阿里百炼API密鑰未配置，跳過測試")
    
    print()
    
    # 測試Google AI嵌入（會失败）
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key:
        print("📊 測試Google AI嵌入功能（預期失败）")
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "google"
        
        try:
            memory = FinancialSituationMemory("test_google_embedding", config)
            embedding = memory.get_embedding("Apple stock analysis")
            print(f"✅ Google AI嵌入成功（意外）")
            print(f"   嵌入維度: {len(embedding)}")
        except Exception as e:
            print(f"❌ Google AI嵌入失败（預期）: {e}")
            print("   原因: Google AI没有專門的嵌入配置，嘗試使用OpenAI API")
    else:
        print("⚠️ Google API密鑰未配置，跳過測試")

def show_solutions():
    """顯示解決方案"""
    print("\n💡 解決方案")
    print("=" * 60)
    
    print("🔧 方案1: 為Google AI添加專門的嵌入配置")
    print("   - 使用Google的嵌入API（如果有）")
    print("   - 或者使用其他兼容的嵌入服務")
    
    print("\n🔧 方案2: 禁用內存功能")
    print("   - 設置 memory_enabled = False")
    print("   - 修複代碼中的None檢查")
    
    print("\n🔧 方案3: 使用阿里百炼嵌入")
    print("   - 即使LLM使用Google AI")
    print("   - 嵌入仍然使用阿里百炼")
    
    print("\n🔧 方案4: 使用本地嵌入")
    print("   - 安裝Ollama")
    print("   - 下載nomic-embed-text模型")
    print("   - 完全本地運行")
    
    print("\n📋 各方案對比:")
    print("   方案1: 最理想，但需要Google嵌入API")
    print("   方案2: 最簡單，但失去記忆功能")
    print("   方案3: 實用，混合使用不同服務")
    print("   方案4: 隐私最佳，但需要本地資源")

def main():
    """主測試函數"""
    print("🧪 嵌入模型使用場景分析")
    print("=" * 70)
    
    test_embedding_selection()
    test_embedding_functionality()
    show_solutions()
    
    print(f"\n📊 总結:")
    print("=" * 50)
    print("1. nomic-embed-text 是本地Ollama使用的嵌入模型")
    print("2. Google AI没有專門的嵌入配置，默認嘗試使用OpenAI")
    print("3. 這就是為什么測試Google AI時內存功能不可用")
    print("4. 需要為Google AI添加合適的嵌入解決方案")

if __name__ == "__main__":
    main()
