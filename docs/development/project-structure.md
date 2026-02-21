# 

## 

TradingAgents-CN 

## 

```
TradingAgentsCN/
 tradingagents/ # 
 web/ # Web
 docs/ # 
 tests/ # 
 scripts/ # 
 env/ # Python
 README.md # 
 requirements.txt # 
 .env.example # 
 VERSION # 
 CHANGELOG.md # 
```

## 

### tests/ - 
****: 

#### 
- `test_*.py` - 
- `*_test.py` - 
- `test_*_integration.py` - 
- `test_*_performance.py` - 
- `check_*.py` - 
- `debug_*.py` - 

#### 
```
tests/
 README.md # 
 __init__.py # Python
 integration/ # 
 test_*.py # 
 *_test.py # 
 test_*_performance.py # 
```

#### 
- `test_analysis.py` - 
- `test_finnhub_connection.py` - FinnHub
- `test_redis_performance.py` - Redis

### scripts/ - 
****: 

#### 
- `release_*.py` - 
- `setup_*.py` - 
- `deploy_*.py` - 
- `migrate_*.py` - 
- `backup_*.py` - 

#### 
- `test_*.py` - tests/
- `*_test.py` - tests/
- `check_*.py` - tests/

### docs/ - 
****: 

#### 
```
docs/
 guides/ # 
 development/ # 
 data/ # 
 api/ # API
 localization/ # 
```

### web/ - Web
****: Web

#### 
```
web/
 app.py # 
 components/ # UI
 utils/ # Web
 static/ # 
 templates/ # 
```

### tradingagents/ - 
****: 

#### 
```
tradingagents/
 agents/ # 
 dataflows/ # 
 tools/ # 
 utils/ # 
```

## 

### 
- `test_*.py` - tests/
- `*_test.py` - tests/
- `debug_*.py` - tests/
- `check_*.py` - tests/
- 
- IDE.gitignore

### scripts/
- 
- 
- 

## 

### 
- ****: `test_<module_name>.py`
- ****: `test_<feature>_integration.py`
- ****: `test_<component>_performance.py`
- ****: `<component>_test.py`
- ****: `check_<feature>.py`
- ****: `debug_<issue>.py`

### 
- ****: `release_v<version>.py`
- ****: `setup_<component>.py`
- ****: `deploy_<environment>.py`

### 
- ****: `<feature>-guide.md`
- ****: `<component>-integration.md`
- **API**: `<api>-api.md`

## 

### 
 `tests/check_project_structure.py` 

```python
def check_no_tests_in_root():
 """"""
 
def check_no_tests_in_scripts():
 """scripts"""
 
def check_all_tests_in_tests_dir():
 """tests"""
```

### 

- [ ] test_*.py
- [ ] *_test.py
- [ ] scripts/
- [ ] tests/
- [ ] tests/README.md
- [ ] 

## 

### 1. 
```bash
# tests
touch tests/test_new_feature.py

# 
touch test_new_feature.py
```

### 2. 
```bash
# tests
python tests/fast_tdx_test.py
python -m pytest tests/

# 
python fast_tdx_test.py
```

### 3. 
```markdown
<!-- -->
`python tests/fast_tdx_test.py`

<!-- -->
`python fast_tdx_test.py`
```

## 



### tests
```bash
# Windows
move test_*.py tests\
move *_test.py tests\

# Linux/macOS
mv test_*.py tests/
mv *_test.py tests/
```

### 
1. 
2. import
3. CI/CD

## 

1. **** - 
2. **** - 
3. **** - CI/CD
4. **** - 
5. **** - 

---

**** 
