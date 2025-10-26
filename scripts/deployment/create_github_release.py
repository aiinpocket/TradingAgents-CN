#!/usr/bin/env python3
"""
創建GitHub Release的腳本
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')


def run_command(command, cwd=None):
    """運行命令並返回結果"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_release_notes():
    """創建發布說明"""
    release_notes = """
## 🌐 Web管理界面和Google AI支持

TradingAgents-CN v0.1.2 帶來了重大更新，新增了完整的Web管理界面和Google AI模型支持！

### ✨ 主要新功能

#### 🌐 Streamlit Web管理界面
- 🎯 完整的Web股票分析平台
- 📊 直觀的用戶界面和實時進度顯示
- 🤖 支持多種LLM提供商選擇（阿里百炼/Google AI）
- 📈 可視化的分析結果展示
- 📱 響應式設計，支持移動端訪問

#### 🤖 Google AI模型集成
- 🧠 完整的Google Gemini模型支持
- 🔧 支持gemini-2.0-flash、gemini-1.5-pro等模型
- 🌍 智能混合嵌入服務（Google AI推理 + 阿里百炼嵌入）
- 💾 完美的中文分析能力和穩定的LangChain集成

#### 🔧 多LLM提供商支持
- 🔄 Web界面支持LLM提供商無缝切換
- ⚙️ 自動配置最優嵌入服務
- 🎛️ 統一的配置管理界面

### 🔧 改進優化

- 📊 新增分析配置信息顯示
- 🗂️ 項目結構優化（tests/docs/web目錄規範化）
- 🔑 多種API服務配置支持
- 🧪 完整的測試體系（25+個測試文件）
- 📚 完整的使用文档和配置指南

### 🚀 快速開始

#### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

#### 2. 配置API密鑰
```bash
# 複制環境變量模板
cp .env.example .env

# 編辑.env文件，添加您的API密鑰
# DASHSCOPE_API_KEY=your_dashscope_key  # 阿里百炼（推薦）
# GOOGLE_API_KEY=your_google_key        # Google AI（可選）
```

#### 3. 啟動Web界面
```bash
# 啟動Web管理界面
python -m streamlit run web/app.py

# 或使用快捷腳本
start_web.bat  # Windows
```

#### 4. 使用CLI工具
```bash
# 使用阿里百炼模型
python cli/main.py --stock AAPL --analysts market fundamentals

# 使用Google AI模型
python cli/main.py --llm-provider google --model gemini-2.0-flash --stock TSLA
```

### 📚 文档和支持

- 📖 [完整文档](./docs/)
- 🌐 [Web界面指南](./web/README.md)
- 🤖 [Google AI配置指南](./docs/configuration/google-ai-setup.md)
- 🧪 [測試指南](./tests/README.md)
- 💡 [示例代碼](./examples/)

### 🎯 推薦配置

**最佳性能組合**：
- **LLM提供商**: Google AI
- **推薦模型**: gemini-2.0-flash
- **嵌入服務**: 阿里百炼（自動配置）
- **分析師**: 市場技術 + 基本面分析師

### 🙏 致谢

感谢 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 原始項目的開發者們，為金融AI領域提供了優秀的開源框架。

### 📄 許可證

本項目遵循 Apache 2.0 許可證。

---

**🚀 立即體驗**: `python -m streamlit run web/app.py`
"""
    return release_notes.strip()

def show_release_info():
    """顯示發布信息"""
    logger.info(f"🎉 TradingAgents-CN v0.1.2 已成功發布到GitHub！")
    logger.info(f"=")
    
    logger.info(f"\n📋 發布內容:")
    logger.info(f"  🌐 完整的Web管理界面")
    logger.info(f"  🤖 Google AI模型集成")
    logger.info(f"  🔧 多LLM提供商支持")
    logger.info(f"  🧪 完整的測試體系")
    logger.info(f"  📚 詳細的使用文档")
    
    logger.info(f"\n🔗 GitHub鏈接:")
    logger.info(f"  📦 Release: https://github.com/hsliuping/TradingAgents-CN/releases/tag/cn-v0.1.2")
    logger.info(f"  📝 代碼: https://github.com/hsliuping/TradingAgents-CN")
    
    logger.info(f"\n🚀 快速開始:")
    logger.info(f"  1. git clone https://github.com/hsliuping/TradingAgents-CN.git")
    logger.info(f"  2. cd TradingAgents-CN")
    logger.info(f"  3. pip install -r requirements.txt")
    logger.info(f"  4. python -m streamlit run web/app.py")
    
    logger.info(f"\n💡 主要特性:")
    logger.info(f"  ✅ Web界面股票分析")
    logger.info(f"  ✅ Google AI + 阿里百炼雙模型支持")
    logger.info(f"  ✅ 實時分析進度顯示")
    logger.info(f"  ✅ 多分析師協作決策")
    logger.info(f"  ✅ 完整的中文支持")

def main():
    """主函數"""
    logger.info(f"🚀 創建GitHub Release")
    logger.info(f"=")
    
    # 檢查是否在正確的分支
    success, stdout, stderr = run_command("git branch --show-current")
    if not success or stdout.strip() != "main":
        logger.error(f"❌ 請確保在main分支上，當前分支: {stdout.strip()}")
        return False
    
    # 檢查是否有未推送的提交
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        logger.error(f"❌ Git狀態檢查失败: {stderr}")
        return False
    
    if stdout.strip():
        logger.error(f"❌ 發現未提交的更改，請先提交所有更改")
        return False
    
    logger.info(f"✅ Git狀態檢查通過")
    
    # 檢查標簽是否存在
    success, stdout, stderr = run_command("git tag -l cn-v0.1.2")
    if not success or "cn-v0.1.2" not in stdout:
        logger.error(f"❌ 標簽 cn-v0.1.2 不存在")
        return False
    
    logger.info(f"✅ 版本標簽檢查通過")
    
    # 生成發布說明
    release_notes = create_release_notes()
    
    # 保存發布說明到文件
    with open("RELEASE_NOTES_v0.1.2.md", "w", encoding="utf-8") as f:
        f.write(release_notes)
    
    logger.info(f"✅ 發布說明已生成")
    
    # 顯示GitHub Release創建指南
    logger.info(f"\n📋 GitHub Release創建指南:")
    logger.info(f"=")
    logger.info(f"1. 訪問: https://github.com/hsliuping/TradingAgents-CN/releases/new")
    logger.info(f"2. 選擇標簽: cn-v0.1.2")
    logger.info(f"3. 發布標題: TradingAgents-CN v0.1.2 - Web管理界面和Google AI支持")
    logger.info(f"4. 複制 RELEASE_NOTES_v0.1.2.md 的內容到描述框")
    logger.info(f"5. 勾選 'Set as the latest release'")
    logger.info(f"6. 點擊 'Publish release'")
    
    # 顯示發布信息
    show_release_info()
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info(f"\n🎉 GitHub Release準备完成！")
        logger.info(f"請按照上述指南在GitHub上創建Release")
    else:
        logger.error(f"\n❌ GitHub Release準备失败")
        sys.exit(1)
