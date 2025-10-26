#!/bin/bash
# 上游贡献Git工作流腳本
# 自動化處理Fork、分支管理、PR準备等任務

set -e

# 配置變量
UPSTREAM_REPO="https://github.com/TauricResearch/TradingAgents.git"
FORK_REPO="https://github.com/YOUR_USERNAME/TradingAgents.git"  # 需要替換為實际的Fork地址
WORK_DIR="./upstream_work"
CONTRIBUTION_DIR="./upstream_contribution"

# 颜色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日誌函數
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 檢查依賴
check_dependencies() {
    log_info "Checking dependencies..."
    
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 is not installed"
        exit 1
    fi
    
    log_success "All dependencies are available"
}

# 設置上游仓庫
setup_upstream_repo() {
    log_info "Setting up upstream repository..."
    
    if [ -d "$WORK_DIR" ]; then
        log_warning "Work directory already exists, removing..."
        rm -rf "$WORK_DIR"
    fi
    
    # Clone上游仓庫
    git clone "$UPSTREAM_REPO" "$WORK_DIR"
    cd "$WORK_DIR"
    
    # 添加Fork作為远程仓庫
    git remote add fork "$FORK_REPO"
    
    # 獲取最新代碼
    git fetch origin
    git fetch fork
    
    log_success "Upstream repository setup completed"
}

# 創建功能分支
create_feature_branch() {
    local batch_name=$1
    local branch_name="feature/${batch_name}"
    
    log_info "Creating feature branch: $branch_name"
    
    cd "$WORK_DIR"
    
    # 確保在main分支
    git checkout main
    git pull origin main
    
    # 創建新分支
    git checkout -b "$branch_name"
    
    log_success "Feature branch $branch_name created"
}

# 應用贡献代碼
apply_contribution() {
    local batch_name=$1
    local batch_dir="../$CONTRIBUTION_DIR/$batch_name"
    
    log_info "Applying contribution: $batch_name"
    
    if [ ! -d "$batch_dir" ]; then
        log_error "Batch directory not found: $batch_dir"
        return 1
    fi
    
    cd "$WORK_DIR"
    
    # 複制文件
    while IFS= read -r -d '' file; do
        local rel_path=$(realpath --relative-to="$batch_dir" "$file")
        local target_path="$rel_path"
        
        # 跳過文档文件
        if [[ "$rel_path" == *.md ]] || [[ "$rel_path" == *.json ]]; then
            continue
        fi
        
        # 確保目標目錄存在
        mkdir -p "$(dirname "$target_path")"
        
        # 複制文件
        cp "$file" "$target_path"
        log_info "Copied: $rel_path"
        
    done < <(find "$batch_dir" -type f -print0)
    
    log_success "Contribution $batch_name applied"
}

# 運行測試
run_tests() {
    log_info "Running tests..."
    
    cd "$WORK_DIR"
    
    # 安裝依賴
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    fi
    
    # 運行測試
    if [ -d "tests" ]; then
        python3 -m pytest tests/ -v
        if [ $? -eq 0 ]; then
            log_success "All tests passed"
        else
            log_error "Some tests failed"
            return 1
        fi
    else
        log_warning "No tests directory found"
    fi
}

# 提交更改
commit_changes() {
    local batch_name=$1
    local batch_info=$2
    
    log_info "Committing changes for $batch_name"
    
    cd "$WORK_DIR"
    
    # 添加所有更改
    git add .
    
    # 檢查是否有更改
    if git diff --cached --quiet; then
        log_warning "No changes to commit"
        return 0
    fi
    
    # 提交更改
    local commit_message="feat: $batch_info

- Add intelligent caching system
- Improve error handling
- Enhance performance and reliability
- Maintain backward compatibility

Resolves: #XXX"
    
    git commit -m "$commit_message"
    
    log_success "Changes committed"
}

# 推送到Fork
push_to_fork() {
    local branch_name=$1
    
    log_info "Pushing to fork: $branch_name"
    
    cd "$WORK_DIR"
    
    git push fork "$branch_name"
    
    log_success "Pushed to fork"
}

# 生成PR信息
generate_pr_info() {
    local batch_name=$1
    local batch_dir="../$CONTRIBUTION_DIR/$batch_name"
    
    log_info "Generating PR information..."
    
    if [ -f "$batch_dir/PR_TEMPLATE.md" ]; then
        echo "PR Template:"
        echo "============"
        cat "$batch_dir/PR_TEMPLATE.md"
        echo ""
    fi
    
    echo "Branch: feature/${batch_name}"
    echo "Base: main"
    echo "Compare: YOUR_USERNAME:feature/${batch_name}"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://github.com/TauricResearch/TradingAgents"
    echo "2. Click 'New Pull Request'"
    echo "3. Select your fork and branch"
    echo "4. Use the PR template above"
    echo "5. Submit the PR"
}

# 處理單個批次
process_batch() {
    local batch_name=$1
    local batch_info=$2
    local branch_name="feature/${batch_name}"
    
    log_info "Processing batch: $batch_name"
    echo "Description: $batch_info"
    echo ""
    
    # 創建分支
    create_feature_branch "$batch_name"
    
    # 應用贡献
    apply_contribution "$batch_name"
    
    # 運行測試
    if ! run_tests; then
        log_error "Tests failed for $batch_name"
        return 1
    fi
    
    # 提交更改
    commit_changes "$batch_name" "$batch_info"
    
    # 推送到Fork
    push_to_fork "$branch_name"
    
    # 生成PR信息
    generate_pr_info "$batch_name"
    
    log_success "Batch $batch_name processed successfully"
}

# 主函數
main() {
    echo "🚀 Upstream Contribution Git Workflow"
    echo "====================================="
    echo ""
    
    # 檢查參數
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <batch_name> [batch_info]"
        echo ""
        echo "Available batches:"
        echo "  batch1_caching - Intelligent Caching System"
        echo "  batch2_error_handling - Error Handling Improvements"
        echo "  batch3_data_sources - US Data Source Optimization"
        echo ""
        echo "Example:"
        echo "  $0 batch1_caching 'Add intelligent caching system'"
        exit 1
    fi
    
    local batch_name=$1
    local batch_info=${2:-"Contribution batch $batch_name"}
    
    # 檢查依賴
    check_dependencies
    
    # 設置仓庫
    setup_upstream_repo
    
    # 處理批次
    process_batch "$batch_name" "$batch_info"
    
    echo ""
    log_success "Workflow completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Review the generated PR information above"
    echo "2. Create the Pull Request on GitHub"
    echo "3. Respond to reviewer feedback"
    echo "4. Iterate until merged"
}

# 運行主函數
main "$@"
