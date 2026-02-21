# 

## 

 TradingAgents 

## 

### 
- **CPU**: 2.0GHz ()
- ****: 4GB RAM ( 8GB )
- ****: 5GB 
- ****: (API)

### 
- ****: 
 - Windows 10/11 (64)
 - macOS 10.15 (Catalina) 
 - Linux (Ubuntu 18.04+, CentOS 7+, )
- **Python**: 3.10, 3.11, 3.12 ( 3.11)
- **Git**: 

## 

### 1. Python

#### Windows
```powershell
# 1: 
# https://www.python.org/downloads/windows/
# Python 3.11.x 

# 2: Chocolatey
choco install python311

# 3: Microsoft Store
# Microsoft Store "Python 3.11" 

# 
python --version
pip --version
```

#### macOS
```bash
# 1: Homebrew ()
brew install python@3.11

# 2: pyenv
brew install pyenv
pyenv install 3.11.7
pyenv global 3.11.7

# 3: 
# https://www.python.org/downloads/macos/

# 
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)
```bash
# 
sudo apt update

# Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv

# Python ()
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# 
python3 --version
pip3 --version
```

#### Linux (CentOS/RHEL)
```bash
# EPEL 
sudo yum install epel-release

# Python 3.11
sudo yum install python311 python311-pip

# dnf ()
sudo dnf install python3.11 python3.11-pip

# 
python3.11 --version
pip3.11 --version
```

### 2. 

```bash
# 
git clone https://github.com/TauricResearch/TradingAgents.git

# 
cd TradingAgents

# 
ls -la
```

### 3. 

#### venv ()
```bash
# Windows
python -m venv tradingagents
tradingagents\Scripts\activate

# macOS/Linux
python3 -m venv tradingagents
source tradingagents/bin/activate

# 
which python # Python
```

#### conda
```bash
# 
conda create -n tradingagents python=3.11

# 
conda activate tradingagents

# 
conda info --envs
```

#### pipenv
```bash
# pipenv
pip install pipenv

# 
pipenv install

# 
pipenv shell
```

### 4. 

#### 
```bash
# pip
pip install --upgrade pip

# 
pip install -r requirements.txt

# 
pip list | grep langchain
pip list | grep tradingagents
```

#### 
```bash
# ( requirements-dev.txt)
pip install -r requirements-dev.txt

# 
pip install -e .

# 
pip install pytest black flake8 mypy jupyter
```

#### 
```bash
# Redis ()
pip install redis

# 
pip install sqlalchemy psycopg2-binary

# 
pip install matplotlib seaborn plotly

# Jupyter 
pip install jupyter ipykernel
python -m ipykernel install --user --name=tradingagents
```

### 5. API 

#### API 

**OpenAI API**
1. [OpenAI Platform](https://platform.openai.com/)
2. 
3. API Keys 
4. API 
5. (: )

**FinnHub API**
1. [FinnHub](https://finnhub.io/)
2. 
3. API 
4. 

** API**
- **Anthropic**: [console.anthropic.com](https://console.anthropic.com/)

#### 

**Windows (PowerShell)**
```powershell
# ()
$env:OPENAI_API_KEY="your_openai_api_key"
$env:FINNHUB_API_KEY="your_finnhub_api_key"

# ()
[Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "your_openai_api_key", "User")
[Environment]::SetEnvironmentVariable("FINNHUB_API_KEY", "your_finnhub_api_key", "User")
```

**Windows (Command Prompt)**
```cmd
# 
set OPENAI_API_KEY=your_openai_api_key
set FINNHUB_API_KEY=your_finnhub_api_key

# ()
setx OPENAI_API_KEY "your_openai_api_key"
setx FINNHUB_API_KEY "your_finnhub_api_key"
```

**macOS/Linux**
```bash
# ()
export OPENAI_API_KEY="your_openai_api_key"
export FINNHUB_API_KEY="your_finnhub_api_key"

# ( ~/.bashrc ~/.zshrc)
echo 'export OPENAI_API_KEY="your_openai_api_key"' >> ~/.bashrc
echo 'export FINNHUB_API_KEY="your_finnhub_api_key"' >> ~/.bashrc
source ~/.bashrc
```

#### .env ()
```bash
# .env 
cat > .env << EOF
OPENAI_API_KEY=your_openai_api_key
FINNHUB_API_KEY=your_finnhub_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
TRADINGAGENTS_RESULTS_DIR=./results
TRADINGAGENTS_LOG_LEVEL=INFO
EOF

# python-dotenv ()
pip install python-dotenv
```

### 6. 

#### 
```bash
# Python 
python --version

# 
pip list | grep -E "(langchain|tradingagents|openai|finnhub)"

# 
python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('FinnHub:', bool(os.getenv('FINNHUB_API_KEY')))"
```

#### 
```python
# test_installation.py
import sys
import os

def test_installation():
 """"""
 
 print("=== TradingAgents ===\n")
 
 # 1. Python 
 print(f"Python : {sys.version}")
 if sys.version_info < (3, 10):
 print(" Python 3.10 ")
 return False
 else:
 print(" Python ")
 
 # 2. 
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
 print(f" {package} ")
 except ImportError:
 print(f" {package} ")
 missing_packages.append(package)
 
 if missing_packages:
 print(f"\n: {missing_packages}")
 return False
 
 # 3. API 
 api_keys = {
 'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
 'FINNHUB_API_KEY': os.getenv('FINNHUB_API_KEY')
 }
 
 for key_name, key_value in api_keys.items():
 if key_value:
 print(f" {key_name} ")
 else:
 print(f" {key_name} ")
 
 # 4. TradingAgents 
 try:
 from tradingagents.graph.trading_graph import TradingAgentsGraph
 from tradingagents.default_config import DEFAULT_CONFIG
 print(" TradingAgents ")
 except ImportError as e:
 print(f" TradingAgents : {e}")
 return False
 
 print("\n !")
 return True

if __name__ == "__main__":
 success = test_installation()
 sys.exit(0 if success else 1)
```

:
```bash
python test_installation.py
```

## 

### 1. Python 
```bash
# : python 
# :

# Windows: py 
py -3.11 --version

# macOS/Linux: 
python3.11 --version

# (Linux/macOS)
alias python=python3.11
```

### 2. 
```bash
# : pip 
# :

# 
pip install --user -r requirements.txt

# ()
python -m venv venv
source venv/bin/activate # Linux/macOS
# venv\Scripts\activate # Windows
```

### 3. 
```bash
# : pip 
# :

# 
pip install -r requirements.txt --timeout 120

# 
pip install -r requirements-lock.txt
```

### 4. 
```bash
# : 
# :

# 
pip freeze > installed_packages.txt
pip uninstall -r installed_packages.txt -y
pip install -r requirements.txt

# 
deactivate
rm -rf tradingagents # 
python -m venv tradingagents
source tradingagents/bin/activate
pip install -r requirements.txt
```

### 5. API 
```bash
# : API 
# :

# 
echo $OPENAI_API_KEY | wc -c # 51 (sk-...)

# 
unset OPENAI_API_KEY
export OPENAI_API_KEY="your_correct_api_key"

# API 
python -c "
import openai
import os
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('API ')
"
```

## 

### 1. Docker 
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
# 
docker build -t tradingagents .

# 
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -e FINNHUB_API_KEY=$FINNHUB_API_KEY tradingagents
```

### 2. 
```bash
# 
pip install pre-commit black isort flake8 mypy pytest

# pre-commit hooks
pre-commit install

# IDE (VS Code)
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
```

### 3. 
```bash
# 
pip install numpy scipy numba

# GPU ()
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

## 

### 
```bash
# 
deactivate

# 
rm -rf tradingagents # Linux/macOS
rmdir /s tradingagents # Windows

# 
cd ..
rm -rf TradingAgents

# ()
unset OPENAI_API_KEY
unset FINNHUB_API_KEY
```

 [](quick-start.md) TradingAgents
