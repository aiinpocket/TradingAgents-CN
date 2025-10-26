#!/usr/bin/env python3
"""
TradingAgents-CN Web應用啟動腳本
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')

def check_dependencies():
    """檢查必要的依賴是否已安裝"""

    required_packages = ['streamlit', 'plotly']
    missing_packages = []

    for package in required_packages:
        try:
            if package == 'streamlit':
                import streamlit
            elif package == 'plotly':
                import plotly
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        logger.error(f"❌ 缺少必要的依賴包: {', '.join(missing_packages)}")
        logger.info(f"請運行以下命令安裝:")
        logger.info(f"pip install {' '.join(missing_packages)}")
        return False

    logger.info(f"✅ 依賴包檢查通過")
    return True

def clean_cache_files(force_clean=False):
    """
    清理Python緩存文件，避免Streamlit文件監控錯誤

    Args:
        force_clean: 是否强制清理，默認False（可選清理）
    """

    project_root = Path(__file__).parent.parent

    # 安全的緩存目錄搜索，避免遞歸錯誤
    cache_dirs = []
    try:
        # 限制搜索深度，避免循環符號鏈接問題
        for root, dirs, files in os.walk(project_root):
            # 限制搜索深度為5層，避免過深遞歸
            depth = root.replace(str(project_root), '').count(os.sep)
            if depth >= 5:
                dirs[:] = []  # 不再深入搜索
                continue

            # 跳過已知的問題目錄
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', '.venv', 'env', '.tox'}]

            if '__pycache__' in dirs:
                cache_dirs.append(Path(root) / '__pycache__')

    except (OSError, RecursionError) as e:
        logger.warning(f"⚠️ 緩存搜索遇到問題: {e}")
        logger.info(f"💡 跳過緩存清理，繼续啟動應用")

    if not cache_dirs:
        logger.info(f"✅ 無需清理緩存文件")
        return

    # 檢查環境變量是否禁用清理（使用强健的布爾值解析）
    try:
        from tradingagents.config.env_utils import parse_bool_env
        skip_clean = parse_bool_env('SKIP_CACHE_CLEAN', False)
    except ImportError:
        # 回退到原始方法
        skip_clean = os.getenv('SKIP_CACHE_CLEAN', 'false').lower() == 'true'

    if skip_clean and not force_clean:
        logger.info(f"⏭️ 跳過緩存清理（SKIP_CACHE_CLEAN=true）")
        return

    project_root = Path(__file__).parent.parent

    # 安全地查找緩存目錄，避免遞歸深度問題
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
                            dirs.clear()  # 不再深入搜索
                            continue

                        if Path(root).name == "__pycache__":
                            cache_dirs.append(Path(root))

                except (RecursionError, OSError) as e:
                    logger.warning(f"跳過目錄 {search_dir}: {e}")
                    continue

    except Exception as e:
        logger.warning(f"查找緩存目錄時出錯: {e}")
        logger.info(f"✅ 跳過緩存清理")
        return

    if not cache_dirs:
        logger.info(f"✅ 無需清理緩存文件")
        return

    if not force_clean:
        # 可選清理：只清理項目代碼的緩存，不清理虛擬環境
        project_cache_dirs = [d for d in cache_dirs if 'env' not in str(d)]
        if project_cache_dirs:
            logger.info(f"🧹 清理項目緩存文件...")
            for cache_dir in project_cache_dirs:
                try:
                    import shutil
                    shutil.rmtree(cache_dir)
                    logger.info(f"  ✅ 已清理: {cache_dir.relative_to(project_root)}")
                except Exception as e:
                    logger.error(f"  ⚠️ 清理失败: {cache_dir.relative_to(project_root)} - {e}")
            logger.info(f"✅ 項目緩存清理完成")
        else:
            logger.info(f"✅ 無需清理項目緩存")
    else:
        # 强制清理：清理所有緩存
        logger.info(f"🧹 强制清理所有緩存文件...")
        for cache_dir in cache_dirs:
            try:
                import shutil
                shutil.rmtree(cache_dir)
                logger.info(f"  ✅ 已清理: {cache_dir.relative_to(project_root)}")
            except Exception as e:
                logger.error(f"  ⚠️ 清理失败: {cache_dir.relative_to(project_root)} - {e}")
        logger.info(f"✅ 所有緩存清理完成")

def check_api_keys():
    """檢查API密鑰配置"""
    
    from dotenv import load_dotenv
    
    # 加載環境變量
    project_root = Path(__file__).parent.parent
    load_dotenv(project_root / ".env")
    
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    
    if not dashscope_key or not finnhub_key:
        logger.warning(f"⚠️ API密鑰配置不完整")
        logger.info(f"請確保在.env文件中配置以下密鑰:")
        if not dashscope_key:
            logger.info(f"  - DASHSCOPE_API_KEY (阿里百炼)")
        if not finnhub_key:
            logger.info(f"  - FINNHUB_API_KEY (金融數據)")
        logger.info(f"\n配置方法:")
        logger.info(f"1. 複制 .env.example 為 .env")
        logger.info(f"2. 編辑 .env 文件，填入真實API密鑰")
        return False
    
    logger.info(f"✅ API密鑰配置完成")
    return True

# 在文件顶部添加導入
import signal
import psutil

# 修改 main() 函數中的啟動部分
def main():
    """主函數"""
    
    logger.info(f"🚀 TradingAgents-CN Web應用啟動器")
    logger.info(f"=")
    
    # 清理緩存文件（可選，避免Streamlit文件監控錯誤）
    clean_cache_files(force_clean=False)
    
    # 檢查依賴
    logger.debug(f"🔍 檢查依賴包...")
    if not check_dependencies():
        return
    
    # 檢查API密鑰
    logger.info(f"🔑 檢查API密鑰...")
    if not check_api_keys():
        logger.info(f"\n💡 提示: 您仍可以啟動Web應用查看界面，但無法進行實际分析")
        response = input("是否繼续啟動? (y/n): ").lower().strip()
        if response != 'y':
            return
    
    # 啟動Streamlit應用
    logger.info(f"\n🌐 啟動Web應用...")
    
    web_dir = Path(__file__).parent
    app_file = web_dir / "app.py"
    
    if not app_file.exists():
        logger.error(f"❌ 找不到應用文件: {app_file}")
        return
    
    # 構建Streamlit命令
    config_dir = web_dir.parent / ".streamlit"
    cmd = [
        sys.executable, "-m", "streamlit", "run", 
        str(app_file),
        "--server.port", "8501",
        "--server.address", "localhost",
        "--browser.gatherUsageStats", "false",
        "--server.fileWatcherType", "auto",
        "--server.runOnSave", "true"
    ]
    
    # 如果配置目錄存在，添加配置路徑
    if config_dir.exists():
        logger.info(f"📁 使用配置目錄: {config_dir}")
        # Streamlit會自動查找.streamlit/config.toml文件
    
    logger.info(f"執行命令: {' '.join(cmd)}")
    logger.info(f"\n🎉 Web應用啟動中...")
    logger.info(f"📱 浏覽器将自動打開 http://localhost:8501")
    logger.info(f"⏹️  按 Ctrl+C 停止應用")
    logger.info(f"=")
    
    # 創建進程對象而不是直接運行
    process = None
    
    def signal_handler(signum, frame):
        """信號處理函數"""
        logger.info(f"\n\n⏹️ 接收到停止信號，正在關闭Web應用...")
        if process:
            try:
                # 终止進程及其子進程
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    child.terminate()
                parent.terminate()
                
                # 等待進程結束
                parent.wait(timeout=5)
                logger.info(f"✅ Web應用已成功停止")
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                logger.warning(f"⚠️ 强制终止進程")
                if process:
                    process.kill()
        sys.exit(0)
    
    # 註冊信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 啟動Streamlit進程
        process = subprocess.Popen(cmd, cwd=web_dir)
        process.wait()  # 等待進程結束
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    except Exception as e:
        logger.error(f"\n❌ 啟動失败: {e}")

if __name__ == "__main__":
    import sys

    # 檢查命令行參數
    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-clean":
            # 設置環境變量跳過清理
            import os
            os.environ['SKIP_CACHE_CLEAN'] = 'true'
            logger.info(f"🚀 啟動模式: 跳過緩存清理")
        elif sys.argv[1] == "--force-clean":
            # 强制清理所有緩存
            logger.info(f"🚀 啟動模式: 强制清理所有緩存")
            clean_cache_files(force_clean=True)
        elif sys.argv[1] == "--help":
            logger.info(f"🚀 TradingAgents-CN Web應用啟動器")
            logger.info(f"=")
            logger.info(f"用法:")
            logger.info(f"  python run_web.py           # 默認啟動（清理項目緩存）")
            logger.info(f"  python run_web.py --no-clean      # 跳過緩存清理")
            logger.info(f"  python run_web.py --force-clean   # 强制清理所有緩存")
            logger.info(f"  python run_web.py --help          # 顯示幫助")
            logger.info(f"\n環境變量:")
            logger.info(f"  SKIP_CACHE_CLEAN=true       # 跳過緩存清理")
            exit(0)

    main()
