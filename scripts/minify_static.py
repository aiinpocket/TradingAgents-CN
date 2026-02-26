"""
靜態資源壓縮腳本（Docker 構建階段使用）
對 CSS/JS 做基本壓縮：移除註解、多餘空白、空行
不依賴任何第三方套件，僅使用 Python 標準庫
"""

import os
import re
import sys


def minify_css(content: str) -> str:
    """壓縮 CSS：移除註解、多餘空白、換行"""
    # 移除多行註解 /* ... */
    content = re.sub(r"/\*[\s\S]*?\*/", "", content)
    # 移除行首/行尾空白
    content = "\n".join(line.strip() for line in content.splitlines())
    # 移除空行
    content = re.sub(r"\n{2,}", "\n", content)
    # 移除選擇器前後多餘空格
    content = re.sub(r"\s*([{};:,>~+])\s*", r"\1", content)
    # 保留 calc() 內的空格（修復 calc(100% - 10px) 被破壞的問題）
    # 還原 - / + 前的空格（CSS calc 需要）
    content = re.sub(r"calc\(([^)]+)\)", _fix_calc, content)
    # 移除前導換行
    content = content.strip()
    return content


def _fix_calc(match: re.Match) -> str:
    """修復 calc() 表達式中被移除的空格"""
    expr = match.group(1)
    # 確保 +、- 運算子前後有空格（CSS calc 規範要求）
    expr = re.sub(r"(?<=\w)([+-])(?=\w)", r" \1 ", expr)
    return f"calc({expr})"


def minify_js(content: str) -> str:
    """壓縮 JS：移除單行註解、多餘空白（保守策略避免破壞語意）"""
    lines = content.splitlines()
    result = []
    in_multiline_comment = False
    in_template_literal = False

    for line in lines:
        # 追蹤多行註解
        if in_multiline_comment:
            end_idx = line.find("*/")
            if end_idx >= 0:
                in_multiline_comment = False
                line = line[end_idx + 2:]
            else:
                continue

        # 跳過樣板字串內容（不做壓縮）
        backtick_count = line.count("`")
        if backtick_count % 2 == 1:
            in_template_literal = not in_template_literal

        if in_template_literal:
            result.append(line)
            continue

        # 移除多行註解開頭
        while "/*" in line:
            start = line.index("/*")
            end = line.find("*/", start + 2)
            if end >= 0:
                line = line[:start] + line[end + 2:]
            else:
                in_multiline_comment = True
                line = line[:start]
                break

        # 移除獨立行的單行註解（但保留 URL 中的 //）
        stripped = line.strip()
        if stripped.startswith("//"):
            continue

        # 移除行首行尾空白（但保留縮排結構以免破壞語意）
        stripped = line.rstrip()
        if stripped:
            result.append(stripped)

    return "\n".join(result)


def process_directory(static_dir: str):
    """處理指定目錄下的所有 CSS/JS 檔案"""
    total_before = 0
    total_after = 0

    for root, _dirs, files in os.walk(static_dir):
        for fname in files:
            filepath = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower()

            if ext not in (".css", ".js"):
                continue

            with open(filepath, "r", encoding="utf-8") as f:
                original = f.read()

            before_size = len(original.encode("utf-8"))

            if ext == ".css":
                minified = minify_css(original)
            else:
                minified = minify_js(original)

            after_size = len(minified.encode("utf-8"))

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(minified)

            total_before += before_size
            total_after += after_size
            reduction = (1 - after_size / before_size) * 100 if before_size else 0
            print(f"  {filepath}: {before_size:,} -> {after_size:,} ({reduction:.1f}% 縮減)")

    if total_before:
        total_reduction = (1 - total_after / total_before) * 100
        print(f"\n  合計: {total_before:,} -> {total_after:,} ({total_reduction:.1f}% 縮減)")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "app/static"
    if not os.path.isdir(target):
        print(f"目錄不存在: {target}")
        sys.exit(1)
    print(f"壓縮靜態資源: {target}")
    process_directory(target)
