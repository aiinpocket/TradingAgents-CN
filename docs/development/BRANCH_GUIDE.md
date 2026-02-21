# 

TradingAgents-CN

## 

### 
- **main**: 
- **develop**: 
- **feature/***: 
- **hotfix/***: 

### 
```
feature/ # 
hotfix/ # 
release/ # 
docs/ # 
```

## 

### 1. 
```bash
# 1. develop
git checkout develop
git pull origin develop
git checkout -b feature/new-feature

# 2. 
# ... ...

# 3. 
git add .
git commit -m "feat: "

# 4. 
git push origin feature/new-feature

# 5. Pull Requestdevelop
```

### 2. 
```bash
# 1. main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# 2. 
# ... ...

# 3. 
git add .
git commit -m "fix: "

# 4. 
git push origin hotfix/critical-fix

# 5. PRmaindevelop
```

### 3. 
```bash
# 1. develop
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 2. 
# ... ...

# 3. 
# ... ...

# 4. main
git checkout main
git merge release/v1.0.0
git tag v1.0.0

# 5. develop
git checkout develop
git merge release/v1.0.0
```

## 

### main
- 
- Pull Request
- 
- 

### develop
- 
- Pull Request
- 

## 

### 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] 

### 
1. Pull Request
2. 
3. 
4. 
5. 

## 

### 
```
feat: 
fix: 
docs: 
style: 
refactor: 
test: 
chore: 
```

### 
- 
- 
- 
- 

### 
```bash
# 1. 
git checkout develop
git pull origin develop

# 2. 
git checkout feature/my-feature

# 3. develop
git rebase develop

# 4. 
# ... ...

# 5. 
git rebase --continue

# 6. 
git push --force-with-lease origin feature/my-feature
```

## 

### 
```bash
# 
git branch -a

# 
git status

# 
git log --oneline --graph

# 
git remote show origin
```

### 
```bash
# 
git branch --merged | grep -v main | xargs git branch -d

# 
git remote prune origin

# 
git gc --prune=now
```

## 

### Git
```bash
# 
git config user.name "Your Name"
git config user.email "your.email@example.com"

# 
git config init.defaultBranch main

# 
git config push.default simple
```

### IDE
- Git
- 
- 
- 

---


