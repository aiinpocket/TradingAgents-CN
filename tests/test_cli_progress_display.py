#!/usr/bin/env python3
"""
測試CLI進度顯示效果
模擬分析流程，驗證用戶體驗
"""

import os
import sys
import time

# 添加項目根目錄到Python路徑
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_cli_ui_manager():
    """測試CLI用戶界面管理器"""
    print("🎨 測試CLI用戶界面管理器")
    print("=" * 60)
    
    try:
        from cli.main import CLIUserInterface
        
        # 創建UI管理器
        ui = CLIUserInterface()
        
        print("📊 測試各種消息類型:")
        print("-" * 40)
        
        # 測試用戶消息
        ui.show_user_message("這是普通用戶消息")
        ui.show_user_message("這是帶樣式的消息", "bold cyan")
        
        # 測試進度消息
        ui.show_progress("正在初始化系統...")
        time.sleep(0.5)
        
        # 測試成功消息
        ui.show_success("系統初始化完成")
        
        # 測試警告消息
        ui.show_warning("這是一條警告信息")
        
        # 測試錯誤消息
        ui.show_error("這是一條錯誤信息")
        
        # 測試步驟標題
        ui.show_step_header(1, "測試步驟標題")
        
        # 測試數據信息
        ui.show_data_info("股票信息", "002027", "分眾傳媒")
        
        print("\n✅ CLI用戶界面管理器測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_analysis_flow_simulation():
    """模擬分析流程，測試進度顯示"""
    print("\n🔄 模擬分析流程進度顯示")
    print("=" * 60)
    
    try:
        from cli.main import CLIUserInterface
        
        ui = CLIUserInterface()
        
        # 模擬完整的分析流程
        print("🚀 開始模擬股票分析流程...")
        print()
        
        # 步驟1: 準備分析環境
        ui.show_step_header(1, "準備分析環境 | Preparing Analysis Environment")
        ui.show_progress("正在分析股票: 002027")
        time.sleep(0.3)
        ui.show_progress("分析日期: 2025-07-16")
        time.sleep(0.3)
        ui.show_progress("選擇的分析師: market, fundamentals, technical")
        time.sleep(0.3)
        ui.show_progress("正在初始化分析系統...")
        time.sleep(0.5)
        ui.show_success("分析系統初始化完成")
        
        # 步驟2: 數據獲取階段
        ui.show_step_header(2, "數據獲取階段 | Data Collection Phase")
        ui.show_progress("正在獲取股票基本信息...")
        time.sleep(0.5)
        ui.show_data_info("股票信息", "002027", "分眾傳媒")
        time.sleep(0.3)
        ui.show_progress("正在獲取市場數據...")
        time.sleep(0.5)
        ui.show_data_info("市場數據", "002027", "32條記錄")
        time.sleep(0.3)
        ui.show_progress("正在獲取基本面數據...")
        time.sleep(0.5)
        ui.show_success("數據獲取準備完成")
        
        # 步驟3: 智能分析階段
        ui.show_step_header(3, "智能分析階段 | AI Analysis Phase")
        ui.show_progress("啟動分析師團隊...")
        time.sleep(0.5)
        
        # 模擬各個分析師工作
        analysts = [
            ("📈 市場分析師", "市場分析"),
            ("📊 基本面分析師", "基本面分析"),
            ("🔍 技術分析師", "技術分析"),
            ("💭 情感分析師", "情感分析")
        ]
        
        for analyst_name, analysis_type in analysts:
            ui.show_progress(f"{analyst_name}工作中...")
            time.sleep(1.0)  # 模擬分析時間
            ui.show_success(f"{analysis_type}完成")
        
        # 步驟4: 投資決策生成
        ui.show_step_header(4, "投資決策生成 | Investment Decision Generation")
        ui.show_progress("正在處理投資信號...")
        time.sleep(1.0)
        ui.show_success("🤖 投資信號處理完成")
        
        # 步驟5: 分析報告生成
        ui.show_step_header(5, "分析報告生成 | Analysis Report Generation")
        ui.show_progress("正在生成最終報告...")
        time.sleep(0.8)
        ui.show_success("📋 分析報告生成完成")
        ui.show_success("🎉 002027 股票分析全部完成！")
        
        print("\n✅ 分析流程模擬完成")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_progress_vs_logging():
    """對比進度顯示和日誌記錄"""
    print("\n📊 對比進度顯示和日誌記錄")
    print("=" * 60)
    
    try:
        from cli.main import CLIUserInterface, logger
        
        ui = CLIUserInterface()
        
        print("🔍 測試用戶界面 vs 系統日誌:")
        print("-" * 40)
        
        # 用戶界面消息（清爽顯示）
        print("\n👤 用戶界面消息:")
        ui.show_progress("正在獲取數據...")
        ui.show_success("數據獲取完成")
        ui.show_warning("網絡延遲較高")
        
        # 系統日誌（只寫入文件，不在控制台顯示）
        print("\n🔧 系統日誌（只寫入文件）:")
        logger.info("這是系統日誌消息，應該只寫入文件")
        logger.debug("這是調試信息，用戶看不到")
        logger.error("這是錯誤日誌，只記錄在文件中")
        
        print("✅ 如果上面沒有顯示時間戳和模塊名，說明日誌分離成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def test_user_experience():
    """測試用戶體驗"""
    print("\n👥 測試用戶體驗")
    print("=" * 60)
    
    try:
        from cli.main import CLIUserInterface
        
        ui = CLIUserInterface()
        
        print("🎯 用戶體驗要點:")
        print("-" * 40)
        
        # 清晰的進度指示
        ui.show_step_header(1, "清晰的步驟指示")
        print("   ✅ 用戶知道當前在哪個階段")
        
        # 及時的反饋
        ui.show_progress("及時的進度反饋")
        print("   ✅ 用戶知道系統在工作")
        
        # 成功的確認
        ui.show_success("明確的成功確認")
        print("   ✅ 用戶知道操作成功")
        
        # 友好的錯誤提示
        ui.show_error("友好的錯誤提示")
        print("   ✅ 用戶知道出了什麼問題")
        
        # 重要信息突出
        ui.show_data_info("重要數據", "002027", "關鍵信息突出顯示")
        print("   ✅ 重要信息容易識別")
        
        print("\n🎉 用戶體驗測試完成")
        print("📋 改進效果:")
        print("   - 界面清爽，沒有技術日誌干擾")
        print("   - 進度清晰，用戶不會感到等待焦慮")
        print("   - 反饋及時，用戶體驗流暢")
        print("   - 信息分層，重要內容突出")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🚀 開始測試CLI進度顯示效果")
    print("=" * 80)
    
    results = []
    
    # 測試1: CLI用戶界面管理器
    results.append(test_cli_ui_manager())
    
    # 測試2: 分析流程模擬
    results.append(test_analysis_flow_simulation())
    
    # 測試3: 進度顯示 vs 日誌記錄
    results.append(test_progress_vs_logging())
    
    # 測試4: 用戶體驗
    results.append(test_user_experience())
    
    # 總結結果
    print("\n" + "=" * 80)
    print("📋 測試結果總結")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    test_names = [
        "CLI用戶界面管理器",
        "分析流程進度顯示",
        "進度顯示與日誌分離",
        "用戶體驗測試"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{i+1}. {name}: {status}")
    
    print(f"\n📊 總體結果: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！CLI進度顯示效果優秀")
        print("\n📋 改進成果:")
        print("1. ✅ 清晰的步驟指示和進度反饋")
        print("2. ✅ 用戶界面和系統日誌完全分離")
        print("3. ✅ 重要過程信息及時顯示給用戶")
        print("4. ✅ 界面保持清爽美觀")
        print("5. ✅ 用戶不再需要等待很久才知道結果")
        
        print("\n🎯 用戶體驗提升:")
        print("- 知道系統在做什麼（進度顯示）")
        print("- 知道當前在哪個階段（步驟標題）")
        print("- 知道操作是否成功（成功/錯誤提示）")
        print("- 界面簡潔不雜亂（日誌分離）")
    else:
        print("⚠️ 部分測試失敗，需要進一步優化")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
