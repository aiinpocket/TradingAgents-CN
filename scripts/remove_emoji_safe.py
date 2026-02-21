"""
安全移除 emoji 腳本 - 使用精確 Unicode 範圍，不影響 CJK 中文字元

每個範圍都經過驗證，確保不會與 CJK Unified Ideographs (U+4E00-U+9FFF) 重疊
"""

import re
import os
import sys

# 精確的 emoji Unicode 範圍（每個都獨立指定，避免跨 CJK 區段）
EMOJI_PATTERN = re.compile(
    "["
    "\U0000200D"          # Zero Width Joiner
    "\U0000FE0F"          # Variation Selector-16
    "\U00002600-\U000026FF"  # Miscellaneous Symbols (天氣、棋子等)
    "\U00002702-\U000027B0"  # Dingbats
    "\U0000FE00-\U0000FE0F"  # Variation Selectors
    "\U0001F000-\U0001F02F"  # Mahjong Tiles
    "\U0001F0A0-\U0001F0FF"  # Playing Cards
    "\U0001F100-\U0001F1FF"  # Enclosed Alphanumeric Supplement
    "\U0001F200-\U0001F2FF"  # Enclosed Ideographic Supplement
    "\U0001F300-\U0001F5FF"  # Miscellaneous Symbols and Pictographs
    "\U0001F600-\U0001F64F"  # Emoticons
    "\U0001F680-\U0001F6FF"  # Transport and Map Symbols
    "\U0001F700-\U0001F77F"  # Alchemical Symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002934-\U00002935"  # Arrows
    "\U00003030"             # Wavy Dash
    "\U0000303D"             # Part Alternation Mark
    "\U00003297"             # Circled Ideograph Congratulation
    "\U00003299"             # Circled Ideograph Secret
    # 保留 (c) 和 (R) 符號 - 這些是合法文字符號
    "\U0000200D"             # ZWJ
    "\U000020E3"             # Combining Enclosing Keycap
    "\U0000231A-\U0000231B"  # Watch, Hourglass
    "\U000023E9-\U000023F3"  # Various media symbols
    "\U000023F8-\U000023FA"  # More media symbols
    "\U000025AA-\U000025AB"  # Small squares
    "\U000025B6"             # Play button
    "\U000025C0"             # Reverse play
    "\U000025FB-\U000025FE"  # Medium/small squares
    "\U00002614-\U00002615"  # Umbrella, Hot Beverage
    "\U00002648-\U00002653"  # Zodiac signs
    "\U0000267F"             # Wheelchair
    "\U00002693"             # Anchor
    "\U000026A1"             # High Voltage
    "\U000026AA-\U000026AB"  # Circles
    "\U000026BD-\U000026BE"  # Soccer, Baseball
    "\U000026C4-\U000026C5"  # Snowman, Sun Behind Cloud
    "\U000026CE"             # Ophiuchus
    "\U000026D4"             # No Entry
    "\U000026EA"             # Church
    "\U000026F2-\U000026F3"  # Fountain, Golf
    "\U000026F5"             # Sailboat
    "\U000026FA"             # Tent
    "\U000026FD"             # Fuel Pump
    "]+"
)


def remove_emoji_from_file(filepath):
    """從單一檔案移除 emoji，保留所有中文和其他文字"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return False

    new_content = EMOJI_PATTERN.sub('', content)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False


def main():
    """掃描專案所有 .py 和 .md 檔案，安全移除 emoji"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 排除目錄
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'env', '.eggs'}

    modified_files = []
    scanned = 0

    for root, dirs, files in os.walk(project_root):
        # 排除不需要的目錄
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for fname in files:
            if not (fname.endswith('.py') or fname.endswith('.md')):
                continue

            filepath = os.path.join(root, fname)
            scanned += 1

            if remove_emoji_from_file(filepath):
                rel_path = os.path.relpath(filepath, project_root)
                modified_files.append(rel_path)

    print(f"掃描: {scanned} 個檔案")
    print(f"修改: {len(modified_files)} 個檔案")

    if modified_files:
        for f in sorted(modified_files):
            print(f"  - {f}")

    return len(modified_files)


if __name__ == '__main__':
    count = main()
    sys.exit(0 if count >= 0 else 1)
