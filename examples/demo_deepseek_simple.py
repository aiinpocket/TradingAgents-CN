#!/usr/bin/env python3
"""
簡化的DeepSeek演示 - 避免所有複雜導入
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# 加載環境變量
load_dotenv()

class SimpleDeepSeekAdapter:
    """簡化的DeepSeek適配器"""
    
    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def chat(self, message: str) -> str:
        """簡單聊天"""
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": message}],
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content

def demo_simple_chat():
    """演示簡單對話"""
    print("\n🤖 演示DeepSeek簡單對話...")
    
    try:
        adapter = SimpleDeepSeekAdapter()
        
        message = """
        請簡要介紹股票投資的基本概念，包括：
        1. 什么是股票
        2. 股票投資的風險
        3. 基本的投資策略
        請用中文回答，控制在200字以內。
        """
        
        print("💭 正在生成回答...")
        response = adapter.chat(message)
        print(f"🎯 DeepSeek回答:\n{response}")
        
        return True
        
    except Exception as e:
        print(f"❌ 簡單對話演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_stock_analysis():
    """演示股票分析"""
    print("\n📊 演示DeepSeek股票分析...")
    
    try:
        adapter = SimpleDeepSeekAdapter()
        
        query = """
        假設你是一個專業的股票分析師，請分析以下情况：
        
        公司A：
        - 市盈率：15倍
        - 營收增長率：20%
        - 负债率：30%
        - 行業：科技
        
        公司B：
        - 市盈率：25倍
        - 營收增長率：8%
        - 负债率：50%
        - 行業：傳統制造
        
        請從投資價值角度比較這两家公司，並給出投資建议。
        """
        
        print("🧠 正在進行股票分析...")
        response = adapter.chat(query)
        print(f"📈 分析結果:\n{response}")
        
        return True
        
    except Exception as e:
        print(f"❌ 股票分析演示失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🚀 開始DeepSeek演示...")
    
    # 檢查API密鑰
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 未找到DEEPSEEK_API_KEY環境變量")
        print("請在.env文件中配置DEEPSEEK_API_KEY")
        return
    
    print(f"✅ 找到API密鑰: {api_key[:10]}...")
    
    # 運行演示
    demos = [
        ("簡單對話", demo_simple_chat),
        ("股票分析", demo_stock_analysis)
    ]
    
    results = []
    for name, demo_func in demos:
        print(f"\n{'='*50}")
        print(f"🎯 運行演示: {name}")
        print(f"{'='*50}")
        
        success = demo_func()
        results.append((name, success))
        
        if success:
            print(f"✅ {name} 演示成功")
        else:
            print(f"❌ {name} 演示失败")
    
    # 总結
    print(f"\n{'='*50}")
    print(f"📊 演示总結")
    print(f"{'='*50}")
    
    for name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{name}: {status}")
    
    successful_count = sum(1 for _, success in results if success)
    total_count = len(results)
    
    if successful_count == total_count:
        print(f"\n🎉 所有演示都成功完成！({successful_count}/{total_count})")
    else:
        print(f"\n⚠️  部分演示失败 ({successful_count}/{total_count})")

if __name__ == "__main__":
    main()