#!/usr/bin/env python3
"""
獨立的檔案轉換測試指令碼
用於測試Markdown到Word/PDF的轉換，無需重新生成分析內容
"""

import os
import tempfile
import pypandoc
from datetime import datetime

def test_markdown_content():
    """生成測試用的Markdown內容"""
    
    # 模擬真實的分析結果資料
    test_content = """# 605499 股票分析報告

**生成時間**: 2025-01-12 16:20:00  
**分析狀態**: 正式分析

##  投資決策摘要

| 指標 | 數值 |
|------|------|
| **投資建議** | BUY |
| **置信度** | 85.0% |
| **風險評分** | 25.0% |
| **目標價位** | ¥275.00 |

### 分析推理
基於技術分析和基本面分析，該股票顯示出強勁的上漲趨勢。市場情緒積極，建議買入。

##  分析配置資訊

- **LLM提供商**: openai
- **LLM模型**: gpt-4o-mini  
- **分析師**: market, fundamentals
- **研究深度**: 標準分析

##  市場技術分析

### 技術指標分析
- **趨勢方向**: 上漲
- **支撐位**: ¥250.00
- **阻力位**: ¥300.00
- **RSI指標**: 65 (中性偏強)

### 成交量分析
近期成交量放大，顯示市場關注度提升。

##  基本面分析

### 財務狀況
- **營收增長**: 15.2%
- **淨利潤率**: 8.5%
- **ROE**: 12.3%

### 行業地位
公司在行業中處於領先地位，具有較強的競爭優勢。

##  風險提示

1. **市場風險**: 整體市場波動可能影響股價
2. **行業風險**: 行業政策變化風險
3. **公司風險**: 經營管理風險

##  免責聲明

本報告僅供參考，不構成投資建議。投資有風險，入市需謹慎。

---
*報告生成時間: 2025-01-12 16:20:00*
"""
    
    return test_content

def save_test_content():
    """保存測試內容到檔案"""
    content = test_markdown_content()
    
    with open('test_content.md', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f" 測試內容已保存到 test_content.md")
    print(f" 內容長度: {len(content)} 字符")
    return content

def test_word_conversion(md_content):
    """測試Word轉換"""
    print("\n 測試Word轉換...")
    
    try:
        # 建立暫存檔案
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        print(f" 暫存檔案: {output_file}")
        
        # 測試不同的轉換參數
        test_cases = [
            {
                'name': '基礎轉換',
                'format': 'markdown',
                'extra_args': []
            },
            {
                'name': '帶目錄轉換',
                'format': 'markdown',
                'extra_args': ['--toc', '--number-sections']
            },
            {
                'name': '禁用YAML轉換',
                'format': 'markdown',
                'extra_args': ['--from=markdown-yaml_metadata_block']
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n 測試 {i}: {test_case['name']}")
            print(f" 參數: format={test_case['format']}, extra_args={test_case['extra_args']}")
            
            try:
                pypandoc.convert_text(
                    md_content,
                    'docx',
                    format=test_case['format'],
                    outputfile=output_file,
                    extra_args=test_case['extra_args']
                )
                
                # 檢查檔案
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    file_size = os.path.getsize(output_file)
                    print(f" 轉換成功! 檔案大小: {file_size} 位元組")
                    
                    # 保存成功的檔案
                    success_file = f"test_output_{i}.docx"
                    os.rename(output_file, success_file)
                    print(f" 檔案已保存為: {success_file}")
                    return True
                else:
                    print(f" 轉換失敗: 檔案未生成或為空")
                    
            except Exception as e:
                print(f" 轉換失敗: {e}")
                
            # 清理暫存檔案
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return False
        
    except Exception as e:
        print(f" Word轉換測試失敗: {e}")
        return False

def test_pdf_conversion(md_content):
    """測試PDF轉換"""
    print("\n 測試PDF轉換...")
    
    try:
        # 建立暫存檔案
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            output_file = tmp_file.name
        
        print(f" 暫存檔案: {output_file}")
        
        # 測試不同的PDF引擎
        test_engines = [
            ('wkhtmltopdf', 'HTML轉PDF引擎'),
            ('weasyprint', '現代HTML轉PDF引擎'),
            (None, '預設引擎')
        ]
        
        for i, (engine, description) in enumerate(test_engines, 1):
            print(f"\n 測試 {i}: {description}")
            
            try:
                extra_args = []
                if engine:
                    extra_args.append(f'--pdf-engine={engine}')
                    print(f" 使用引擎: {engine}")
                else:
                    print(f" 使用預設引擎")
                
                pypandoc.convert_text(
                    md_content,
                    'pdf',
                    format='markdown',
                    outputfile=output_file,
                    extra_args=extra_args
                )
                
                # 檢查檔案
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    file_size = os.path.getsize(output_file)
                    print(f" 轉換成功! 檔案大小: {file_size} 位元組")
                    
                    # 保存成功的檔案
                    success_file = f"test_output_{i}.pdf"
                    os.rename(output_file, success_file)
                    print(f" 檔案已保存為: {success_file}")
                    return True
                else:
                    print(f" 轉換失敗: 檔案未生成或為空")
                    
            except Exception as e:
                print(f" 轉換失敗: {e}")
                
            # 清理暫存檔案
            if os.path.exists(output_file):
                os.unlink(output_file)
        
        return False
        
    except Exception as e:
        print(f" PDF轉換測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print(" 獨立檔案轉換測試 (Volume映射版本)")
    print("=" * 50)
    print(f" 當前工作目錄: {os.getcwd()}")
    print(f" Docker環境檢測: {os.path.exists('/.dockerenv')}")
    
    # 保存測試內容
    md_content = save_test_content()
    
    # 測試Word轉換
    word_success = test_word_conversion(md_content)
    
    # 測試PDF轉換
    pdf_success = test_pdf_conversion(md_content)
    
    # 總結
    print("\n" + "=" * 50)
    print(" 測試結果總結")
    print("=" * 50)
    print(f"Word轉換: {' 成功' if word_success else ' 失敗'}")
    print(f"PDF轉換:  {' 成功' if pdf_success else ' 失敗'}")
    
    if word_success or pdf_success:
        print("\n 至少有一種格式轉換成功!")
        print(" 可以將成功的參數應用到主程式中")
    else:
        print("\n 所有轉換都失敗了")
        print(" 需要檢查pandoc安裝和配置")

if __name__ == "__main__":
    main()
