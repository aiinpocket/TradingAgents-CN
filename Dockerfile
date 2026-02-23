# 使用官方Python映像
FROM python:3.10-slim-bookworm

WORKDIR /app

RUN mkdir -p /app/data /app/logs

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 使用 Debian 官方源（全球 CDN）
RUN echo 'deb http://deb.debian.org/debian/ bookworm main' > /etc/apt/sources.list && \
    echo 'deb-src http://deb.debian.org/debian/ bookworm main' >> /etc/apt/sources.list && \
    echo 'deb http://deb.debian.org/debian/ bookworm-updates main' >> /etc/apt/sources.list && \
    echo 'deb-src http://deb.debian.org/debian/ bookworm-updates main' >> /etc/apt/sources.list && \
    echo 'deb http://deb.debian.org/debian-security bookworm-security main' >> /etc/apt/sources.list && \
    echo 'deb-src http://deb.debian.org/debian-security bookworm-security main' >> /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    wkhtmltopdf \
    xvfb \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-liberation \
    pandoc \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 啟動Xvfb虛擬顯示器
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 -ac +extension GLX &\nexport DISPLAY=:99\nexec "$@"' > /usr/local/bin/start-xvfb.sh \
    && chmod +x /usr/local/bin/start-xvfb.sh

COPY requirements-docker.txt requirements.txt ./

# 使用全球官方 PyPI 源安裝依賴（Docker 專用版本，已排除 Windows 套件）
# 分步執行以便定位問題
RUN pip install --no-cache-dir --upgrade pip

# 安裝 requirements-docker.txt 中的依賴
RUN pip install --no-cache-dir -r requirements-docker.txt

# 複製專案源碼（pip install -e . 需要這些檔案）
COPY . .

# 安裝 tradingagents 套件本身（不安裝依賴）
RUN pip install --no-deps -e .

# 安全：以非 root 用戶執行（明確指定 UID/GID 1000，與 k8s fsGroup 一致）
RUN groupadd -r -g 1000 appuser && useradd -r -u 1000 -g appuser -d /app appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=90s --retries=3 \
    CMD curl -f http://localhost:8501/health || exit 1

# 使用 FastAPI + Uvicorn 啟動
CMD ["python", "start_app.py", "--host", "0.0.0.0", "--port", "8501"]
