# 🧪 

## 📋 測試目標

幫助用戶系統性地測試

## 🚀 快速測試流程

### 第一步：環境準備

```bash
# 1. 克隆預覽分支
git clone -b feature/
cd TradingAgents-CN

# 2. 創建虛擬環境
python -m venv env
env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/macOS

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 配置環境變量
cp .env.example .env
```

### 第二步：獲取

1. 訪問 [OpenAI Platform](https://platform.openai.com/) 或 [Google AI Studio](https://aistudio.google.com/)
2. 註冊帳號
3. 進入控制台 → API Keys
4. 建立新的API Key
5. 複製API Key到.env文件：
   ```bash
   OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

### 第三步：基礎功能測試

```bash
# 測試
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('
"

# 測試基本面分析
python tests/test_fundamentals_analysis.py

# 測試
python tests/test_
```

## 📊 詳細測試項目

### 1. 

#### 1.1 API連接測試
```bash
# 測試基本連接
python -c "
from tradingagents.llm_adapters.
llm = Chat
response = llm.invoke('你好，請簡單介紹一下股票投資')
print('響應:', response.content[:100] + '...')
"
```

**測試要點**：
- [ ] API密鑰是否正確配置
- [ ] 網絡連接是否正常
- [ ] 響應時間是否合理（通常5-15秒）
- [ ] 返回內容是否為中文

#### 1.2 Token統計測試
```bash
# 測試Token使用統計
python examples/demo_
```

**測試要點**：
- [ ] Token使用量是否正確統計
- [ ] 成本計算是否準確（輸入¥0.001/1K，輸出¥0.002/1K）
- [ ] 統計信息是否實時更新
- [ ] 會話級別的成本跟蹤是否正常

### 2. 基本面分析功能測試

#### 2.1 分析測試
```bash
# 測試基本面分析
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config.update({
    'llm_provider': '
    'llm_model': '
    'quick_think_llm': '
    'deep_think_llm': '
})

ta = TradingAgentsGraph(
    selected_analysts=['fundamentals'],
    config=config
)

# 測試招商銀行
result = ta.run_analysis('000001', '2025-01-08')
print('分析結果:', result)
"
```

**測試股票建議**：
- `000001` - 平安銀行
- `600519` - 贵州茅台  
- `000858` - 五糧液
- `002594` - 比亞迪
- `300750` - 寧德時代

**測試要點**：
- [ ] 是否包含真實財務指標（PE、PB、ROE等）
- [ ] 投資建議是否使用中文（買入/持有/賣出）
- [ ] 行業識別是否準確
- [ ] 評分系統是否合理（0-10分）
- [ ] 風險評估是否完整

#### 2.2 美股分析測試
```bash
# 測試美股基本面分析
python -c "
# 同上配置，測試美股
result = ta.run_analysis('AAPL', '2025-01-08')
print('蘋果公司分析:', result)
"
```

**測試股票建議**：
- `AAPL` - 蘋果公司
- `MSFT` - 微軟
- `GOOGL` - 谷歌
- `TSLA` - 特斯拉

### 3. Web界面測試

```bash
# 啟動Web界面
streamlit run web/app.py
```

訪問 http://localhost:8501 進行測試：

#### 3.1 配置頁面測試
- [ ] 
- [ ] API密鑰狀態顯示是否正確
- [ ] 模型切換是否正常工作

#### 3.2 分析頁面測試
- [ ] 股票代碼輸入是否正常
- [ ] 分析師選擇是否包含基本面分析師
- [ ] 分析過程是否顯示進度
- [ ] 結果展示是否完整清晰

#### 3.3 Token統計頁面測試
- [ ] 
- [ ] 成本計算是否準確
- [ ] 歷史記錄是否正確保存

### 4. CLI界面測試

```bash
# 啟動CLI界面
python -m cli.main
```

**測試流程**：
1. 選擇"
2. 選擇"
3. 輸入股票代碼進行分析
4. 檢查分析結果品質

**測試要點**：
- [ ] 
- [ ] 模型選擇是否正常
- [ ] 分析流程是否順暢
- [ ] 結果輸出是否完整

## 🐛 常見問題排查

### 問題1：API密鑰錯誤
```
錯誤：Authentication failed
```
**解決方案**：
1. 檢查API密鑰格式（應以sk-開頭）
2. 確認API密鑰有效且有餘額
3. 檢查網絡連接

### 問題2：Token統計顯示¥0.0000
**可能原因**：
1. API響應中缺少usage信息
2. Token提取邏輯問題

**排查方法**：
```bash
# 啟用調試模式
export TRADINGAGENTS_LOG_LEVEL=DEBUG
python tests/test_
```

### 問題3：基本面分析顯示模板內容
**可能原因**：
1. 數據獲取失敗
2. 分析邏輯問題

**排查方法**：
```bash
# 測試數據獲取
python -c "
from tradingagents.dataflows.tdx_utils import get_china_stock_data
data = get_china_stock_data('000001', '2025-01-01', '2025-01-08')
print('數據獲取結果:', data[:200] if data else '獲取失敗')
"
```

## 📝 反饋模板

### 成功測試反饋
```markdown
## ✅ 測試成功

**測試環境**：
- 操作系統：Windows 11 / macOS / Ubuntu
- Python版本：3.10.x
- 測試時間：2025-01-08

**測試項目**：
- [x] 
- [x] Token統計功能
- [x] 基本面分析
- [x] Web界面
- [x] CLI界面

**測試體驗**：
- 響應速度：快/中等/慢
- 分析品質：優秀/良好/一般
- 成本控制：滿意/一般/不滿意
- 整體評價：推薦/可用/需改進

**建議改進**：
（可選）提出改進建議
```

### 問題反饋
```markdown
## 🐛 問題反饋

**問題描述**：
簡要描述遇到的問題

**複現步驟**：
1. 執行的命令或操作
2. 預期結果
3. 實際結果

**環境信息**：
- 操作系統：
- Python版本：
- 
- 錯誤日誌：

**截圖**：
（如果有界面問題，請提供截圖）
```

## 🎯 測試重點關註

### 高優先級測試
1. **
2. **Token統計準確性**
3. **基本面分析品質**
4. **中文輸出正確性**

### 中優先級測試
1. **Web界面用戶體驗**
2. **CLI界面流畅性**
3. **錯誤處理機制**
4. **性能表現**

### 低優先級測試
1. **邊界情況處理**
2. **並發使用測試**
3. **長時間運行穩定性**

## 📞 獲取幫助

- **GitHub Issues**：https://github.com/hsliuping/TradingAgents-CN/issues
- **測試討論**：GitHub Discussions
- **實時反饋**：在Issue中@hsliuping

---

**感謝您參與測試！您的反饋將幫助我們打造更好的AI金融分析工具。** 🙏
