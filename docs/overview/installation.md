# 詳細安裝指南

## 概述

本指南提供了 TradingAgents 框架的詳細安裝說明，包括不同操作系統的安裝步驟、依賴管理、環境配置和常見問題解決方案。

## 系統要求

### 硬件要求
- **CPU**: 雙核 2.0GHz 或更高 (推薦四核)
- **內存**: 最少 4GB RAM (推薦 8GB 或更高)
- **存儲**: 至少 5GB 可用磁盤空間
- **網絡**: 穩定的互聯網連接 (用於API調用和數據獲取)

### 軟體要求
- **操作系統**: 
  - Windows 10/11 (64位)
  - macOS 10.15 (Catalina) 或更高版本
  - Linux (Ubuntu 18.04+, CentOS 7+, 或其他主流發行版)
- **Python**: 3.10, 3.11, 或 3.12 (推薦 3.11)
- **Git**: 用於克隆代碼倉庫

## 安裝步驟

### 1. 安裝 Python

#### Windows
```powershell
# 方法1: 從官網下載安裝包
# 訪問 https://www.python.org/downloads/windows/
# 下載 Python 3.11.x 安裝包並運行

# 方法2: 使用 Chocolatey
choco install python311

# 方法3: 使用 Microsoft Store
# 在 Microsoft Store 搜索 "Python 3.11" 並安裝

# 驗證安裝
python --version
pip --version
```

#### macOS
```bash
# 方法1: 使用 Homebrew (推薦)
brew install python@3.11

# 方法2: 使用 pyenv
brew install pyenv
pyenv install 3.11.7
pyenv global 3.11.7

# 方法3: 從官網下載
# 訪問 https://www.python.org/downloads/macos/

# 驗證安裝
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)
```bash
# 更新包列表
sudo apt update

# 安裝 Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv

# 設置默認 Python 版本 (可選)
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# 驗證安裝
python3 --version
pip3 --version
```

#### Linux (CentOS/RHEL)
```bash
# 安裝 EPEL 倉庫
sudo yum install epel-release

# 安裝 Python 3.11
sudo yum install python311 python311-pip

# 或使用 dnf (較新版本)
sudo dnf install python3.11 python3.11-pip

# 驗證安裝
python3.11 --version
pip3.11 --version
```

### 2. 克隆項目

```bash
# 克隆項目倉庫
git clone https://github.com/TauricResearch/TradingAgents.git

# 進入項目目錄
cd TradingAgents

# 查看項目結構
ls -la
```

### 3. 創建虛擬環境

#### 使用 venv (推薦)
```bash
# Windows
python -m venv tradingagents
tradingagents\Scripts\activate

# macOS/Linux
python3 -m venv tradingagents
source tradingagents/bin/activate

# 驗證虛擬環境
which python  # 應該指向虛擬環境中的 Python
```

#### 使用 conda
```bash
# 創建環境
conda create -n tradingagents python=3.11

# 激活環境
conda activate tradingagents

# 驗證環境
conda info --envs
```

#### 使用 pipenv
```bash
# 安裝 pipenv
pip install pipenv

# 創建環境並安裝依賴
pipenv install

# 激活環境
pipenv shell
```

### 4. 安裝依賴

#### 基礎安裝
```bash
# 升級 pip
pip install --upgrade pip

# 安裝項目依賴
pip install -r requirements.txt

# 驗證安裝
pip list | grep langchain
pip list | grep tradingagents
```

#### 開發環境安裝
```bash
# 安裝開發依賴 (如果有 requirements-dev.txt)
pip install -r requirements-dev.txt

# 或安裝可編辑模式
pip install -e .

# 安裝額外的開發工具
pip install pytest black flake8 mypy jupyter
```

#### 可選依賴
```bash
# Redis 支持 (用於高級緩存)
pip install redis

# 數據庫支持
pip install sqlalchemy psycopg2-binary

# 可視化支持
pip install matplotlib seaborn plotly

# Jupyter 支持
pip install jupyter ipykernel
python -m ipykernel install --user --name=tradingagents
```

### 5. 配置 API 密鑰

#### 獲取 API 密鑰

**OpenAI API**
1. 訪問 [OpenAI Platform](https://platform.openai.com/)
2. 註冊帳戶並登錄
3. 導航到 API Keys 頁面
4. 創建新的 API 密鑰
5. 複制密鑰 (註意: 只顯示一次)

**FinnHub API**
1. 訪問 [FinnHub](https://finnhub.io/)
2. 註冊免費帳戶
3. 在儀表板中找到 API 密鑰
4. 複制密鑰

**其他可選 API**
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)

#### 設置環境變量

**Windows (PowerShell)**
```powershell
# 臨時設置 (當前會話)
$env:OPENAI_API_KEY="your_openai_api_key"
$env:FINNHUB_API_KEY="your_finnhub_api_key"

# 永久設置 (系統環境變量)
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_openai_api_key", "User")
[Environment]::SetEnvironmentVariable("FINNHUB_API_KEY", "your_finnhub_api_key", "User")
```

**Windows (Command Prompt)**
```cmd
# 臨時設置
set OPENAI_API_KEY=your_openai_api_key
set FINNHUB_API_KEY=your_finnhub_api_key

# 永久設置 (需要重啟)
setx OPENAI_API_KEY "your_openai_api_key"
setx FINNHUB_API_KEY "your_finnhub_api_key"
```

**macOS/Linux**
```bash
# 臨時設置 (當前會話)
export OPENAI_API_KEY="your_openai_api_key"
export FINNHUB_API_KEY="your_finnhub_api_key"

# 永久設置 (添加到 ~/.bashrc 或 ~/.zshrc)
echo 'export OPENAI_API_KEY="your_openai_api_key"' >> ~/.bashrc
echo 'export FINNHUB_API_KEY="your_finnhub_api_key"' >> ~/.bashrc
source ~/.bashrc
```

#### 使用 .env 文件 (推薦)
```bash
# 創建 .env 文件
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key
FINNHUB_API_KEY=your_finnhub_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
TRADINGAGENTS_RESULTS_DIR=./results
TRADINGAGENTS_LOG_LEVEL=INFO
EOF

# 安裝 python-dotenv (如果未安裝)
pip install python-dotenv
```

### 6. 驗證安裝

#### 基本驗證
```bash
# 檢查 Python 版本
python --version

# 檢查已安裝的包
pip list | grep -E "(langchain|tradingagents|openai|finnhub)"

# 檢查環境變量
python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('FinnHub:', bool(os.getenv('FINNHUB_API_KEY')))"
```

#### 功能驗證
```python
# test_installation.py
import sys
import os

def test_installation():
    """測試安裝是否成功"""
    
    print("=== TradingAgents 安裝驗證 ===\n")
    
    # 1. Python 版本檢查
    print(f"Python 版本: {sys.version}")
    if sys.version_info < (3, 10):
        print("❌ Python 版本過低，需要 3.10 或更高版本")
        return False
    else:
        print("✅ Python 版本符合要求")
    
    # 2. 依賴包檢查
    required_packages = [
        'langchain_openai',
        'langgraph',
        'finnhub',
        'pandas',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} 已安裝")
        except ImportError:
            print(f"❌ {package} 未安裝")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n缺少依賴包: {missing_packages}")
        return False
    
    # 3. API 密鑰檢查
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'FINNHUB_API_KEY': os.getenv('FINNHUB_API_KEY')
    }
    
    for key_name, key_value in api_keys.items():
        if key_value:
            print(f"✅ {key_name} 已設置")
        else:
            print(f"❌ {key_name} 未設置")
    
    # 4. TradingAgents 導入測試
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG
        print("✅ TradingAgents 核心模塊導入成功")
    except ImportError as e:
        print(f"❌ TradingAgents 導入失敗: {e}")
        return False
    
    print("\n🎉 安裝驗證完成!")
    return True

if __name__ == "__main__":
    success = test_installation()
    sys.exit(0 if success else 1)
```

運行驗證腳本:
```bash
python test_installation.py
```

## 常見問題解決

### 1. Python 版本問題
```bash
# 問題: python 命令找不到或版本錯誤
# 解決方案:

# Windows: 使用 py 啟動器
py -3.11 --version

# macOS/Linux: 使用具體版本
python3.11 --version

# 創建別名 (Linux/macOS)
alias python=python3.11
```

### 2. 權限問題
```bash
# 問題: pip 安裝時權限被拒絕
# 解決方案:

# 使用用戶安裝
pip install --user -r requirements.txt

# 或使用虛擬環境 (推薦)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows
```

### 3. 網路連線問題
```bash
# 問題: pip 安裝超時或連線失敗
# 解決方案:

# 增加超時時間
pip install -r requirements.txt --timeout 120

# 使用鎖定版本安裝（速度更快，無需依賴解析）
pip install -r requirements-lock.txt
```

### 4. 依賴衝突問題
```bash
# 問題: 包版本衝突
# 解決方案:

# 清理環境重新安裝
pip freeze > installed_packages.txt
pip uninstall -r installed_packages.txt -y
pip install -r requirements.txt

# 或使用新的虛擬環境
deactivate
rm -rf tradingagents  # 刪除舊環境
python -m venv tradingagents
source tradingagents/bin/activate
pip install -r requirements.txt
```

### 5. API 密鑰問題
```bash
# 問題: API 密鑰無效或未設置
# 解決方案:

# 檢查密鑰格式
echo $OPENAI_API_KEY | wc -c  # 應該是 51 字符 (sk-...)

# 重新設置密鑰
unset OPENAI_API_KEY
export OPENAI_API_KEY="your_correct_api_key"

# 測試 API 連接
python -c "
import openai
import os
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('API 連接測試成功')
"
```

## 高級安裝選項

### 1. Docker 安裝
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["python", "-m", "cli.main"]
```

```bash
# 構建鏡像
docker build -t tradingagents .

# 運行容器
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -e FINNHUB_API_KEY=$FINNHUB_API_KEY tradingagents
```

### 2. 開發環境設置
```bash
# 安裝開發工具
pip install pre-commit black isort flake8 mypy pytest

# 設置 pre-commit hooks
pre-commit install

# 配置 IDE (VS Code)
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
```

### 3. 性能優化
```bash
# 安裝加速庫
pip install numpy scipy numba

# GPU 支持 (如果需要)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 卸載指南

### 完全卸載
```bash
# 停用虛擬環境
deactivate

# 刪除虛擬環境
rm -rf tradingagents  # Linux/macOS
rmdir /s tradingagents  # Windows

# 刪除項目文件
cd ..
rm -rf TradingAgents

# 清理環境變量 (可選)
unset OPENAI_API_KEY
unset FINNHUB_API_KEY
```

安裝完成後，您可以繼續閱讀 [快速開始指南](quick-start.md) 來開始使用 TradingAgents。
