"""
國際化模組

提供多語言翻譯支援，預設語言為繁體中文（zh-TW），另支援英文（en）。
透過 t() 函式取得翻譯文字，透過 set_language() 切換語言。
"""

from .translator import get_translator, set_language, get_current_language, t

__all__ = ["get_translator", "set_language", "get_current_language", "t"]
