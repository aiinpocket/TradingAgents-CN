#!/bin/bash
# ChromaDB 問題診斷和修複腳本 (Linux/Mac版本)
# 用於解決 "Configuration error: An instance of Chroma already exists for ephemeral with different settings" 錯誤

echo "=== ChromaDB 問題診斷和修複工具 ==="
echo "適用環境: Linux/Mac Bash"
echo ""

# 1. 檢查Python進程中的ChromaDB實例
echo "1. 檢查Python進程..."
python_pids=$(pgrep -f python)
if [ ! -z "$python_pids" ]; then
    echo "發現Python進程:"
    ps aux | grep python | grep -v grep
    echo ""
    read -p "是否终止所有Python進程? (y/N): " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        pkill -f python
        echo "✅ 已终止所有Python進程"
        sleep 2
    fi
else
    echo "✅ 未發現Python進程"
fi

# 2. 清理ChromaDB臨時文件和緩存
echo ""
echo "2. 清理ChromaDB臨時文件..."

# 清理臨時目錄中的ChromaDB文件
temp_paths=(
    "/tmp/chroma*"
    "$HOME/.chroma*"
    "./chroma*"
    "./.chroma*"
)

cleaned_files=0
for path in "${temp_paths[@]}"; do
    if ls $path 1> /dev/null 2>&1; then
        echo "清理: $path"
        rm -rf $path 2>/dev/null || echo "⚠️ 無法刪除: $path"
        ((cleaned_files++))
    fi
done

if [ $cleaned_files -gt 0 ]; then
    echo "✅ 已清理 $cleaned_files 個ChromaDB臨時文件"
else
    echo "✅ 未發現ChromaDB臨時文件"
fi

# 3. 清理Python緩存
echo ""
echo "3. 清理Python緩存..."
pycache_paths=(
    "./__pycache__"
    "./tradingagents/__pycache__"
    "./tradingagents/agents/__pycache__"
    "./tradingagents/agents/utils/__pycache__"
)

cleaned_cache=0
for path in "${pycache_paths[@]}"; do
    if [ -d "$path" ]; then
        rm -rf "$path"
        echo "清理: $path"
        ((cleaned_cache++))
    fi
done

if [ $cleaned_cache -gt 0 ]; then
    echo "✅ 已清理 $cleaned_cache 個Python緩存目錄"
else
    echo "✅ 未發現Python緩存目錄"
fi

# 4. 檢查ChromaDB版本兼容性
echo ""
echo "4. 檢查ChromaDB版本..."
chroma_version=$(python -c "import chromadb; print(chromadb.__version__)" 2>/dev/null)
if [ ! -z "$chroma_version" ]; then
    echo "ChromaDB版本: $chroma_version"
    
    # 檢查是否為推薦版本
    if [[ "$chroma_version" == 1.0.* ]]; then
        echo "✅ ChromaDB版本兼容"
    else
        echo "⚠️ 建议使用ChromaDB 1.0.x版本"
        read -p "是否升級ChromaDB? (y/N): " upgrade
        if [[ "$upgrade" == "y" || "$upgrade" == "Y" ]]; then
            echo "升級ChromaDB..."
            pip install --upgrade "chromadb>=1.0.12"
        fi
    fi
else
    echo "❌ 無法檢測ChromaDB版本"
fi

# 5. 檢查環境變量冲突
echo ""
echo "5. 檢查環境變量..."
chroma_env_vars=(
    "CHROMA_HOST"
    "CHROMA_PORT"
    "CHROMA_DB_IMPL"
    "CHROMA_API_IMPL"
    "CHROMA_TELEMETRY"
)

found_env_vars=()
for var in "${chroma_env_vars[@]}"; do
    value=$(printenv $var)
    if [ ! -z "$value" ]; then
        found_env_vars+=("$var=$value")
    fi
done

if [ ${#found_env_vars[@]} -gt 0 ]; then
    echo "發現ChromaDB環境變量:"
    for var in "${found_env_vars[@]}"; do
        echo "  $var"
    done
    echo "⚠️ 這些環境變量可能導致配置冲突"
else
    echo "✅ 未發現ChromaDB環境變量冲突"
fi

# 6. 測試ChromaDB初始化
echo ""
echo "6. 測試ChromaDB初始化..."
test_script='
import chromadb
from chromadb.config import Settings
import sys

try:
    # 測試基本初始化
    client = chromadb.Client()
    print("✅ 基本初始化成功")
    
    # 測試項目配置
    settings = Settings(
        allow_reset=True,
        anonymized_telemetry=False,
        is_persistent=False
    )
    client2 = chromadb.Client(settings)
    print("✅ 項目配置初始化成功")
    
    # 測試集合創建
    collection = client2.create_collection(name="test_collection")
    print("✅ 集合創建成功")
    
    # 清理測試
    client2.delete_collection(name="test_collection")
    print("✅ ChromaDB測試完成")
    
except Exception as e:
    print(f"❌ ChromaDB測試失败: {e}")
    sys.exit(1)
'

python -c "$test_script" 2>&1

# 7. 提供解決方案建议
echo ""
echo "=== 解決方案建议 ==="
echo "如果問題仍然存在，請嘗試以下方案:"
echo ""
echo "方案1: 重啟系統"
echo "  - 完全清理內存中的ChromaDB實例"
echo ""
echo "方案2: 使用虛擬環境"
echo "  python -m venv fresh_env"
echo "  source fresh_env/bin/activate"
echo "  pip install -r requirements.txt"
echo ""
echo "方案3: 重新安裝ChromaDB"
echo "  pip uninstall chromadb -y"
echo "  pip install chromadb==1.0.12"
echo ""
echo "方案4: 檢查Python版本兼容性"
echo "  - 確保使用Python 3.8-3.11"
echo "  - 避免使用Python 3.12+"
echo ""

echo "🔧 修複完成！請重新運行應用程序。"