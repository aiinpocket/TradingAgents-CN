#!/bin/bash
# TradingAgents 目錄初始化腳本
# 創建Docker容器需要的本地目錄結構

echo "🚀 TradingAgents 目錄初始化"
echo "=========================="

# 獲取腳本所在目錄的父目錄（項目根目錄）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📁 項目根目錄: $PROJECT_ROOT"

# 創建必要的目錄
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
echo "📂 創建目錄結構..."

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "✅ 創建目錄: $dir"
    else
        echo "📁 目錄已存在: $dir"
    fi
done

# 設置目錄權限
echo ""
echo "🔧 設置目錄權限..."

# 確保日誌目錄可寫
chmod 755 logs
echo "✅ 設置 logs 目錄權限: 755"

# 確保數據目錄可寫
chmod 755 data
chmod 755 data/cache
chmod 755 data/exports
chmod 755 data/temp
echo "✅ 設置 data 目錄權限: 755"

# 確保配置目錄可寫
chmod 755 config
chmod 755 config/runtime
echo "✅ 設置 config 目錄權限: 755"

# 創建 .gitkeep 文件保持目錄結構
echo ""
echo "📝 創建 .gitkeep 文件..."

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
        echo "✅ 創建: $dir/.gitkeep"
    fi
done

# 創建日誌配置文件
echo ""
echo "📋 創建日誌配置文件..."

LOG_CONFIG_FILE="config/logging.toml"
if [ ! -f "$LOG_CONFIG_FILE" ]; then
    cat > "$LOG_CONFIG_FILE" << 'EOF'
# TradingAgents 日誌配置文件
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

[logging.loggers.akshare]
level = "WARNING"
handlers = ["file"]
propagate = false

[logging.loggers.tushare]
level = "WARNING"
handlers = ["file"]
propagate = false

[logging.root]
level = "INFO"
handlers = ["console", "file"]
EOF
    echo "✅ 創建日誌配置: $LOG_CONFIG_FILE"
else
    echo "📁 日誌配置已存在: $LOG_CONFIG_FILE"
fi

# 創建 .gitignore 文件
echo ""
echo "📝 更新 .gitignore 文件..."

GITIGNORE_ENTRIES=(
    "# 日誌文件"
    "logs/*.log"
    "logs/*.log.*"
    ""
    "# 數據緩存"
    "data/cache/*"
    "data/temp/*"
    "!data/cache/.gitkeep"
    "!data/temp/.gitkeep"
    ""
    "# 運行時配置"
    "config/runtime/*"
    "!config/runtime/.gitkeep"
    ""
    "# 導出文件"
    "data/exports/*.pdf"
    "data/exports/*.docx"
    "data/exports/*.xlsx"
    "!data/exports/.gitkeep"
)

# 檢查 .gitignore 是否存在
if [ ! -f ".gitignore" ]; then
    touch ".gitignore"
fi

# 添加條目到 .gitignore（如果不存在）
for entry in "${GITIGNORE_ENTRIES[@]}"; do
    if [ -n "$entry" ] && ! grep -Fxq "$entry" .gitignore; then
        echo "$entry" >> .gitignore
    fi
done

echo "✅ 更新 .gitignore 文件"

# 創建 README 文件
echo ""
echo "📚 創建目錄說明文件..."

README_FILE="logs/README.md"
if [ ! -f "$README_FILE" ]; then
    cat > "$README_FILE" << 'EOF'
# TradingAgents 日誌目錄

此目錄用於存储 TradingAgents 應用的日誌文件。

## 日誌文件說明

- `tradingagents.log` - 主應用日誌文件
- `tradingagents_error.log` - 錯誤日誌文件
- `tradingagents.log.1`, `tradingagents.log.2` 等 - 轮轉的歷史日誌文件

## 日誌級別

- **DEBUG** - 詳細的調試信息
- **INFO** - 一般信息
- **WARNING** - 警告信息
- **ERROR** - 錯誤信息
- **CRITICAL** - 嚴重錯誤

## 日誌轮轉

- 主日誌文件最大 100MB，保留 5 個歷史文件
- 錯誤日誌文件最大 50MB，保留 3 個歷史文件

## 獲取日誌

如果遇到問題需要發送日誌給開發者，請發送：
1. `tradingagents.log` - 主日誌文件
2. `tradingagents_error.log` - 錯誤日誌文件（如果存在）

## Docker 環境

在 Docker 環境中，此目錄映射到容器內的 `/app/logs` 目錄。
EOF
    echo "✅ 創建日誌說明: $README_FILE"
fi

# 顯示目錄結構
echo ""
echo "📋 目錄結構預覽:"
echo "=================="

if command -v tree >/dev/null 2>&1; then
    tree -a -I '.git' --dirsfirst -L 3
else
    find . -type d -not -path './.git*' | head -20 | sort
fi

echo ""
echo "🎉 目錄初始化完成！"
echo ""
echo "💡 接下來的步骤:"
echo "1. 運行 Docker Compose: docker-compose up -d"
echo "2. 檢查日誌文件: ls -la logs/"
echo "3. 實時查看日誌: tail -f logs/tradingagents.log"
echo ""
echo "📁 重要目錄說明:"
echo "   logs/     - 應用日誌文件"
echo "   data/     - 數據緩存和導出文件"
echo "   config/   - 運行時配置文件"
echo ""
echo "🔧 如果遇到權限問題，請運行:"
echo "   sudo chown -R \$USER:\$USER logs data config"
