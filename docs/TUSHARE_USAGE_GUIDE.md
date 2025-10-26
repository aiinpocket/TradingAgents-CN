# Tushare使用指南

## 🎉 恭喜！您的Tushare配置已完成

您的系統已經成功配置並使用Tushare作為默認的中國股票數據源。現在您可以享受高质量、穩定的A股數據服務！

## ✅ 當前配置狀態

```
📊 數據源狀態: ✅ 正常
🔑 TUSHARE_TOKEN: ✅ 已配置 (56字符)
🎯 默認數據源: tushare
📦 可用數據源: tushare, akshare, baostock, tdx(已弃用)
🔗 API連接: ✅ 成功
```

## 🚀 立即開始使用

### 1. 命令行界面 (推薦)

```bash
# 啟動CLI
python -m cli.main

# 選擇分析中國股票
# 系統會自動使用Tushare數據源獲取數據
```

### 2. Web界面

```bash
# 啟動Web界面
python -m streamlit run web/app.py

# 在浏覽器中訪問: http://localhost:8501
# 系統會自動使用Tushare數據源
```

### 3. API調用示例

```python
from tradingagents.dataflows import (
    get_china_stock_data_unified,
    get_china_stock_info_unified
)

# 獲取平安銀行歷史數據
data = get_china_stock_data_unified("000001", "2024-01-01", "2024-12-31")
print(data)

# 獲取股票基本信息
info = get_china_stock_info_unified("000001")
print(info)
```

## 📊 Tushare數據優势

### 与TDX對比
| 特性 | TDX (旧) | Tushare (新) |
|------|----------|--------------|
| 數據质量 | ⚠️ 個人接口 | ✅ 專業API |
| 連接穩定性 | ⚠️ 經常斷線 | ✅ 高可用 |
| 數據完整性 | ⚠️ 部分缺失 | ✅ 完整準確 |
| 更新頻率 | ⚠️ 延迟較大 | ✅ 及時更新 |
| 技術支持 | ❌ 無官方支持 | ✅ 專業支持 |

### 數據覆蓋
- ✅ **股票基础數據**: 所有A股股票信息
- ✅ **歷史行情**: 日線、周線、月線數據
- ✅ **財務數據**: 三大財務報表
- ✅ **實時數據**: 最新價格和交易信息
- ✅ **技術指標**: 常用技術分析指標

## 🎯 常用功能示例

### 1. 股票分析

```python
# 分析平安銀行
from tradingagents.dataflows import get_china_stock_fundamentals_tushare

# 獲取基本面分析
fundamentals = get_china_stock_fundamentals_tushare("000001")
print(fundamentals)
```

### 2. 股票搜索

```python
# 搜索銀行股
from tradingagents.dataflows import search_china_stocks_tushare

results = search_china_stocks_tushare("銀行")
print(results)
```

### 3. 數據源切換

```python
# 查看當前數據源
from tradingagents.dataflows import get_current_china_data_source

current = get_current_china_data_source()
print(current)

# 切換數據源（如果需要）
from tradingagents.dataflows import switch_china_data_source

switch_china_data_source("tushare")  # 確保使用Tushare
```

## ⚡ 性能優化建议

### 1. 利用緩存
- 系統自動緩存數據，重複查詢會更快
- 緩存有效期24小時，確保數據新鮮度

### 2. 批量查詢
```python
# 批量獲取多只股票信息
stocks = ["000001", "000002", "600036", "600519"]
for stock in stocks:
    info = get_china_stock_info_unified(stock)
    print(f"{stock}: {info.split('股票名稱: ')[1].split('\\n')[0]}")
```

### 3. 合理使用API
- Tushare有調用頻率限制
- 建议間隔0.1秒進行連续調用
- 充分利用緩存减少API調用

## 🔧 故障排除

### 常见問題

1. **Token無效**
   ```
   錯誤: 無效的token
   解決: 檢查.env文件中的TUSHARE_TOKEN是否正確
   ```

2. **API調用超限**
   ```
   錯誤: 調用頻率超限
   解決: 等待一分鐘後重試，或升級Tushare账號
   ```

3. **網絡連接問題**
   ```
   錯誤: 連接超時
   解決: 檢查網絡連接，重試操作
   ```

### 調試命令

```bash
# 檢查配置
python -c "
import os
print('TUSHARE_TOKEN:', '已設置' if os.getenv('TUSHARE_TOKEN') else '未設置')
print('DEFAULT_CHINA_DATA_SOURCE:', os.getenv('DEFAULT_CHINA_DATA_SOURCE', 'tushare'))
"

# 測試連接
python -c "
import tushare as ts
import os
ts.set_token(os.getenv('TUSHARE_TOKEN'))
pro = ts.pro_api()
print('Tushare連接測試成功')
"
```

## 📈 高級功能

### 1. 自定義數據源策略

```python
from tradingagents.dataflows.data_source_manager import get_data_source_manager

manager = get_data_source_manager()

# 查看所有可用數據源
print("可用數據源:", [s.value for s in manager.available_sources])

# 設置备用數據源策略
# 主: Tushare -> 备用1: AKShare -> 备用2: BaoStock
```

### 2. 數據质量監控

```python
# 獲取數據時檢查质量
data = get_china_stock_data_unified("000001", "2024-01-01", "2024-12-31")

if "❌" in data:
    print("數據獲取失败，請檢查網絡或API配置")
else:
    print("數據獲取成功，质量良好")
```

## 🎯 最佳實踐

### 1. 環境配置
- 確保`.env`文件中正確設置`TUSHARE_TOKEN`
- 設置`DEFAULT_CHINA_DATA_SOURCE=tushare`
- 定期檢查Token有效性

### 2. 代碼使用
- 優先使用統一接口`get_china_stock_data_unified()`
- 充分利用緩存機制
- 合理控制API調用頻率

### 3. 錯誤處理
- 总是檢查返回結果
- 實現適當的重試機制
- 記錄錯誤日誌便於調試

## 📞 獲取幫助

### 技術支持
- **GitHub Issues**: 報告問題和功能請求
- **文档**: 查看詳細的API文档
- **測試**: 運行`python tests/test_tushare_integration.py`

### Tushare官方
- **官網**: https://tushare.pro/
- **文档**: https://tushare.pro/document/2
- **社区**: Tushare用戶群和論坛

---

🎉 **恭喜您成功配置Tushare！現在可以享受高质量的A股數據服務了！**

💡 **建议**: 立即嘗試運行`python -m cli.main`開始您的股票分析之旅！
