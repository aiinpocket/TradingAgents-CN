#!/usr/bin/env python3
"""
Docker環境PDF功能測試腳本
"""

import sys
import os
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_docker_environment():
    """測試Docker環境檢測"""
    print("🔍 測試Docker環境檢測...")
    
    try:
        from web.utils.docker_pdf_adapter import is_docker_environment
        is_docker = is_docker_environment()
        print(f"Docker環境: {'是' if is_docker else '否'}")
        return is_docker
    except ImportError as e:
        print(f"❌ 導入Docker適配器失败: {e}")
        return False

def test_docker_dependencies():
    """測試Docker依賴"""
    print("\n🔍 測試Docker依賴...")
    
    try:
        from web.utils.docker_pdf_adapter import check_docker_pdf_dependencies
        deps_ok, message = check_docker_pdf_dependencies()
        print(f"依賴檢查: {'✅' if deps_ok else '❌'} {message}")
        return deps_ok
    except ImportError as e:
        print(f"❌ 導入Docker適配器失败: {e}")
        return False

def test_docker_pdf_generation():
    """測試Docker PDF生成"""
    print("\n🔍 測試Docker PDF生成...")
    
    try:
        from web.utils.docker_pdf_adapter import test_docker_pdf_generation
        pdf_ok = test_docker_pdf_generation()
        print(f"PDF生成: {'✅' if pdf_ok else '❌'}")
        return pdf_ok
    except ImportError as e:
        print(f"❌ 導入Docker適配器失败: {e}")
        return False

def test_report_exporter():
    """測試報告導出器Docker集成"""
    print("\n🔍 測試報告導出器Docker集成...")
    
    try:
        from web.utils.report_exporter import ReportExporter
        
        exporter = ReportExporter()
        print(f"導出器創建: ✅")
        print(f"  export_available: {exporter.export_available}")
        print(f"  pandoc_available: {exporter.pandoc_available}")
        print(f"  is_docker: {exporter.is_docker}")
        
        # 測試Markdown導出
        test_results = {
            'stock_symbol': 'DOCKER_TEST',
            'decision': {
                'action': 'buy',
                'confidence': 0.85,
                'risk_score': 0.3,
                'target_price': '¥15.50',
                'reasoning': 'Docker環境測試報告生成。'
            },
            'state': {
                'market_report': 'Docker環境技術分析測試。',
                'fundamentals_report': 'Docker環境基本面分析測試。'
            },
            'llm_provider': 'test',
            'llm_model': 'test-model',
            'analysts': ['Docker測試分析師'],
            'research_depth': '測試分析',
            'is_demo': True
        }
        
        # 測試Markdown生成
        md_content = exporter.generate_markdown_report(test_results)
        print(f"Markdown生成: ✅ ({len(md_content)} 字符)")
        
        # 如果在Docker環境且pandoc可用，測試PDF生成
        if exporter.is_docker and exporter.pandoc_available:
            try:
                pdf_content = exporter.generate_pdf_report(test_results)
                print(f"Docker PDF生成: ✅ ({len(pdf_content)} 字節)")
                return True
            except Exception as e:
                print(f"Docker PDF生成: ❌ {e}")
                return False
        else:
            print("跳過PDF測試 (非Docker環境或pandoc不可用)")
            return True
            
    except Exception as e:
        print(f"❌ 報告導出器測試失败: {e}")
        return False

def main():
    """主測試函數"""
    print("🐳 Docker環境PDF功能測試")
    print("=" * 50)
    
    tests = [
        ("Docker環境檢測", test_docker_environment),
        ("Docker依賴檢查", test_docker_dependencies),
        ("Docker PDF生成", test_docker_pdf_generation),
        ("報告導出器集成", test_report_exporter),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 測試異常: {e}")
            results.append((test_name, False))
    
    # 总結
    print("\n" + "="*50)
    print("📊 Docker測試結果总結")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失败"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n总計: {passed}/{total} 測試通過")
    
    # 環境建议
    print("\n💡 環境建议:")
    print("-" * 30)
    
    if passed == total:
        print("🎉 Docker PDF功能完全正常！")
    elif passed >= total - 1:
        print("⚠️ 大部分功能正常，可能有小問題")
        print("建议: 檢查Docker鏡像是否包含所有必要依賴")
    else:
        print("❌ Docker PDF功能存在問題")
        print("建议:")
        print("1. 重新構建Docker鏡像")
        print("2. 確保Dockerfile包含PDF依賴")
        print("3. 檢查容器運行權限")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
