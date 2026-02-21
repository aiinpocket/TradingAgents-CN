# TradingAgents-CN 

## 

 TradingAgents-CN Pull Request

## 

- 
- 
- LLM 
- API 

## 

TradingAgents LLM 

```
tradingagents/
 llm_adapters/ # LLM 
 __init__.py # 
 openai_compatible_base.py # OpenAI ()
 
 
 
 
 google_openai_adapter.py # Google AI 
 web/
 components/sidebar.py # 
 utils/analysis_runner.py # 
```

### 

1. : <mcsymbol name="OpenAICompatibleBase" filename="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py" startline="32" type="class"></mcsymbol> —— OpenAI LLM <mcfile name="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py"></mcfile>
2. : <mcsymbol name="create_openai_compatible_llm" filename="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py" startline="329" type="function"></mcsymbol> —— 
3. : <mcfile name="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py"></mcfile> `OPENAI_COMPATIBLE_PROVIDERS` —— base_urlAPI Key 
4. : <mcfile name="sidebar.py" path="web/components/sidebar.py"></mcfile> —— llm_provider llm_model 
5. : <mcfile name="trading_graph.py" path="tradingagents/graph/trading_graph.py"></mcfile> LLM<mcfile name="analysis_runner.py" path="web/utils/analysis_runner.py"></mcfile> 

## 

### 

1. **Fork **

 ```bash
 git clone https://github.com/your-username/TradingAgentsCN.git
 cd TradingAgentsCN
 ```
2. ****

 ```bash
 pip install -e .
 # uv
 uv pip install -e .
 ```
3. ****

 ```bash
 git checkout develop
 git checkout -b feature/add-{provider_name}-llm
 ```

### 

 API 

#### OpenAI API

 OpenAI API MiniMax

****

- 
- 
- 

> OpenAI provider `` `_API_KEY` _INTEGRATION_GUIDE.mdpricing.json 

#### API 

 OpenAI 

****

- 
- 
- 

## 

### OpenAI 

#### 1. 

 `tradingagents/llm_adapters/` 

```python
# tradingagents/llm_adapters/your_provider_adapter.py

from .openai_compatible_base import OpenAICompatibleBase
import os
from tradingagents.utils.tool_logging import log_llm_call
import logging

logger = logging.getLogger(__name__)

class ChatYourProvider(OpenAICompatibleBase):
 """ OpenAI """
 
 def __init__(
 self,
 model: str = "your-default-model",
 temperature: float = 0.7,
 max_tokens: int = 4096,
 **kwargs
 ) -> None:
 super().__init__(
 provider_name="your_provider",
 model=model,
 temperature=temperature,
 max_tokens=max_tokens,
 api_key_env_var="YOUR_PROVIDER_API_KEY",
 base_url="https://api.yourprovider.com/v1",
 **kwargs
 )
```

#### 2. 

 `tradingagents/llm_adapters/openai_compatible_base.py`

```python
# OPENAI_COMPATIBLE_PROVIDERS 
OPENAI_COMPATIBLE_PROVIDERS = {
 # ... ...
 
 "your_provider": {
 "adapter_class": ChatYourProvider,
 "base_url": "https://api.yourprovider.com/v1",
 "api_key_env": "YOUR_PROVIDER_API_KEY",
 "models": {
 "your-model-1": {"context_length": 8192, "supports_function_calling": True},
 "your-model-2": {"context_length": 32768, "supports_function_calling": True},
 }
 },
}
```

#### 3. 

 `tradingagents/llm_adapters/__init__.py`

```python
from .your_provider_adapter import ChatYourProvider

__all__ = ["Chat
```

#### 4. 

 `web/components/sidebar.py`

```python
# llm_provider 
options=["

# 
format_mapping={
 # ... ...
 "your_provider": " ",
}

# 
elif llm_provider == "your_provider":
 your_provider_options = ["your-model-1", "your-model-2"]
 
 current_index = 0
 if st.session_state.llm_model in your_provider_options:
 current_index = your_provider_options.index(st.session_state.llm_model)
 
 llm_model = st.selectbox(
 "",
 options=your_provider_options,
 index=current_index,
 format_func=lambda x: {
 "your-model-1": "Model 1 - ",
 "your-model-2": "Model 2 - ",
 }.get(x, x),
 help="",
 key="your_provider_model_select"
 )
```

#### 5. 

 OpenAI <mcfile name="analysis_runner.py" path="web/utils/analysis_runner.py"></mcfile>

- <mcfile name="sidebar.py" path="web/components/sidebar.py"></mcfile> `llm_provider` `llm_model`
- <mcfile name="trading_graph.py" path="tradingagents/graph/trading_graph.py"></mcfile> <mcsymbol name="create_openai_compatible_llm" filename="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py" startline="329" type="function"></mcsymbol> `OPENAI_COMPATIBLE_PROVIDERS` 
- “” <mcfile name="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py"></mcfile> analysis_runner 



- <mcfile name="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py"></mcfile> `OPENAI_COMPATIBLE_PROVIDERS`base_urlapi_key 
- <mcfile name="sidebar.py" path="web/components/sidebar.py"></mcfile> `llm_provider` 
- <mcfile name="analysis_runner.py" path="web/utils/analysis_runner.py"></mcfile> 

 analysis_runner

- “/”
- header
- 



- analysis_runner API `OPENAI_COMPATIBLE_PROVIDERS`
- <mcsymbol name="create_openai_compatible_llm" filename="openai_compatible_base.py" path="tradingagents/llm_adapters/openai_compatible_base.py" startline="329" type="function"></mcsymbol> 

 `web/utils/analysis_runner.py`

```python
elif llm_provider == "your_provider":
 config["backend_url"] = "https://api.yourprovider.com/v1"
 logger.info(f" [] : {llm_model}")
 logger.info(f" [] API: https://api.yourprovider.com/v1")
```

### 

 `.env.example` 

```bash
# API 
YOUR_PROVIDER_API_KEY=your_api_key_here
```

## 

### 1. 

 `test_your_provider.py`

```python
import os
from tradingagents.llm_adapters.your_provider_adapter import ChatYourProvider

def test_basic_connection():
 """"""
 # 
 os.environ["YOUR_PROVIDER_API_KEY"] = "your_test_key"
 
 try:
 llm = ChatYourProvider(model="your-model-1")
 response = llm.invoke("Hello, world!")
 print(f" : {response.content}")
 return True
 except Exception as e:
 print(f" : {e}")
 return False

if __name__ == "__main__":
 test_basic_connection()
```

### 2. 

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
 """"""
 return f"{city}25°C"

def test_function_calling():
 """"""
 llm = ChatYourProvider(model="your-model-1")
 llm_with_tools = llm.bind_tools([get_weather])
 
 response = llm_with_tools.invoke("")
 print(f": {response}")
```

### 3. Web 

 Web 

```bash
cd web
streamlit run app.py
```



- [ ] 
- [ ] 
- [ ] API 
- [ ] 

## 

 PR 

### 

- [ ] 
- [ ] `OPENAI_COMPATIBLE_PROVIDERS` 
- [ ] `__init__.py` 
- [ ] 
- [ ] 

### 

- [ ] `.env.example`
- [ ] API 
- [ ] 

### 

- [ ] 
- [ ] 
- [ ] Web 
- [ ] 

### 

- [ ] README 
- [ ] 
- [ ] 

## 

### 1. API 

****: API 

****:

- API 
- 
- `.env` 
- ****: `_API_KEY`

### 2. 

****: 

****:

- Function Calling
- API OpenAI 
- 
- ****: 

### 3. 

****: 

****:

- 
- `sidebar.py` 
- Streamlit 
- ****: 

### 4. 

****: API 

****:

- `timeout` 
- API 
- 
- ****: 

### 5. 

****: 

****:

```python
# UTF-8 
import json

def safe_json_dumps(data):
 return json.dumps(data, ensure_ascii=False, indent=2)

def safe_json_loads(text):
 return json.loads(text.encode('utf-8').decode('utf-8'))
```
### 6. 

****: 

****:

- `max_tokens` 
- 
- 

```python
# 
def select_model_by_task(task_complexity: str) -> str:
 if task_complexity == "simple":
 return "
 elif task_complexity == "medium":
 return "
 else:
 return "
```
## PR 

### 

```
feat(llm): add {ProviderName} LLM integration

- Add {ProviderName} OpenAI-compatible adapter
- Update frontend model selection UI
- Add configuration and environment variables
- Include basic tests and documentation

Closes #{issue_number}
```
### PR 

```markdown
## {ProviderName}

### 
- {ProviderName} OpenAI 
- 
- 
- 

### 
- [x] 
- [x] 
- [x] Web 
- [x] 

### 
- `model-1`: 
- `model-2`: 

### 
`YOUR_PROVIDER_API_KEY`

### 


### 
- [x] 
- [x] 
- [x] 
- [x] 
```
## 

### 1. 

- 
- API 
- 

### 2. 

- 
- 
- API 

### 3. 

- 
- 
- token 

### 4. 

- 
- 
- 

## 



1. ****: `
2. ****: `openai_compatible_base.py` 
3. ** Issue**: GitHub 
4. ****: Discussion 

## 

1. ****: `feature/add-{provider}-llm`
2. ****: 
3. ****: 
4. ****: 

---

** TradingAgentsCN ** 


