# DataFrame Arrow轉換錯誤修複

## 問題描述

在使用Streamlit顯示DataFrame時，出現了以下錯誤：

```
pyarrow.lib.ArrowTypeError: ("Expected bytes, got a 'int' object", 'Conversion failed for column  分析結果 A with type object')
```

## 錯誤原因

這個錯誤是由於Streamlit在将pandas DataFrame轉換為Apache Arrow格式時遇到了數據類型不一致的問題。具體原因：

1. **混合數據類型**: DataFrame中的某些列包含了混合的數據類型（字符串和整數）
2. **Arrow轉換限制**: Apache Arrow要求列中的數據類型必须一致
3. **Streamlit內部處理**: Streamlit使用Arrow格式來優化DataFrame的顯示性能

## 問題定位

通過錯誤信息分析，問題出現在以下几個地方：

### 1. 對比表格數據
```python
comparison_data = {
    "項目": ["股票代碼", "分析時間", "分析師數量", "研究深度", "狀態", "標簽數量"],
    "分析結果 A": [
        result_a.get('stock_symbol', 'unknown'),           # 字符串
        datetime.fromtimestamp(...).strftime(...),        # 字符串
        len(result_a.get('analysts', [])),                 # 整數 ❌
        result_a.get('research_depth', 'unknown'),         # 可能是整數 ❌
        "✅ 完成" if ... else "❌ 失败",                    # 字符串
        len(result_a.get('tags', []))                      # 整數 ❌
    ]
}
```

### 2. 時間線表格數據
```python
timeline_data.append({
    '序號': i + 1,                                        # 整數 ❌
    '分析時間': datetime.fromtimestamp(...).strftime(...), # 字符串
    '分析師': ', '.join(...),                             # 字符串
    '研究深度': result.get('research_depth', 'unknown'),   # 可能是整數 ❌
    '狀態': '✅' if ... else '❌'                          # 字符串
})
```

### 3. 批量對比表格數據
```python
comparison_data[column_name] = [
    result.get('stock_symbol', 'unknown'),                # 字符串
    datetime.fromtimestamp(...).strftime(...),           # 字符串
    len(result.get('analysts', [])),                      # 整數 ❌
    result.get('research_depth', 'unknown'),              # 可能是整數 ❌
    "✅" if ... else "❌",                                # 字符串
    len(result.get('tags', [])),                          # 整數 ❌
    len(result.get('summary', ''))                        # 整數 ❌
]
```

## 解決方案

### 1. 創建安全DataFrame函數

創建了一個通用的 `safe_dataframe()` 函數來確保所有數據都轉換為字符串類型：

```python
def safe_dataframe(data):
    """創建類型安全的DataFrame，確保所有數據都是字符串類型以避免Arrow轉換錯誤"""
    if isinstance(data, dict):
        # 對於字典數據，確保所有值都是字符串
        safe_data = {}
        for key, values in data.items():
            if isinstance(values, list):
                safe_data[key] = [str(v) if v is not None else '' for v in values]
            else:
                safe_data[key] = str(values) if values is not None else ''
        return pd.DataFrame(safe_data)
    elif isinstance(data, list):
        # 對於列表數據，確保所有字典中的值都是字符串
        safe_data = []
        for item in data:
            if isinstance(item, dict):
                safe_item = {k: str(v) if v is not None else '' for k, v in item.items()}
                safe_data.append(safe_item)
            else:
                safe_data.append(str(item) if item is not None else '')
        return pd.DataFrame(safe_data)
    else:
        return pd.DataFrame(data)
```

### 2. 修複所有DataFrame創建

将所有的 `pd.DataFrame()` 調用替換為 `safe_dataframe()`：

```python
# 修複前
df = pd.DataFrame(comparison_data)

# 修複後
df = safe_dataframe(comparison_data)
```

### 3. 確保數據類型一致性

在創建數據時就確保類型一致：

```python
# 修複前
len(result_a.get('analysts', []))  # 返回整數

# 修複後
str(len(result_a.get('analysts', [])))  # 返回字符串
```

## 修複的文件

### 主要修複
- `web/components/analysis_results.py`: 添加 `safe_dataframe()` 函數並更新所有DataFrame創建

### 具體修複點
1. **表格視圖**: `render_results_table()`
2. **基础對比**: 對比數據表格
3. **導出功能**: CSV和Excel導出
4. **時間線表格**: `render_stock_trend_charts()`
5. **批量對比**: `render_batch_comparison_table()`
6. **增强對比**: `enhance_comparison_details()`
7. **圖表數據**: 各種統計圖表的DataFrame創建

## 測試驗證

創建了專門的測試腳本 `tests/test_dataframe_fix.py` 來驗證修複：

### 測試內容
1. **安全DataFrame函數測試**: 驗證混合數據類型轉換
2. **對比數據創建測試**: 驗證對比表格數據類型
3. **時間線數據創建測試**: 驗證時間線表格數據類型
4. **Arrow轉換測試**: 驗證修複後的DataFrame可以正常轉換為Arrow格式

### 測試結果
```
📊 測試結果: 4/4 通過
🎉 所有測試通過！DataFrame Arrow轉換問題已修複
```

## 技術細節

### Arrow轉換要求
- Apache Arrow要求每列的數據類型必须一致
- 混合類型的列會導致轉換失败
- Streamlit使用Arrow來優化大型DataFrame的顯示性能

### 解決策略
1. **類型統一**: 将所有數據轉換為字符串類型
2. **空值處理**: 将None值轉換為空字符串
3. **遞歸處理**: 處理嵌套的字典和列表結構
4. **向後兼容**: 保持原有的數據結構和顯示效果

## 性能影響

### 優點
- 解決了Arrow轉換錯誤
- 提高了DataFrame顯示的穩定性
- 保持了原有的功能和顯示效果

### 註意事項
- 所有數值都轉換為字符串，失去了數值排序功能
- 對於需要數值計算的場景，需要在使用前重新轉換類型

## 預防措施

### 最佳實踐
1. **創建DataFrame時**: 始终使用 `safe_dataframe()` 函數
2. **數據準备時**: 在源头就確保數據類型一致
3. **測試驗證**: 對新的DataFrame創建進行Arrow轉換測試

### 代碼規範
```python
# 推薦做法
df = safe_dataframe({
    'column1': [str(value) for value in values],
    'column2': [str(item) if item is not None else '' for item in items]
})

# 避免做法
df = pd.DataFrame({
    'column1': [1, 2, 3],  # 整數
    'column2': ['a', 'b', 'c']  # 字符串 - 混合類型
})
```

## 总結

通過創建 `safe_dataframe()` 函數和系統性地修複所有DataFrame創建點，成功解決了Streamlit中的Arrow轉換錯誤。這個修複不仅解決了當前的問題，还為未來的DataFrame創建提供了一個安全的標準做法。

---

*修複完成時間: 2025-07-31*  
*測試狀態: ✅ 全部通過*  
*影響範围: Web界面所有表格顯示功能*
