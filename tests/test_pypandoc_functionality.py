#!/usr/bin/env python3
"""
測試pypandoc功能
驗證導出功能的依賴是否正常工作
"""

import sys
import os
import tempfile
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_pypandoc_import():
    """測試pypandoc導入"""
    print("🔍 測試pypandoc導入...")
    try:
        import pypandoc
        print("✅ pypandoc導入成功")
        return True
    except ImportError as e:
        print(f"❌ pypandoc導入失敗: {e}")
        return False

def test_pandoc_version():
    """測試pandoc版本"""
    print("\n🔍 測試pandoc版本...")
    try:
        import pypandoc
        version = pypandoc.get_pandoc_version()
        print(f"✅ Pandoc版本: {version}")
        return True
    except Exception as e:
        print(f"❌ 獲取pandoc版本失敗: {e}")
        return False

def test_pandoc_download():
    """測試pandoc自動下載"""
    print("\n🔍 測試pandoc自動下載...")
    try:
        import pypandoc
        
        # 檢查是否已有pandoc
        try:
            version = pypandoc.get_pandoc_version()
            print(f"✅ Pandoc已存在: {version}")
            return True
        except:
            print("⚠️ Pandoc不存在，嘗試下載...")
            
        # 嘗試下載
        pypandoc.download_pandoc()
        
        # 再次檢查
        version = pypandoc.get_pandoc_version()
        print(f"✅ Pandoc下載成功: {version}")
        return True
        
    except Exception as e:
        print(f"❌ Pandoc下載失敗: {e}")
        return False

def test_markdown_conversion():
    """測試Markdown轉換功能"""
    print("\n🔍 測試Markdown轉換...")
    
    try:
        import pypandoc
        
        # 測試內容
        test_markdown = """# 測試報告

## 基本信息
- **股票代碼**: TEST001
- **生成時間**: 2025-01-12 15:30:00

## 分析結果
這是一個測試報告，用於驗證pypandoc的轉換功能。

### 技術分析
- 價格趨勢：上漲
- 成交量：正常
- 技術指標：良好

### 投資建議
**建議**: 買入
**置信度**: 85%

---
*報告生成時間: 2025-01-12 15:30:00*
"""
        
        print("📄 測試Markdown內容準備完成")
        
        # 測試轉換為HTML
        try:
            html_output = pypandoc.convert_text(test_markdown, 'html', format='markdown')
            print("✅ Markdown → HTML 轉換成功")
            print(f"   輸出長度: {len(html_output)} 字符")
        except Exception as e:
            print(f"❌ Markdown → HTML 轉換失敗: {e}")
            return False
        
        # 測試轉換為DOCX
        try:
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            pypandoc.convert_text(
                test_markdown,
                'docx',
                format='markdown',
                outputfile=output_file,
                extra_args=['--toc', '--number-sections']
            )
            
            # 檢查文件是否生成
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✅ Markdown → DOCX 轉換成功")
                print(f"   文件大小: {file_size} 字節")
                
                # 清理臨時文件
                os.unlink(output_file)
            else:
                print("❌ DOCX文件未生成")
                return False
                
        except Exception as e:
            print(f"❌ Markdown → DOCX 轉換失敗: {e}")
            return False
        
        # 測試轉換為PDF (可能失敗，因為需要額外工具)
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                output_file = tmp_file.name
            
            pypandoc.convert_text(
                test_markdown,
                'pdf',
                format='markdown',
                outputfile=output_file,
                extra_args=['--pdf-engine=wkhtmltopdf']
            )
            
            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print(f"✅ Markdown → PDF 轉換成功")
                print(f"   文件大小: {file_size} 字節")
                
                # 清理臨時文件
                os.unlink(output_file)
            else:
                print("⚠️ PDF文件未生成 (可能缺少PDF引擎)")
                
        except Exception as e:
            print(f"⚠️ Markdown → PDF 轉換失敗: {e}")
            print("   這是正常的，PDF轉換需要額外的工具如wkhtmltopdf")
        
        return True
        
    except Exception as e:
        print(f"❌ 轉換測試失敗: {e}")
        return False

def test_report_exporter():
    """測試報告導出器"""
    print("\n🔍 測試報告導出器...")
    
    try:
        from web.utils.report_exporter import ReportExporter
        
        # 創建導出器實例
        exporter = ReportExporter()
        print(f"✅ 報告導出器創建成功")
        print(f"   導出功能可用: {exporter.export_available}")
        print(f"   Pandoc可用: {exporter.pandoc_available}")
        
        # 測試數據
        test_results = {
            'stock_symbol': 'TEST001',
            'decision': {
                'action': 'buy',
                'confidence': 0.85,
                'risk_score': 0.3,
                'target_price': '¥15.50',
                'reasoning': '基於技術分析和基本面分析，該股票具有良好的投資價值。'
            },
            'state': {
                'market_report': '技術指標顯示上漲趨勢，成交量放大。',
                'fundamentals_report': '公司財務狀況良好，盈利能力強。',
                'sentiment_report': '市場情緒積極，投資者信心較強。'
            },
            'analysts': ['技術分析師', '基本面分析師', '情緒分析師'],
            'research_depth': '深度分析',
            'is_demo': False
        }
        
        # 測試Markdown導出
        try:
            md_content = exporter.generate_markdown_report(test_results)
            print("✅ Markdown報告生成成功")
            print(f"   內容長度: {len(md_content)} 字符")
        except Exception as e:
            print(f"❌ Markdown報告生成失敗: {e}")
            return False
        
        # 測試DOCX導出 (如果pandoc可用)
        if exporter.pandoc_available:
            try:
                docx_content = exporter.generate_docx_report(test_results)
                print("✅ DOCX報告生成成功")
                print(f"   內容大小: {len(docx_content)} 字節")
            except Exception as e:
                print(f"❌ DOCX報告生成失敗: {e}")
                return False
        else:
            print("⚠️ 跳過DOCX測試 (pandoc不可用)")
        
        return True
        
    except Exception as e:
        print(f"❌ 報告導出器測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("🧪 pypandoc功能測試")
    print("=" * 50)
    
    tests = [
        ("pypandoc導入", test_pypandoc_import),
        ("pandoc版本", test_pandoc_version),
        ("pandoc下載", test_pandoc_download),
        ("Markdown轉換", test_markdown_conversion),
        ("報告導出器", test_report_exporter),
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
    
    # 總結
    print("\n" + "="*50)
    print("📊 測試結果總結")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n總計: {passed}/{total} 測試通過")
    
    if passed == total:
        print("🎉 所有測試通過！pypandoc功能正常")
        return True
    else:
        print("⚠️ 部分測試失敗，請檢查配置")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
