# 

## 

TradingAgents-CNWordPDFMarkdown

## Word

### 1: YAML

****:

```
Pandoc died with exitcode "64" during conversion: 
YAML parse exception at line 1, column 1,
while scanning an alias:
did not find expected alphabetic or numeric character
```

****:

- Markdown `|------|------| ` pandocYAML
- YAML

****:

```python
# 
extra_args = ['--from=markdown-yaml_metadata_block'] # YAML
```

****:

```bash
# Word
docker exec TradingAgents-web python test_conversion.py
```

### 2: 

****:

- Word
- ¥%

****:

1. **Docker**:

 ```bash
 # Docker
 docker-compose up -d
 ```
2. ****:

 ```bash
 # Windows
 # 

 # Linux
 sudo apt-get install fonts-noto-cjk

 # macOS
 # 
 ```

### 3: Word

****:

- .docxWord
- 0

****:

```bash
# 1. 
docker exec TradingAgents-web ls -la /app/test_*.docx

# 2. pandoc
docker exec TradingAgents-web pandoc --version

# 3. 
docker exec TradingAgents-web python test_conversion.py
```

****:

```bash
# Docker
docker-compose down
docker build -t tradingagents-cn:latest . --no-cache
docker-compose up -d
```

## PDF

### 1: PDF

****:

```
PDF: wkhtmltopdf not found
```

****:

1. **Docker**:

 ```bash
 # PDF
 docker exec TradingAgents-web wkhtmltopdf --version
 docker exec TradingAgents-web weasyprint --version
 ```
2. ****:

 ```bash
 # Windows
 choco install wkhtmltopdf

 # macOS
 brew install wkhtmltopdf

 # Linux
 sudo apt-get install wkhtmltopdf
 ```

### 2: PDF

****:

- PDF
- 

****:

```python
# 
max_execution_time = 180 # 3
```

****:

```bash
# Web
docker-compose restart web
```

### 3: PDF

****:

- PDF
- 

****:

```bash
# Docker
docker build -t tradingagents-cn:latest . --no-cache
```

## Markdown

### 1: 

****:

- &<>
- 

****:

```python
# 
text = text.replace('&', '&')
text = text.replace('<', '<')
text = text.replace('>', '>')
```

### 2: 

****:

- Markdown
- 

****:

```python
# UTF-8
with open(file_path, 'w', encoding='utf-8') as f:
 f.write(content)
```

## 

### 

1. ****:

 ```bash
 # 
 docker exec TradingAgents-web python test_conversion.py

 # 
 docker exec TradingAgents-web python test_real_conversion.py

 # 
 docker exec TradingAgents-web python test_existing_reports.py
 ```
2. ****:

 ```bash
 # 
 docker-compose ps

 # 
 docker logs TradingAgents-web --tail 50

 # 
 docker exec TradingAgents-web df -h
 ```
3. ****:

 ```bash
 # Python
 docker exec TradingAgents-web pip list | grep -E "(pandoc|docx|pypandoc)"

 # 
 docker exec TradingAgents-web which pandoc
 docker exec TradingAgents-web which wkhtmltopdf
 ```

### 



```bash
# 1. 
docker-compose down

# 2. Docker
docker system prune -f

# 3. 
docker build -t tradingagents-cn:latest . --no-cache

# 4. 
docker-compose up -d

# 5. 
docker exec TradingAgents-web python test_conversion.py
```

### 

1. ****:

 ```yaml
 # docker-compose.yml
 services:
 web:
 deploy:
 resources:
 limits:
 memory: 2G # 
 ```
2. ****:

 ```bash
 # 
 docker exec TradingAgents-web find /tmp -name "*.docx" -delete
 docker exec TradingAgents-web find /tmp -name "*.pdf" -delete
 ```

## 

### 



1. ****:

 ```bash
 docker logs TradingAgents-web --tail 100 > error.log
 ```
2. ****:

 ```bash
 docker exec TradingAgents-web python --version
 docker exec TradingAgents-web pandoc --version
 docker --version
 docker-compose --version
 ```
3. ****:

 ```bash
 docker exec TradingAgents-web python test_conversion.py > test_result.log 2>&1
 ```

### 


| | | |
| ------------ | -------------- | -------------- |
| YAML | Web | |
| PDF | Docker | |
| | Docker | |
| | | Docker |
| | | |
| | | |

### 

1. ****:

 ```bash
 git pull origin develop
 docker-compose pull
 ```
2. ****:

 ```bash
 docker stats TradingAgents-web
 ```
3. ****:

 ```bash
 cp .env .env.backup
 ```

---

*: 2025-07-13*
*: v0.1.7*
