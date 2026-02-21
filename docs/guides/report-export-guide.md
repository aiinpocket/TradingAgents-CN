# 

## 

TradingAgents-CN v0.1.7 WordPDFMarkdown

## 

### 

| | | | |
|------|--------|----------|------|
| ** Markdown** | .md | | Git |
| ** Word** | .docx | | |
| ** PDF** | .pdf | | |

### 

- ****: 
- ****: 
- ****: 
- ****: 
- ****: 

## 

### 

#### Docker ()
```bash
# Docker
docker-compose up -d
```

#### 
```bash
# Pandoc ()
# Windows: https://pandoc.org/installing.html
# Linux: sudo apt install pandoc
# macOS: brew install pandoc

# wkhtmltopdf (PDF)
# Windows: https://wkhtmltopdf.org/downloads.html
# Linux: sudo apt install wkhtmltopdf
# macOS: brew install wkhtmltopdf

# 
pandoc --version
wkhtmltopdf --version
```

### 

```bash
# .env
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf
EXPORT_OUTPUT_PATH=./exports
```

## 

### 

#### 1. 
```bash
# Web
http://localhost:8501

# 
# 1. LLM
# 2. (: AAPL, MSFT)
# 3. 
# 4. ""
# 5. 
```

#### 2. 
```bash
# 
# 1. 
# 2. ""
# 3. :
# - Markdown
# - Word
# - PDF
# 4. ""
# 5. 
# 6. 
```

### 

#### Markdown

****:
- 
- 
- 
- 

****:
```bash
# :
 
 
 
 
```

****:
```markdown
# : Apple Inc. (AAPL)

## 
- ****: AAPL
- ****: Apple Inc.
- ****: 2025-07-13 14:30:00
- ****: $198.45

## 
### 
...
```

#### Word

****:
- 
- 
- 
- 

****:
```bash
# :
 
 
 
 
```

****:
- 
- 
- 
- 
- 

#### PDF

****:
- 
- 
- 
- 

****:
```bash
# :
 
 
 
 
```

****:
- 
- 
- 
- (A4)

## 

### 

```bash
# .env 
# === ===
EXPORT_ENABLED=true
EXPORT_DEFAULT_FORMAT=word,pdf,markdown
EXPORT_OUTPUT_PATH=./exports
EXPORT_FILENAME_FORMAT={symbol}_analysis_{timestamp}

# === ===
PANDOC_PATH=/usr/bin/pandoc
WKHTMLTOPDF_PATH=/usr/bin/wkhtmltopdf

# === ===
EXPORT_INCLUDE_DEBUG=false
EXPORT_WATERMARK=false
EXPORT_COMPRESS_PDF=true

# === Word ===
WORD_TEMPLATE_PATH=./templates/report_template.docx
WORD_REFERENCE_DOC=./templates/reference.docx

# === PDF ===
PDF_PAGE_SIZE=A4
PDF_MARGIN_TOP=2cm
PDF_MARGIN_BOTTOM=2cm
PDF_MARGIN_LEFT=2cm
PDF_MARGIN_RIGHT=2cm
```

### 

#### Word
```bash
# 1. 
mkdir -p templates

# 2. Word
# templates/report_template.docx
# - 
# - 
# - 

# 3. 
WORD_TEMPLATE_PATH=./templates/report_template.docx
```

#### PDF
```bash
# CSS
# templates/pdf_style.css

body {
 font-family: "SimSun", serif;
 font-size: 12pt;
 line-height: 1.6;
 margin: 2cm;
}

h1 {
 color: #2c3e50;
 border-bottom: 2px solid #3498db;
 padding-bottom: 10px;
}

table {
 border-collapse: collapse;
 width: 100%;
 margin: 20px 0;
}
```

## 

### 

#### 1. 

****: 

****:
```bash
# .env
EXPORT_ENABLED=true

# 
docker-compose restart web
# 
streamlit run web/app.py
```

#### 2. Word

****: PandocYAML

****:
```bash
# Docker ()
docker-compose restart web

# 
# 1. Pandoc
sudo apt install pandoc # Linux
brew install pandoc # macOS

# 2. Pandoc
pandoc --version
```

#### 3. PDF

****: wkhtmltopdf

****:
```bash
# Docker ()
docker logs TradingAgents-web

# 
# 1. wkhtmltopdf
sudo apt install wkhtmltopdf # Linux
brew install wkhtmltopdf # macOS

# 2. 
sudo apt install fonts-wqy-zenhei # Linux
```

#### 4. 

****: 

****:
```bash
# 1. 
# 2. 
chmod 755 exports/
chmod 644 exports/*.pdf

# 3. 
# exports/ 
```

### 

```bash
# 1. 
EXPORT_PARALLEL=true
EXPORT_MAX_WORKERS=3

# 2. 
EXPORT_CACHE_ENABLED=true
EXPORT_CACHE_TTL=3600

# 3. 
EXPORT_COMPRESS_PDF=true
EXPORT_OPTIMIZE_IMAGES=true
```

## 

### 

```python
# Python
import os
from tradingagents.export.report_exporter import ReportExporter

# 
exporter = ReportExporter()

# 
symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
for symbol in symbols:
 # 
 analysis_result = get_analysis_result(symbol)
 
 # 
 exporter.export_all_formats(
 analysis_result, 
 output_dir=f'exports/{symbol}'
 )
```

### 

```bash
# 
crontab -e

# 
0 18 * * 1-5 cd /path/to/TradingAgents-CN && python scripts/daily_export.py
```

## 

### 1. 
```bash
# 
{}_{}_{}.{}

# 
AAPL_comprehensive_20250713.pdf
MSFT_technical_20250713.docx
TSLA_fundamental_20250713.md
```

### 2. 
```bash
# 
find exports/ -name "*.pdf" -mtime +30 -delete
find exports/ -name "*.docx" -mtime +30 -delete

# 
tar -czf exports_archive_$(date +%Y%m).tar.gz exports/
```

### 3. 
```bash
# 
 
 
 
 

# 
 
 
 
 
```

---

## 



- [GitHub Issues](https://github.com/aiinpocket/TradingAgents-CN/issues)
- [GitHub Issues](https://github.com/aiinpocket/TradingAgents-CN/issues)
- [Pandoc](https://pandoc.org/MANUAL.html)

---

*: 2025-07-13* 
*: cn-0.1.7* 
*: [@baiyuxiong](https://github.com/baiyuxiong)*
