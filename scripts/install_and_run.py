#!/usr/bin/env python3
"""
TradingAgents-CN 安裝和啟動指令碼
提供一鍵安裝依賴並啟動 FastAPI 應用
"""

import os
import sys
import subprocess
from pathlib import Path


def check_virtual_env():
    """檢查是否在虛擬環境中"""
    in_venv = (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

    if not in_venv:
        print("請先啟用虛擬環境:")
        print("  Windows: .\\env\\Scripts\\activate")
        print("  Linux/macOS: source env/bin/activate")
        return False

    print("虛擬環境已啟用")
    return True


def install_project():
    """安裝專案到虛擬環境"""
    print("\n安裝專案依賴...")

    project_root = Path(__file__).parent.parent

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=project_root,
            check=True,
            capture_output=True,
            text=True,
        )
        print("專案安裝成功")
        return True

    except subprocess.CalledProcessError as e:
        print(f"專案安裝失敗: {e}")
        if e.stderr:
            print(f"錯誤輸出: {e.stderr[:500]}")
        return False


def check_env_file():
    """檢查 .env 檔案"""
    print("\n檢查環境配置...")

    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    env_example = project_root / ".env_example"

    if not env_file.exists():
        if env_example.exists():
            print(".env 檔案不存在，正在從 .env_example 建立...")
            try:
                import shutil
                shutil.copy(env_example, env_file)
                print(".env 檔案已建立，請編輯並配置 API 密鑰")
            except Exception as e:
                print(f"建立 .env 檔案失敗: {e}")
                return False
        else:
            print("找不到 .env_example 檔案")
            return False
    else:
        print(".env 檔案存在")

    return True


def start_app():
    """啟動 FastAPI 應用"""
    print("\n啟動應用...")

    project_root = Path(__file__).parent.parent
    start_file = project_root / "start_app.py"

    if not start_file.exists():
        print(f"找不到啟動檔案: {start_file}")
        return False

    cmd = [sys.executable, str(start_file)]

    print("應用啟動中...")
    print("開啟瀏覽器存取 http://localhost:8501")
    print("按 Ctrl+C 停止應用")
    print("=" * 50)

    try:
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        print("\n應用已停止")
    except Exception as e:
        print(f"\n啟動失敗: {e}")
        return False

    return True


def main():
    """主函式"""
    print("TradingAgents-CN 安裝和啟動工具")
    print("=" * 50)

    if not check_virtual_env():
        return

    if not install_project():
        return

    if not check_env_file():
        return

    start_app()


if __name__ == "__main__":
    main()
