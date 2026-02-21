# TradingAgents-CN 

## 



### 
- **main** - 
- **develop** - 
- **feature/-integration** - v0.1.6
- **feature/

### 
- **feature/
- **feature/data-source-upgrade** - 
- **hotfix/*** - 

## 

### 1. 

#### 
```
main ()
 develop ()
 feature/v0.1.7 ()
 hotfix/* ()
```

#### 
```bash
# 1. main
# 2. 
# 3. 
```

### 2. 

#### v0.1.6
```bash
# Step 1: feature/-integrationv0.1.6
git checkout feature/-integration
git status

# Step 2: develop
git checkout develop
git merge feature/-integration

# Step 3: main
git checkout main
git merge develop
git tag v0.1.6
git push origin main --tags

# Step 4: 
git branch -d feature/-integration
git push origin --delete feature/-integration
```

### 3. 

#### v0.1.7
```bash
# Step 1: main
git checkout main
git pull origin main
git checkout -b feature/v0.1.7

# Step 2: 
# ... ...

# Step 3: main
git checkout main
git pull origin main
git checkout feature/v0.1.7
git merge main

# Step 4: main
git checkout main
git merge feature/v0.1.7
git tag v0.1.7
```

## 

### 
```bash
#!/bin/bash
echo " "
echo "=================="

echo " :"
git branch

echo -e "\n :"
git branch -r

echo -e "\n :"
git log --oneline --graph --all -10

echo -e "\n :"
git branch --show-current

echo -e "\n :"
git status --porcelain
```

### 
```bash
#!/bin/bash
echo " "
echo "=================="

# 1. main
git checkout main
git pull origin main

# 2. 
echo " main:"
git branch --merged main

# 3. 
echo " main:"
git branch --no-merged main

# 4. 
echo " ..."
git branch --merged main | grep -E "feature/|hotfix/" | while read branch; do
 echo ": $branch"
 read -p "? (y/N): " confirm
 if [[ $confirm == [yY] ]]; then
 git branch -d "$branch"
 git push origin --delete "$branch" 2>/dev/null || true
 fi
done
```

## 

### 

#### 1. 
```bash
# 
git branch --show-current

# 
git status

# 
git log --oneline -5
```

#### 2. v0.1.6
```bash
# feature/-integration
# v0.1.6
git add .
git commit -m "v0.1.6"

# 
git push origin feature/-integration
```

#### 3. v0.1.6
```bash
# main
git checkout main
git merge feature/-integration

# 
git tag -a v0.1.6 -m "TradingAgents-CN v0.1.6"

# 
git push origin main --tags
```

### 

#### 1. 
- ****: `feature/` `feature/v`
- ****: `hotfix/`
- ****: `release/v` ()

#### 2. 
```
(): 



- 1
- 2

Closes #issue
```

#### 3. 
- [ ] 
- [ ] 
- [ ] 
- [ ] 
- [ ] CHANGELOG
- [ ] 

## 

### 
1. ****
2. ****
3. **v0.1.6**

### 
1. ****
2. ****
3. **v0.1.7**

### 
1. ****
2. ****
3. ****

## 

### Git
```bash
# Git
git config --global alias.br branch
git config --global alias.co checkout
git config --global alias.st status
git config --global alias.lg "log --oneline --graph --all"
git config --global alias.cleanup "!git branch --merged main | grep -v main | xargs -n 1 git branch -d"
```

### VSCode
- **GitLens** - Git
- **Git Graph** - 
- **Git History** - 

## 



1. ****
 ```bash
 git stash push -m ""
 ```

2. ****
 - Git
 - `git help <command>`
 - 

3. ****
 ```bash
 git stash pop
 ```

---

****: 
