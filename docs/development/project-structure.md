# 項目結構規範

## 📁 目錄組織原則

TradingAgents-CN 項目遵循清晰的目錄結構規範，確保代碼組織有序、易於維護。

## 🏗️ 項目根目錄結構

```
TradingAgentsCN/
├── 📁 tradingagents/          # 核心代碼包
├── 📁 web/                    # Web界面代碼
├── 📁 docs/                   # 項目文档
├── 📁 tests/                  # 所有測試文件
├── 📁 scripts/                # 工具腳本
├── 📁 env/                    # Python虛擬環境
├── 📄 README.md               # 項目說明
├── 📄 requirements.txt        # 依賴列表
├── 📄 .env.example           # 環境變量模板
├── 📄 VERSION                 # 版本號
└── 📄 CHANGELOG.md           # 更新日誌
```

## 📋 目錄職责說明

### 🧪 tests/ - 測試目錄
**規則**: 所有測試相關的文件必须放在此目錄下

#### 允許的文件類型：
- ✅ `test_*.py` - 單元測試文件
- ✅ `*_test.py` - 快速測試腳本
- ✅ `test_*_integration.py` - 集成測試
- ✅ `test_*_performance.py` - 性能測試
- ✅ `check_*.py` - 檢查腳本
- ✅ `debug_*.py` - 調試腳本

#### 子目錄組織：
```
tests/
├── 📄 README.md                    # 測試說明文档
├── 📄 __init__.py                  # Python包初始化
├── 📁 integration/                 # 集成測試
├── 📄 test_*.py                   # 單元測試
├── 📄 *_test.py                   # 快速測試
└── 📄 test_*_performance.py       # 性能測試
```

#### 示例文件：
- `test_analysis.py` - 分析功能單元測試
- `fast_tdx_test.py` - Tushare數據接口快速測試
- `test_tdx_integration.py` - Tushare數據接口集成測試
- `test_redis_performance.py` - Redis性能測試

### 🔧 scripts/ - 工具腳本目錄
**規則**: 仅放置非測試的工具腳本

#### 允許的文件類型：
- ✅ `release_*.py` - 發布腳本
- ✅ `setup_*.py` - 安裝配置腳本
- ✅ `deploy_*.py` - 部署腳本
- ✅ `migrate_*.py` - 數據迁移腳本
- ✅ `backup_*.py` - 备份腳本

#### 不允許的文件：
- ❌ `test_*.py` - 測試文件應放在tests/
- ❌ `*_test.py` - 測試腳本應放在tests/
- ❌ `check_*.py` - 檢查腳本應放在tests/

### 📚 docs/ - 文档目錄
**規則**: 所有項目文档按類型組織

#### 目錄結構：
```
docs/
├── 📁 guides/                     # 使用指南
├── 📁 development/                # 開發文档
├── 📁 data/                       # 數據源文档
├── 📁 api/                        # API文档
└── 📁 localization/               # 本土化文档
```

### 🌐 web/ - Web界面目錄
**規則**: Web相關代碼統一管理

#### 目錄結構：
```
web/
├── 📄 app.py                      # 主應用入口
├── 📁 components/                 # UI組件
├── 📁 utils/                      # Web工具函數
├── 📁 static/                     # 静態資源
└── 📁 templates/                  # 模板文件
```

### 🧠 tradingagents/ - 核心代碼包
**規則**: 核心業務逻辑代碼

#### 目錄結構：
```
tradingagents/
├── 📁 agents/                     # 智能體代碼
├── 📁 dataflows/                  # 數據流處理
├── 📁 tools/                      # 工具函數
└── 📁 utils/                      # 通用工具
```

## 🚫 禁止的文件位置

### 根目錄禁止項：
- ❌ `test_*.py` - 必须放在tests/
- ❌ `*_test.py` - 必须放在tests/
- ❌ `debug_*.py` - 必须放在tests/
- ❌ `check_*.py` - 必须放在tests/
- ❌ 臨時文件和調試文件
- ❌ IDE配置文件（應在.gitignore中）

### scripts/目錄禁止項：
- ❌ 任何測試相關文件
- ❌ 調試腳本
- ❌ 檢查腳本

## ✅ 文件命名規範

### 測試文件命名：
- **單元測試**: `test_<module_name>.py`
- **集成測試**: `test_<feature>_integration.py`
- **性能測試**: `test_<component>_performance.py`
- **快速測試**: `<component>_test.py`
- **檢查腳本**: `check_<feature>.py`
- **調試腳本**: `debug_<issue>.py`

### 工具腳本命名：
- **發布腳本**: `release_v<version>.py`
- **安裝腳本**: `setup_<component>.py`
- **部署腳本**: `deploy_<environment>.py`

### 文档文件命名：
- **使用指南**: `<feature>-guide.md`
- **技術文档**: `<component>-integration.md`
- **API文档**: `<api>-api.md`

## 🔍 項目結構檢查

### 自動檢查腳本
創建 `tests/check_project_structure.py` 來驗證項目結構：

```python
def check_no_tests_in_root():
    """檢查根目錄没有測試文件"""
    
def check_no_tests_in_scripts():
    """檢查scripts目錄没有測試文件"""
    
def check_all_tests_in_tests_dir():
    """檢查所有測試文件都在tests目錄"""
```

### 手動檢查清單
發布前檢查：
- [ ] 根目錄没有test_*.py文件
- [ ] 根目錄没有*_test.py文件
- [ ] scripts/目錄没有測試文件
- [ ] 所有測試文件都在tests/目錄
- [ ] tests/README.md已更新
- [ ] 文档中的路徑引用正確

## 📝 最佳實踐

### 1. 新增測試文件
```bash
# ✅ 正確：在tests目錄創建
touch tests/test_new_feature.py

# ❌ 錯誤：在根目錄創建
touch test_new_feature.py
```

### 2. 運行測試
```bash
# ✅ 正確：指定tests目錄
python tests/fast_tdx_test.py
python -m pytest tests/

# ❌ 錯誤：從根目錄運行
python fast_tdx_test.py
```

### 3. 文档引用
```markdown
<!-- ✅ 正確：使用完整路徑 -->
運行測試：`python tests/fast_tdx_test.py`

<!-- ❌ 錯誤：使用相對路徑 -->
運行測試：`python fast_tdx_test.py`
```

## 🔧 迁移現有文件

如果發現文件位置不符合規範：

### 移動測試文件到tests目錄：
```bash
# Windows
move test_*.py tests\
move *_test.py tests\

# Linux/macOS
mv test_*.py tests/
mv *_test.py tests/
```

### 更新引用：
1. 更新文档中的路徑引用
2. 更新腳本中的import路徑
3. 更新CI/CD配置中的測試路徑

## 🎯 遵循規範的好處

1. **清晰的項目結構** - 新開發者容易理解
2. **便於維護** - 文件位置可預測
3. **自動化友好** - CI/CD腳本更簡單
4. **避免混乱** - 測試和業務代碼分離
5. **專業形象** - 符合開源項目標準

---

**請嚴格遵循此項目結構規範，確保代碼庫的整潔和專業性！** 📁✨
