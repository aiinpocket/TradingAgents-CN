"""
翻譯器核心模組

負責載入語言檔案、管理當前語言狀態，並提供翻譯查詢功能。
採用執行緒安全的單例模式，確保在多執行緒環境下正確運作。
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional


class Translator:
    """翻譯器類別，負責管理多語言翻譯資源"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls) -> "Translator":
        """確保只建立一個翻譯器實例（執行緒安全的單例模式）"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """初始化翻譯器，僅在首次建立時載入語言資源"""
        if self._initialized:
            return
        self._initialized = True
        # 預設語言為繁體中文
        self._current_language: str = "zh_TW"
        # 語言資源快取，避免重複讀取檔案
        self._translations: Dict[str, Dict[str, Any]] = {}
        # 語言檔案目錄路徑
        self._locales_dir: Path = Path(__file__).parent / "locales"
        # 支援的語言清單
        self._supported_languages: list = ["zh_TW", "en"]
        # 載入預設語言
        self._load_language(self._current_language)

    def _load_language(self, lang_code: str) -> None:
        """載入指定語言的翻譯檔案"""
        if lang_code in self._translations:
            return

        file_path = self._locales_dir / f"{lang_code}.json"
        if not file_path.exists():
            self._translations[lang_code] = {}
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self._translations[lang_code] = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._translations[lang_code] = {}

    def set_language(self, lang_code: str) -> None:
        """切換當前使用的語言"""
        if lang_code not in self._supported_languages:
            return
        with self._lock:
            self._current_language = lang_code
            self._load_language(lang_code)

    def get_current_language(self) -> str:
        """取得當前使用的語言代碼"""
        return self._current_language

    def get_supported_languages(self) -> list:
        """取得所有支援的語言清單"""
        return self._supported_languages.copy()

    def _resolve_key(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """透過巢狀鍵路徑取得對應的翻譯值

        支援以點號分隔的巢狀路徑，例如 "nav.stock_analysis" 會先查找
        data["nav"]，再從中查找 ["stock_analysis"]。
        """
        parts = key.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        # 最終結果必須是字串才視為有效翻譯
        if isinstance(current, str):
            return current
        return None

    def t(self, key: str, **kwargs: Any) -> str:
        """取得翻譯文字

        先查找當前語言的翻譯，若找不到則嘗試繁體中文作為備援，
        最終仍找不到時回傳鍵名本身。支援以 format 語法插入變數，
        例如 t("welcome", name="User") 會將 "{name}" 替換為 "User"。
        """
        # 從當前語言查找
        translations = self._translations.get(self._current_language, {})
        result = self._resolve_key(translations, key)

        # 找不到時嘗試繁體中文備援
        if result is None and self._current_language != "zh_TW":
            fallback = self._translations.get("zh_TW", {})
            result = self._resolve_key(fallback, key)

        # 備援也找不到時回傳鍵名
        if result is None:
            return key

        # 插入變數
        if kwargs:
            try:
                result = result.format(**kwargs)
            except (KeyError, IndexError):
                pass

        return result

    def reload(self) -> None:
        """重新載入所有語言檔案，用於開發階段即時更新翻譯"""
        with self._lock:
            self._translations.clear()
            self._load_language(self._current_language)


# 建立全域翻譯器實例
_translator = Translator()


def get_translator() -> Translator:
    """取得全域翻譯器實例"""
    return _translator


def set_language(lang_code: str) -> None:
    """切換全域語言設定"""
    _translator.set_language(lang_code)


def get_current_language() -> str:
    """取得當前全域語言代碼"""
    return _translator.get_current_language()


def t(key: str, **kwargs: Any) -> str:
    """全域翻譯函式，為最常用的快捷介面"""
    return _translator.t(key, **kwargs)
