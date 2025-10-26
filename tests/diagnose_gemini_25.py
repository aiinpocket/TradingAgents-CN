#!/usr/bin/env python3
"""
診斷Gemini 2.5模型問題
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

def test_gemini_models():
    """測試不同的Gemini模型"""
    print("🧪 診斷Gemini模型問題")
    print("=" * 60)
    
    models_to_test = [
        "gemini-2.5-pro",
        "gemini-2.5-flash", 
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]
    
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ Google API密鑰未配置")
        return
    
    print(f"✅ Google API密鑰已配置: {google_api_key[:20]}...")
    
    working_models = []
    
    for model_name in models_to_test:
        print(f"\n🔍 測試模型: {model_name}")
        print("-" * 40)
        
        try:
            # 測試直接API
            print("📝 測試直接Google API...")
            import google.generativeai as genai
            genai.configure(api_key=google_api_key)
            
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("請用中文說：你好，我是Gemini模型")
            
            if response and response.text:
                print(f"✅ 直接API成功: {response.text[:100]}...")
                direct_success = True
            else:
                print("❌ 直接API失败：無響應")
                direct_success = False
                
        except Exception as e:
            print(f"❌ 直接API失败: {e}")
            direct_success = False
        
        try:
            # 測試LangChain
            print("📝 測試LangChain集成...")
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.1,
                max_tokens=200,
                google_api_key=google_api_key
            )
            
            response = llm.invoke("請用中文簡單介紹一下你自己")
            
            if response and response.content:
                print(f"✅ LangChain成功: {response.content[:100]}...")
                langchain_success = True
            else:
                print("❌ LangChain失败：無響應")
                langchain_success = False
                
        except Exception as e:
            print(f"❌ LangChain失败: {e}")
            langchain_success = False
        
        # 記錄結果
        if direct_success or langchain_success:
            working_models.append({
                'name': model_name,
                'direct': direct_success,
                'langchain': langchain_success
            })
            print(f"✅ {model_name} 部分或完全可用")
        else:
            print(f"❌ {model_name} 完全不可用")
    
    return working_models

def test_best_working_model(working_models):
    """測試最佳可用模型"""
    if not working_models:
        print("\n❌ 没有找到可用的模型")
        return None
    
    # 選擇最佳模型（優先選擇2.5版本，然後是LangChain可用的）
    best_model = None
    for model in working_models:
        if model['langchain']:  # LangChain可用
            if '2.5' in model['name']:  # 優先2.5版本
                best_model = model['name']
                break
            elif best_model is None:  # 如果还没有選擇，就選這個
                best_model = model['name']
    
    if best_model is None:
        # 如果没有LangChain可用的，選擇直接API可用的
        for model in working_models:
            if model['direct']:
                best_model = model['name']
                break
    
    if best_model:
        print(f"\n🎯 選擇最佳模型進行詳細測試: {best_model}")
        print("=" * 60)
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            
            llm = ChatGoogleGenerativeAI(
                model=best_model,
                temperature=0.1,
                max_tokens=800,
                google_api_key=os.getenv('GOOGLE_API_KEY')
            )
            
            # 測試股票分析
            print("📊 測試股票分析能力...")
            response = llm.invoke("""
            請用中文分析苹果公司(AAPL)的投資價值。
            請簡要分析：
            1. 公司優势
            2. 主要風險
            3. 投資建议
            """)
            
            if response and response.content and len(response.content) > 100:
                print("✅ 股票分析測試成功")
                print(f"   響應長度: {len(response.content)} 字符")
                print(f"   響應預覽: {response.content[:200]}...")
                return best_model
            else:
                print("❌ 股票分析測試失败")
                return None
                
        except Exception as e:
            print(f"❌ 詳細測試失败: {e}")
            return None
    
    return None

def main():
    """主函數"""
    print("🧪 Gemini模型診斷")
    print("=" * 70)
    
    # 測試所有模型
    working_models = test_gemini_models()
    
    # 顯示結果
    print(f"\n📊 測試結果总結:")
    print("=" * 50)
    
    if working_models:
        print(f"✅ 找到 {len(working_models)} 個可用模型:")
        for model in working_models:
            direct_status = "✅" if model['direct'] else "❌"
            langchain_status = "✅" if model['langchain'] else "❌"
            print(f"   {model['name']}: 直接API {direct_status} | LangChain {langchain_status}")
        
        # 測試最佳模型
        best_model = test_best_working_model(working_models)
        
        if best_model:
            print(f"\n🎉 推薦使用模型: {best_model}")
            print(f"\n💡 配置建议:")
            print(f"   1. 在Web界面中選擇'Google'作為LLM提供商")
            print(f"   2. 使用模型名稱: {best_model}")
            print(f"   3. 该模型已通過股票分析測試")
        else:
            print(f"\n⚠️ 虽然找到可用模型，但詳細測試失败")
            print(f"   建议使用: {working_models[0]['name']}")
    else:
        print("❌ 没有找到任何可用的Gemini模型")
        print("💡 可能的原因:")
        print("   1. API密鑰權限不足")
        print("   2. 網絡連接問題")
        print("   3. 模型名稱已更新")
        print("   4. API配額限制")

if __name__ == "__main__":
    main()
