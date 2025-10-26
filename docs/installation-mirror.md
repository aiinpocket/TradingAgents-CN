# 國內鏡像加速安裝指南

## 問題

安裝依賴時速度很慢或經常卡死，特別是安裝 torch、transformers 等大型包。

## 解決方案

使用國內 PyPI 鏡像源加速安裝。

---

## 🚀 快速使用（推薦）

### 方式 1: 使用鎖定版本（最快，强烈推薦）

```bash
# 步骤 1: 安裝所有依賴包（使用鎖定版本，速度最快）
pip install -r requirements-lock.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 步骤 2: 安裝本項目（可編辑模式，--no-deps 避免重新解析依賴）
pip install -e . --no-deps
```

**優势**：
- ✅ **安裝速度極快**（無需依賴解析，直接下載指定版本）
- ✅ **環境完全可重現**（所有包版本鎖定）
- ✅ **避免版本冲突**和 PyYAML 編譯錯誤
- ✅ **節省時間**（從几分鐘縮短到几十秒）

**說明**: `--no-deps` 參數告诉 pip 不要檢查和安裝依賴，因為我們已經通過 requirements-lock.txt 安裝了所有依賴。

### 方式 2: 使用可編辑模式（開發時推薦）

```bash
# 使用清華鏡像
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或使用阿里云鏡像
pip install -e . -i https://mirrors.aliyun.com/pypi/simple/

# 或使用中科大鏡像
pip install -e . -i https://mirrors.ustc.edu.cn/pypi/web/simple
```

**註意**: 此方式需要 pip 解析依賴，速度較慢（可能需要几分鐘），但適合開發時修改代碼。

---

## 🔧 永久配置鏡像（推薦）

### Windows

```powershell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Linux / macOS

```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

配置後，以後所有 `pip install` 命令都會自動使用鏡像源。

---

## 📋 推薦鏡像源

| 鏡像源 | URL | 說明 |
|--------|-----|------|
| 清華大學 | `https://pypi.tuna.tsinghua.edu.cn/simple` | ⭐ 推薦，速度快，穩定 |
| 阿里云 | `https://mirrors.aliyun.com/pypi/simple/` | 穩定，速度快 |
| 中科大 | `https://mirrors.ustc.edu.cn/pypi/web/simple` | 教育網友好 |
| 豆瓣 | `https://pypi.douban.com/simple/` | 备選 |

---

## ✅ 完整安裝示例

```bash
# 1. 配置鏡像（一次性）
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 升級 pip
pip install --upgrade pip

# 3. 安裝項目
pip install -e .

# 完成！
```

---

## 🔄 取消鏡像配置

如果需要恢複默認 PyPI 源：

```bash
pip config unset global.index-url
```

---

## 💡 其他加速方法

### 使用 uv（更快的包管理器）

```bash
# 安裝 uv
pip install uv

# 使用 uv 安裝（自動使用最快的源）
uv pip install -e .
```

---

## 🐛 常见問題

### 問題 1: PyYAML 編譯錯誤（Windows）

**錯誤信息**:
```
AttributeError: cython_sources
Getting requirements to build wheel did not run successfully
```

**原因**: PyYAML 在 Windows 上需要編譯，但缺少 C 編譯器或 Cython 依賴。

**解決方案**:

**方法 1: 使用預編譯的二進制包（推薦）**
```bash
# 先單獨安裝 PyYAML 的預編譯版本
pip install --only-binary :all: pyyaml -i https://pypi.tuna.tsinghua.edu.cn/simple

# 然後安裝項目
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**方法 2: 升級 pip 和 setuptools**
```bash
python -m pip install --upgrade pip setuptools wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**方法 3: 安裝 Microsoft C++ Build Tools**
- 下載: https://visualstudio.microsoft.com/visual-cpp-build-tools/
- 安裝 "Desktop development with C++" 工作负載
- 重啟後再安裝

---

### 問題 2: 安裝仍然很慢

如果使用鏡像後仍然很慢：

1. 嘗試更換其他鏡像源
2. 檢查網絡連接
3. 使用 `uv` 包管理器
4. 在 GitHub Issues 中反馈

---

**推薦配置**: 清華鏡像 + pip 永久配置，一劳永逸！🎉

