#!/bin/bash
# TradingAgents 目錄初始化指令碼
# 建立 Docker 容器需要的本地目錄結構

echo "TradingAgents 目錄初始化"
echo "=========================="

# 取得指令碼所在目錄的父目錄（專案根目錄）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "專案根目錄: $PROJECT_ROOT"

# 建立必要的目錄
DIRECTORIES=(
    "logs"
    "data"
    "data/cache"
    "data/exports"
    "data/temp"
    "config"
    "config/runtime"
)

echo ""
echo "建立目錄結構..."

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "[OK] 建立目錄: $dir"
    else
        echo "[SKIP] 目錄已存在: $dir"
    fi
done

# 設定目錄權限
echo ""
echo "設定目錄權限..."

# 確保日誌目錄可寫
chmod 755 logs
echo "[OK] 設定 logs 目錄權限: 755"

# 確保資料目錄可寫
chmod 755 data
chmod 755 data/cache
chmod 755 data/exports
chmod 755 data/temp
echo "[OK] 設定 data 目錄權限: 755"

# 確保配置目錄可寫
chmod 755 config
chmod 755 config/runtime
echo "[OK] 設定 config 目錄權限: 755"

# 建立 .gitkeep 檔案保持目錄結構
echo ""
echo "建立 .gitkeep 檔案..."

GITKEEP_DIRS=(
    "logs"
    "data/cache"
    "data/exports"
    "data/temp"
    "config/runtime"
)

for dir in "${GITKEEP_DIRS[@]}"; do
    if [ ! -f "$dir/.gitkeep" ]; then
        touch "$dir/.gitkeep"
        echo "[OK] 建立: $dir/.gitkeep"
    fi
done

# 建立日誌配置檔案
echo ""
echo "建立日誌配置檔案..."

LOG_CONFIG_FILE="config/logging.toml"
if [ ! -f "$LOG_CONFIG_FILE" ]; then
    cat > "$LOG_CONFIG_FILE" << 'EOF'
# TradingAgents 日誌配置檔案
[logging]
version = 1
disable_existing_loggers = false

[logging.formatters.standard]
format = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"

[logging.formatters.detailed]
format = "%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"

[logging.handlers.console]
class = "logging.StreamHandler"
level = "INFO"
formatter = "standard"
stream = "ext://sys.stdout"

[logging.handlers.file]
class = "logging.handlers.RotatingFileHandler"
level = "DEBUG"
formatter = "detailed"
filename = "/app/logs/tradingagents.log"
maxBytes = 104857600  # 100MB
backupCount = 5
encoding = "utf8"

[logging.handlers.error_file]
class = "logging.handlers.RotatingFileHandler"
level = "ERROR"
formatter = "detailed"
filename = "/app/logs/tradingagents_error.log"
maxBytes = 52428800  # 50MB
backupCount = 3
encoding = "utf8"

[logging.loggers.tradingagents]
level = "DEBUG"
handlers = ["console", "file", "error_file"]
propagate = false

[logging.loggers.streamlit]
level = "INFO"
handlers = ["console", "file"]
propagate = false

[logging.loggers.yfinance]
level = "WARNING"
handlers = ["file"]
propagate = false

[logging.loggers.finnhub]
level = "WARNING"
handlers = ["file"]
propagate = false

[logging.root]
level = "INFO"
handlers = ["console", "file"]
EOF
    echo "[OK] 建立日誌配置: $LOG_CONFIG_FILE"
else
    echo "[SKIP] 日誌配置已存在: $LOG_CONFIG_FILE"
fi

# 建立 .gitignore 檔案
echo ""
echo "更新 .gitignore 檔案..."

GITIGNORE_ENTRIES=(
    "# 日誌檔案"
    "logs/*.log"
    "logs/*.log.*"
    ""
    "# 資料快取"
    "data/cache/*"
    "data/temp/*"
    "!data/cache/.gitkeep"
    "!data/temp/.gitkeep"
    ""
    "# 執行時配置"
    "config/runtime/*"
    "!config/runtime/.gitkeep"
    ""
    "# 匯出檔案"
    "data/exports/*.pdf"
    "data/exports/*.docx"
    "data/exports/*.xlsx"
    "!data/exports/.gitkeep"
)

# 檢查 .gitignore 是否存在
if [ ! -f ".gitignore" ]; then
    touch ".gitignore"
fi

# 新增條目到 .gitignore（如果不存在）
for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if [ -n "$entry" ] && ! grep -Fxq "$entry" .gitignore; then
        echo "$entry" >> .gitignore
    fi
done

echo "[OK] 更新 .gitignore 檔案"

# 建立 README 檔案
echo ""
echo "建立目錄說明檔案..."

README_FILE="logs/README.md"
if [ ! -f "$README_FILE" ]; then
    cat > "$README_FILE" << 'EOF'
# TradingAgents 日誌目錄

此目錄用於儲存 TradingAgents 應用的日誌檔案。

## 日誌檔案說明

- `tradingagents.log` - 主應用日誌檔案
- `tradingagents_error.log` - 錯誤日誌檔案
- `tradingagents.log.1`, `tradingagents.log.2` 等 - 輪轉的歷史日誌檔案

## 日誌等級

- **DEBUG** - 詳細的除錯資訊
- **INFO** - 一般資訊
- **WARNING** - 警告資訊
- **ERROR** - 錯誤資訊
- **CRITICAL** - 嚴重錯誤

## 日誌輪轉

- 主日誌檔案最大 100MB，保留 5 個歷史檔案
- 錯誤日誌檔案最大 50MB，保留 3 個歷史檔案

## 取得日誌

如果遇到問題需要發送日誌給開發者，請發送：
1. `tradingagents.log` - 主日誌檔案
2. `tradingagents_error.log` - 錯誤日誌檔案（如果存在）

## Docker 環境

在 Docker 環境中，此目錄映射到容器內的 `/app/logs` 目錄。
EOF
    echo "[OK] 建立日誌說明: $README_FILE"
fi

# 顯示目錄結構
echo ""
echo "目錄結構預覽:"
echo "=================="

if command -v tree >/dev/null 2>&1; then
    tree -a -I '.git' --dirsfirst -L 3
else
    find . -type d -not -path './.git*' | head -20 | sort
fi

echo ""
echo "目錄初始化完成！"
echo ""
echo "接下來的步驟:"
echo "1. 執行 Docker Compose: docker-compose up -d"
echo "2. 檢查日誌檔案: ls -la logs/"
echo "3. 即時查看日誌: tail -f logs/tradingagents.log"
echo ""
echo "重要目錄說明:"
echo "   logs/     - 應用日誌檔案"
echo "   data/     - 資料快取和匯出檔案"
echo "   config/   - 執行時配置檔案"
echo ""
echo "如果遇到權限問題，請執行:"
echo "   sudo chown -R \$USER:\$USER logs data config"
