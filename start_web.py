#!/usr/bin/env python3
"""
TradingAgents-CN 啟動腳本
設定 PYTHONPATH 後委託給 web/run_web.py
"""

import os
import sys
from pathlib import Path


def main():
    """設定環境並啟動 Web 應用"""
    project_root = Path(__file__).parent

    # 確保項目根目錄在 Python 路徑中（未安裝套件時必要）
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 設定 PYTHONPATH 環境變量（子進程也能正確匯入）
    current_path = os.environ.get('PYTHONPATH', '')
    if str(project_root) not in current_path:
        separator = os.pathsep if current_path else ''
        os.environ['PYTHONPATH'] = f"{project_root}{separator}{current_path}"

    # 委託給 web/run_web.py
    from web.run_web import main as run_web_main
    run_web_main()


if __name__ == "__main__":
    main()
