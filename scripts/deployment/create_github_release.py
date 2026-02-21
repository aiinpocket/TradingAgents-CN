#!/usr/bin/env python3
"""
建立GitHub Release的指令碼
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')


def run_command(command, cwd=None):
    """執行命令並返回結果（不使用 shell=True，避免命令注入風險）"""
    import shlex
    try:
        args = shlex.split(command) if isinstance(command, str) else command
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_release_notes():
    """建立發布說明"""
    release_notes = """
## Web管理介面與多LLM提供商支援

TradingAgents-CN v0.1.2 帶來了重大更新，新增了完整的Web管理介面和多LLM提供商支援！

### 主要新功能

#### Streamlit Web管理介面
- 完整的Web股票分析平台
- 直觀的使用者介面和即時進度顯示
- 支援多種LLM提供商選擇（OpenAI / Anthropic）
- 視覺化的分析結果展示
- 回應式設計，支援行動裝置存取

#### 多LLM提供商支援
- OpenAI（GPT-4、GPT-4o-mini）
- Anthropic（Claude 4 系列）
- Web介面支援LLM提供商無縫切換
- 統一的配置管理介面

### 改進優化

- 新增分析配置資訊顯示
- 項目結構優化（tests/docs/web目錄規範化）
- 多種API服務配置支援
- 完整的測試體系（25+個測試檔案）
- 完整的使用檔案和配置指南

### 快速開始

#### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

#### 2. 配置API密鑰
```bash
# 複製環境變數模板
cp .env.example .env

# 編輯 .env 檔案，新增您的API密鑰
# OPENAI_API_KEY=your_openai_key        # OpenAI（推薦）
# ANTHROPIC_API_KEY=your_anthropic_key  # Anthropic（可選）
```

#### 3. 啟動Web介面
```bash
# 啟動Web管理介面
python -m streamlit run web/app.py

# 或使用啟動指令碼
python start_web.py
```

#### 4. 使用CLI工具
```bash
# 使用OpenAI模型
python cli/main.py --stock AAPL --analysts market fundamentals

# 使用Anthropic模型
python cli/main.py --llm-provider anthropic --model claude-sonnet-4 --stock TSLA
```

### 檔案和支援

- [完整檔案](./docs/)
- [Web介面指南](./web/README.md)
- [測試指南](./tests/README.md)
- [範例程式碼](./examples/)

### 推薦配置

**最佳性能組合**：
- **LLM提供商**: OpenAI 或 Anthropic
- **推薦模型**: gpt-4o-mini / claude-sonnet-4
- **分析師**: 市場技術 + 基本面分析師

### 致謝

感謝 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 原始項目的開發者們，為金融AI領域提供了優秀的開源框架。

### 許可證

本項目遵循 Apache 2.0 許可證。

---

**立即體驗**: `python -m streamlit run web/app.py`
"""
    return release_notes.strip()

def show_release_info():
    """顯示發布資訊"""
    logger.info(f" TradingAgents-CN v0.1.2 已成功發布到GitHub！")
    logger.info(f"=")
    
    logger.info(f"\n 發布內容:")
    logger.info(f"  完整的Web管理介面")
    logger.info(f"  多LLM提供商支援（OpenAI / Anthropic）")
    logger.info(f"  完整的測試體系")
    logger.info(f"  詳細的使用檔案")
    
    logger.info(f"\n GitHub連結:")
    logger.info(f"   Release: https://github.com/aiinpocket/TradingAgents-CN/releases/tag/cn-v0.1.2")
    logger.info(f"   代碼: https://github.com/aiinpocket/TradingAgents-CN")
    
    logger.info(f"\n 快速開始:")
    logger.info(f"  1. git clone https://github.com/aiinpocket/TradingAgents-CN.git")
    logger.info(f"  2. cd TradingAgents-CN")
    logger.info(f"  3. pip install -r requirements.txt")
    logger.info(f"  4. python -m streamlit run web/app.py")
    
    logger.info(f"\n主要特性:")
    logger.info(f"  Web介面股票分析")
    logger.info(f"  多LLM提供商支援（OpenAI / Anthropic）")
    logger.info(f"  即時分析進度顯示")
    logger.info(f"  多分析師協作決策")
    logger.info(f"  完整的繁體中文支援")

def main():
    """主函式"""
    logger.info(f" 建立GitHub Release")
    logger.info(f"=")
    
    # 檢查是否在正確的分支
    success, stdout, stderr = run_command("git branch --show-current")
    if not success or stdout.strip() != "main":
        logger.error(f" 請確保在main分支上，當前分支: {stdout.strip()}")
        return False
    
    # 檢查是否有未推送的提交
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        logger.error(f" Git狀態檢查失敗: {stderr}")
        return False
    
    if stdout.strip():
        logger.error(f" 發現未提交的更改，請先提交所有更改")
        return False
    
    logger.info(f" Git狀態檢查通過")
    
    # 檢查標籤是否存在
    success, stdout, stderr = run_command("git tag -l cn-v0.1.2")
    if not success or "cn-v0.1.2" not in stdout:
        logger.error(f" 標籤 cn-v0.1.2 不存在")
        return False
    
    logger.info(f" 版本標籤檢查通過")
    
    # 生成發布說明
    release_notes = create_release_notes()
    
    # 保存發布說明到檔案
    with open("RELEASE_NOTES_v0.1.2.md", "w", encoding="utf-8") as f:
        f.write(release_notes)
    
    logger.info(f" 發布說明已生成")
    
    # 顯示GitHub Release建立指南
    logger.info(f"\n GitHub Release建立指南:")
    logger.info(f"=")
    logger.info(f"1. 存取: https://github.com/aiinpocket/TradingAgents-CN/releases/new")
    logger.info(f"2. 選擇標籤: cn-v0.1.2")
    logger.info(f"3. 發布標題: TradingAgents-CN v0.1.2 - Web管理介面")
    logger.info(f"4. 複製 RELEASE_NOTES_v0.1.2.md 的內容到描述框")
    logger.info(f"5. 勾選 'Set as the latest release'")
    logger.info(f"6. 點擊 'Publish release'")
    
    # 顯示發布資訊
    show_release_info()
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info(f"\n GitHub Release準備完成！")
        logger.info(f"請按照上述指南在GitHub上建立Release")
    else:
        logger.error(f"\n GitHub Release準備失敗")
        sys.exit(1)
