# 🧪 DeepSeek V3 預覽版測試指南

## 📋 測試目標

幫助用戶系統性地測試DeepSeek V3集成功能，發現問題並提供反馈，共同完善這個高性價比的AI金融分析工具。

## 🚀 快速測試流程

### 第一步：環境準备

```bash
# 1. 克隆預覽分支
git clone -b feature/deepseek-v3-integration https://github.com/hsliuping/TradingAgents-CN.git
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

### 第二步：獲取DeepSeek API密鑰

1. 訪問 [DeepSeek平台](https://platform.deepseek.com/)
2. 註冊账號（支持手機號註冊）
3. 進入控制台 → API Keys
4. 創建新的API Key
5. 複制API Key到.env文件：
   ```bash
   DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   DEEPSEEK_ENABLED=true
   ```

### 第三步：基础功能測試

```bash
# 測試DeepSeek連接
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('DeepSeek API Key:', '✅ 已配置' if os.getenv('DEEPSEEK_API_KEY') else '❌ 未配置')
"

# 測試基本面分析
python tests/test_fundamentals_analysis.py

# 測試DeepSeek Token統計
python tests/test_deepseek_token_tracking.py
```

## 📊 詳細測試項目

### 1. DeepSeek模型集成測試

#### 1.1 API連接測試
```bash
# 測試基本連接
python -c "
from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek
llm = ChatDeepSeek(model='deepseek-chat', temperature=0.1)
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
python examples/demo_deepseek_analysis.py
```

**測試要點**：
- [ ] Token使用量是否正確統計
- [ ] 成本計算是否準確（輸入¥0.001/1K，輸出¥0.002/1K）
- [ ] 統計信息是否實時更新
- [ ] 會話級別的成本跟蹤是否正常

### 2. 基本面分析功能測試

#### 2.1 A股分析測試
```bash
# 測試A股基本面分析
python -c "
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config.update({
    'llm_provider': 'deepseek',
    'llm_model': 'deepseek-chat',
    'quick_think_llm': 'deepseek-chat',
    'deep_think_llm': 'deepseek-chat',
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

**測試股票建议**：
- `000001` - 平安銀行
- `600519` - 贵州茅台  
- `000858` - 五粮液
- `002594` - 比亚迪
- `300750` - 宁德時代

**測試要點**：
- [ ] 是否包含真實財務指標（PE、PB、ROE等）
- [ ] 投資建议是否使用中文（买入/持有/卖出）
- [ ] 行業识別是否準確
- [ ] 評分系統是否合理（0-10分）
- [ ] 風險評估是否完整

#### 2.2 美股分析測試
```bash
# 測試美股基本面分析
python -c "
# 同上配置，測試美股
result = ta.run_analysis('AAPL', '2025-01-08')
print('苹果公司分析:', result)
"
```

**測試股票建议**：
- `AAPL` - 苹果公司
- `MSFT` - 微软
- `GOOGL` - 谷歌
- `TSLA` - 特斯拉

### 3. Web界面測試

```bash
# 啟動Web界面
streamlit run web/app.py
```

訪問 http://localhost:8501 進行測試：

#### 3.1 配置页面測試
- [ ] DeepSeek模型是否出現在選擇列表中
- [ ] API密鑰狀態顯示是否正確
- [ ] 模型切換是否正常工作

#### 3.2 分析页面測試
- [ ] 股票代碼輸入是否正常
- [ ] 分析師選擇是否包含基本面分析師
- [ ] 分析過程是否顯示進度
- [ ] 結果展示是否完整清晰

#### 3.3 Token統計页面測試
- [ ] DeepSeek使用統計是否顯示
- [ ] 成本計算是否準確
- [ ] 歷史記錄是否正確保存

### 4. CLI界面測試

```bash
# 啟動CLI界面
python -m cli.main
```

**測試流程**：
1. 選擇"DeepSeek V3"作為LLM提供商
2. 選擇"deepseek-chat"模型
3. 輸入股票代碼進行分析
4. 檢查分析結果质量

**測試要點**：
- [ ] DeepSeek選項是否可用
- [ ] 模型選擇是否正常
- [ ] 分析流程是否顺畅
- [ ] 結果輸出是否完整

## 🐛 常见問題排查

### 問題1：API密鑰錯誤
```
錯誤：Authentication failed
```
**解決方案**：
1. 檢查API密鑰格式（應以sk-開头）
2. 確認API密鑰有效且有余額
3. 檢查網絡連接

### 問題2：Token統計顯示¥0.0000
**可能原因**：
1. API響應中缺少usage信息
2. Token提取逻辑問題

**排查方法**：
```bash
# 啟用調試模式
export TRADINGAGENTS_LOG_LEVEL=DEBUG
python tests/test_deepseek_token_tracking.py
```

### 問題3：基本面分析顯示模板內容
**可能原因**：
1. 數據獲取失败
2. 分析逻辑問題

**排查方法**：
```bash
# 測試數據獲取
python -c "
from tradingagents.dataflows.tdx_utils import get_china_stock_data
data = get_china_stock_data('000001', '2025-01-01', '2025-01-08')
print('數據獲取結果:', data[:200] if data else '獲取失败')
"
```

## 📝 反馈模板

### 成功測試反馈
```markdown
## ✅ 測試成功

**測試環境**：
- 操作系統：Windows 11 / macOS / Ubuntu
- Python版本：3.10.x
- 測試時間：2025-01-08

**測試項目**：
- [x] DeepSeek API連接
- [x] Token統計功能
- [x] 基本面分析
- [x] Web界面
- [x] CLI界面

**測試體驗**：
- 響應速度：快/中等/慢
- 分析质量：優秀/良好/一般
- 成本控制：满意/一般/不满意
- 整體評價：推薦/可用/需改進

**建议改進**：
（可選）提出改進建议
```

### 問題反馈
```markdown
## 🐛 問題反馈

**問題描述**：
簡要描述遇到的問題

**複現步骤**：
1. 執行的命令或操作
2. 預期結果
3. 實际結果

**環境信息**：
- 操作系統：
- Python版本：
- DeepSeek API密鑰狀態：
- 錯誤日誌：

**截圖**：
（如果有界面問題，請提供截圖）
```

## 🎯 測試重點關註

### 高優先級測試
1. **DeepSeek API集成穩定性**
2. **Token統計準確性**
3. **基本面分析质量**
4. **中文輸出正確性**

### 中優先級測試
1. **Web界面用戶體驗**
2. **CLI界面流畅性**
3. **錯誤處理機制**
4. **性能表現**

### 低優先級測試
1. **邊界情况處理**
2. **並發使用測試**
3. **長時間運行穩定性**

## 📞 獲取幫助

- **GitHub Issues**：https://github.com/hsliuping/TradingAgents-CN/issues
- **測試討論**：GitHub Discussions
- **實時反馈**：在Issue中@hsliuping

---

**感谢您參与測試！您的反馈将幫助我們打造更好的AI金融分析工具。** 🙏
