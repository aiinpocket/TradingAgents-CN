# CLI 和 Web 端報告內容統一優化

## 📋 問題描述

用戶反饋 CLI 命令行生成的報告內容和 Web 端生成的報告內容不一樣，Web 端的內容少了一些團隊決策分析部分。

## 🔍 問題分析

### CLI 端包含的完整報告結構：
- ✅ **I. 分析師團隊報告** (Analyst Team Reports)
  - 市場分析師 (Market Analyst)
  - 社交媒體分析師 (Social Analyst) 
  - 新聞分析師 (News Analyst)
  - 基本面分析師 (Fundamentals Analyst)

- ✅ **II. 研究團隊決策** (Research Team Decision)
  - 多頭研究員 (Bull Researcher)
  - 空頭研究員 (Bear Researcher) 
  - 研究經理決策 (Research Manager)

- ✅ **III. 交易團隊計劃** (Trading Team Plan)
  - 交易員計劃 (Trader Plan)

- ✅ **IV. 風險管理團隊決策** (Risk Management Team)
  - 激進分析師 (Aggressive Analyst)
  - 保守分析師 (Conservative Analyst)
  - 中性分析師 (Neutral Analyst)

- ✅ **V. 投資組合經理決策** (Portfolio Manager Decision)

### Web 端原來僅包含的簡化報告結構：
- ✅ **基礎分析模塊**
  - 市場技術分析 (market_report)
  - 基本面分析 (fundamentals_report)
  - 市場情緒分析 (sentiment_report)
  - 新聞事件分析 (news_report)
  - 風險評估 (risk_assessment)
  - 投資建議 (investment_plan)

## 🛠️ 優化方案

### 1. 擴展 Web 端狀態處理邏輯

**文件**: `web/utils/analysis_runner.py`

```python
# 處理各個分析模塊的結果 - 包含完整的智能體團隊分析
analysis_keys = [
    'market_report',
    'fundamentals_report', 
    'sentiment_report',
    'news_report',
    'risk_assessment',
    'investment_plan',
    # 添加缺失的團隊決策數據，確保與CLI端一致
    'investment_debate_state',  # 研究團隊辩論（多頭/空頭研究員）
    'trader_investment_plan',   # 交易團隊計劃
    'risk_debate_state',        # 風險管理團隊決策
    'final_trade_decision'      # 最終交易決策
]
```

### 2. 增強 Web 端報告生成器

**文件**: `web/utils/report_exporter.py`

#### 添加團隊決策報告生成方法：
- `_add_team_decision_reports()` - 添加完整的團隊決策報告
- `_format_team_decision_content()` - 格式化團隊決策內容

#### 新增報告部分：
- 🔬 研究團隊決策
- 💼 交易團隊計劃  
- ⚖️ 風險管理團隊決策
- 🎯 最終交易決策

### 3. 改進分模塊報告保存

添加團隊決策報告模塊：
- `research_team_decision.md` - 研究團隊決策報告
- `risk_management_decision.md` - 風險管理團隊決策報告

## ✅ 優化結果

### 統一後的完整報告結構：

1. **🎯 投資決策摘要**
   - 投資建議、置信度、風險評分、目標價位

2. **📊 詳細分析報告**
   - 📈 市場技術分析
   - 💰 基本面分析
   - 💭 市場情緒分析
   - 📰 新聞事件分析
   - ⚠️ 風險評估
   - 📋 投資建議

3. **🔬 研究團隊決策** *(新增)*
   - 📈 多頭研究員分析
   - 📉 空頭研究員分析
   - 🎯 研究經理綜合決策

4. **💼 交易團隊計劃** *(新增)*
   - 專業交易員制定的具體交易執行計劃

5. **⚖️ 風險管理團隊決策** *(新增)*
   - 🚀 激進分析師評估
   - 🛡️ 保守分析師評估
   - ⚖️ 中性分析師評估
   - 🎯 投資組合經理最終決策

6. **🎯 最終交易決策** *(新增)*
   - 綜合所有團隊分析後的最終投資決策

## 🎉 優化效果

- ✅ **內容一致性**: CLI 和 Web 端現在生成相同結構和內容的報告
- ✅ **完整性提升**: Web 端報告現在包含所有智能體團隊的分析結果
- ✅ **用戶體驗**: 用戶無論使用哪種方式都能獲得完整的分析報告
- ✅ **模塊化保存**: 支持將團隊決策報告保存為獨立的模塊文件

## 📝 使用說明

優化後，Web 端生成的報告將包含：
- 完整的智能體團隊分析過程
- 多頭/空頭研究員的辩論分析
- 風險管理團隊的多角度評估
- 最終的綜合投資決策

這確保了 CLI 和 Web 端用戶都能獲得相同品質和深度的分析報告。
