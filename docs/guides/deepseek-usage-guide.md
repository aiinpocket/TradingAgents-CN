# 🧠 DeepSeek V3 使用指南

## 📋 概述

DeepSeek V3 是TradingAgents-CN v0.1.7新集成的成本優化AI模型，專為中文金融場景設計。相比GPT-4，DeepSeek V3在保持優秀分析质量的同時，成本降低90%以上，是進行股票分析的理想選擇。

## 🎯 DeepSeek V3 特色

### 核心優势

| 特性 | DeepSeek V3 | GPT-4 | 優势說明 |
|------|-------------|-------|----------|
| **💰 成本** | $0.14/1M tokens | $15/1M tokens | 便宜90%+ |
| **🇨🇳 中文理解** | 優秀 | 良好 | 專門優化 |
| **🔧 工具調用** | 强大 | 强大 | 數學計算優势 |
| **⚡ 響應速度** | 快速 | 中等 | 更快響應 |
| **📊 金融分析** | 專業 | 通用 | 領域優化 |

### 技術特性

- ✅ **64K上下文長度**: 支持長文档分析
- ✅ **Function Calling**: 强大的工具調用能力
- ✅ **數學推理**: 優秀的數值計算和逻辑推理
- ✅ **中文優化**: 專為中文場景训練
- ✅ **實時響應**: 平均響應時間<3秒

## 🚀 快速開始

### 獲取API密鑰

#### 1. 註冊DeepSeek账號
```bash
# 訪問DeepSeek平台
https://platform.deepseek.com/

# 註冊流程:
1. 點擊"註冊"按钮
2. 填寫邮箱和密碼
3. 驗證邮箱
4. 完成實名認證 (可選)
```

#### 2. 創建API密鑰
```bash
# 登錄後操作:
1. 進入控制台
2. 點擊"API Keys"
3. 點擊"創建新密鑰"
4. 設置密鑰名稱
5. 複制API密鑰 (sk-開头)
```

#### 3. 充值账戶
```bash
# 充值建议:
- 新用戶: ¥50-100 (可用很久)
- 重度用戶: ¥200-500
- 企業用戶: ¥1000+

# 成本參考:
- 單次分析: ¥0.01-0.05
- 日常使用: ¥5-20/月
- 重度使用: ¥50-100/月
```

### 配置DeepSeek

#### 環境變量配置
```bash
# 編辑.env文件
DEEPSEEK_API_KEY=sk-your_deepseek_api_key_here
DEEPSEEK_ENABLED=true
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

#### Docker環境配置
```bash
# docker-compose.yml 已自動配置
# 只需在.env文件中設置API密鑰即可

# 重啟服務應用配置
docker-compose restart web
```

#### 本地環境配置
```bash
# 確保已安裝最新依賴
pip install -r requirements.txt

# 重啟應用
streamlit run web/app.py
```

## 📊 使用指南

### 基础使用

#### 1. 選擇DeepSeek模型
```bash
# 在Web界面中:
1. 訪問 http://localhost:8501
2. 在左侧邊栏選擇"LLM模型"
3. 選擇"DeepSeek V3"
4. 確認模型狀態為"可用"
```

#### 2. 進行股票分析
```bash
# 分析流程:
1. 輸入股票代碼 (如: 000001, AAPL)
2. 選擇分析深度:
   - 快速分析 (2-3分鐘)
   - 標準分析 (5-8分鐘)  
   - 深度分析 (10-15分鐘)
3. 選擇分析師類型:
   - 技術分析師
   - 基本面分析師
   - 新聞分析師
   - 综合分析
4. 點擊"開始分析"
```

#### 3. 查看分析結果
```bash
# 分析結果包含:
📈 技術指標分析
💰 基本面評估
📰 新聞情绪分析
🎯 投資建议
⚠️ 風險提示
📊 價格預測
```

### 高級功能

#### 智能模型路由
```bash
# 配置智能路由
LLM_SMART_ROUTING=true
LLM_PRIORITY_ORDER=deepseek,qwen,gemini,openai

# 路由策略:
- 常規分析 → DeepSeek V3 (成本優化)
- 複雜推理 → Gemini (推理能力)
- 中文內容 → 通義千問 (中文理解)
- 通用任務 → GPT-4 (综合能力)
```

#### 成本控制
```bash
# 成本監控配置
LLM_DAILY_COST_LIMIT=10.0          # 日成本限制 (美元)
LLM_COST_ALERT_THRESHOLD=8.0       # 告警阈值
LLM_AUTO_SWITCH_ON_LIMIT=true      # 超限自動切換

# 成本優化策略:
✅ 優先使用DeepSeek V3
✅ 啟用智能緩存
✅ 避免重複分析
✅ 合理選擇分析深度
```

## 💰 成本分析

### 成本對比

#### 單次分析成本
| 分析類型 | DeepSeek V3 | GPT-4 | 節省 |
|---------|-------------|-------|------|
| **快速分析** | ¥0.01-0.02 | ¥0.15-0.30 | 90%+ |
| **標準分析** | ¥0.02-0.05 | ¥0.30-0.60 | 90%+ |
| **深度分析** | ¥0.05-0.10 | ¥0.60-1.20 | 90%+ |

#### 月度使用成本
| 使用頻率 | DeepSeek V3 | GPT-4 | 節省 |
|---------|-------------|-------|------|
| **轻度使用** (10次/天) | ¥5-10 | ¥50-100 | 90%+ |
| **中度使用** (50次/天) | ¥20-40 | ¥200-400 | 90%+ |
| **重度使用** (100次/天) | ¥40-80 | ¥400-800 | 90%+ |

### 成本優化建议

#### 1. 合理選擇分析深度
```bash
# 建议策略:
✅ 日常監控 → 快速分析
✅ 投資決策 → 標準分析
✅ 重要決策 → 深度分析
✅ 學习研究 → 深度分析
```

#### 2. 啟用緩存機制
```bash
# 緩存配置
LLM_ENABLE_CACHE=true
LLM_CACHE_TTL=3600  # 1小時緩存

# 緩存效果:
- 重複查詢成本為0
- 相似股票分析成本降低50%
- 歷史數據查詢免費
```

#### 3. 批量分析優化
```bash
# 批量分析策略:
✅ 同時分析多只相關股票
✅ 使用行業對比分析
✅ 利用歷史分析結果
✅ 合並相似查詢
```

## 🔧 最佳實踐

### 1. 提示詞優化

#### 针對中文股票
```bash
# 優化的提示詞示例:
"請分析A股股票{股票代碼}的投資價值，重點關註：
1. 技術指標趋势
2. 基本面財務狀况  
3. 行業地位和競爭優势
4. 近期新聞和政策影響
5. 風險因素和投資建议

請用專業的中文金融術語，提供具體的數據支撑。"
```

#### 针對美股
```bash
# 美股分析提示詞:
"Please analyze the US stock {symbol} focusing on:
1. Technical indicators and trends
2. Fundamental analysis and financials
3. Market position and competitive advantages  
4. Recent news and market sentiment
5. Risk assessment and investment recommendations

Please provide data-driven insights with specific metrics."
```

### 2. 參數調優

#### 模型參數配置
```bash
# 推薦參數設置
DEEPSEEK_TEMPERATURE=0.3        # 降低隨機性，提高一致性
DEEPSEEK_MAX_TOKENS=4000        # 適中的輸出長度
DEEPSEEK_TOP_P=0.8             # 平衡創造性和準確性
DEEPSEEK_FREQUENCY_PENALTY=0.1  # 减少重複內容
```

#### 請求優化
```bash
# 性能優化配置
DEEPSEEK_REQUEST_TIMEOUT=30     # 請求超時時間
DEEPSEEK_MAX_RETRIES=3         # 最大重試次數
DEEPSEEK_RETRY_DELAY=1         # 重試延迟
DEEPSEEK_CONCURRENT_REQUESTS=3  # 並發請求數
```

### 3. 质量控制

#### 結果驗證
```bash
# 分析质量檢查:
✅ 數據準確性驗證
✅ 逻辑一致性檢查
✅ 中文表達质量
✅ 專業術語使用
✅ 投資建议合理性
```

#### 錯誤處理
```bash
# 常见問題處理:
- API限流 → 自動重試
- 網絡超時 → 降級處理
- 余額不足 → 切換模型
- 內容過濾 → 調整提示詞
```

## 🚨 故障排除

### 常见問題

#### 1. API密鑰無效
```bash
# 檢查步骤:
1. 確認API密鑰格式 (sk-開头)
2. 檢查密鑰是否過期
3. 驗證账戶余額
4. 確認API權限

# 解決方案:
- 重新生成API密鑰
- 充值账戶余額
- 聯系DeepSeek客服
```

#### 2. 請求失败
```bash
# 常见錯誤:
- 429: 請求頻率過高 → 降低並發數
- 401: 認證失败 → 檢查API密鑰
- 500: 服務器錯誤 → 稍後重試
- 超時: 網絡問題 → 檢查網絡連接

# 調試方法:
docker logs TradingAgents-web | grep deepseek
```

#### 3. 分析质量問題
```bash
# 质量優化:
- 調整temperature參數
- 優化提示詞內容
- 增加上下文信息
- 使用更具體的指令
```

### 性能監控

```bash
# 監控指標:
📊 API調用成功率
⏱️ 平均響應時間
💰 成本使用情况
🔄 緩存命中率
⚠️ 錯誤率統計

# 監控命令:
# 查看使用統計
curl http://localhost:8501/api/stats

# 查看成本統計
curl http://localhost:8501/api/costs
```

## 📈 進階技巧

### 1. 自定義分析模板
```python
# 創建專門的DeepSeek分析模板
deepseek_template = """
作為專業的中國股市分析師，請對{symbol}進行全面分析：

## 技術分析
- K線形態和趋势
- 主要技術指標 (MA, RSI, MACD)
- 支撑位和阻力位
- 成交量分析

## 基本面分析  
- 財務指標評估
- 行業地位分析
- 競爭優势評估
- 成長性分析

## 風險評估
- 市場風險
- 行業風險  
- 公司特定風險
- 政策風險

請提供具體的投資建议和目標價位。
"""
```

### 2. 批量分析腳本
```python
# 批量分析多只股票
import asyncio
from tradingagents.llm_adapters.deepseek_adapter import ChatDeepSeek

async def batch_analysis(symbols):
    llm = ChatDeepSeek()
    results = {}
    
    for symbol in symbols:
        try:
            result = await llm.analyze_stock(symbol)
            results[symbol] = result
            print(f"✅ {symbol} 分析完成")
        except Exception as e:
            print(f"❌ {symbol} 分析失败: {e}")
    
    return results

# 使用示例
symbols = ['000001', '600519', '000858', '002415']
results = asyncio.run(batch_analysis(symbols))
```

---

## 📞 獲取幫助

### DeepSeek支持
- 🌐 [DeepSeek官網](https://platform.deepseek.com/)
- 📚 [DeepSeek文档](https://platform.deepseek.com/docs)
- 💬 [DeepSeek社区](https://github.com/deepseek-ai)

### TradingAgents-CN支持
- 🐛 [GitHub Issues](https://github.com/hsliuping/TradingAgents-CN/issues)
- 💬 [GitHub Discussions](https://github.com/hsliuping/TradingAgents-CN/discussions)
- 📚 [完整文档](https://github.com/hsliuping/TradingAgents-CN/tree/main/docs)

---

*最後更新: 2025-07-13*  
*版本: cn-0.1.7*  
*模型版本: DeepSeek V3*
