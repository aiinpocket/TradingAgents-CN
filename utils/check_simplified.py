#!/usr/bin/env python3
"""
檢查項目中是否還有簡體中文字符
"""

import re
from pathlib import Path
from collections import defaultdict

def has_simplified_chinese(text):
    """
    檢測文本中是否包含簡體中文特徵字符
    返回找到的簡體字列表
    """
    # 常見的簡體中文特徵字符（鍵是簡體，值是繁體）
    simplified_chars = {
        '認': '認', '為': '為', '這': '這', '樣': '樣', '國': '國',
        '簡': '簡', '經': '經', '現': '現', '實': '實', '進': '進',
        '們': '們', '來': '來', '對': '對', '會': '會', '發': '發',
        '動': '動', '產': '產', '種': '種', '後': '後', '學': '學',
        '問': '問', '意': '意', '建': '建', '條': '條', '結': '結',
        '題': '題', '黨': '黨', '提': '提', '較': '較', '論': '論',
        '運': '運', '農': '農', '決': '決', '據': '據', '處': '處',
        '隊': '隊', '給': '給', '門': '門', '熱': '熱', '領': '領',
        '導': '導', '壓': '壓', '濟': '濟', '階': '階', '術': '術',
        '極': '極', '聯': '聯', '證': '證', '改': '改', '轉': '轉',
        '單': '單', '帶': '帶', '車': '車', '達': '達', '積': '積',
        '聲': '聲', '報': '報', '類': '類', '離': '離', '華': '華',
        '確': '確', '馬': '馬', '節': '節', '話': '話', '溫': '溫',
        '傳': '傳', '許': '許', '廣': '廣', '記': '記', '織': '織',
        '裝': '裝', '眾': '眾', '書': '書', '驗': '驗', '連': '連',
        '斷': '斷', '難': '難', '千': '千', '約': '約', '歷': '歷',
        '稱': '稱', '準': '準', '號': '號', '維': '維', '劃': '劃',
        '選': '選', '標': '標', '寫': '寫', '查': '查', '層': '層',
        '適': '適', '屬': '屬', '圓': '圓', '參': '參', '細': '細',
        '聽': '聽', '鐵': '鐵', '價': '價', '嚴': '嚴', '齊': '齊',
        '庫': '庫', '預': '預', '談': '談', '錄': '錄', '環': '環',
        '護': '護', '討': '討', '紀': '紀', '檢': '檢', '貨': '貨',
        '評': '評', '審': '審', '義': '義', '慮': '慮', '臨': '臨',
        '幫': '幫', '銷': '銷', '試': '試', '練': '練', '職': '職',
        '繼': '繼', '雙': '雙', '夠': '夠', '獨': '獨', '訪': '訪',
        '歸': '歸', '醫': '醫', '絕': '絕', '擔': '擔', '補': '補',
        '藥': '藥', '顯': '顯', '獲': '獲', '擊': '擊', '純': '純',
        '顧': '顧', '雜': '雜', '錢': '錢', '態': '態', '歐': '歐',
        '營': '營', '詞': '詞', '損': '損', '載': '載', '鮮': '鮮',
        '競': '競', '冊': '冊', '讀': '讀', '誤': '誤', '擁': '擁',
        '紹': '紹', '貿': '貿', '啟': '啟', '診': '診', '輸': '輸',
        '簽': '簽', '億': '億', '虛': '虛', '額': '額', '觸': '觸',
        '絡': '絡', '踐': '踐', '賽': '賽', '脫': '脫', '聞': '聞',
        '財': '財', '隨': '隨', '講': '講', '擴': '擴', '險': '險',
        '覽': '覽', '穩': '穩', '攜': '攜', '衛': '衛', '遺': '遺',
        '鑒': '鑒', '躍': '躍', '譯': '譯', '廢': '廢', '緊': '緊',
        '齡': '齡', '購': '購', '缺': '缺', '勵': '勵', '遞': '遞',
        '儀': '儀', '測': '測', '攝': '攝', '輛': '輛',
    }

    found = []
    for char, traditional in simplified_chars.items():
        if char in text:
            found.append((char, traditional))

    return found

def scan_file(file_path):
    """掃描單個文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        simplified_found = has_simplified_chinese(content)
        return simplified_found

    except Exception as e:
        return None

def main():
    project_root = Path(__file__).parent.parent
    print(f"📁 項目根目錄: {project_root}\n")
    print("🔍 正在掃描簡體中文字符...\n")

    # 文件類型
    extensions = {'.py', '.md', '.yaml', '.yml', '.json', '.txt', '.sh', '.rst'}

    # 排除目錄
    exclude_dirs = {
        '.git', '.venv', 'venv', '__pycache__', '.pytest_cache',
        'node_modules', '.idea', '.vscode', 'dist', 'build',
        'data_backup_', 'data_cache', 'results', 'logs', 'env'
    }

    # 統計
    total_files = 0
    files_with_simplified = 0
    simplified_chars_count = defaultdict(int)

    # 掃描文件
    for root, dirs, files in os.walk(project_root):
        # 過濾目錄
        dirs[:] = [d for d in dirs if not any(exc in d for exc in exclude_dirs)]

        for file in files:
            file_path = Path(root) / file

            if file_path.suffix not in extensions:
                continue

            total_files += 1
            result = scan_file(file_path)

            if result:
                files_with_simplified += 1
                rel_path = file_path.relative_to(project_root)
                print(f"⚠️  {rel_path}")
                for simp, trad in result[:5]:  # 只顯示前5個
                    print(f"    '{simp}' → '{trad}'")
                    simplified_chars_count[simp] += 1
                if len(result) > 5:
                    print(f"    ...還有 {len(result) - 5} 個簡體字")
                print()

    # 輸出統計
    print(f"\n{'='*60}")
    print(f"📊 掃描結果統計")
    print(f"{'='*60}")
    print(f"   掃描文件總數: {total_files}")
    print(f"   含簡體的文件: {files_with_simplified}")

    if simplified_chars_count:
        print(f"\n   最常見的簡體字:")
        sorted_chars = sorted(simplified_chars_count.items(), key=lambda x: x[1], reverse=True)
        for char, count in sorted_chars[:20]:
            print(f"      '{char}': {count} 次")

    if files_with_simplified == 0:
        print(f"\n   ✅ 太棒了！沒有發現簡體中文！")
    else:
        print(f"\n   ⚠️  建議運行轉換工具進行處理")

    print(f"{'='*60}")

import os
if __name__ == "__main__":
    main()
