#!/usr/bin/env python3
"""
測試DashScope適配器的token統計功能
"""

import os
import sys
import time
from datetime import datetime

# 添加項目根目錄到Python路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tradingagents.llm_adapters.dashscope_adapter import ChatDashScope
from tradingagents.config.config_manager import config_manager, token_tracker
from langchain_core.messages import HumanMessage


def test_dashscope_token_tracking():
    """測試DashScope適配器的token統計功能"""
    print("🧪 開始測試DashScope Token統計功能...")
    
    # 檢查API密鑰
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ 未找到DASHSCOPE_API_KEY環境變量")
        print("請在.env文件中設置DASHSCOPE_API_KEY")
        return False
    
    try:
        # 初始化DashScope適配器
        print("📝 初始化DashScope適配器...")
        llm = ChatDashScope(
            model="qwen-turbo",
            api_key=api_key,
            temperature=0.7,
            max_tokens=500
        )
        
        # 獲取初始統計
        initial_stats = config_manager.get_usage_statistics(1)
        initial_cost = initial_stats.get("total_cost", 0)
        initial_requests = initial_stats.get("total_requests", 0)
        
        print(f"📊 初始統計 - 成本: ¥{initial_cost:.4f}, 請求數: {initial_requests}")
        
        # 測試消息
        test_messages = [
            HumanMessage(content="請簡單介紹一下股票投資的基本概念，不超過100字。")
        ]
        
        # 生成會話ID
        session_id = f"test_session_{int(time.time())}"
        
        print(f"🚀 發送測試請求 (會話ID: {session_id})...")
        
        # 調用LLM（傳入session_id和analysis_type）
        response = llm.invoke(
            test_messages,
            session_id=session_id,
            analysis_type="test_analysis"
        )
        
        print(f"✅ 收到響應: {response.content[:100]}...")
        
        # 等待一下確保記錄已保存
        time.sleep(1)
        
        # 獲取更新後的統計
        updated_stats = config_manager.get_usage_statistics(1)
        updated_cost = updated_stats.get("total_cost", 0)
        updated_requests = updated_stats.get("total_requests", 0)
        
        print(f"📊 更新後統計 - 成本: ¥{updated_cost:.4f}, 請求數: {updated_requests}")
        
        # 檢查是否有新的記錄
        cost_increase = updated_cost - initial_cost
        requests_increase = updated_requests - initial_requests
        
        print(f"📈 變化 - 成本增加: ¥{cost_increase:.4f}, 請求增加: {requests_increase}")
        
        # 驗證結果
        if requests_increase > 0:
            print("✅ Token統計功能正常工作！")
            
            # 顯示供應商統計
            provider_stats = updated_stats.get("provider_stats", {})
            dashscope_stats = provider_stats.get("dashscope", {})
            
            if dashscope_stats:
                print(f"📊 DashScope統計:")
                print(f"   - 成本: ¥{dashscope_stats.get('cost', 0):.4f}")
                print(f"   - 輸入tokens: {dashscope_stats.get('input_tokens', 0)}")
                print(f"   - 輸出tokens: {dashscope_stats.get('output_tokens', 0)}")
                print(f"   - 請求數: {dashscope_stats.get('requests', 0)}")
            
            # 測試會話成本查詢
            session_cost = token_tracker.get_session_cost(session_id)
            print(f"💰 會話成本: ¥{session_cost:.4f}")
            
            return True
        else:
            print("❌ Token統計功能未正常工作")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mongodb_storage():
    """測試MongoDB存储功能"""
    print("\n🧪 測試MongoDB存储功能...")
    
    # 檢查是否啟用了MongoDB
    use_mongodb = os.getenv("USE_MONGODB_STORAGE", "false").lower() == "true"
    
    if not use_mongodb:
        print("ℹ️ MongoDB存储未啟用，跳過MongoDB測試")
        print("要啟用MongoDB存储，請在.env文件中設置 USE_MONGODB_STORAGE=true")
        return True
    
    # 檢查MongoDB連接
    if config_manager.mongodb_storage and config_manager.mongodb_storage.is_connected():
        print("✅ MongoDB連接正常")
        
        # 測試清理功能（清理超過1天的測試記錄）
        try:
            deleted_count = config_manager.mongodb_storage.cleanup_old_records(1)
            print(f"🧹 清理了 {deleted_count} 條旧的測試記錄")
        except Exception as e:
            print(f"⚠️ 清理旧記錄失败: {e}")
        
        return True
    else:
        print("❌ MongoDB連接失败")
        print("請檢查MongoDB配置和連接字符串")
        return False


def main():
    """主測試函數"""
    print("🔬 DashScope Token統計和MongoDB存储測試")
    print("=" * 50)
    
    # 顯示配置狀態
    env_status = config_manager.get_env_config_status()
    print(f"📋 配置狀態:")
    print(f"   - .env文件存在: {env_status['env_file_exists']}")
    print(f"   - DashScope API: {env_status['api_keys']['dashscope']}")
    
    # 檢查MongoDB配置
    use_mongodb = os.getenv("USE_MONGODB_STORAGE", "false").lower() == "true"
    print(f"   - MongoDB存储: {use_mongodb}")
    
    if use_mongodb:
        mongodb_conn = os.getenv("MONGODB_CONNECTION_STRING", "未配置")
        mongodb_db = os.getenv("MONGODB_DATABASE_NAME", "tradingagents")
        print(f"   - MongoDB連接: {mongodb_conn}")
        print(f"   - MongoDB數據庫: {mongodb_db}")
    
    print("\n" + "=" * 50)
    
    # 運行測試
    success = True
    
    # 測試DashScope token統計
    if not test_dashscope_token_tracking():
        success = False
    
    # 測試MongoDB存储
    if not test_mongodb_storage():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有測試通過！")
    else:
        print("❌ 部分測試失败")
    
    return success


if __name__ == "__main__":
    main()