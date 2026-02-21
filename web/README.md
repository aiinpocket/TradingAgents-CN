# TradingAgents-CN Web 

 Streamlit  TradingAgents Web  LLM 

## 

###  Web 
- 
- 
- 
-  UI 

###  LLM 
- **OpenAI**: gpt-4o, gpt-4o-mini
- **Anthropic Claude**: claude-opus-4, claude-sonnet-4
- ****: 

### 
- ****: 
- ****: 
- ****: 
- ****: 

## 

### 1. 

```bash
# 
.\env\Scripts\activate  # Windows
source env/bin/activate  # Linux/macOS

# 
pip install -r requirements.txt

# !
pip install -e .

#  API 
cp .env.example .env
#  .env  API 
```

### 2.  Web 

```bash
#  1: 
python start_web.py

#  2: 
python web/run_web.py

#  3: 
# Windows
start_web.bat

# Linux/macOS
./start_web.sh

#  4: 
python -m streamlit run web/app.py
```

### 3. 

 `http://localhost:8501`

## 

### 

#### 

1. **API **
   -  API 
   - 

2. ****
   - ** LLM **: OpenAI  Anthropic Claude
   - ****:
     - OpenAI: gpt-4o() / gpt-4o-mini()
     - Anthropic: claude-opus-4() / claude-sonnet-4()

3. ****
   - ****: 
   - ****: 
   - ****: 

#### 

1. ****
   - ****:  AAPLTSLA
   - ****: 
   - ****: 
     -  - 
     -  - 
     -  - 
     -  - 
   - ****: 1-5 

### 

1. ****
2. ****:
   - 
   - 
   - 
   - 
   - 

3. **** 2-5 

### 

#### 
- ****: BUY/SELL/HOLD
- ****: 
- ****: 
- ****: 

#### 
- **LLM **: 
- ****: 
- ****: 
- ****: 

#### 
- ****: 
- ****: 
- ****: 
- ****: 
- ****: 

## 

### 

```
web/
 app.py                 # 
 run_web.py            # 
 components/           # UI 
    __init__.py
    sidebar.py        # 
    analysis_form.py  # 
    results_display.py # 
    header.py         # 
 utils/                # 
    __init__.py
    analysis_runner.py # 
    api_checker.py    # API 
    progress_tracker.py # 
 static/               # 
 README.md            # 
```

### 

```
 ->  -> API  ->  -> 
    |           |           |           |           |
     ->    ->    ->    -> 
```

### 

- **sidebar.py**:  API 
- **analysis_form.py**: 
- **results_display.py**: 
- **analysis_runner.py**:  LLM 
- **progress_tracker.py**: 

## 

### 

 `.env` 

```env
# OpenAI API (recommended)
OPENAI_API_KEY=your_openai_api_key

# Anthropic API (optional, Claude models)
ANTHROPIC_API_KEY=your_anthropic_api_key

# FinnHub API (optional, US stock data)
FINNHUB_API_KEY=your_finnhub_key

# FinnHub API (social media sentiment analysis)
FINNHUB_API_KEY=your_finnhub_key
```

### 

#### OpenAI 
- **gpt-4o**: 
- **gpt-4o-mini**: 

#### Anthropic Claude 
- **claude-opus-4**: 
- **claude-sonnet-4**: 

## 

### 

#### 1. 
```bash
#  Python 
python --version  #  3.10+

# 
pip list | grep streamlit

# 
netstat -an | grep 8501
```

#### 2. API 
-  `.env` 
-  API 
-  API 

#### 3. 
- 
- 
- 

#### 4. 
- 
- 
- 

### 



```bash
#  Streamlit 
streamlit run web/app.py --logger.level=debug

# 
# 
```

### 



1.  [](../docs/)
2.  [](../tests/test_web_fix.py)
3.  [GitHub Issue](https://github.com/aiinpocket/TradingAgents-CN/issues)

## 

### 

1.  `components/` 
2. 
3.  `app.py` 

```python
# components/new_component.py
import streamlit as st

def render_new_component():
    """"""
    st.subheader("")
    # 
    return component_data

# app.py
from components.new_component import render_new_component

# 
data = render_new_component()
```

### 

 `static/`  CSS 

```css
/* static/custom.css */
.custom-style {
    background-color: #f0f0f0;
    padding: 10px;
    border-radius: 5px;
}
```



```python
#  CSS
st.markdown('<link rel="stylesheet" href="static/custom.css">', unsafe_allow_html=True)
```

## 

 Apache 2.0  [LICENSE](../LICENSE) 

## 

 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 
