# 贡献指南

感谢您對TradingAgents-CN項目的關註！我們欢迎各種形式的贡献。

## 🤝 如何贡献

### 1. 報告問題
- 使用GitHub Issues報告Bug
- 提供詳細的問題描述和複現步骤
- 包含系統環境信息

### 2. 功能建议
- 在GitHub Issues中提出功能請求
- 詳細描述功能需求和使用場景
- 討論實現方案

### 3. 代碼贡献
1. Fork項目仓庫
2. 創建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 創建Pull Request

### 4. 文档贡献
- 改進現有文档
- 添加使用示例
- 翻譯文档
- 修正錯誤

## 📋 開發規範

### 代碼風格
- 遵循PEP 8 Python代碼規範
- 使用有意義的變量和函數名
- 添加適當的註釋和文档字符串
- 保持代碼簡潔和可讀性

### 提交規範
- 使用清晰的提交信息
- 一個提交只做一件事
- 提交信息使用中文或英文

### 測試要求
- 為新功能添加測試用例
- 確保所有測試通過
- 保持測試覆蓋率

## 🔧 開發環境設置

### 1. 克隆仓庫
```bash
git clone https://github.com/hsliuping/TradingAgents-CN.git
cd TradingAgents-CN
```

### 2. 創建虛擬環境
```bash
python -m venv env
source env/bin/activate  # Linux/macOS
# 或
env\Scripts\activate  # Windows
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 配置環境變量
```bash
cp .env.example .env
# 編辑.env文件，添加必要的API密鑰
```

### 5. 運行測試
```bash
python -m pytest tests/
```

## 📝 Pull Request指南

### 提交前檢查
- [ ] 代碼遵循項目規範
- [ ] 添加了必要的測試
- [ ] 更新了相關文档
- [ ] 所有測試通過
- [ ] 没有引入新的警告

### PR描述模板
```markdown
## 更改類型
- [ ] Bug修複
- [ ] 新功能
- [ ] 文档更新
- [ ] 性能優化
- [ ] 其他

## 更改描述
簡要描述此PR的更改內容

## 測試
描述如何測試這些更改

## 相關Issue
關聯的Issue編號（如果有）
```

## 🎯 贡献重點

### 優先級高的贡献
1. **Bug修複**: 修複現有功能問題
2. **文档改進**: 完善使用文档和示例
3. **測試增强**: 增加測試覆蓋率
4. **性能優化**: 提升系統性能

### 欢迎的贡献
1. **新數據源**: 集成更多金融數據源
2. **新LLM支持**: 支持更多大語言模型
3. **界面優化**: 改進Web界面用戶體驗
4. **國际化**: 支持更多語言

## 📞 聯系我們

- **GitHub Issues**: 問題報告和討論
- **GitHub Discussions**: 社区交流
- **項目文档**: 詳細的開發指南

## 📄 許可證

通過贡献代碼，您同意您的贡献将在Apache 2.0許可證下發布。

---

感谢您的贡献！🎉
