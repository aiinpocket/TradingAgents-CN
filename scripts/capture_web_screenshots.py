#!/usr/bin/env python3
"""
Web界面截圖捕獲腳本
用於自動化捕獲TradingAgents-CN Web界面的截圖
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.utils.logging_manager import get_logger
logger = get_logger('screenshot')

def check_dependencies():
    """檢查截圖所需的依賴"""
    try:
        import selenium
        from selenium import webdriver
        logger.info(" Selenium已安裝")
        return True
    except ImportError:
        logger.error(" 缺少Selenium依賴")
        logger.info(" 安裝命令: pip install selenium")
        return False

def check_web_service():
    """檢查Web服務是否運行"""
    try:
        import requests
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            logger.info(" Web服務正在運行")
            return True
        else:
            logger.warning(f" Web服務響應異常: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f" 無法連接到Web服務: {e}")
        return False

def start_web_service():
    """啟動Web服務"""
    logger.info(" 正在啟動Web服務...")
    
    # 檢查是否有Docker環境
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(" 檢測到Docker環境，嘗試啟動Docker服務...")
            subprocess.run(["docker-compose", "up", "-d"], cwd=project_root)
            time.sleep(10)  # 等待服務啟動
            return check_web_service()
    except FileNotFoundError:
        pass
    
    # 嘗試本地啟動
    logger.info(" 嘗試本地啟動Web服務...")
    try:
        # 啟動Web服務（後台運行）
        subprocess.Popen([
            sys.executable, "start_web.py"
        ], cwd=project_root)
        
        # 等待服務啟動
        for i in range(30):
            time.sleep(2)
            if check_web_service():
                return True
            logger.info(f" 等待服務啟動... ({i+1}/30)")
        
        logger.error(" Web服務啟動超時")
        return False
        
    except Exception as e:
        logger.error(f" 啟動Web服務失敗: {e}")
        return False

def capture_screenshots():
    """捕獲Web界面截圖"""
    if not check_dependencies():
        return False
    
    if not check_web_service():
        logger.info(" Web服務未運行，嘗試啟動...")
        if not start_web_service():
            return False
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        
        # 配置Chrome選項
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 無頭模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # 創建WebDriver
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # 訪問Web界面
            logger.info(" 正在訪問Web界面...")
            driver.get("http://localhost:8501")
            
            # 等待頁面載入
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 等待Streamlit完全載入
            time.sleep(5)
            
            # 創建截圖目錄
            screenshots_dir = project_root / "docs" / "images"
            screenshots_dir.mkdir(exist_ok=True)
            
            # 截圖1: 主界面
            logger.info(" 捕獲主界面截圖...")
            driver.save_screenshot(str(screenshots_dir / "web-interface-main.png"))
            
            # 模擬輸入股票代碼
            try:
                stock_input = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
                stock_input.clear()
                stock_input.send_keys("AAPL")
                time.sleep(2)
            except Exception:
                logger.warning(" 無法找到股票輸入框")
            
            # 截圖2: 配置界面
            logger.info(" 捕獲配置界面截圖...")
            driver.save_screenshot(str(screenshots_dir / "web-interface-config.png"))
            
            # 嘗試點擊分析按鈕（如果存在）
            try:
                analyze_button = driver.find_element(By.XPATH, "//button[contains(text(), '開始分析')]")
                analyze_button.click()
                time.sleep(3)
                
                # 截圖3: 進度界面
                logger.info(" 捕獲進度界面截圖...")
                driver.save_screenshot(str(screenshots_dir / "web-interface-progress.png"))
                
            except Exception:
                logger.warning(" 無法找到分析按鈕或觸發分析")
            
            # 截圖4: 側邊欄
            logger.info(" 捕獲側邊欄截圖...")
            driver.save_screenshot(str(screenshots_dir / "web-interface-sidebar.png"))
            
            logger.info(" 截圖捕獲完成")
            return True
            
        finally:
            driver.quit()
            
    except Exception as e:
        logger.error(f" 截圖捕獲失敗: {e}")
        return False

def create_screenshot_guide():
    """創建截圖指南"""
    guide_content = f"""#  Web界面截圖捕獲指南

##  自動截圖

運行自動截圖腳本:
```bash
python scripts/capture_web_screenshots.py
```

##  手動截圖步驟

### 1. 啟動Web服務
```bash
# 方法1: 本地啟動
python start_web.py

# 方法2: Docker啟動  
docker-compose up -d
```

### 2. 訪問界面
打開瀏覽器訪問: http://localhost:8501

### 3. 捕獲截圖
按照以下場景進行截圖:

####  主界面 (web-interface-main.png)
- 顯示完整的分析配置表單
- 輸入示例股票代碼: AAPL 或 MSFT
- 選擇標準分析深度 (3級)

####  分析進度 (web-interface-progress.png)  
- 開始分析後的進度顯示
- 顯示進度條和預計時間
- 顯示已完成的分析步驟

####  分析結果 (web-interface-results.png)
- 完整的分析報告展示
- 投資建議和風險評估
- 導出按鈕區域

####  模型配置 (web-interface-models.png)
- 側邊欄的模型配置界面
- LLM提供商選擇
- 快速選擇按鈕

##  截圖規範

- **分辨率**: 1920x1080 或更高
- **格式**: PNG格式
- **質量**: 高清，文字清晰
- **內容**: 完整功能區域，真實數據

##  故障排除

### Chrome驅動問題
```bash
# 安裝ChromeDriver
# Windows: choco install chromedriver
# Mac: brew install chromedriver  
# Linux: apt-get install chromium-chromedriver
```

### Selenium安裝
```bash
pip install selenium
```

---
生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    guide_path = project_root / "docs" / "images" / "screenshot-guide.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    logger.info(f" 截圖指南已創建: {guide_path}")

def main():
    """主函數"""
    logger.info(" TradingAgents-CN Web界面截圖捕獲工具")
    logger.info("=" * 50)
    
    # 創建截圖指南
    create_screenshot_guide()
    
    # 詢問用戶是否要自動捕獲截圖
    try:
        choice = input("\n是否要自動捕獲Web界面截圖? (y/n): ").lower().strip()
        if choice in ['y', 'yes', '是']:
            if capture_screenshots():
                logger.info(" 截圖捕獲成功完成!")
                logger.info(" 截圖保存位置: docs/images/")
            else:
                logger.error(" 截圖捕獲失敗")
                logger.info(" 請參考手動截圖指南: docs/images/screenshot-guide.md")
        else:
            logger.info(" 請參考手動截圖指南: docs/images/screenshot-guide.md")
    except KeyboardInterrupt:
        logger.info("\n 用戶取消操作")

if __name__ == "__main__":
    main()
