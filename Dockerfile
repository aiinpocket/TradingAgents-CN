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

COPY requirements.txt .

# 使用全球官方 PyPI 源安裝依賴
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制日志配置文件
COPY config/ ./config/

COPY . .

EXPOSE 8501

CMD ["python", "-m", "streamlit", "run", "web/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
