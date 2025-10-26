# 用戶密碼管理工具

這個工具集提供了通過命令行管理TradingAgents-CN用戶账戶的功能，包括修改密碼、創建用戶、刪除用戶等操作。

## 文件說明

- `user_password_manager.py` - 核心Python腳本
- `user_manager.bat` - Windows批處理文件
- `user_manager.ps1` - PowerShell腳本

## 使用方法

### 1. 使用Python腳本（推薦）

```bash
# 列出所有用戶
python scripts/user_password_manager.py list

# 修改用戶密碼
python scripts/user_password_manager.py change-password admin newpassword123

# 創建新用戶
python scripts/user_password_manager.py create-user newuser password123 --role user

# 創建管理員用戶
python scripts/user_password_manager.py create-user newadmin adminpass123 --role admin

# 刪除用戶
python scripts/user_password_manager.py delete-user olduser

# 重置為默認配置
python scripts/user_password_manager.py reset
```

### 2. 使用Windows批處理文件

```cmd
# 列出所有用戶
scripts\user_manager.bat list

# 修改用戶密碼
scripts\user_manager.bat change-password admin newpassword123

# 創建新用戶
scripts\user_manager.bat create-user newuser password123 user

# 刪除用戶
scripts\user_manager.bat delete-user olduser

# 重置為默認配置
scripts\user_manager.bat reset
```

### 3. 使用PowerShell腳本

```powershell
# 列出所有用戶
.\scripts\user_manager.ps1 list

# 修改用戶密碼
.\scripts\user_manager.ps1 change-password admin newpassword123

# 創建新用戶
.\scripts\user_manager.ps1 create-user newuser password123 user

# 刪除用戶
.\scripts\user_manager.ps1 delete-user olduser

# 重置為默認配置
.\scripts\user_manager.ps1 reset
```

## 功能詳解

### 列出用戶 (list)
顯示所有用戶的詳細信息，包括用戶名、角色、權限和創建時間。

### 修改密碼 (change-password)
修改指定用戶的密碼。密碼會自動進行SHA256哈希處理。

**語法**: `change-password <用戶名> <新密碼>`

### 創建用戶 (create-user)
創建新的用戶账戶。

**語法**: `create-user <用戶名> <密碼> [--role <角色>] [--permissions <權限列表>]`

**參數**:
- `--role`: 用戶角色，可選值為 `user` 或 `admin`，默認為 `user`
- `--permissions`: 權限列表，如不指定則根據角色自動分配

**默認權限**:
- `user` 角色: `["analysis"]`
- `admin` 角色: `["analysis", "config", "admin"]`

### 刪除用戶 (delete-user)
刪除指定的用戶账戶。為了安全，不能刪除最後一個管理員用戶。

**語法**: `delete-user <用戶名>`

### 重置配置 (reset)
将用戶配置重置為默認設置，包含以下默認用戶：
- `admin` / `admin123` (管理員)
- `user` / `user123` (普通用戶)

## 安全註意事項

1. **密碼安全**: 所有密碼都使用SHA256進行哈希處理，不會以明文形式存储
2. **權限控制**: 管理員用戶擁有所有權限，普通用戶只能進行分析操作
3. **备份建议**: 在進行重置操作前，建议备份現有的用戶配置文件
4. **訪問控制**: 確保只有授權人員能夠訪問這些管理工具

## 配置文件位置

用戶配置文件位於: `web/config/users.json`

## 故障排除

### 1. 找不到Python
確保Python已正確安裝並添加到系統PATH環境變量中。

### 2. 權限錯誤
在Windows上，可能需要以管理員身份運行命令提示符或PowerShell。

### 3. 配置文件不存在
工具會自動創建默認的用戶配置文件，如果仍有問題，請檢查文件路徑和權限。

### 4. PowerShell執行策略
如果PowerShell腳本無法執行，可能需要修改執行策略：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 示例場景

### 場景1: 首次部署後修改默認密碼
```bash
# 修改管理員密碼
python scripts/user_password_manager.py change-password admin your_secure_password

# 修改普通用戶密碼
python scripts/user_password_manager.py change-password user your_user_password
```

### 場景2: 為团隊添加新用戶
```bash
# 添加分析師用戶
python scripts/user_password_manager.py create-user analyst analyst123 --role user

# 添加新管理員
python scripts/user_password_manager.py create-user manager manager123 --role admin
```

### 場景3: 清理不需要的用戶
```bash
# 刪除測試用戶
python scripts/user_password_manager.py delete-user testuser

# 查看當前用戶列表
python scripts/user_password_manager.py list
```