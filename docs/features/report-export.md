# 

## 

TradingAgents-CN 

## 

### 1. ** Markdown**

- ****: 
- ****: 
- ****: 

### 2. ** Word (.docx)**

- ****: 
- ****: 
- ****: 

### 3. ** PDF (.pdf)**

- ****: 
- ****: 
- ****: 

## 

### Web

1. ****

 - Web
 - 
 - 
2. ****

 - 
 - 
 - ** Markdown**
 - ** Word**
 - ** PDF**
3. ****

 - 
 - 
 - `{}_analysis_{}.{}`

### 

```bash
# CLI
python main.py --symbol AAPL --export-format word,pdf
```

## 

### 

1. ** **

 - 
 - 
 - 
 - 
2. ** **

 - //
 - 
 - 
 - 
3. ** **

 - 
 - 
 - 
 - 
4. ** **

 - 
 - 
 - 
5. ** **

 - 
 - 
 - 
6. ** **

 - LLM
 - 
 - 
 - 

## 

### 

- ****: Pandoc
- **Word**: pypandoc + python-docx
- **PDF**: wkhtmltopdf / weasyprint
- ****: YAML

### Docker

```yaml
# Docker
- pandoc: 
- wkhtmltopdf: PDF
- python-docx: Word
- : 
```

### 

1. **YAML**

 ```python
 # YAML
 extra_args = ['--from=markdown-yaml_metadata_block']
 ```
2. ****

 ```python
 # 
 content = content.replace('---', '—') # 
 content = content.replace('...', '…') # 
 ```
3. ****

 ```python
 # PDF
 engines = ['wkhtmltopdf', 'weasyprint', 'default']
 ```

## 

### 

```bash
# .env 
EXPORT_ENABLED=true # 
EXPORT_DEFAULT_FORMAT=word,pdf # 
EXPORT_INCLUDE_DEBUG=false # 
EXPORT_WATERMARK=false # 
```

### Web

- ****: 
- ****: 
- ****: 

## 

### 

```
: {}_analysis_{YYYYMMDD_HHMMSS}.{}
: 
- AAPL_analysis_20250113_143022.docx
- MSFT_analysis_20250113_143022.pdf
- TSLA_analysis_20250113_143022.md
```

### 

- **Web**: 
- **CLI**: `./exports/` 
- **Docker**: 

## 

### 

1. **Word**

 ```
 : YAML parse exception
 : 
 ```
2. **PDF**

 ```
 : wkhtmltopdf not found
 : Docker
 ```
3. ****

 ```
 : 
 : Docker
 ```

### 

1. ****

 ```bash
 docker logs TradingAgents-web --follow
 ```
2. ****

 ```bash
 docker exec TradingAgents-web python test_conversion.py
 ```
3. ****

 ```bash
 docker exec TradingAgents-web pandoc --version
 docker exec TradingAgents-web wkhtmltopdf --version
 ```

## 

### 

1. ****

 - ****: Markdown
 - ****: Word
 - ****: PDF
2. ****

 - CLI
 - 
 - 
3. ****

 - 
 - 
 - 

## 

### 

1. ** **
 - 
 - 
 - 

2. ** **
 - 
 - 
 - 

3. ** **
 - 
 - 
 - 

4. ** **
 - 
 - 
 - 

## 

### 

 **[@baiyuxiong](https://github.com/baiyuxiong)** (baiyuxiong@163.com) 

- 
- Pandoc
- Word/PDF
- 
- 

TradingAgents-CN

---

*: 2025-07-13*
*: cn-0.1.7*
*: [@baiyuxiong](https://github.com/baiyuxiong)*
