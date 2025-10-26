#!/bin/bash
# 設置Fork環境的腳本

set -e

# 配置變量
UPSTREAM_REPO="https://github.com/TauricResearch/TradingAgents.git"
FORK_REPO="https://github.com/hsliuping/TradingAgents.git"
LOCAL_DIR="TradingAgents-Fork"
TRADINGAGENTS_CN_DIR="../TradingAgentsCN"  # 假設TradingAgents-CN在上級目錄

# 颜色輸出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 設置TradingAgents Fork開發環境${NC}"
echo "=================================="

# 1. 克隆Fork仓庫
echo -e "${YELLOW}📥 克隆Fork仓庫...${NC}"
if [ -d "$LOCAL_DIR" ]; then
    echo "目錄已存在，刪除旧目錄..."
    rm -rf "$LOCAL_DIR"
fi

git clone "$FORK_REPO" "$LOCAL_DIR"
cd "$LOCAL_DIR"

# 2. 添加上游仓庫
echo -e "${YELLOW}🔗 添加上游仓庫...${NC}"
git remote add upstream "$UPSTREAM_REPO"
git remote -v

# 3. 獲取最新代碼
echo -e "${YELLOW}📡 獲取最新代碼...${NC}"
git fetch upstream
git fetch origin

# 4. 確保main分支是最新的
echo -e "${YELLOW}🔄 同步main分支...${NC}"
git checkout main
git merge upstream/main
git push origin main

# 5. 創建開發分支
echo -e "${YELLOW}🌿 創建開發分支...${NC}"
git checkout -b feature/intelligent-caching
git push -u origin feature/intelligent-caching

echo -e "${GREEN}✅ Fork環境設置完成！${NC}"
echo ""
echo "下一步："
echo "1. 準备贡献代碼"
echo "2. 創建GitHub Issue討論"
echo "3. 提交Pull Request"
echo ""
echo "當前分支: feature/intelligent-caching"
echo "远程仓庫:"
git remote -v
