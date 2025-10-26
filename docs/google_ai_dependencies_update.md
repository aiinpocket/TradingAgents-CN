# Google AI 依賴包更新

## 📦 更新內容

### 新增的依賴包

在 `pyproject.toml` 和 `requirements.txt` 中添加了以下 Google AI 相關包：

1. **`google-genai>=0.1.0`** - Google 新的統一 Gen AI SDK
   - 這是 Google 推薦的新 SDK，支持 Gemini 2.0、Veo、Imagen 等模型
   - 提供更好的性能和最新功能

2. **`google-generativeai>=0.8.0`** - Google Generative AI SDK (遺留)
   - 項目中現有代碼使用的包
   - 虽然被標記為遺留，但仍需要保持兼容性

3. **`langchain-google-genai>=2.1.5`** - LangChain Google AI 集成
   - 已存在，用於 LangChain 框架集成
   - 項目主要使用的 Google AI 接口

## 🔧 技術細節

### 包的用途

- **`langchain-google-genai`**: 主要用於項目中的 LangChain 集成
- **`google.generativeai`**: 用於直接調用 Google AI API
- **`google.genai`**: 新的統一 SDK，為未來迁移做準备

### 依賴冲突解決

在安裝過程中遇到了依賴版本冲突：
- `google-ai-generativelanguage` 版本不兼容
- 通過升級到最新版本解決

## 📋 驗證結果

✅ 所有包導入成功  
✅ 模型實例創建正常  
✅ Web 應用運行正常  
✅ 現有功能未受影響  

## 🚀 使用建议

1. **當前項目**: 繼续使用 `langchain-google-genai`
2. **新功能開發**: 可以考慮使用新的 `google-genai` SDK
3. **API 密鑰**: 確保在 `.env` 文件中配置 `GOOGLE_API_KEY`

## 📝 安裝命令

如果需要重新安裝依賴：

```bash
# 使用 pip
pip install -e .

# 或使用 uv (推薦)
uv pip install -e .
```

## 🔗 相關文档

- [Google Gen AI SDK 文档](https://cloud.google.com/vertex-ai/generative-ai/docs/sdks/overview)
- [LangChain Google AI 集成](https://python.langchain.com/docs/integrations/llms/google_ai)
- [項目 Google 模型指南](./google_models_guide.md)

---

*更新時間: 2025-08-02*  
*更新內容: 添加 Google AI 相關依賴包*