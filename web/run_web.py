#!/usr/bin/env python3
"""
TradingAgents-CN Web應用啟動指令碼
"""

import os
import shutil
import signal
import sys
import subprocess
from pathlib import Path

import psutil

# 新增專案根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')

def check_dependencies():
    """檢查必要的依賴是否已安裝"""

    required_packages = ['streamlit', 'plotly']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        logger.error(f"缺少必要的依賴套件: {', '.join(missing_packages)}")
        logger.info("請執行以下命令安裝:")
        logger.info(f"pip install {' '.join(missing_packages)}")
        return False

    logger.info("依賴套件檢查通過")
    return True

def clean_cache_files(force_clean=False):
    """
    清理Python快取檔案，避免Streamlit檔案監控錯誤

    Args:
        force_clean: 是否強制清理，預設False（可選清理）
    """

    # 檢查環境變數是否禁用清理
    try:
        from tradingagents.config.env_utils import parse_bool_env
        skip_clean = parse_bool_env('SKIP_CACHE_CLEAN', False)
    except ImportError:
        skip_clean = os.getenv('SKIP_CACHE_CLEAN', 'false').lower() == 'true'

    if skip_clean and not force_clean:
        logger.info("跳過快取清理（SKIP_CACHE_CLEAN=true）")
        return

    project_root = Path(__file__).parent.parent

    # 在特定目錄中安全查找快取，避免遞歸深度問題
    cache_dirs = []
    try:
        # 只在特定目錄中查找，避免深度遞歸
        search_dirs = [
            project_root / "web",
            project_root / "tradingagents",
            project_root / "tests",
            project_root / "scripts",
            project_root / "examples"
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                try:
                    # 使用有限深度的搜索，最多3層深度
                    for root, dirs, files in os.walk(search_dir):
                        # 限制搜索深度
                        level = len(Path(root).relative_to(search_dir).parts)
                        if level > 3:
                            dirs.clear() # 不再深入搜索
                            continue

                        if Path(root).name == "__pycache__":
                            cache_dirs.append(Path(root))

                except (RecursionError, OSError) as e:
                    logger.warning(f"跳過目錄 {search_dir}: {e}")
                    continue

    except Exception as e:
        logger.warning(f"查找快取目錄時出錯: {e}")
        logger.info("跳過快取清理")
        return

    if not cache_dirs:
        logger.info("無需清理快取檔案")
        return

    if not force_clean:
        # 可選清理：只清理專案程式碼的快取，不清理虛擬環境
        project_cache_dirs = [d for d in cache_dirs if 'env' not in str(d)]
        if project_cache_dirs:
            logger.info("清理專案快取檔案...")
            for cache_dir in project_cache_dirs:
                try:
                    shutil.rmtree(cache_dir)
                    logger.info(f"已清理: {cache_dir.relative_to(project_root)}")
                except Exception as e:
                    logger.error(f"清理失敗: {cache_dir.relative_to(project_root)} - {e}")
            logger.info("專案快取清理完成")
        else:
            logger.info("無需清理專案快取")
    else:
        # 強制清理：清理所有快取
        logger.info("強制清理所有快取檔案...")
        for cache_dir in cache_dirs:
            try:
                import shutil
                shutil.rmtree(cache_dir)
                logger.info(f"已清理: {cache_dir.relative_to(project_root)}")
            except Exception as e:
                logger.error(f"清理失敗: {cache_dir.relative_to(project_root)} - {e}")
        logger.info("所有快取清理完成")

def check_api_keys():
    """檢查API密鑰配置"""
    
    from dotenv import load_dotenv
    
    # 載入環境變數
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
    
    # 檢查至少一個 LLM 提供商的 API 密鑰已配置
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")

    llm_configured = openai_key or anthropic_key

    if not llm_configured:
        logger.warning("未檢測到任何 LLM 提供商的 API 密鑰")
        logger.info("請確保在.env 檔案中至少配置以下其中一個密鑰:")
        logger.info("- OPENAI_API_KEY (OpenAI GPT 模型)")
        logger.info("- ANTHROPIC_API_KEY (Anthropic Claude 模型)")
        logger.info("\n配置方法:")
        logger.info("1. 複製 .env.example 為 .env")
        logger.info("2. 編輯 .env 檔案，填入真實API密鑰")
        return False

    if not finnhub_key:
        logger.warning("FINNHUB_API_KEY 未設定，部分美股資料功能可能受限")

    logger.info("API密鑰配置完成")
    return True

def main():
    """主函式"""
    
    logger.info("TradingAgents-CN Web應用啟動器")
    logger.info("=")
    
    # 清理快取檔案（可選，避免Streamlit檔案監控錯誤）
    clean_cache_files(force_clean=False)
    
    # 檢查依賴
    logger.debug("檢查依賴套件...")
    if not check_dependencies():
        return
    
    # 檢查API密鑰
    logger.info("檢查API密鑰...")
    if not check_api_keys():
        logger.info("\n 提示: 您仍可以啟動Web應用查看介面，但無法進行實際分析")
        response = input("是否繼續啟動? (y/n): ").lower().strip()
        if response != 'y':
            return
    
    # 啟動Streamlit應用
    logger.info("\n 啟動Web應用...")
    
    web_dir = Path(__file__).parent
    app_file = web_dir / "app.py"
    
    if not app_file.exists():
        logger.error(f"找不到應用檔案: {app_file}")
        return
    
    # 構建Streamlit命令
    config_dir = web_dir.parent / ".streamlit"
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_file),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false",
        "--server.fileWatcherType", "none",
        "--server.runOnSave", "false"
    ]
    
    # 如果配置目錄存在，新增配置路徑
    if config_dir.exists():
        logger.info(f"使用配置目錄: {config_dir}")
        # Streamlit會自動查找.streamlit/config.toml 檔案
    
    logger.info(f"執行命令: {' '.join(cmd)}")
    logger.info("\n Web應用啟動中...")
    logger.info("瀏覽器將自動開啟 http://localhost:8501")
    logger.info("按 Ctrl+C 停止應用")
    logger.info("=")
    
    # 建立行程物件而不是直接執行
    process = None
    
    def signal_handler(signum, frame):
        """訊號處理函式"""
        logger.info("\n\n 接收到停止訊號，正在關閉Web應用...")
        if process:
            try:
                # 終止行程及其子行程
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                
                # 等待行程結束
                parent.wait(timeout=5)
                logger.info("Web應用已成功停止")
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                logger.warning("強制終止行程")
                if process:
                    process.kill()
        sys.exit(0)
    
    # 註冊訊號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 啟動 Streamlit 行程（從專案根目錄執行，確保讀取 .streamlit/config.toml）
        process = subprocess.Popen(cmd, cwd=web_dir.parent)
        process.wait() # 等待行程結束
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"\n 啟動失敗: {e}")

if __name__ == "__main__":
    # 檢查命令列參數
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-clean":
            os.environ['SKIP_CACHE_CLEAN'] = 'true'
            logger.info("啟動模式: 跳過快取清理")
        elif sys.argv[1] == "--force-clean":
            # 強制清理所有快取
            logger.info("啟動模式: 強制清理所有快取")
            clean_cache_files(force_clean=True)
        elif sys.argv[1] == "--help":
            logger.info("TradingAgents-CN Web應用啟動器")
            logger.info("=")
            logger.info("用法:")
            logger.info("python run_web.py # 預設啟動（清理專案快取）")
            logger.info("python run_web.py --no-clean # 跳過快取清理")
            logger.info("python run_web.py --force-clean # 強制清理所有快取")
            logger.info("python run_web.py --help # 顯示幫助")
            logger.info("\n環境變數:")
            logger.info("SKIP_CACHE_CLEAN=true # 跳過快取清理")
            exit(0)

    main()
