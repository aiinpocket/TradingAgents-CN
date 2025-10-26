#!/usr/bin/env python3
"""
測試DeepSeek成本計算詳細調試
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv()

def test_deepseek_cost_debug():
    """測試DeepSeek成本計算，觀察詳細日誌"""
    print("🔬 DeepSeek成本計算詳細調試")
    print("=" * 60)
    
    # 檢查API密鑰
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("❌ 未找到DEEPSEEK_API_KEY，無法測試")
        return False
    
    try:
        from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
        
        print("🔧 創建DeepSeek實例...")
        
        # 創建DeepSeek實例
        deepseek_llm = ChatDeepSeek(
            model="deepseek-chat",
            temperature=0.1,
            max_tokens=50  # 限制token數量，减少輸出
        )
        
        print(f"📊 模型名稱: {deepseek_llm.model_name}")
        print("\n" + "="*80)
        print("開始調用DeepSeek，觀察詳細的成本計算日誌：")
        print("="*80)
        
        # 測試調用
        result = deepseek_llm.invoke("你好")
        
        print("="*80)
        print("調用完成！")
        print("="*80)
        
        print(f"📊 響應內容: {result.content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🔬 DeepSeek成本計算詳細調試測試")
    print("=" * 80)
    print("📝 這個測試将顯示成本計算的每個步骤")
    print("=" * 80)
    
    success = test_deepseek_cost_debug()
    
    if success:
        print("\n🎉 測試完成！")
        print("請查看上面的詳細日誌，找出成本計算為0的原因。")
    else:
        print("\n❌ 測試失败")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
