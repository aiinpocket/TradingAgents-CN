---
name: Bug 回報 / Bug Report
about: 回報一個問題幫助我們改進 / Report a bug to help us improve
title: '[BUG] '
labels: ['bug', 'needs-triage']
assignees: ''
---

## 問題描述 / Bug Description

**問題類型 / Issue Type:**
- [ ] 啟動/安裝問題 / Startup/Installation Issue
- [ ] Web 介面問題 / Web Interface Issue
- [ ] CLI 工具問題 / CLI Tool Issue
- [ ] LLM 呼叫問題 / LLM API Issue
- [ ] 資料取得問題 / Data Acquisition Issue
- [ ] Docker 部署問題 / Docker Deployment Issue
- [ ] 配置問題 / Configuration Issue
- [ ] 功能異常 / Feature Malfunction
- [ ] 效能問題 / Performance Issue
- [ ] 其他 / Other: ___________

**簡要描述問題 / Brief description:**
清晰簡潔地描述遇到的問題。

**期望行為 / Expected behavior:**
描述您期望發生的行為。

**實際行為 / Actual behavior:**
描述實際發生的行為。

## 重現步驟 / Steps to Reproduce

請提供詳細的重現步驟：

1. 進入 '...'
2. 點擊 '....'
3. 捲動到 '....'
4. 看到錯誤

## 環境資訊 / Environment

**系統資訊 / System Info:**
- 作業系統 / OS: [例如 Windows 11, macOS 13, Ubuntu 22.04]
- Python 版本 / Python Version: [例如 3.10.0]
- 專案版本 / Project Version: [例如 v0.1.15]

**安裝方式 / Installation Method:**
- [ ] 本機安裝 / Local Installation
- [ ] Docker 部署 / Docker Deployment
- [ ] 其他 / Other: ___________

**依賴版本 / Dependencies:**
```bash
# 請執行以下指令並貼上結果 / Please run the following command and paste the result
pip list | grep -E "(fastapi|uvicorn|langchain|openai|requests|yfinance|finnhub)"
```

**瀏覽器資訊 / Browser Info (僅 Web 介面問題):**
- 瀏覽器 / Browser: [例如 Chrome 120, Firefox 121, Safari 17]
- 瀏覽器版本 / Version:
- 是否使用無痕模式 / Incognito mode: [ ] 是 / Yes [ ] 否 / No

## 配置資訊 / Configuration

**API 配置 / API Configuration:**
- [ ] 已配置 OpenAI API Key
- [ ] 已配置 Google API Key
- [ ] 已配置 Anthropic API Key
- [ ] 已配置 FinnHub API Key
- [ ] 已配置資料庫 / Database configured

**資料來源 / Data Sources:**
- 美股資料來源 / US Stock Source: [yfinance/finnhub]

## 錯誤日誌 / Error Logs

**主控台錯誤 / Console Errors:**
```
請貼上完整的錯誤資訊和堆疊追蹤
Please paste the complete error message and stack trace
```

**日誌檔案 / Log Files:**
```bash
# 如果啟用了日誌記錄，請提供相關日誌
# If logging is enabled, please provide relevant logs

# Web 應用日誌 / Web app logs
tail -n 50 logs/tradingagents.log

# Docker 日誌 / Docker logs
docker-compose logs web
```

**網路請求錯誤 / Network Request Errors:**
如果是 API 呼叫問題，請提供：
- API 回應狀態碼 / API response status code
- 錯誤回應內容 / Error response content
- 請求參數（隱藏敏感資訊）/ Request parameters (hide sensitive info)

## 截圖 / Screenshots

如果適用，請新增截圖來幫助說明問題。
If applicable, add screenshots to help explain your problem.

## 額外資訊 / Additional Context

新增任何其他有關問題的上下文資訊。
Add any other context about the problem here.

## 檢查清單 / Checklist

請確認您已經：
- [ ] 搜尋了現有的 issues，確認這不是重複問題
- [ ] 使用了最新版本的程式碼
- [ ] 提供了完整的錯誤資訊
- [ ] 包含了重現步驟
- [ ] 填寫了環境資訊

---

**感謝您的回饋！我們會盡快處理這個問題。**
**Thank you for your feedback! We will address this issue as soon as possible.**
