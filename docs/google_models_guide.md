# Google AI 模型使用指南

## 經過驗證的模型列表

基於實際測試結果，以下6個模型已驗證可用：

### 1. gemini-2.5-flash-lite-preview-06-17 ⚡
- **平均響應時間**: 1.45秒
- **推薦用途**: 超快響應、實時交互、高頻調用
- **適合場景**: 快速分析、實時問答、簡單任務

### 2. gemini-2.0-flash 🚀
- **平均響應時間**: 1.87秒
- **推薦用途**: 快速響應、實時分析
- **適合場景**: 日常分析、快速決策

### 3. gemini-1.5-pro ⚖️
- **平均響應時間**: 2.25秒
- **推薦用途**: 平衡性能、複雜分析
- **適合場景**: 標準分析、專業任務

### 4. gemini-2.5-flash ⚡
- **平均響應時間**: 2.73秒
- **推薦用途**: 通用快速模型
- **適合場景**: 通用分析、高頻使用

### 5. gemini-1.5-flash 💨
- **平均響應時間**: 2.87秒
- **推薦用途**: 備用快速模型
- **適合場景**: 簡單分析、備用選擇

### 6. gemini-2.5-pro 🧠
- **平均響應時間**: 16.68秒
- **推薦用途**: 功能強大、複雜推理
- **適合場景**: 深度分析、複雜任務、高品質輸出

## 使用建議

### 按分析深度選擇模型

1. **快速分析 (1級)**:
   - 快速模型: `gemini-2.5-flash-lite-preview-06-17`
   - 深度模型: `gemini-2.0-flash`

2. **基礎分析 (2級)**:
   - 快速模型: `gemini-2.0-flash`
   - 深度模型: `gemini-1.5-pro`

3. **標準分析 (3級)**:
   - 快速模型: `gemini-1.5-pro`
   - 深度模型: `gemini-2.5-flash`

4. **深度分析 (4級)**:
   - 快速模型: `gemini-2.5-flash`
   - 深度模型: `gemini-2.5-pro`

5. **全面分析 (5級)**:
   - 快速模型: `gemini-2.5-pro`
   - 深度模型: `gemini-2.5-pro`

### 按使用場景選擇模型

- **實時交互**: `gemini-2.5-flash-lite-preview-06-17`
- **快速決策**: `gemini-2.0-flash`
- **平衡分析**: `gemini-1.5-pro`
- **深度思考**: `gemini-2.5-pro`

## 配置示例

```python
# 快速配置
config = {
    "llm_provider": "google",
    "quick_think_llm": "gemini-2.5-flash-lite-preview-06-17",
    "deep_think_llm": "gemini-2.0-flash"
}

# 平衡配置
config = {
    "llm_provider": "google", 
    "quick_think_llm": "gemini-1.5-pro",
    "deep_think_llm": "gemini-2.5-flash"
}

# 強力配置
config = {
    "llm_provider": "google",
    "quick_think_llm": "gemini-2.5-flash",
    "deep_think_llm": "gemini-2.5-pro"
}
```

## 註意事項

1. 所有模型都支持Function Calling
2. 響應時間基於實際測試，可能因網絡和負載而變化
3. 建議根據具體需求選擇合適的模型組合
4. 對於成本敏感的應用，優先使用快速模型
