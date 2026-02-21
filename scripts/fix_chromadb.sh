#!/bin/bash
# ChromaDB  (Linux/Mac)
#  "Configuration error: An instance of Chroma already exists for ephemeral with different settings" 

echo "=== ChromaDB  ==="
echo ": Linux/Mac Bash"
echo ""

# 1. PythonChromaDB
echo "1. Python..."
python_pids=$(pgrep -f python)
if [ ! -z "$python_pids" ]; then
echo "Python:"
ps aux | grep python | grep -v grep
echo ""
read -p "Python? (y/N): " choice
if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
pkill -f python
echo " Python"
sleep 2
fi
else
echo " Python"
fi

# 2. ChromaDB
echo ""
echo "2. ChromaDB..."

# ChromaDB
temp_paths=(
"/tmp/chroma*"
"$HOME/.chroma*"
"./chroma*"
"./.chroma*"
)

cleaned_files=0
for path in "${temp_paths[@]}"; do
if ls $path 1> /dev/null 2>&1; then
echo ": $path"
rm -rf $path 2>/dev/null || echo " : $path"
((cleaned_files++))
fi
done

if [ $cleaned_files -gt 0 ]; then
echo "  $cleaned_files ChromaDB"
else
echo " ChromaDB"
fi

# 3. Python
echo ""
echo "3. Python..."
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
echo ": $path"
((cleaned_cache++))
fi
done

if [ $cleaned_cache -gt 0 ]; then
echo "  $cleaned_cache Python"
else
echo " Python"
fi

# 4. ChromaDB
echo ""
echo "4. ChromaDB..."
chroma_version=$(python -c "import chromadb; print(chromadb.__version__)" 2>/dev/null)
if [ ! -z "$chroma_version" ]; then
echo "ChromaDB: $chroma_version"
    
# 
if [[ "$chroma_version" == 1.0.* ]]; then
echo " ChromaDB"
else
echo " ChromaDB 1.0.x"
read -p "ChromaDB? (y/N): " upgrade
if [[ "$upgrade" == "y" || "$upgrade" == "Y" ]]; then
echo "ChromaDB..."
pip install --upgrade "chromadb>=1.0.12"
fi
fi
else
echo " ChromaDB"
fi

# 5. 
echo ""
echo "5. ..."
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
echo "ChromaDB:"
for var in "${found_env_vars[@]}"; do
echo "  $var"
done
echo " "
else
echo " ChromaDB"
fi

# 6. ChromaDB
echo ""
echo "6. ChromaDB..."
test_script='
import chromadb
from chromadb.config import Settings
import sys

try:
# 
client = chromadb.Client()
print(" ")
    
# 
settings = Settings(
allow_reset=True,
anonymized_telemetry=False,
is_persistent=False
)
client2 = chromadb.Client(settings)
print(" ")
    
# 
collection = client2.create_collection(name="test_collection")
print(" ")
    
# 
client2.delete_collection(name="test_collection")
print(" ChromaDB")
    
except Exception as e:
print(f" ChromaDB: {e}")
sys.exit(1)
'

python -c "$test_script" 2>&1

# 7. 
echo ""
echo "===  ==="
echo ":"
echo ""
echo "1: "
echo "  - ChromaDB"
echo ""
echo "2: "
echo "  python -m venv fresh_env"
echo "  source fresh_env/bin/activate"
echo "  pip install -r requirements.txt"
echo ""
echo "3: ChromaDB"
echo "  pip uninstall chromadb -y"
echo "  pip install chromadb==1.0.12"
echo ""
echo "4: Python"
echo "  - Python 3.8-3.11"
echo "  - Python 3.12+"
echo ""

echo " "