# API密鑰安全指南

## 🚨 重要安全提醒

### ⚠️ 絕對不要做的事情

1. **不要将.env文件提交到Git仓庫**
   - .env文件包含敏感的API密鑰
   - 一旦提交到公開仓庫，密鑰可能被恶意使用
   - 即使刪除提交，Git歷史中仍然存在

2. **不要在代碼中硬編碼API密鑰**
   ```python
   # ❌ 錯誤做法
   api_key = "sk-1234567890abcdef"
   
   # ✅ 正確做法
   api_key = os.getenv("DASHSCOPE_API_KEY")
   ```

3. **不要在日誌中輸出完整的API密鑰**
   ```python
   # ❌ 錯誤做法
   print(f"Using API key: {api_key}")
   
   # ✅ 正確做法
   print(f"Using API key: {api_key[:12]}...")
   ```

### ✅ 安全最佳實踐

#### 1. 使用環境變量
```bash
# 在.env文件中配置
DASHSCOPE_API_KEY=your_real_api_key_here
FINNHUB_API_KEY=your_real_finnhub_key_here
```

#### 2. 正確的文件權限
```bash
# 設置.env文件只有所有者可讀寫
chmod 600 .env
```

#### 3. 使用.gitignore
確保.gitignore包含：
```
.env
.env.local
.env.*.local
```

#### 4. 定期轮換API密鑰
- 定期更換API密鑰
- 如果怀疑密鑰泄露，立即更換
- 監控API使用情况，發現異常立即處理

## 🔧 配置步骤

### 1. 複制示例文件
```bash
cp .env.example .env
```

### 2. 編辑.env文件
```bash
# 使用您喜欢的編辑器
notepad .env        # Windows
nano .env           # Linux/Mac
code .env           # VS Code
```

### 3. 填入真實API密鑰
```bash
# API密鑰 (推薦)
DASHSCOPE_API_KEY=sk-your-real-

# 金融數據API密鑰 (必需)
FINNHUB_API_KEY=your-real-finnhub-key
```

### 4. 驗證配置
```bash
python -m cli.main config
```

## 🔍 API密鑰獲取指南

###  (推薦)
1. 訪問 https://
2. 註冊/登錄阿里云账號
3. 開通百炼服務
4. 在控制台獲取API密鑰

### FinnHub (必需)
1. 訪問 https://finnhub.io/
2. 註冊免費账號
3. 在Dashboard獲取API密鑰
4. 免費账戶每分鐘60次請求

### OpenAI (可選)
1. 訪問 https://platform.openai.com/
2. 註冊账號並充值
3. 在API Keys页面創建密鑰

## 🚨 如果API密鑰泄露了怎么办？

### 立即行動
1. **立即撤銷泄露的API密鑰**
   - 登錄對應的API提供商控制台
   - 刪除或禁用泄露的密鑰

2. **生成新的API密鑰**
   - 創建新的API密鑰
   - 更新.env文件中的配置

3. **檢查使用記錄**
   - 查看API使用日誌
   - 確認是否有異常使用

4. **更新代碼配置**
   - 更新本地.env文件
   - 通知团隊成員更新配置

### 預防措施
1. **使用Git hooks**
   - 設置pre-commit hooks檢查敏感文件
   - 防止意外提交.env文件

2. **定期審計**
   - 定期檢查Git歷史
   - 確保没有敏感信息泄露

3. **团隊培训**
   - 培训团隊成員安全意识
   - 建立安全操作規範

## 📋 安全檢查清單

- [ ] .env文件已添加到.gitignore
- [ ] 没有在代碼中硬編碼API密鑰
- [ ] .env文件權限設置正確 (600)
- [ ] 定期轮換API密鑰
- [ ] 監控API使用情况
- [ ] 团隊成員了解安全規範
- [ ] 設置了pre-commit hooks (可選)

## 🔗 相關資源

- [Git安全最佳實踐](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure)
- [環境變量安全指南](https://12factor.net/config)
- [API密鑰管理最佳實踐](https://owasp.org/www-project-api-security/)

---

**記住：安全無小事，API密鑰保護是每個開發者的责任！** 🔐
