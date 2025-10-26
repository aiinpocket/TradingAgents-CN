#!/usr/bin/env python3
"""
檢查可用的Gemini模型
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

def list_available_models():
    """列出可用的Gemini模型"""
    try:
        print("🔍 檢查可用的Gemini模型")
        print("=" * 50)
        
        import google.generativeai as genai
        
        # 配置API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        if not google_api_key:
            print("❌ Google API密鑰未配置")
            return []
        
        genai.configure(api_key=google_api_key)
        
        # 列出所有可用模型
        print("📋 獲取可用模型列表...")
        models = genai.list_models()
        
        available_models = []
        for model in models:
            print(f"   模型名稱: {model.name}")
            print(f"   顯示名稱: {model.display_name}")
            print(f"   支持的方法: {model.supported_generation_methods}")
            print(f"   描述: {model.description}")
            print("-" * 40)
            
            # 檢查是否支持generateContent
            if 'generateContent' in model.supported_generation_methods:
                available_models.append(model.name)
        
        print(f"\n✅ 支持generateContent的模型: {len(available_models)}")
        for model in available_models:
            print(f"   - {model}")
        
        return available_models
        
    except Exception as e:
        print(f"❌ 獲取模型列表失败: {e}")
        import traceback
        print(traceback.format_exc())
        return []

def test_specific_model(model_name):
    """測試特定模型"""
    try:
        print(f"\n🧪 測試模型: {model_name}")
        print("=" * 50)
        
        import google.generativeai as genai
        
        # 配置API密鑰
        google_api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=google_api_key)
        
        # 創建模型實例
        model = genai.GenerativeModel(model_name)
        
        print("✅ 模型實例創建成功")
        
        # 測試生成內容
        print("📝 測試內容生成...")
        response = model.generate_content("請用中文簡單介紹一下人工智能的發展")
        
        if response and response.text:
            print("✅ 模型調用成功")
            print(f"   響應長度: {len(response.text)} 字符")
            print(f"   響應預覽: {response.text[:200]}...")
            return True
        else:
            print("❌ 模型調用失败：無響應內容")
            return False
            
    except Exception as e:
        print(f"❌ 模型測試失败: {e}")
        return False

def test_langchain_with_correct_model(model_name):
    """使用正確的模型名稱測試LangChain"""
    try:
        print(f"\n🧪 測試LangChain与模型: {model_name}")
        print("=" * 50)
        
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        # 創建LangChain Gemini實例
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,
            max_tokens=1000,
            google_api_key=os.getenv('GOOGLE_API_KEY')
        )
        
        print("✅ LangChain Gemini實例創建成功")
        
        # 測試調用
        print("📝 測試LangChain調用...")
        response = llm.invoke("請用中文分析一下苹果公司的投資價值")
        
        if response and response.content:
            print("✅ LangChain Gemini調用成功")
            print(f"   響應長度: {len(response.content)} 字符")
            print(f"   響應預覽: {response.content[:200]}...")
            return True
        else:
            print("❌ LangChain Gemini調用失败：無響應內容")
            return False
            
    except Exception as e:
        print(f"❌ LangChain測試失败: {e}")
        return False

def main():
    """主函數"""
    print("🧪 Gemini模型檢查和測試")
    print("=" * 60)
    
    # 檢查API密鑰
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ Google API密鑰未配置")
        return
    
    print(f"✅ Google API密鑰已配置: {google_api_key[:20]}...")
    
    # 獲取可用模型
    available_models = list_available_models()
    
    if not available_models:
        print("❌ 没有找到可用的模型")
        return
    
    # 測試第一個可用模型
    test_model = available_models[0]
    print(f"\n🎯 選擇測試模型: {test_model}")
    
    # 測試直接API
    direct_success = test_specific_model(test_model)
    
    # 測試LangChain集成
    langchain_success = test_langchain_with_correct_model(test_model)
    
    # 总結結果
    print(f"\n📊 測試結果总結:")
    print("=" * 50)
    print(f"  可用模型數量: {len(available_models)}")
    print(f"  推薦模型: {test_model}")
    print(f"  直接API測試: {'✅ 通過' if direct_success else '❌ 失败'}")
    print(f"  LangChain集成: {'✅ 通過' if langchain_success else '❌ 失败'}")
    
    if direct_success and langchain_success:
        print(f"\n🎉 Gemini模型 {test_model} 完全可用！")
        print(f"\n💡 使用建议:")
        print(f"   1. 在配置中使用模型名稱: {test_model}")
        print(f"   2. 替換所有 'gemini-pro' 為 '{test_model}'")
        print(f"   3. 確保API密鑰有效且有足夠配額")
    else:
        print(f"\n⚠️ 模型測試部分失败，請檢查API密鑰和網絡連接")

if __name__ == "__main__":
    main()
