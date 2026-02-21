# 

## 

 TradingAgents-CN [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 

## 

### 
- ****: 
- ****: Bug
- ****: 
- ****: 

### 
- ****: 
- ****: 
- ****: 
- ****: 

## 

### 1. 

#### 
```bash
# GitHub
# 1. https://github.com/TauricResearch/TradingAgents
# 2. "Watch" -> "Custom" -> "Releases" "Issues"
# 3. 
```

#### 
- ****: 
- ****: 
- ****: Bug

### 2. 

```
main ()
 upstream-sync-YYYYMMDD ()
 feature/chinese-enhancement ()
 hotfix/urgent-fixes ()

upstream/main ()
```

#### 
- **main**: 
- **upstream-sync-YYYYMMDD**: 
- **feature/chinese-enhancement**: 
- **hotfix/urgent-fixes**: 

### 3. 

#### 

```bash
# 1. 
git status
git log --oneline -5

# 2. 
git fetch upstream

# 3. 
git log --oneline HEAD..upstream/main

# 4. 
python scripts/sync_upstream.py

# 5. 
# 
git add <resolved_files>
git commit

# 6. 
python -m pytest tests/
python examples/basic_example.py

# 7. 
git push origin main
```

#### 

```bash
# 
python scripts/sync_upstream.py

# rebase
python scripts/sync_upstream.py --strategy rebase

# 
python scripts/sync_upstream.py --auto
```

## 

### 

#### 1. 
****: 

****:
```bash
# 
# : README.md, docs/
# : 
```

#### 2. 
****: 

****:
```bash
# 
git diff HEAD upstream/main -- config/
# 
```

#### 3. 
****: 

****:
```bash
# 
# 1. 
git checkout --theirs <conflicted_file>
# 2. 
# 3. 
```

### 

1. ****: 
2. **Bug**: 
3. ****: 
4. ****: 
5. ****: 

## 

### 
- [ ] 
- [ ] 
- [ ] Issue
- [ ] 

### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

## 

### 
```bash
# 
python -m pytest tests/ -v

# 
python examples/basic_example.py

# 
python tests/performance_test.py
```

### 
```bash
# 
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG.copy())
state, decision = ta.propagate('AAPL', '2024-01-15')
print(f'Decision: {decision}')
"

# 
# docs/ 
```

## 

### 
```json
{
 "sync_time": "2024-01-15T10:30:00Z",
 "upstream_commits": 5,
 "conflicts_resolved": 2,
 "files_changed": ["tradingagents/core.py", "config/default.yaml"],
 "tests_passed": true,
 "notes": ""
}
```

### 
```bash
# 
git tag -a v1.0.0-cn-pre-sync -m ""

# 
git tag -a v1.0.1-cn -m " v1.2.3"

# 
git push origin --tags
```

## 

### 
```bash
# 
git reset --hard v1.0.0-cn-pre-sync

# 
git reset --hard HEAD~1

# 
git push origin main --force-with-lease
```

### 
```bash
# 
git checkout -b hotfix/urgent-fix

# 
# ... ...

# 
git checkout main
git merge hotfix/urgent-fix
git push origin main

# 
git branch -d hotfix/urgent-fix
```

## 

### 
- ****: 
- ****: 
- ****: 

### 
- ****: 24
- **Bug**: 48
- ****: 12

## 

### 
- **Issue**: Bug
- ****: 
- ****: 

### 
- ****: 
- ****: 
- ****: 

 TradingAgents-CN 
