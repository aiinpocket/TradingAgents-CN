#!/usr/bin/env python3
"""
TradingAgents-CN v0.1.2 版本發布腳本
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime

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

def check_git_status():
    """檢查Git狀態"""
    logger.debug(f"🔍 檢查Git狀態...")
    
    success, stdout, stderr = run_command("git status --porcelain")
    if not success:
        logger.error(f"❌ Git狀態檢查失败: {stderr}")
        return False
    
    if stdout.strip():
        logger.info(f"📝 發現未提交的更改:")
        print(stdout)
        return True
    else:
        logger.info(f"✅ 工作目錄干净")
        return True

def create_release_tag():
    """創建發布標簽"""
    logger.info(f"🏷️ 創建版本標簽...")
    
    tag_name = "cn-v0.1.2"
    tag_message = "TradingAgents-CN v0.1.2 - Web管理界面和Google AI支持"
    
    # 檢查標簽是否已存在
    success, stdout, stderr = run_command(f"git tag -l {tag_name}")
    if success and tag_name in stdout:
        logger.warning(f"⚠️ 標簽 {tag_name} 已存在")
        return True
    
    # 創建標簽
    success, stdout, stderr = run_command(f'git tag -a {tag_name} -m "{tag_message}"')
    if success:
        logger.info(f"✅ 標簽 {tag_name} 創建成功")
        return True
    else:
        logger.error(f"❌ 標簽創建失败: {stderr}")
        return False

def generate_release_notes():
    """生成發布說明"""
    logger.info(f"📝 生成發布說明...")
    
    release_notes = """
# TradingAgents-CN v0.1.2 發布說明

## 🌐 Web管理界面和Google AI支持

### ✨ 主要新功能

#### 🌐 Streamlit Web管理界面
- 完整的Web股票分析平台
- 直觀的用戶界面和實時進度顯示
- 支持多種分析師組合選擇
- 可視化的分析結果展示
- 響應式設計，支持移動端訪問

#### 🤖 Google AI模型集成
- 完整的Google Gemini模型支持
- 支持gemini-2.0-flash、gemini-1.5-pro等模型
- 智能混合嵌入服務（Google AI + 阿里百炼）
- 完美的中文分析能力
- 穩定的LangChain集成

#### 🔧 多LLM提供商支持
- Web界面支持LLM提供商選擇
- 阿里百炼和Google AI無缝切換
- 自動配置最優嵌入服務
- 統一的配置管理界面

### 🔧 改進優化

- 📊 新增分析配置信息顯示
- 🗂️ 項目結構優化（tests/docs/web目錄規範化）
- 🔑 多種API服務配置支持
- 🧪 完整的測試體系（25+個測試文件）

### 🚀 快速開始

#### 安裝依賴
```bash
pip install -r requirements.txt
```

#### 配置API密鑰
```bash
# 複制環境變量模板
cp .env.example .env

# 編辑.env文件，添加您的API密鑰
# DASHSCOPE_API_KEY=your_dashscope_key
# GOOGLE_API_KEY=your_google_key  # 可選
```

#### 啟動Web界面
```bash
# Windows
start_web.bat

# Linux/Mac
python -m streamlit run web/app.py
```

#### 使用CLI工具
```bash
python cli/main.py --stock AAPL --analysts market fundamentals
```

### 📚 文档和支持

- 📖 [完整文档](./docs/)
- 🧪 [測試指南](./tests/README.md)
- 🌐 [Web界面指南](./web/README.md)
- 💡 [示例代碼](./examples/)

### 🙏 致谢

感谢 [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) 原始項目的開發者們，為金融AI領域提供了優秀的開源框架。

### 📄 許可證

本項目遵循 Apache 2.0 許可證。
"""
    
    # 保存發布說明
    release_file = Path("RELEASE_NOTES_v0.1.2.md")
    with open(release_file, 'w', encoding='utf-8') as f:
        f.write(release_notes.strip())
    
    logger.info(f"✅ 發布說明已保存到: {release_file}")
    return True

def show_release_summary():
    """顯示發布摘要"""
    logger.info(f"\n")
    logger.info(f"🎉 TradingAgents-CN v0.1.2 發布準备完成！")
    logger.info(f"=")
    
    logger.info(f"\n📋 本次發布包含:")
    logger.info(f"  🌐 Streamlit Web管理界面")
    logger.info(f"  🤖 Google AI模型集成")
    logger.info(f"  🔧 多LLM提供商支持")
    logger.info(f"  🧪 完整的測試體系")
    logger.info(f"  🗂️ 項目結構優化")
    
    logger.info(f"\n📁 主要文件更新:")
    logger.info(f"  ✅ VERSION: 0.1.1 → 0.1.2")
    logger.info(f"  ✅ CHANGELOG.md: 新增v0.1.2更新日誌")
    logger.info(f"  ✅ README-CN.md: 新增Web界面和Google AI使用說明")
    logger.info(f"  ✅ web/README.md: 完整的Web界面使用指南")
    logger.info(f"  ✅ docs/configuration/google-ai-setup.md: Google AI配置指南")
    logger.info(f"  ✅ web/: 完整的Web界面，支持多LLM提供商")
    logger.info(f"  ✅ tests/: 25+個測試文件，規範化目錄結構")
    
    logger.info(f"\n🚀 下一步操作:")
    logger.info(f"  1. 檢查所有更改: git status")
    logger.info(f"  2. 提交更改: git add . && git commit -m 'Release v0.1.2'")
    logger.info(f"  3. 推送標簽: git push origin cn-v0.1.2")
    logger.info(f"  4. 創建GitHub Release")
    
    logger.info(f"\n💡 使用方法:")
    logger.info(f"  Web界面: python -m streamlit run web/app.py")
    logger.info(f"  CLI工具: python cli/main.py --help")
    logger.info(f"  測試: python tests/test_web_interface.py")

def main():
    """主函數"""
    logger.info(f"🚀 TradingAgents-CN v0.1.2 版本發布")
    logger.info(f"=")
    
    # 檢查Git狀態
    if not check_git_status():
        return False
    
    # 創建發布標簽
    if not create_release_tag():
        return False
    
    # 生成發布說明
    if not generate_release_notes():
        return False
    
    # 顯示發布摘要
    show_release_summary()
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info(f"\n🎉 版本發布準备完成！")
    else:
        logger.error(f"\n❌ 版本發布準备失败")
        sys.exit(1)
