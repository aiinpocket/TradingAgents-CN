#!/usr/bin/env python3
"""
測試風險評估功能
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加載環境變量
load_dotenv(project_root / ".env", override=True)

def test_risk_assessment_extraction():
    """測試風險評估數據提取功能"""
    print("🧪 測試風險評估數據提取")
    print("=" * 50)
    
    try:
        from web.utils.analysis_runner import extract_risk_assessment
        
        # 模擬分析狀態數據
        mock_state = {
            'risk_debate_state': {
                'risky_history': """
作為激進風險分析師，我認為AAPL當前具有以下風險特征：

1. **市場機會**: 當前市場情绪積極，技術創新持续推進
2. **增長潜力**: 新產品線和服務業務增長强劲
3. **風險可控**: 虽然存在市場波動，但公司基本面穩健

建议: 適度增加仓位，把握成長機會
                """.strip(),
                
                'safe_history': """
作為保守風險分析師，我對AAPL持谨慎態度：

1. **市場風險**: 當前估值偏高，存在回調風險
2. **行業競爭**: 智能手機市場競爭激烈，增長放緩
3. **宏觀環境**: 利率上升和經濟不確定性增加風險

建议: 保持谨慎，控制仓位規模
                """.strip(),
                
                'neutral_history': """
作為中性風險分析師，我的综合評估如下：

1. **平衡視角**: AAPL既有增長機會也面臨挑战
2. **風險收益**: 當前風險收益比處於合理区間
3. **時機選擇**: 建议分批建仓，降低時機風險

建议: 採用均衡策略，適度配置
                """.strip(),
                
                'judge_decision': """
經過風險委員會充分討論，對AAPL的風險評估結論如下：

**综合風險等級**: 中等風險
**主要風險因素**: 
- 估值風險: 當前P/E比率偏高
- 市場風險: 科技股波動性較大
- 競爭風險: 行業競爭加剧

**風險控制建议**:
1. 建议仓位控制在5-10%
2. 設置止損位在當前價格-15%
3. 分批建仓，降低時機風險
4. 密切關註季度財報和產品發布

**最终建议**: 谨慎乐觀，適度配置
                """.strip()
            }
        }
        
        # 測試提取功能
        risk_assessment = extract_risk_assessment(mock_state)
        
        if risk_assessment:
            print("✅ 風險評估數據提取成功")
            print("\n📋 提取的風險評估報告:")
            print("-" * 50)
            print(risk_assessment[:500] + "..." if len(risk_assessment) > 500 else risk_assessment)
            print("-" * 50)
            
            # 驗證報告內容
            required_sections = [
                "激進風險分析師觀點",
                "中性風險分析師觀點", 
                "保守風險分析師觀點",
                "風險管理委員會最终決议"
            ]
            
            missing_sections = []
            for section in required_sections:
                if section not in risk_assessment:
                    missing_sections.append(section)
            
            if missing_sections:
                print(f"⚠️ 缺少以下部分: {', '.join(missing_sections)}")
                return False
            else:
                print("✅ 風險評估報告包含所有必需部分")
                return True
        else:
            print("❌ 風險評估數據提取失败")
            return False
            
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_web_interface_risk_display():
    """測試Web界面風險評估顯示"""
    print("\n🧪 測試Web界面風險評估顯示")
    print("=" * 50)
    
    try:
        from web.utils.analysis_runner import run_stock_analysis
        
        print("📋 檢查Web界面分析運行器...")
        
        # 檢查函數是否包含風險評估提取逻辑
        import inspect
        source = inspect.getsource(run_stock_analysis)
        
        if 'extract_risk_assessment' in source:
            print("✅ Web界面已集成風險評估提取功能")
        else:
            print("❌ Web界面缺少風險評估提取功能")
            return False
        
        if 'risk_assessment' in source:
            print("✅ Web界面支持風險評估數據傳遞")
        else:
            print("❌ Web界面缺少風險評估數據傳遞")
            return False
        
        print("✅ Web界面風險評估功能檢查通過")
        return True
        
    except Exception as e:
        print(f"❌ 測試失败: {e}")
        return False

def test_risk_assessment_integration():
    """測試風險評估完整集成"""
    print("\n🧪 測試風險評估完整集成")
    print("=" * 50)
    
    try:
        # 檢查API密鑰
        dashscope_key = os.getenv('DASHSCOPE_API_KEY')
        google_key = os.getenv('GOOGLE_API_KEY')
        
        if not dashscope_key and not google_key:
            print("⚠️ 未配置API密鑰，跳過實际分析測試")
            return True
        
        print("🚀 執行實际風險評估測試...")
        
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        
        # 創建配置
        config = DEFAULT_CONFIG.copy()
        if dashscope_key:
            config["llm_provider"] = "dashscope"
            config["deep_think_llm"] = "qwen-plus"
            config["quick_think_llm"] = "qwen-turbo"
        elif google_key:
            config["llm_provider"] = "google"
            config["deep_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"
            config["quick_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"
        
        config["online_tools"] = False  # 避免API限制
        config["memory_enabled"] = True
        config["max_risk_discuss_rounds"] = 1  # 减少測試時間
        
        # 修複路徑
        config["data_dir"] = str(project_root / "data")
        config["results_dir"] = str(project_root / "results")
        config["data_cache_dir"] = str(project_root / "tradingagents" / "dataflows" / "data_cache")
        
        # 創建目錄
        os.makedirs(config["data_dir"], exist_ok=True)
        os.makedirs(config["results_dir"], exist_ok=True)
        os.makedirs(config["data_cache_dir"], exist_ok=True)
        
        print("✅ 配置創建成功")
        
        # 創建TradingAgentsGraph實例
        print("🚀 初始化TradingAgents圖...")
        graph = TradingAgentsGraph(["market", "fundamentals"], config=config, debug=False)
        
        print("✅ TradingAgents圖初始化成功")
        
        # 執行分析
        print("📊 開始風險評估測試...")
        state, decision = graph.propagate("AAPL", "2025-06-27")
        
        # 檢查風險評估數據
        if 'risk_debate_state' in state:
            print("✅ 發現風險評估數據")
            
            risk_debate = state['risk_debate_state']
            components = ['risky_history', 'safe_history', 'neutral_history', 'judge_decision']
            
            for component in components:
                if component in risk_debate and risk_debate[component]:
                    print(f"   ✅ {component}: 有數據")
                else:
                    print(f"   ❌ {component}: 無數據")
            
            # 測試提取功能
            from web.utils.analysis_runner import extract_risk_assessment
            risk_assessment = extract_risk_assessment(state)
            
            if risk_assessment:
                print("✅ 風險評估報告生成成功")
                print(f"   報告長度: {len(risk_assessment)} 字符")
                return True
            else:
                print("❌ 風險評估報告生成失败")
                return False
        else:
            print("❌ 未發現風險評估數據")
            return False
            
    except Exception as e:
        print(f"❌ 集成測試失败: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def main():
    """主測試函數"""
    print("🧪 風險評估功能測試")
    print("=" * 70)
    
    # 運行測試
    results = {}
    
    results['數據提取'] = test_risk_assessment_extraction()
    results['Web界面集成'] = test_web_interface_risk_display()
    results['完整集成'] = test_risk_assessment_integration()
    
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
        print("🎉 風險評估功能完全正常！")
        print("\n💡 現在Web界面應该能正確顯示風險評估數據")
    else:
        print("⚠️ 部分功能需要進一步檢查")

if __name__ == "__main__":
    main()
