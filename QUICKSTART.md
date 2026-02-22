# TradingAgents-CN 

> ****: 0.1.18 | ****: 2026-02-21
> ****: 5 

## 

### Docker 

****: 

```bash
# 1. 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 
cp .env.example .env
#  .env  API 

# 3. 
docker-compose up -d --build

#  Docker  5-10 
# 
# -  800MB
# - pandocwkhtmltopdf 
# -  Python 
# - 

# 4. 
# Web : http://localhost:8501
# : http://localhost:8081
# : http://localhost:8082
```

### 



```bash
#  A: 
# 1.  Docker 
docker build -t tradingagents-cn:latest .

# 2. 
docker-compose up -d

#  B: 
docker-compose up -d --build
```

### 

****: 

```bash
# 1. 
git clone https://github.com/aiinpocket/TradingAgents-CN.git
cd TradingAgents-CN

# 2. 
python -m venv env
env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/macOS

# 3.  pip
python -m pip install --upgrade pip

# 4. 
pip install -r requirements-lock.txt
pip install -e . --no-deps

# 
# pip install -e .

# 5. 
cp .env.example .env
#  .env 

# 6. Web
python start_app.py
```

## 

### 

 `.env` 

```bash
# === LLM ===

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Anthropic Claude
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### API 

|  |  |  |  |
| --- | --- | --- | --- |
| **OpenAI** | [platform.openai.com](https://platform.openai.com/) |  |  |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) |  |  |

### 

```bash
# === ===
FINNHUB_API_KEY=your_finnhub_key          # 

# === Docker ===
MONGODB_URL=mongodb://mongodb:27017/tradingagents  # Docker 
REDIS_URL=redis://redis:6379                       # Docker 

# ===  ===
EXPORT_ENABLED=true                       # 
EXPORT_DEFAULT_FORMAT=word,pdf            # 
```

## 

### 1.  Web 

```bash
# 
http://localhost:8501
```

### 2. 

- ** LLM **: GPT-4 / Claude
- ****:  /  / 
- ****:  /  / 

### 3. 

```bash
# 
AAPL    # Apple
TSLA    # Tesla
MSFT    # Microsoft
NVDA    # NVIDIA
GOOGL   # Alphabet
AMZN    # Amazon
```

### 4. 

1. 
2. ****: 
   - 
   - 
   - 
3. ****: 2-10 
   - 
   - 
4. ****: 
   - 
   - 
5. ****:  Word/PDF/Markdown 

## 

### 

|  |  |  |
| --- | --- | --- |
| **Markdown** |  |  |
| **Word** |  |  |
| **PDF** |  |  |

### 

1. 
2. 
3. 
4. 

## 

### 

- ****: 
- ****: 
- ****: 
- ****: 
- ****: 

### 

- **GPT-4**: 
- **Claude**: 

### 

- ****: NYSE/NASDAQ
- ****: 
- ****: FinnHub 

## 

### 

1. ** API **: 
2. ****:  API
3. ****:  LLM 
4. ****: 

### 

1. ****: gpt-4o-mini 
2. ****:  Redis 
3. ****: 
4. ****: 

### Docker 

```bash
# 
docker-compose ps

# 
docker logs TradingAgents-web

# 
docker-compose restart
```

## 

### 

1. ****: [](./docs/)
2. ****: [](./docs/DEVELOPMENT_SETUP.md)
3. ****: [](./docs/troubleshooting/)
4. ****: [](./docs/architecture/)

### 

- [](https://github.com/aiinpocket/TradingAgents-CN/issues)
- [](https://github.com/aiinpocket/TradingAgents-CN/issues)
- [](https://github.com/aiinpocket/TradingAgents-CN/pulls)
- [](https://github.com/aiinpocket/TradingAgents-CN/tree/develop/docs)

---

## 

****: 

****: [GitHub Issues](https://github.com/aiinpocket/TradingAgents-CN/issues)

---

*: 2026-02-21 | : 0.1.18*
