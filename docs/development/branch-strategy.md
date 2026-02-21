# 

## 

### 

```
main ()
 develop ()
 feature/* ()
 enhancement/* ()
 hotfix/* ()
 release/* ()
 upstream-sync/* ()
```

### 

#### **main** - 
- ****: 
- ****: PR
- ****: develophotfixupstream-sync
- ****: 

#### **develop** - 
- ****: 
- ****: PR
- ****: featureenhancement
- ****: 

#### **feature/** - 
- ****: `feature/`
- ****: 
- ****: 1-2
- ****: `feature/portfolio-optimization`

#### **enhancement/** - 
- ****: `enhancement/`
- ****: 
- ****: 2-4
- ****: `enhancement/chinese-llm-integration`

#### **hotfix/** - 
- ****: `hotfix/`
- ****: Bug
- ****: 1-3
- ****: `hotfix/api-timeout-fix`

#### **release/** - 
- ****: `release/`
- ****: 
- ****: 3-7
- ****: `release/v1.1.0-cn`

#### **upstream-sync/** - 
- ****: `upstream-sync/`
- ****: 
- ****: 1
- ****: `upstream-sync/20240115`

## 

### 

```mermaid
graph LR
 A[main] --> B[develop]
 B --> C[feature/new-feature]
 C --> D[]
 D --> E[PR to develop]
 E --> F[]
 F --> G[develop]
 G --> H[]
 H --> I[PR to main]
 I --> J[]
```

### 

```mermaid
graph LR
 A[develop] --> B[enhancement/chinese-feature]
 B --> C[]
 C --> D[]
 D --> E[]
 E --> F[PR to develop]
 F --> G[]
```

### 

```mermaid
graph LR
 A[main] --> B[hotfix/urgent-fix]
 B --> C[]
 C --> D[]
 D --> E[PR to main]
 E --> F[]
 F --> G[develop]
```

## 

### 

```bash
# develop
git checkout develop
git pull origin develop
git checkout -b feature/portfolio-analysis

# 
git push -u origin feature/portfolio-analysis
```

### 

```bash
# develop
git checkout develop
git pull origin develop
git checkout -b enhancement/finnhub-enhancement

# 
git push -u origin enhancement/finnhub-enhancement
```

### 

```bash
# main
git checkout main
git pull origin main
git checkout -b hotfix/api-error-fix

# 
git push -u origin hotfix/api-error-fix
```

## 

### main
- PR
- 
- 
- 
- 

### develop
- PR
- CI
- 

### 
- 
- 

## 

### 

```bash
# 
feature/-
feature/chinese-data-source
feature/risk-management-enhancement

# 
enhancement/-
enhancement/llm-baidu-integration
enhancement/chinese-financial-terms

# Bug
hotfix/
hotfix/memory-leak-fix
hotfix/config-loading-error

# 
release/
release/v1.1.0-cn
release/v1.2.0-cn-beta
```

### 

```bash
# 
feat(agents): 
feat(data): FinnHub

# 
enhance(llm): LLM API
enhance(docs): 

# Bug
fix(api): API
fix(config): 

# 
docs(readme): 
docs(api): API
```

## 

### 

#### feature
- > 80%
- 
- 

#### enhancement
- 
- 
- 

#### develop
- 
- 
- 

#### main
- 
- 
- 

## 

### 

```bash
# 
git branch -a --merged # 
git branch -a --no-merged # 

# 
git log develop..main --oneline
git log feature/branch..develop --oneline

# 
git rev-list --count develop..feature/branch
```

### 

```bash
# 
git branch --merged develop | grep -v "develop\|main" | xargs -n 1 git branch -d

# 
git remote prune origin

# 
git for-each-ref --format='%(refname:short) %(committerdate)' refs/heads | awk '$2 <= "'$(date -d '30 days ago' '+%Y-%m-%d')'"' | cut -d' ' -f1
```

## 

### 

1. ****
 ```bash
 git checkout develop
 git pull origin develop
 git checkout -b release/v1.1.0-cn
 ```

2. ****
 ```bash
 # 
 # CHANGELOG.md
 # 
 ```

3. **main**
 ```bash
 git checkout main
 git merge release/v1.1.0-cn
 git tag v1.1.0-cn
 git push origin main --tags
 ```

4. **develop**
 ```bash
 git checkout develop
 git merge main
 git push origin develop
 ```

## 

### Git Hooks

```bash
# pre-commit hook
#!/bin/sh
# 
black --check .
flake8 .

# pre-push hook
#!/bin/sh
# 
python -m pytest tests/
```

### GitHub Actions

```yaml
# 
on:
 pull_request:
 branches: [main, develop]
 
jobs:
 test:
 runs-on: ubuntu-latest
 steps:
 - uses: actions/checkout@v4
 - name: Run tests
 run: python -m pytest
```

## 

### 1. 

#### 
```bash
# 1: 
python scripts/branch_manager.py create feature portfolio-optimization -d ""

# 2: 
# ...
git add .
git commit -m "feat: "

# 3: develop
git fetch origin
git merge origin/develop # git rebase origin/develop

# 4: 
git push origin feature/portfolio-optimization

# 5: Pull Request
# GitHubPR: feature/portfolio-optimization -> develop
# PR

# 6: 
# 

# 7: 
# PR
python scripts/branch_manager.py delete feature/portfolio-optimization
```

#### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

### 2. 

#### 
```bash
# 1: 
python scripts/branch_manager.py create enhancement finnhub-integration -d "FinnHub"

# 2: 
# 
git add tradingagents/dataflows/yfin_utils.py
git commit -m "enhance(data): Yahoo Finance"

# 
git add config/market_config.yaml
git commit -m "enhance(config): "

# 3: 
git add docs/data/finnhub-integration.md
git commit -m "docs: FinnHub"

# 4: 
python -m pytest tests/test_finnhub_connection.py
git add tests/test_finnhub_connection.py
git commit -m "test: FinnHub"

# 5: 
git push origin enhancement/finnhub-integration
# PRdevelop
```

#### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

### 3. 

#### Bug
```bash
# 1: main
python scripts/branch_manager.py create hotfix api-timeout-fix -d "API"

# 2: 
# 
# 
git add tradingagents/api/client.py
git commit -m "fix: API"

# 3: 
python -m pytest tests/test_api_client.py -v
# 

# 4: main
git push origin hotfix/api-timeout-fix
# PRmain

# 5: develop
git checkout develop
git merge main
git push origin develop
```

#### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

### 4. 

#### 
```bash
# 1: 
python scripts/branch_manager.py create release v1.1.0-cn -d "v1.1.0"

# 2: 
# 
echo "1.1.0-cn" > VERSION
git add VERSION
git commit -m "bump: v1.1.0-cn"

# 
git add CHANGELOG.md
git commit -m "docs: v1.1.0-cn"

# 
python -m pytest tests/ --cov=tradingagents
python examples/full_test.py

# 3: main
git checkout main
git merge release/v1.1.0-cn
git tag v1.1.0-cn
git push origin main --tags

# 4: develop
git checkout develop
git merge main
git push origin develop

# 5: 
python scripts/branch_manager.py delete release/v1.1.0-cn
```

#### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

### 5. 

#### 
```bash
# 1: 
python scripts/sync_upstream.py

# 2: 
# upstream-sync/20240115

# 3: 
# 
# 

# 4: 
python -m pytest tests/
python examples/basic_example.py

# 5: 
git checkout main
git merge upstream-sync/20240115
git push origin main

# 6: develop
git checkout develop
git merge main
git push origin develop
```

## 

### 

1. **** - 
2. **** - 
3. **** - develop
4. **** - 
5. **** - 

### 

1. **PR** - PR
2. **** - 
3. **** - 
4. **** - 
5. **** - 

### 

1. **** - PRCI
2. **** - 80%
3. **** - 
4. **** - 
5. **** - 


