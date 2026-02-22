#!/usr/bin/env python3
"""
TradingAgents 應用程式啟動器
使用 FastAPI + Uvicorn 取代 Streamlit
"""

import argparse
import sys
import os
from pathlib import Path

# 確保專案根目錄在路徑中
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
os.chdir(project_root)


def main():
    parser = argparse.ArgumentParser(description="TradingAgents 應用程式")
    parser.add_argument("--host", default="127.0.0.1", help="監聽地址 (預設: 127.0.0.1，Docker 內使用 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8501, help="監聽埠號 (預設: 8501)")
    parser.add_argument("--reload", action="store_true", help="啟用熱重載（開發模式）")
    parser.add_argument("--workers", type=int, default=1, help="工作程序數（預設: 1）")
    args = parser.parse_args()

    try:
        import uvicorn
    except ImportError:
        print("錯誤: 請先安裝 uvicorn: pip install uvicorn[standard]")
        sys.exit(1)

    print(f"TradingAgents 啟動中...")
    print(f"  地址: http://{args.host}:{args.port}")
    print(f"  模式: {'開發' if args.reload else '生產'}")
    print(f"  API 文件: http://{args.host}:{args.port}/api/docs")

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers,
        log_level="info",
    )


if __name__ == "__main__":
    main()
