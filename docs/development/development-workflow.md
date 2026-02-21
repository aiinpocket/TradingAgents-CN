# 

## 

 TradingAgents 

## 

### 

```mermaid
graph TD
 A[] --> B[]
 B --> C[]
 C --> D[]
 D --> E[]
 E --> F[]
 F --> G{?}
 G -->|| C
 G -->|| H[develop]
 H --> I[]
 I --> J{?}
 J -->|| K[]
 K --> C
 J -->|| L[]
 L --> M[main]
 M --> N[]
```

## 

### 1. 

#### 1.1 
```bash
# 
# 1. Issue
# 2. 
# 3. 
# 4. 
```

#### 1.2 
```bash
# develop
git checkout develop
git pull origin develop

# 
python scripts/branch_manager.py create feature risk-management-v2 -d ""

# 
git branch --show-current
# : feature/risk-management-v2
```

#### 1.3 
```bash
# 
# 1. 
git add tradingagents/risk/manager_v2.py
git commit -m "feat(risk): "

# 2. 
git add config/risk_management_v2.yaml
git commit -m "feat(config): v2"

# 3. 
git add tradingagents/graph/trading_graph.py
git commit -m "feat(graph): v2"

# develop
git fetch origin
git rebase origin/develop # merge
```

#### 1.4 
```bash
# 
git add tests/risk/test_manager_v2.py
git commit -m "test(risk): v2"

# 
git add tests/integration/test_risk_integration.py
git commit -m "test(integration): "

# 
python -m pytest tests/risk/ -v
python -m pytest tests/integration/test_risk_integration.py -v
```

#### 1.5 
```bash
# API
git add docs/api/risk-management.md
git commit -m "docs(api): API"

# 
git add examples/risk_management_example.py
git commit -m "docs(examples): "

# 
git add docs/configuration/risk-config.md
git commit -m "docs(config): "
```

#### 1.6 
```bash
# 
git push origin feature/risk-management-v2

# Pull Request
# 1. GitHub
# 2. PR: feature/risk-management-v2 -> develop
# 3. PR
# 4. 
# 5. 

# 
git add .
git commit -m "fix(risk): "
git push origin feature/risk-management-v2
```

### 2. 

#### 2.1 
```bash
# 
python scripts/branch_manager.py create enhancement finnhub-integration -d "FinnHub"

# 
git add tradingagents/dataflows/yfin_utils.py
git commit -m "enhance(data): Yahoo Finance"

# 
git add tradingagents/utils/stock_utils.py
git commit -m "enhance(utils): "

# 
git add config/market_config/
git commit -m "enhance(config): "
```

#### 2.2 
```bash
# 
git add docs/data/finnhub-integration.md
git commit -m "docs: FinnHub"

# 
git add examples/chinese_market_analysis.py
git commit -m "examples: "

# FAQ
git add docs/faq/chinese-features-faq.md
git commit -m "docs: "
```

### 3. 

#### 3.1 
```bash
# 1. 
# 2. 
# 3. 
# 4. 
```

#### 3.2 
```bash
# main
git checkout main
git pull origin main
python scripts/branch_manager.py create hotfix memory-leak-fix -d ""

# 
git add tradingagents/core/memory_manager.py
git commit -m "fix: "

# 
python -m pytest tests/core/test_memory_manager.py -v
python tests/manual/memory_leak_test.py
```

#### 3.3 
```bash
# 
git push origin hotfix/memory-leak-fix

# PRmain
# 

# develop
git checkout develop
git merge main
git push origin develop
```

### 4. 

#### 4.1 
```bash
# 
python scripts/branch_manager.py create release v1.2.0-cn -d "v1.2.0"

# 
echo "1.2.0-cn" > VERSION
git add VERSION
git commit -m "bump: v1.2.0-cn"

# 
# CHANGELOG.md
git add CHANGELOG.md
git commit -m "docs: v1.2.0-cn"
```

#### 4.2 
```bash
# 
python -m pytest tests/ --cov=tradingagents --cov-report=html

# 
python tests/performance/benchmark_test.py

# 
python examples/full_integration_test.py

# 
# 
```

#### 4.3 
```bash
# main
git checkout main
git merge release/v1.2.0-cn

# 
git tag -a v1.2.0-cn -m "TradingAgents v1.2.0"
git push origin main --tags

# develop
git checkout develop
git merge main
git push origin develop

# 
python scripts/branch_manager.py delete release/v1.2.0-cn
```

## 

### 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 80%
- [ ] ****: 
- [ ] ****: API
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 

### 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 

### 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 
- [ ] ****: 

## 

### 
```bash
# 
python scripts/branch_manager.py

# 
python scripts/sync_upstream.py

# 
black tradingagents/
flake8 tradingagents/
mypy tradingagents/

# 
python -m pytest tests/ -v --cov=tradingagents
```

### CI/CD
- **GitHub Actions**: 
- ****: 
- ****: 
- ****: 

## 

### 
- [](branch-strategy.md)
- [](../../BRANCH_GUIDE.md)
- [](../maintenance/upstream-sync.md)

### 
- **GitHub Issues**: [](https://github.com/hsliuping/TradingAgents-CN/issues)
- ****: hsliup@163.com


