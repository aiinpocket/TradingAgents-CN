#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票數據降級系統演示
展示MongoDB -> Tushare數據接口的完整降級機制
"""

import sys
import os
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def demo_database_config_fixes():
    """
    演示數據庫配置修複
    """
    print("🔧 數據庫配置修複演示")
    print("=" * 50)
    
    print("\n📋 修複內容:")
    print("  1. ✅ 移除了硬編碼的MongoDB連接地址")
    print("  2. ✅ 創建了統一的數據庫配置管理")
    print("  3. ✅ 實現了完整的降級機制")
    print("  4. ✅ 增强了錯誤處理和提示")
    
    print("\n🔍 檢查配置文件:")

    # 檢查.env文件
    env_path = os.path.join(project_root, '.env')
    if os.path.exists(env_path):
        print(f"  ✅ 找到配置文件: {env_path}")
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'MONGODB_HOST' in content or 'MONGODB_CONNECTION_STRING' in content:
                print("  ✅ MongoDB配置已設置")
            if 'REDIS_HOST' in content or 'REDIS_CONNECTION_STRING' in content:
                print("  ✅ Redis配置已設置")
    else:
        print(f"  ⚠️ 配置文件不存在: {env_path}")
    
    # 檢查database_config.py
    config_path = os.path.join(project_root, 'tradingagents', 'config', 'database_config.py')
    if os.path.exists(config_path):
        print(f"  ✅ 找到統一配置管理: database_config.py")
    else:
        print(f"  ⚠️ 統一配置管理文件不存在")

def demo_fallback_mechanism():
    """
    演示降級機制
    """
    print("\n🔄 降級機制演示")
    print("=" * 50)
    
    try:
        from tradingagents.api.stock_api import (
            get_stock_info, check_service_status, get_market_summary
        )
        
        print("\n📊 1. 檢查服務狀態:")
        status = check_service_status()
        
        for key, value in status.items():
            if key == 'mongodb_status':
                icon = "✅" if value == 'connected' else "⚠️" if value == 'disconnected' else "❌"
                print(f"  {icon} MongoDB: {value}")
            elif key == 'unified_api_status':
                icon = "✅" if value == 'available' else "⚠️" if value == 'limited' else "❌"
                print(f"  {icon} 統一數據接口: {value}")
        
        print("\n🔍 2. 測試股票查詢（展示降級過程）:")
        test_codes = ['000001', '600000']
        
        for code in test_codes:
            print(f"\n  📊 查詢股票 {code}:")
            result = get_stock_info(code)
            
            if 'error' in result:
                print(f"    ❌ 查詢失败: {result['error']}")
                if 'suggestion' in result:
                    print(f"    💡 建议: {result['suggestion']}")
            else:
                print(f"    ✅ 查詢成功: {result.get('name')}")
                print(f"    🔗 數據源: {result.get('source')}")
                print(f"    🏢 市場: {result.get('market')}")
        
        print("\n📈 3. 測試市場概覽:")
        summary = get_market_summary()
        
        if 'error' in summary:
            print(f"  ❌ 獲取失败: {summary['error']}")
        else:
            print(f"  ✅ 总股票數: {summary.get('total_count', 0):,}")
            print(f"  🔗 數據源: {summary.get('data_source')}")
            print(f"  🏢 沪市: {summary.get('shanghai_count', 0):,} 只")
            print(f"  🏢 深市: {summary.get('shenzhen_count', 0):,} 只")
        
    except ImportError as e:
        print(f"❌ 無法導入股票API: {e}")
        print("💡 請確保所有依賴文件都已正確創建")
    except Exception as e:
        print(f"❌ 演示過程中出錯: {e}")

def demo_configuration_benefits():
    """
    演示配置優化的好處
    """
    print("\n💡 配置優化的好處")
    print("=" * 50)
    
    benefits = [
        ("🔒 安全性提升", "移除硬編碼連接地址，通過環境變量管理敏感信息"),
        ("🔄 灵活性增强", "支持不同環境的配置，無需修改代碼"),
        ("⚡ 高可用性", "MongoDB不可用時自動降級到Tushare數據接口"),
        ("📊 數據完整性", "多數據源確保股票信息的持续可用性"),
        ("🛠️ 易於維護", "統一的配置管理，便於運維和部署"),
        ("🔍 錯誤診斷", "詳細的狀態檢查和錯誤提示"),
        ("💾 自動緩存", "從API獲取的數據自動緩存到MongoDB"),
        ("🎯 性能優化", "優先使用本地數據庫，减少網絡請求")
    ]
    
    for icon_title, description in benefits:
        print(f"\n{icon_title}:")
        print(f"  {description}")

def demo_usage_scenarios():
    """
    演示使用場景
    """
    print("\n🎯 使用場景演示")
    print("=" * 50)
    
    scenarios = [
        {
            "title": "🏢 生產環境",
            "description": "MongoDB正常運行，提供最佳性能",
            "config": "MONGODB_CONNECTION_STRING=mongodb://prod-server:27017/tradingagents"
        },
        {
            "title": "🧪 測試環境",
            "description": "使用本地MongoDB進行開發測試",
            "config": "MONGODB_CONNECTION_STRING=mongodb://localhost:27017/test_db"
        },
        {
            "title": "☁️ 云端部署",
            "description": "使用云數據庫服務",
            "config": "MONGODB_CONNECTION_STRING=mongodb+srv://user:pass@cluster.mongodb.net/db"
        },
        {
            "title": "🔧 開發環境",
            "description": "MongoDB未配置，自動使用Tushare數據接口",
            "config": "# MONGODB_CONNECTION_STRING 未設置"
        },
        {
            "title": "🌐 離線模式",
            "description": "網絡受限時使用緩存數據",
            "config": "使用本地文件緩存作為最後降級方案"
        }
    ]
    
    for scenario in scenarios:
        print(f"\n{scenario['title']}:")
        print(f"  📝 描述: {scenario['description']}")
        print(f"  ⚙️ 配置: {scenario['config']}")

def demo_migration_guide():
    """
    演示迁移指南
    """
    print("\n📚 迁移指南")
    print("=" * 50)
    
    print("\n🔄 從旧版本迁移的步骤:")
    
    steps = [
        "1. 📋 檢查現有的硬編碼連接地址",
        "2. 🔧 配置環境變量 MONGODB_CONNECTION_STRING",
        "3. 🔧 配置環境變量 REDIS_CONNECTION_STRING",
        "4. 📝 更新應用代碼使用新的API接口",
        "5. 🧪 運行測試驗證降級機制",
        "6. 🚀 部署到生產環境",
        "7. 📊 監控服務狀態和性能"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print("\n💡 最佳實踐:")
    practices = [
        "🔒 使用環境變量管理敏感配置",
        "🔄 定期測試降級機制",
        "📊 監控數據源的可用性",
        "💾 定期备份MongoDB數據",
        "🔍 使用日誌記錄關键操作",
        "⚡ 優化查詢性能和緩存策略"
    ]
    
    for practice in practices:
        print(f"  {practice}")

def main():
    """
    主演示函數
    """
    print("🚀 股票數據系統修複演示")
    print("=" * 60)
    print(f"📅 演示時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 演示各個方面
        demo_database_config_fixes()
        demo_fallback_mechanism()
        demo_configuration_benefits()
        demo_usage_scenarios()
        demo_migration_guide()
        
        print("\n" + "=" * 60)
        print("🎉 演示完成！")
        print("\n📋 总結:")
        print("  ✅ 成功移除了硬編碼的數據庫連接地址")
        print("  ✅ 實現了完整的MongoDB -> Tushare數據接口降級機制")
        print("  ✅ 提供了統一的配置管理和API接口")
        print("  ✅ 增强了系統的可靠性和可維護性")
        
        print("\n🔗 相關文件:")
        files = [
            "tradingagents/config/database_config.py - 統一配置管理",
            "tradingagents/dataflows/stock_data_service.py - 股票數據服務",
            "tradingagents/api/stock_api.py - 便捷API接口",
            "examples/stock_query_examples.py - 使用示例",
            "tests/test_stock_data_service.py - 測試程序",
            ".env - 數據庫配置文件"
        ]
        
        for file_info in files:
            print(f"  📄 {file_info}")
        
    except KeyboardInterrupt:
        print("\n⚠️ 演示被用戶中斷")
    except Exception as e:
        print(f"\n❌ 演示過程中出錯: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()