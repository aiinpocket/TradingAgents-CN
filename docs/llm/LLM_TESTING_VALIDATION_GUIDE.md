# LLM 

## 

 LLM TradingAgents 

## 

### 1. 
 LLM API

### 2. 
 function calling TradingAgents 

### 3. Web 
 LLM 

### 4. 
 LLM 

## 

### API 

1. ****
 ```bash
 cp .env.example .env
 ```

2. ** API **
 ```bash
 # .env 
 YOUR_PROVIDER_API_KEY=your_actual_api_key_here
 ```

3. ****
 ```python
 import os
 from dotenv import load_dotenv
 
 load_dotenv()
 api_key = os.getenv("YOUR_PROVIDER_API_KEY")
 print(f"API Key : {'' if api_key else ''}")
 ```

### 

```bash
# 
pip install -e .

# 
pip install pytest pytest-asyncio
```

## 

### 

 `tests/test_your_provider_adapter.py`

### OpenAI 

 `tests/test__adapter.py`

```python
import os
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

def test__api_key_config():
 """ API Key """
 api_key = os.environ.get("_API_KEY")
 
 if not api_key:
 print(" API: _API_KEY")
 return False
 
 if not api_key.startswith("bce-v3/"):
 print(" API bce-v3/ ")
 return False
 
 print(f" API (: {api_key[:10]}...)")
 return True

def test__basic_chat():
 """OpenAI """
 try:
 llm = create_openai_compatible_llm(
 provider="",
 model="ernie-3.5-8k",
 temperature=0.1,
 max_tokens=500
 )
 
 response = llm.invoke([
 HumanMessage(content="")
 ])
 
 print(f" : {response.content[:100]}...")
 return True
 except Exception as e:
 print(f" : {e}")
 return False

def test__function_calling():
 """"""
 try:
 @tool
 def get_stock_price(symbol: str) -> str:
 """
 
 Args:
 symbol: AAPL
 
 Returns:
 
 """
 return f" {symbol} $150.00"
 
 llm = create_openai_compatible_llm(
 provider="",
 model="ernie-4.0-turbo-8k",
 temperature=0.1
 )
 
 llm_with_tools = llm.bind_tools([get_stock_price])
 
 response = llm_with_tools.invoke([
 HumanMessage(content=" AAPL ")
 ])
 
 print(f" : {response.content[:200]}...")
 
 # 
 if "150.00" in response.content or "AAPL" in response.content:
 print(" ")
 return True
 else:
 print(" ")
 return False
 
 except Exception as e:
 print(f" : {e}")
 return False

def test__chinese_analysis():
 """"""
 try:
 llm = create_openai_compatible_llm(
 provider="",
 model="ernie-3.5-8k",
 temperature=0.1
 )
 
 test_prompt = """AAPL
 1. 
 2. 
 3. 
 
 200"""
 
 response = llm.invoke([HumanMessage(content=test_prompt)])
 
 # 
 content = response.content
 if (any('\u4e00' <= char <= '\u9fff' for char in content) and 
 ("" in content or "AAPL" in content) and
 len(content) > 50):
 print(" ")
 print(f" : {content[:150]}...")
 return True
 else:
 print(" ")
 print(f" : {content}")
 return False
 
 except Exception as e:
 print(f" : {e}")
 return False

def test__model_variants():
 """"""
 models_to_test = ["ernie-3.5-8k", "ernie-4.0-turbo-8k", "
 
 for model in models_to_test:
 try:
 llm = create_openai_compatible_llm(
 provider="",
 model=model,
 temperature=0.1,
 max_tokens=100
 )
 
 response = llm.invoke([
 HumanMessage(content="")
 ])
 
 print(f" {model} : {response.content[:50]}...")
 except Exception as e:
 print(f" {model} : {e}")

if __name__ == "__main__":
 print("=== OpenAI ===")
 print()
 
 # 
 test__api_key_config()
 print()
 
 # 
 test__basic_chat()
 print()
 
 # 
 test__function_calling()
 print()
 
 # 
 test__chinese_analysis()
 print()
 
 # 
 print("--- ---")
 test__model_variants()
```

```python
#!/usr/bin/env python3
"""
{Provider} 

"""

import os
import sys
import pytest
from pathlib import Path

# 
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# 
load_dotenv()

def test_api_key_configuration():
 """ API """
 print("\n API ")
 print("=" * 50)
 
 api_key = os.getenv("YOUR_PROVIDER_API_KEY")
 assert api_key is not None, "YOUR_PROVIDER_API_KEY "
 assert len(api_key) > 10, "API "
 
 print(f" API (: {len(api_key)})")
 return True

def test_adapter_import():
 """"""
 print("\n ")
 print("=" * 50)
 
 try:
 from tradingagents.llm_adapters.your_provider_adapter import ChatYourProvider
 print(" ")
 return True
 except ImportError as e:
 print(f" : {e}")
 pytest.fail(f": {e}")

def test_basic_connection():
 """"""
 print("\n ")
 print("=" * 50)
 
 try:
 from tradingagents.llm_adapters.your_provider_adapter import ChatYourProvider
 
 # 
 llm = ChatYourProvider(
 model="your-default-model",
 temperature=0.1,
 max_tokens=100
 )
 
 # 
 response = llm.invoke([
 HumanMessage(content="''")
 ])
 
 print(f" ")
 print(f" : {response.content[:100]}...")
 return True
 
 except Exception as e:
 print(f" : {e}")
 pytest.fail(f": {e}")

def test_function_calling():
 """"""
 print("\n ")
 print("=" * 50)
 
 try:
 from tradingagents.llm_adapters.your_provider_adapter import ChatYourProvider
 
 # 
 @tool
 def get_stock_price(symbol: str) -> str:
 """
 
 Args:
 symbol: AAPL
 
 Returns:
 
 """
 return f" {symbol} $150.00"
 
 # 
 llm = ChatYourProvider(
 model="your-default-model",
 temperature=0.1,
 max_tokens=500
 )
 llm_with_tools = llm.bind_tools([get_stock_price])
 
 # 
 response = llm_with_tools.invoke([
 HumanMessage(content=" AAPL ")
 ])
 
 print(f" ")
 print(f" : {response.content[:200]}...")
 
 # 
 if "150.00" in response.content or "AAPL" in response.content:
 print(" ")
 return True
 else:
 print(" ")
 return False
 
 except Exception as e:
 print(f" : {e}")
 pytest.fail(f": {e}")

def test_factory_function():
 """"""
 print("\n ")
 print("=" * 50)
 
 try:
 from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
 
 # 
 llm = create_openai_compatible_llm(
 provider="your_provider",
 model="your-default-model",
 temperature=0.1,
 max_tokens=100
 )
 
 # 
 response = llm.invoke([
 HumanMessage(content="")
 ])
 
 print(f" ")
 print(f" : {response.content[:100]}...")
 return True
 
 except Exception as e:
 print(f" : {e}")
 pytest.fail(f": {e}")

def test_trading_graph_integration():
 """ TradingGraph """
 print("\n TradingGraph ")
 print("=" * 50)
 
 try:
 from tradingagents.graph.trading_graph import TradingAgentsGraph
 
 # 
 config = {
 "llm_provider": "your_provider",
 "deep_think_llm": "your-default-model",
 "quick_think_llm": "your-default-model",
 "max_debate_rounds": 1,
 "online_tools": False, # 
 "selected_analysts": ["fundamentals_analyst"]
 }
 
 print(" TradingGraph...")
 graph = TradingAgentsGraph(config)
 
 print(" TradingGraph ")
 print(f" Deep thinking LLM: {type(graph.deep_thinking_llm).__name__}")
 print(f" Quick thinking LLM: {type(graph.quick_thinking_llm).__name__}")
 
 return True
 
 except Exception as e:
 print(f" TradingGraph : {e}")
 pytest.fail(f"TradingGraph : {e}")

def run_all_tests():
 """"""
 print(" {Provider} ")
 print("=" * 60)
 
 tests = [
 test_api_key_configuration,
 test_adapter_import,
 test_basic_connection,
 test_function_calling,
 test_factory_function,
 test_trading_graph_integration
 ]
 
 passed = 0
 failed = 0
 
 for test in tests:
 try:
 test()
 passed += 1
 except (AssertionError, Exception) as e:
 print(f" : {test.__name__}")
 print(f" : {e}")
 failed += 1
 print()
 
 print(" ")
 print("=" * 60)
 print(f" : {passed}")
 print(f" : {failed}")
 print(f" : {passed/(passed+failed)*100:.1f}%")
 
 if failed == 0:
 print("\n ")
 else:
 print(f"\n {failed} ")

if __name__ == "__main__":
 run_all_tests()
```

## Web 

### 

1. ** Web **
 ```bash
 python start_web.py
 ```

2. ****
 - "LLM"
 - 
 - 

3. ****
 - 
 - 

4. ****
 - AAPL
 - ""
 - ""
 - 

### Web 

 `tests/test_web_integration.py`

```python
import streamlit as st
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# 
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_sidebar_integration():
 """"""
 print("\n Web ")
 print("=" * 50)
 
 try:
 # Streamlit session state
 with patch('streamlit.session_state') as mock_state:
 mock_state.llm_provider = "your_provider"
 mock_state.llm_model = "your-default-model"
 
 # 
 from web.components.sidebar import create_sidebar
 
 # Streamlit 
 with patch('streamlit.selectbox') as mock_selectbox:
 mock_selectbox.return_value = "your_provider"
 
 # 
 config = create_sidebar()
 
 print(" ")
 return True
 
 except Exception as e:
 print(f" Web : {e}")
 return False

if __name__ == "__main__":
 test_sidebar_integration()
```

## 

### 

- [ ] ****
 - [ ] `OpenAICompatibleBase`
 - [ ] `provider_name``api_key_env_var``base_url`
 - [ ] `OPENAI_COMPATIBLE_PROVIDERS`
 - [ ] `__init__.py`

- [ ] ****
 - [ ] API 
 - [ ] 
 - [ ] 
 - [ ] 

- [ ] ****
 - [ ] Function calling 
 - [ ] 
 - [ ] 
 - [ ] 

### 

- [ ] ****
 - [ ] 
 - [ ] 
 - [ ] UI 
 - [ ] 

- [ ] ****
 - [ ] 
 - [ ] TradingGraph 
 - [ ] 
 - [ ] 

- [ ] ****
 - [ ] 
 - [ ] 
 - [ ] Token 
 - [ ] 

### 

- [ ] ****
 - [ ] 
 - [ ] 
 - [ ] 
 - [ ] 

- [ ] ****
 - [ ] 
 - [ ] 
 - [ ] 
 - [ ] 

- [ ] ****
 - [ ] API 
 - [ ] 
 - [ ] 
 - [ ] 

### 

- [ ] ****
 - [ ] < 30
 - [ ] 
 - [ ] CPU 
 - [ ] 

- [ ] ****
 - [ ] 30 
 - [ ] 50+ 
 - [ ] 
 - [ ] 

## 

### 1: API 

****: `AuthenticationError` `InvalidAPIKey`

****:
```bash
# 
echo $YOUR_PROVIDER_API_KEY

# 
source .env

# API 
python -c "import os; print(f'API Key: {os.getenv(\"YOUR_PROVIDER_API_KEY\")[:10]}...')"
```

### 2: 

****: `ToolCallError` 

****:
```python
# function calling
from tradingagents.llm_adapters.openai_compatible_base import OPENAI_COMPATIBLE_PROVIDERS

provider_config = OPENAI_COMPATIBLE_PROVIDERS["your_provider"]
models = provider_config["models"]
print(f" function calling: {models}")
```

### 3: 

****: 

****:
```python
# sidebar.py 
# options 
# format_func 
```

### 4: 

****: `ModuleNotFoundError` `ImportError`

****:
```bash
# 
pip install -e .

# __init__.py 
python -c "from tradingagents.llm_adapters import ChatYourProvider; print('')"
```

### 5: 

****: `AuthenticationError` `invalid_client`

****:
```bash
# API
echo $_API_KEY

# bce-v3/ 
python -c "import os; print(f'API Key: {os.getenv("_API_KEY", "")[:10]}...')"

# OpenAI AK/SK Token
python - << 'PY'
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
llm = create_openai_compatible_llm(provider="", model="ernie-3.5-8k")
print(llm.invoke("ping").content)
PY
```

### 6: 

****: 

****:
```python
# 
import locale
import sys
print(f": {locale.getpreferredencoding()}")
print(f"Python: {sys.getdefaultencoding()}")

# UTF-8
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 
test_text = ""
print(f": {test_text}")
print(f": {test_text.encode('utf-8')}")
print(f": {test_text.encode('utf-8').decode('utf-8')}")
```

### 7: OpenAI 

****: `AuthenticationError``RateLimitError` `ModelNotFound`

****:
```python
# 1) API Key 
action = "" if os.getenv("_API_KEY") else ""
print(f"_API_KEY: {action}")

# 2) 
from tradingagents.llm_adapters.openai_compatible_base import OPENAI_COMPATIBLE_PROVIDERS
print(OPENAI_COMPATIBLE_PROVIDERS[""]["models"].keys())

# 3) /
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
llm = create_openai_compatible_llm(provider="", model="ernie-3.5-8k", request_timeout=60)
print(llm.invoke("hello").content)
```

## 



```markdown
# {Provider} 

## 
- ****: {Provider}
- ****: Chat{Provider}
- ****: {Date}
- ****: {Name}

## 
- : 
- : 
- Web : 
- : 

## 
- : {X}
- : {X}%
- : {X}MB
- : 

## 
- 

## 
- 
- 
```

## 

1. ****: 
2. ****: 
3. ****: 
4. ****: 
5. ****: git 

## 



- ****: 
- ****: 
- ****: 
- **API **: 

---

 LLM TradingAgents 