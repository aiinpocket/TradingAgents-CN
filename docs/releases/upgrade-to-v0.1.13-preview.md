# 📈 升級指南: v0.1.12 → v0.1.13

## 🎯 升級概述

本指南将幫助您從 TradingAgents-CN v0.1.12 升級到 v0.1.13，享受原生OpenAI支持和Google AI全面集成的新功能。

## ⏰ 預計升級時間

- **簡單升級**: 5-10分鐘 (仅更新代碼和依賴)
- **完整配置**: 15-20分鐘 (包含Google AI配置和測試)
- **深度定制**: 30-45分鐘 (包含自定義端點配置)

## 📋 升級前檢查

### 1. 環境要求
```bash
# 檢查Python版本 (需要 >= 3.10)
python --version

# 檢查當前版本
cat VERSION
# 應该顯示: cn-0.1.12
```

### 2. 备份重要數據
```bash
# 备份配置文件
cp .env .env.backup
cp -r reports reports_backup

# 备份自定義配置 (如果有)
cp -r config config_backup
```

### 3. 檢查當前分支
```bash
git branch
# 確認當前在合適的分支
```

## 🚀 升級步骤

### 步骤 1: 切換到預覽版分支
```bash
# 切換到預覽版分支
git checkout feature/native-openai-support

# 拉取最新代碼
git pull origin feature/native-openai-support

# 確認版本
cat VERSION
# 應该顯示: cn-0.1.13-preview
```

### 步骤 2: 更新依賴包
```bash
# 方法1: 使用requirements.txt
pip install -r requirements.txt

# 方法2: 使用pyproject.toml (推薦)
pip install -e .

# 驗證新增的Google AI包
pip list | grep -E "(google-genai|google-generativeai|langchain-google-genai)"
```

### 步骤 3: 配置Google AI (可選但推薦)
```bash
# 在 .env 文件中添加Google API密鑰
echo "GOOGLE_API_KEY=your_google_api_key_here" >> .env

# 如果没有Google API密鑰，可以從以下地址獲取:
# https://makersuite.google.com/app/apikey
```

### 步骤 4: 驗證安裝
```bash
# 測試Google AI包導入
python -c "
import google.generativeai as genai
import langchain_google_genai
import google.genai
print('✅ All Google AI packages imported successfully')
"

# 運行簡單測試
python tests/test_gemini_simple.py
```

### 步骤 5: 啟動和測試
```bash
# 啟動Web界面
streamlit run web/app.py

# 在浏覽器中訪問 http://localhost:8501
# 測試新的模型選擇功能
```

## 🔧 配置新功能

### 1. Google AI 配置

#### 獲取API密鑰
1. 訪問 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 創建新的API密鑰
3. 複制密鑰到 `.env` 文件

#### 配置示例
```bash
# .env 文件
GOOGLE_API_KEY=AIzaSyC...your_key_here
```

#### 測試配置
```python
# 測試腳本
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# 檢查API密鑰
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print("✅ Google API密鑰已配置")
    
    # 測試模型
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key
    )
    print("✅ Google AI模型創建成功")
else:
    print("⚠️ 請配置GOOGLE_API_KEY環境變量")
```

### 2. 原生OpenAI端點配置

#### 配置自定義端點
```bash
# .env 文件中添加
OPENAI_API_BASE=https://your-custom-endpoint.com/v1
OPENAI_API_KEY=your_custom_api_key
```

#### 支持的端點格式
- OpenAI官方: `https://api.openai.com/v1`
- 自建服務: `https://your-domain.com/v1`
- 代理服務: `https://proxy.example.com/v1`

### 3. Web界面新功能

#### 智能模型選擇
- 🎯 自動檢測可用模型
- 🔄 智能降級機制
- ⚡ 快速模型切換
- 🛡️ 錯誤恢複

#### 使用方法
1. 打開Web界面
2. 在侧邊栏選擇"Google AI"提供商
3. 選擇具體的Google AI模型
4. 開始分析任務

## 🧪 功能測試

### 1. 基础功能測試
```bash
# 測試CLI功能
python cli/main.py --help

# 測試Web界面
streamlit run web/app.py
```

### 2. Google AI功能測試
```bash
# 運行Google AI測試套件
python tests/test_gemini_simple.py
python tests/test_gemini_final.py
python tests/test_google_memory_fix.py
```

### 3. 集成測試
```bash
# 運行完整的股票分析測試
python tests/test_analysis.py

# 測試新聞分析功能
python tests/test_web_fix.py
```

## ⚠️ 常见問題和解決方案

### 問題 1: 依賴冲突
```bash
# 症狀: pip安裝時出現依賴冲突
# 解決方案:
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

### 問題 2: Google AI包導入失败
```bash
# 症狀: ImportError: No module named 'google.generativeai'
# 解決方案:
pip install google-generativeai>=0.8.0
pip install google-genai>=0.1.0
pip install langchain-google-genai>=2.1.5
```

### 問題 3: API密鑰配置問題
```bash
# 症狀: Google API密鑰無效
# 解決方案:
# 1. 檢查密鑰格式 (應以AIzaSy開头)
# 2. 確認密鑰權限
# 3. 檢查API配額
```

### 問題 4: Web界面模型選擇錯誤
```bash
# 症狀: KeyError in model selection
# 解決方案:
# 1. 清除浏覽器緩存
# 2. 重啟Streamlit應用
# 3. 檢查模型配置文件
```

## 📊 升級驗證清單

### ✅ 基础驗證
- [ ] 版本號顯示為 `cn-0.1.13-preview`
- [ ] 所有依賴包安裝成功
- [ ] Web界面正常啟動
- [ ] CLI功能正常工作

### ✅ Google AI驗證
- [ ] Google AI包導入成功
- [ ] API密鑰配置正確
- [ ] 模型創建和調用成功
- [ ] Web界面顯示Google AI選項

### ✅ 功能驗證
- [ ] 股票分析功能正常
- [ ] 新聞分析功能正常
- [ ] 模型切換功能正常
- [ ] 錯誤處理機制正常

### ✅ 性能驗證
- [ ] 響應速度正常或更快
- [ ] 內存使用穩定
- [ ] 錯誤恢複正常
- [ ] 日誌記錄清晰

## 🔄 回滚方案

如果升級過程中遇到問題，可以回滚到v0.1.12：

```bash
# 回滚到v0.1.12
git checkout main  # 或之前的穩定分支
git pull origin main

# 恢複依賴
pip install -r requirements.txt

# 恢複配置文件
cp .env.backup .env
cp -r reports_backup reports
```

## 📞 獲取幫助

### 🐛 問題報告
- **GitHub Issues**: 創建詳細的問題報告
- **錯誤日誌**: 提供完整的錯誤信息和日誌
- **環境信息**: 包含Python版本、操作系統等信息

### 💡 功能建议
- **功能描述**: 詳細描述期望的功能
- **使用場景**: 說明具體的使用需求
- **優先級**: 標明功能的重要性

### 📚 文档資源
- **配置指南**: `docs/configuration/google-ai-setup.md`
- **模型指南**: `docs/google_models_guide.md`
- **故障排除**: `docs/troubleshooting/`

## 🎉 升級完成

恭喜！您已成功升級到 TradingAgents-CN v0.1.13。

現在您可以：
- 🤖 使用原生OpenAI端點支持
- 🧠 體驗Google AI模型的强大功能
- 🔧 享受優化的LLM適配器架構
- 🎨 使用改進的Web界面

感谢您選擇 TradingAgents-CN，祝您使用愉快！