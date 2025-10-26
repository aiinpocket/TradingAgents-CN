# GitHub 分支保護規則設置指南

## 🎯 目標
為 `main` 分支設置嚴格的保護規則，防止未經測試的代碼直接推送到生產分支。

## 📋 設置步骤

### 1. 訪問仓庫設置
1. 打開 GitHub 仓庫：`https://github.com/hsliuping/TradingAgents-CN`
2. 點擊 **Settings** 標簽页
3. 在左侧菜單中選擇 **Branches**

### 2. 添加分支保護規則
1. 點擊 **Add rule** 按钮
2. 在 **Branch name pattern** 中輸入：`main`

### 3. 配置保護規則

#### 🔒 基础保護設置
- [x] **Require a pull request before merging**
  - [x] **Require approvals**: 設置為 `1`
  - [x] **Dismiss stale PR approvals when new commits are pushed**
  - [x] **Require review from code owners** (如果有 CODEOWNERS 文件)

#### 🧪 狀態檢查設置
- [x] **Require status checks to pass before merging**
  - [x] **Require branches to be up to date before merging**
  - 添加必需的狀態檢查（如果有 CI/CD 配置）：
    - [ ] `continuous-integration`
    - [ ] `build`
    - [ ] `test`

#### 🛡️ 高級保護設置
- [x] **Require conversation resolution before merging**
- [x] **Require signed commits**
- [x] **Require linear history**
- [x] **Include administrators** ⚠️ **重要：確保管理員也遵守規則**

#### 🚫 限制設置
- [x] **Restrict pushes that create files**
- [x] **Restrict force pushes**
- [x] **Allow deletions**: **取消勾選** ⚠️ **重要：防止意外刪除**

### 4. 保存設置
點擊 **Create** 按钮保存分支保護規則。

## 🔧 高級配置（可選）

### 自動合並設置
如果需要自動合並功能：
- [x] **Allow auto-merge**
- 配置合並策略：
  - [ ] Allow merge commits
  - [x] Allow squash merging
  - [ ] Allow rebase merging

### 刪除头分支
- [x] **Automatically delete head branches**

## 📊 狀態檢查配置

### 添加 GitHub Actions 工作流
在 `.github/workflows/` 目錄下創建 CI/CD 配置：

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          python -m pytest tests/
      - name: Check code style
        run: |
          python scripts/syntax_checker.py
```

## 🚨 緊急情况處理

### 臨時禁用保護規則
1. 訪問 **Settings** > **Branches**
2. 找到 `main` 分支規則
3. 點擊 **Edit** 
4. 臨時取消勾選相關保護選項
5. **操作完成後立即重新啟用！**

### 管理員绕過保護
即使啟用了 "Include administrators"，仓庫所有者仍可以：
1. 臨時修改分支保護規則
2. 使用 `--force-with-lease` 强制推送
3. **强烈建议**: 建立內部審批流程，即使是管理員也要遵守

## 📝 保護規則驗證

### 測試保護規則是否生效
```bash
# 1. 嘗試直接推送到 main（應该被拒絕）
git checkout main
echo "test" > test.txt
git add test.txt
git commit -m "test commit"
git push origin main  # 應该失败

# 2. 通過 PR 流程（正確方式）
git checkout -b test-protection
git push origin test-protection
# 在 GitHub 上創建 PR 到 main 分支
```

## 🎯 最佳實踐建议

### 1. 渐進式實施
- 先在測試仓庫驗證規則
- 逐步增加保護級別
- 团隊培训和適應

### 2. 監控和審計
- 定期檢查保護規則設置
- 監控嘗試绕過保護的行為
- 記錄所有强制推送操作

### 3. 文档和培训
- 為团隊提供工作流培训
- 維護最新的操作指南
- 建立問題報告機制

## 🔗 相關資源

- [GitHub 分支保護官方文档](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub Actions 工作流語法](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [代碼審查最佳實踐](https://github.com/features/code-review/)

---

**重要提醒：分支保護規則是防止意外的最後一道防線，但不能替代良好的開發习惯和流程！**