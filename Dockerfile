# ===== 階段 1：建置階段（安裝編譯工具 + pip 套件）=====
FROM python:3.10-slim-bookworm AS builder

WORKDIR /build

# 使用 Debian 官方源（全球 CDN，移除不需要的 deb-src 以加速 apt-get update）
RUN echo 'deb http://deb.debian.org/debian/ bookworm main' > /etc/apt/sources.list && \
    echo 'deb http://deb.debian.org/debian/ bookworm-updates main' >> /etc/apt/sources.list && \
    echo 'deb http://deb.debian.org/debian-security bookworm-security main' >> /etc/apt/sources.list

# 安裝編譯工具（僅在此階段使用，不帶入最終映像）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-docker.txt requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-docker.txt


# ===== 階段 2：運行階段（僅包含運行時依賴）=====
FROM python:3.10-slim-bookworm

WORKDIR /app

RUN mkdir -p /app/data /app/logs

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 使用 Debian 官方源（同 builder 階段，無 deb-src）
RUN echo 'deb http://deb.debian.org/debian/ bookworm main' > /etc/apt/sources.list && \
    echo 'deb http://deb.debian.org/debian/ bookworm-updates main' >> /etc/apt/sources.list && \
    echo 'deb http://deb.debian.org/debian-security bookworm-security main' >> /etc/apt/sources.list

# 運行時依賴（不含 build-essential，節省 ~400MB）
RUN apt-get update && apt-get install -y --no-install-recommends \
    wkhtmltopdf \
    xvfb \
    fonts-wqy-zenhei \
    fonts-wqy-microhei \
    fonts-liberation \
    pandoc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 從建置階段複製已編譯的 Python 套件
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 啟動 Xvfb 虛擬顯示器（wkhtmltopdf 需要）
RUN echo '#!/bin/bash\nXvfb :99 -screen 0 1024x768x24 -ac +extension GLX &\nexport DISPLAY=:99\nexec "$@"' > /usr/local/bin/start-xvfb.sh \
    && chmod +x /usr/local/bin/start-xvfb.sh

# 複製專案源碼
COPY . .

# 壓縮靜態資源（CSS/JS minify，減少 ~16% 傳輸量）
RUN python scripts/minify_static.py app/static

# 安裝 tradingagents 套件本身（不安裝依賴，依賴已從 builder 複製）
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
