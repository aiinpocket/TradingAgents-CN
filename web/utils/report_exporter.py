#!/usr/bin/env python3
"""
報告導出工具
支持將分析結果導出為多種格式
"""

import streamlit as st
import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import base64

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('web')

# 導入MongoDB報告管理器
try:
    from web.utils.mongodb_report_manager import mongodb_report_manager
    MONGODB_REPORT_AVAILABLE = True
except ImportError:
    MONGODB_REPORT_AVAILABLE = False
    mongodb_report_manager = None

# 配置日誌 - 確保輸出到stdout以便Docker logs可见
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 輸出到stdout
    ]
)
logger = logging.getLogger(__name__)

# 導入Docker適配器
try:
    from .docker_pdf_adapter import (
        is_docker_environment,
        get_docker_pdf_extra_args,
        setup_xvfb_display,
        get_docker_status_info
    )
    DOCKER_ADAPTER_AVAILABLE = True
except ImportError:
    DOCKER_ADAPTER_AVAILABLE = False
    logger.warning(f"⚠️ Docker適配器不可用")

# 導入導出相關庫
try:
    import markdown
    import re
    import tempfile
    import os
    from pathlib import Path

    # 導入pypandoc（用於markdown轉docx和pdf）
    import pypandoc

    # 檢查pandoc是否可用，如果不可用則嘗試下載
    try:
        pypandoc.get_pandoc_version()
        PANDOC_AVAILABLE = True
    except OSError:
        logger.warning(f"⚠️ 未找到pandoc，正在嘗試自動下載...")
        try:
            pypandoc.download_pandoc()
            PANDOC_AVAILABLE = True
            logger.info(f"✅ pandoc下載成功！")
        except Exception as download_error:
            logger.error(f"❌ pandoc下載失敗: {download_error}")
            PANDOC_AVAILABLE = False

    EXPORT_AVAILABLE = True

except ImportError as e:
    EXPORT_AVAILABLE = False
    PANDOC_AVAILABLE = False
    logger.info(f"導出功能依賴包缺失: {e}")
    logger.info(f"請安裝: pip install pypandoc markdown")


class ReportExporter:
    """報告導出器"""

    def __init__(self):
        self.export_available = EXPORT_AVAILABLE
        self.pandoc_available = PANDOC_AVAILABLE
        self.is_docker = DOCKER_ADAPTER_AVAILABLE and is_docker_environment()

        # 記錄初始化狀態
        logger.info(f"📋 ReportExporter初始化:")
        logger.info(f"  - export_available: {self.export_available}")
        logger.info(f"  - pandoc_available: {self.pandoc_available}")
        logger.info(f"  - is_docker: {self.is_docker}")
        logger.info(f"  - docker_adapter_available: {DOCKER_ADAPTER_AVAILABLE}")

        # Docker環境初始化
        if self.is_docker:
            logger.info("🐳 檢測到Docker環境，初始化PDF支持...")
            logger.info(f"🐳 檢測到Docker環境，初始化PDF支持...")
            setup_xvfb_display()
    
    def _clean_text_for_markdown(self, text: str) -> str:
        """清理文本中可能導致YAML解析問題的字符"""
        if not text:
            return "N/A"

        # 轉換為字符串並清理特殊字符
        text = str(text)

        # 移除可能導致YAML解析問題的字符
        text = text.replace('&', '&amp;')  # HTML轉義
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#39;')

        # 移除可能的YAML特殊字符
        text = text.replace('---', '—')  # 替換三個連字符
        text = text.replace('...', '…')  # 替換三個點

        return text

    def _clean_markdown_for_pandoc(self, content: str) -> str:
        """清理Markdown內容避免pandoc YAML解析問題"""
        if not content:
            return ""

        # 確保內容不以可能被誤認為YAML的字符開頭
        content = content.strip()

        # 如果第一行看起來像YAML分隔符，添加空行
        lines = content.split('\n')
        if lines and (lines[0].startswith('---') or lines[0].startswith('...')):
            content = '\n' + content

        # 替換可能導致YAML解析問題的字符序列，但保護表格分隔符
        # 先保護表格分隔符
        content = content.replace('|------|------|', '|TABLESEP|TABLESEP|')
        content = content.replace('|------|', '|TABLESEP|')

        # 然後替換其他的三連字符
        content = content.replace('---', '—')  # 替換三個連字符
        content = content.replace('...', '…')  # 替換三個點

        # 恢複表格分隔符
        content = content.replace('|TABLESEP|TABLESEP|', '|------|------|')
        content = content.replace('|TABLESEP|', '|------|')

        # 清理特殊引號
        content = content.replace('"', '"')  # 左雙引號
        content = content.replace('"', '"')  # 右雙引號
        content = content.replace(''', "'")  # 左單引號
        content = content.replace(''', "'")  # 右單引號

        # 確保內容以標準Markdown標題開始
        if not content.startswith('#'):
            content = '# 分析報告\n\n' + content

        return content

    def generate_markdown_report(self, results: Dict[str, Any]) -> str:
        """生成Markdown格式的報告"""

        stock_symbol = self._clean_text_for_markdown(results.get('stock_symbol', 'N/A'))
        decision = results.get('decision', {})
        state = results.get('state', {})
        is_demo = results.get('is_demo', False)
        
        # 生成時間戳
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 清理關鍵數據
        action = self._clean_text_for_markdown(decision.get('action', 'N/A')).upper()
        target_price = self._clean_text_for_markdown(decision.get('target_price', 'N/A'))
        reasoning = self._clean_text_for_markdown(decision.get('reasoning', '暫無分析推理'))

        # 構建Markdown內容
        md_content = f"""# {stock_symbol} 股票分析報告

**生成時間**: {timestamp}
**分析狀態**: {'演示模式' if is_demo else '正式分析'}

## 🎯 投資決策摘要

| 指標 | 數值 |
|------|------|
| **投資建議** | {action} |
| **置信度** | {decision.get('confidence', 0):.1%} |
| **風險評分** | {decision.get('risk_score', 0):.1%} |
| **目標價位** | {target_price} |

### 分析推理
{reasoning}

---

## 📋 分析配置信息

- **LLM提供商**: {results.get('llm_provider', 'N/A')}
- **AI模型**: {results.get('llm_model', 'N/A')}
- **分析師數量**: {len(results.get('analysts', []))}個
- **研究深度**: {results.get('research_depth', 'N/A')}

### 參與分析師
{', '.join(results.get('analysts', []))}

---

## 📊 詳細分析報告

"""
        
        # 添加各個分析模塊的內容 - 與CLI端保持一致的完整結構
        analysis_modules = [
            ('market_report', '📈 市場技術分析', '技術指標、價格趨勢、支撐阻力位分析'),
            ('fundamentals_report', '💰 基本面分析', '財務數據、估值水平、盈利能力分析'),
            ('sentiment_report', '💭 市場情緒分析', '投資者情緒、社交媒體情緒指標'),
            ('news_report', '📰 新聞事件分析', '相關新聞事件、市場動態影響分析'),
            ('risk_assessment', '⚠️ 風險評估', '風險因素識別、風險等級評估'),
            ('investment_plan', '📋 投資建議', '具體投資策略、倉位管理建議')
        ]
        
        for key, title, description in analysis_modules:
            md_content += f"\n### {title}\n\n"
            md_content += f"*{description}*\n\n"
            
            if key in state and state[key]:
                content = state[key]
                if isinstance(content, str):
                    md_content += f"{content}\n\n"
                elif isinstance(content, dict):
                    for sub_key, sub_value in content.items():
                        md_content += f"#### {sub_key.replace('_', ' ').title()}\n\n"
                        md_content += f"{sub_value}\n\n"
                else:
                    md_content += f"{content}\n\n"
            else:
                md_content += "暫無數據\n\n"

        # 添加團隊決策報告部分 - 與CLI端保持一致
        md_content = self._add_team_decision_reports(md_content, state)

        # 添加風險提示
        md_content += f"""
---

## ⚠️ 重要風險提示

**投資風險提示**:
- **僅供參考**: 本分析結果僅供參考，不構成投資建議
- **投資風險**: 股票投資有風險，可能導致本金損失
- **理性決策**: 請結合多方信息進行理性投資決策
- **專業咨詢**: 重大投資決策建議咨詢專業財務顧問
- **自擔風險**: 投資決策及其後果由投資者自行承擔

---
*報告生成時間: {timestamp}*
"""
        
        return md_content

    def _add_team_decision_reports(self, md_content: str, state: Dict[str, Any]) -> str:
        """添加團隊決策報告部分，與CLI端保持一致"""

        # II. 研究團隊決策報告
        if 'investment_debate_state' in state and state['investment_debate_state']:
            md_content += "\n---\n\n## 🔬 研究團隊決策\n\n"
            md_content += "*多頭/空頭研究員辯論分析，研究經理綜合決策*\n\n"

            debate_state = state['investment_debate_state']

            # 多頭研究員分析
            if debate_state.get('bull_history'):
                md_content += "### 📈 多頭研究員分析\n\n"
                md_content += f"{self._clean_text_for_markdown(debate_state['bull_history'])}\n\n"

            # 空頭研究員分析
            if debate_state.get('bear_history'):
                md_content += "### 📉 空頭研究員分析\n\n"
                md_content += f"{self._clean_text_for_markdown(debate_state['bear_history'])}\n\n"

            # 研究經理決策
            if debate_state.get('judge_decision'):
                md_content += "### 🎯 研究經理綜合決策\n\n"
                md_content += f"{self._clean_text_for_markdown(debate_state['judge_decision'])}\n\n"

        # III. 交易團隊計劃
        if 'trader_investment_plan' in state and state['trader_investment_plan']:
            md_content += "\n---\n\n## 💼 交易團隊計劃\n\n"
            md_content += "*專業交易員制定的具體交易執行計劃*\n\n"
            md_content += f"{self._clean_text_for_markdown(state['trader_investment_plan'])}\n\n"

        # IV. 風險管理團隊決策
        if 'risk_debate_state' in state and state['risk_debate_state']:
            md_content += "\n---\n\n## ⚖️ 風險管理團隊決策\n\n"
            md_content += "*激進/保守/中性分析師風險評估，投資組合經理最終決策*\n\n"

            risk_state = state['risk_debate_state']

            # 激進分析師
            if risk_state.get('risky_history'):
                md_content += "### 🚀 激進分析師評估\n\n"
                md_content += f"{self._clean_text_for_markdown(risk_state['risky_history'])}\n\n"

            # 保守分析師
            if risk_state.get('safe_history'):
                md_content += "### 🛡️ 保守分析師評估\n\n"
                md_content += f"{self._clean_text_for_markdown(risk_state['safe_history'])}\n\n"

            # 中性分析師
            if risk_state.get('neutral_history'):
                md_content += "### ⚖️ 中性分析師評估\n\n"
                md_content += f"{self._clean_text_for_markdown(risk_state['neutral_history'])}\n\n"

            # 投資組合經理決策
            if risk_state.get('judge_decision'):
                md_content += "### 🎯 投資組合經理最終決策\n\n"
                md_content += f"{self._clean_text_for_markdown(risk_state['judge_decision'])}\n\n"

        # V. 最終交易決策
        if 'final_trade_decision' in state and state['final_trade_decision']:
            md_content += "\n---\n\n## 🎯 最終交易決策\n\n"
            md_content += "*綜合所有團隊分析後的最終投資決策*\n\n"
            md_content += f"{self._clean_text_for_markdown(state['final_trade_decision'])}\n\n"

        return md_content

    def _format_team_decision_content(self, content: Dict[str, Any], module_key: str) -> str:
        """格式化團隊決策內容"""
        formatted_content = ""

        if module_key == 'investment_debate_state':
            # 研究團隊決策格式化
            if content.get('bull_history'):
                formatted_content += "## 📈 多頭研究員分析\n\n"
                formatted_content += f"{content['bull_history']}\n\n"

            if content.get('bear_history'):
                formatted_content += "## 📉 空頭研究員分析\n\n"
                formatted_content += f"{content['bear_history']}\n\n"

            if content.get('judge_decision'):
                formatted_content += "## 🎯 研究經理綜合決策\n\n"
                formatted_content += f"{content['judge_decision']}\n\n"

        elif module_key == 'risk_debate_state':
            # 風險管理團隊決策格式化
            if content.get('risky_history'):
                formatted_content += "## 🚀 激進分析師評估\n\n"
                formatted_content += f"{content['risky_history']}\n\n"

            if content.get('safe_history'):
                formatted_content += "## 🛡️ 保守分析師評估\n\n"
                formatted_content += f"{content['safe_history']}\n\n"

            if content.get('neutral_history'):
                formatted_content += "## ⚖️ 中性分析師評估\n\n"
                formatted_content += f"{content['neutral_history']}\n\n"

            if content.get('judge_decision'):
                formatted_content += "## 🎯 投資組合經理最終決策\n\n"
                formatted_content += f"{content['judge_decision']}\n\n"

        return formatted_content

    def generate_docx_report(self, results: Dict[str, Any]) -> bytes:
        """生成Word文檔格式的報告"""

        logger.info("📄 開始生成Word文檔...")

        if not self.pandoc_available:
            logger.error("❌ Pandoc不可用")
            raise Exception("Pandoc不可用，無法生成Word文檔。請安裝pandoc或使用Markdown格式導出。")

        # 首先生成markdown內容
        logger.info("📝 生成Markdown內容...")
        md_content = self.generate_markdown_report(results)
        logger.info(f"✅ Markdown內容生成完成，長度: {len(md_content)} 字符")

        try:
            logger.info("📁 創建臨時文件用於docx輸出...")
            # 創建臨時文件用於docx輸出
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_file:
                output_file = tmp_file.name
            logger.info(f"📁 臨時文件路徑: {output_file}")

            # 使用強制禁用YAML的參數
            extra_args = ['--from=markdown-yaml_metadata_block']  # 禁用YAML解析
            logger.info(f"🔧 pypandoc參數: {extra_args} (禁用YAML解析)")

            logger.info("🔄 使用pypandoc將markdown轉換為docx...")

            # 調試：保存實際的Markdown內容
            debug_file = '/app/debug_markdown.md'
            try:
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                logger.info(f"🔍 實際Markdown內容已保存到: {debug_file}")
                logger.info(f"📊 內容長度: {len(md_content)} 字符")

                # 顯示前几行內容
                lines = md_content.split('\n')[:5]
                logger.info("🔍 前5行內容:")
                for i, line in enumerate(lines, 1):
                    logger.info(f"  {i}: {repr(line)}")
            except Exception as e:
                logger.error(f"保存調試文件失敗: {e}")

            # 清理內容避免YAML解析問題
            cleaned_content = self._clean_markdown_for_pandoc(md_content)
            logger.info(f"🧹 內容清理完成，清理後長度: {len(cleaned_content)} 字符")

            # 使用測試成功的參數進行轉換
            pypandoc.convert_text(
                cleaned_content,
                'docx',
                format='markdown',  # 基礎markdown格式
                outputfile=output_file,
                extra_args=extra_args
            )
            logger.info("✅ pypandoc轉換完成")

            logger.info("📖 讀取生成的docx文件...")
            # 讀取生成的docx文件
            with open(output_file, 'rb') as f:
                docx_content = f.read()
            logger.info(f"✅ 文件讀取完成，大小: {len(docx_content)} 字節")

            logger.info("🗑️ 清理臨時文件...")
            # 清理臨時文件
            os.unlink(output_file)
            logger.info("✅ 臨時文件清理完成")

            return docx_content
        except Exception as e:
            logger.error(f"❌ Word文檔生成失敗: {e}", exc_info=True)
            raise Exception(f"生成Word文檔失敗: {e}")
    
    
    def generate_pdf_report(self, results: Dict[str, Any]) -> bytes:
        """生成PDF格式的報告"""

        logger.info("📊 開始生成PDF文檔...")

        if not self.pandoc_available:
            logger.error("❌ Pandoc不可用")
            raise Exception("Pandoc不可用，無法生成PDF文檔。請安裝pandoc或使用Markdown格式導出。")

        # 首先生成markdown內容
        logger.info("📝 生成Markdown內容...")
        md_content = self.generate_markdown_report(results)
        logger.info(f"✅ Markdown內容生成完成，長度: {len(md_content)} 字符")

        # 簡化的PDF引擎列表，優先使用最可能成功的
        pdf_engines = [
            ('wkhtmltopdf', 'HTML轉PDF引擎，推薦安裝'),
            ('weasyprint', '現代HTML轉PDF引擎'),
            (None, '使用pandoc默認引擎')  # 不指定引擎，讓pandoc自己選擇
        ]

        last_error = None

        for engine_info in pdf_engines:
            engine, description = engine_info
            try:
                # 創建臨時文件用於PDF輸出
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    output_file = tmp_file.name

                # 使用禁用YAML解析的參數（與Word導出一致）
                extra_args = ['--from=markdown-yaml_metadata_block']

                # 如果指定了引擎，添加引擎參數
                if engine:
                    extra_args.append(f'--pdf-engine={engine}')
                    logger.info(f"🔧 使用PDF引擎: {engine}")
                else:
                    logger.info(f"🔧 使用默認PDF引擎")

                logger.info(f"🔧 PDF參數: {extra_args}")

                # 清理內容避免YAML解析問題（與Word導出一致）
                cleaned_content = self._clean_markdown_for_pandoc(md_content)

                # 使用pypandoc將markdown轉換為PDF - 禁用YAML解析
                pypandoc.convert_text(
                    cleaned_content,
                    'pdf',
                    format='markdown',  # 基礎markdown格式
                    outputfile=output_file,
                    extra_args=extra_args
                )

                # 檢查文件是否生成且有內容
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    # 讀取生成的PDF文件
                    with open(output_file, 'rb') as f:
                        pdf_content = f.read()

                    # 清理臨時文件
                    os.unlink(output_file)

                    logger.info(f"✅ PDF生成成功，使用引擎: {engine or '默認'}")
                    return pdf_content
                else:
                    raise Exception("PDF文件生成失敗或為空")

            except Exception as e:
                last_error = str(e)
                logger.error(f"PDF引擎 {engine or '默認'} 失敗: {e}")

                # 清理可能存在的臨時文件
                try:
                    if 'output_file' in locals() and os.path.exists(output_file):
                        os.unlink(output_file)
                except:
                    pass

                continue

        # 如果所有引擎都失敗，提供詳細的錯誤信息和解決方案
        error_msg = f"""PDF生成失敗，最後錯誤: {last_error}

可能的解決方案:
1. 安裝wkhtmltopdf (推薦):
   Windows: choco install wkhtmltopdf
   macOS: brew install wkhtmltopdf
   Linux: sudo apt-get install wkhtmltopdf

2. 安裝LaTeX:
   Windows: choco install miktex
   macOS: brew install mactex
   Linux: sudo apt-get install texlive-full

3. 使用Markdown或Word格式導出作為替代方案
"""
        raise Exception(error_msg)
    
    def export_report(self, results: Dict[str, Any], format_type: str) -> Optional[bytes]:
        """導出報告為指定格式"""

        logger.info(f"🚀 開始導出報告: format={format_type}")
        logger.info(f"📊 導出狀態檢查:")
        logger.info(f"  - export_available: {self.export_available}")
        logger.info(f"  - pandoc_available: {self.pandoc_available}")
        logger.info(f"  - is_docker: {self.is_docker}")

        if not self.export_available:
            logger.error("❌ 導出功能不可用")
            st.error("❌ 導出功能不可用，請安裝必要的依賴包")
            return None

        try:
            logger.info(f"🔄 開始生成{format_type}格式報告...")

            if format_type == 'markdown':
                logger.info("📝 生成Markdown報告...")
                content = self.generate_markdown_report(results)
                logger.info(f"✅ Markdown報告生成成功，長度: {len(content)} 字符")
                return content.encode('utf-8')

            elif format_type == 'docx':
                logger.info("📄 生成Word文檔...")
                if not self.pandoc_available:
                    logger.error("❌ pandoc不可用，無法生成Word文檔")
                    st.error("❌ pandoc不可用，無法生成Word文檔")
                    return None
                content = self.generate_docx_report(results)
                logger.info(f"✅ Word文檔生成成功，大小: {len(content)} 字節")
                return content

            elif format_type == 'pdf':
                logger.info("📊 生成PDF文檔...")
                if not self.pandoc_available:
                    logger.error("❌ pandoc不可用，無法生成PDF文檔")
                    st.error("❌ pandoc不可用，無法生成PDF文檔")
                    return None
                content = self.generate_pdf_report(results)
                logger.info(f"✅ PDF文檔生成成功，大小: {len(content)} 字節")
                return content

            else:
                logger.error(f"❌ 不支持的導出格式: {format_type}")
                st.error(f"❌ 不支持的導出格式: {format_type}")
                return None

        except Exception as e:
            logger.error(f"❌ 導出失敗: {str(e)}", exc_info=True)
            st.error(f"❌ 導出失敗: {str(e)}")
            return None


# 創建全局導出器實例
report_exporter = ReportExporter()


def _format_team_decision_content(content: Dict[str, Any], module_key: str) -> str:
    """格式化團隊決策內容（獨立函數版本）"""
    formatted_content = ""

    if module_key == 'investment_debate_state':
        # 研究團隊決策格式化
        if content.get('bull_history'):
            formatted_content += "## 📈 多頭研究員分析\n\n"
            formatted_content += f"{content['bull_history']}\n\n"

        if content.get('bear_history'):
            formatted_content += "## 📉 空頭研究員分析\n\n"
            formatted_content += f"{content['bear_history']}\n\n"

        if content.get('judge_decision'):
            formatted_content += "## 🎯 研究經理綜合決策\n\n"
            formatted_content += f"{content['judge_decision']}\n\n"

    elif module_key == 'risk_debate_state':
        # 風險管理團隊決策格式化
        if content.get('risky_history'):
            formatted_content += "## 🚀 激進分析師評估\n\n"
            formatted_content += f"{content['risky_history']}\n\n"

        if content.get('safe_history'):
            formatted_content += "## 🛡️ 保守分析師評估\n\n"
            formatted_content += f"{content['safe_history']}\n\n"

        if content.get('neutral_history'):
            formatted_content += "## ⚖️ 中性分析師評估\n\n"
            formatted_content += f"{content['neutral_history']}\n\n"

        if content.get('judge_decision'):
            formatted_content += "## 🎯 投資組合經理最終決策\n\n"
            formatted_content += f"{content['judge_decision']}\n\n"

    return formatted_content


def save_modular_reports_to_results_dir(results: Dict[str, Any], stock_symbol: str) -> Dict[str, str]:
    """保存分模塊報告到results目錄（CLI版本格式）"""
    try:
        import os
        from pathlib import Path

        # 獲取項目根目錄
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent

        # 獲取results目錄配置
        results_dir_env = os.getenv("TRADINGAGENTS_RESULTS_DIR")
        if results_dir_env:
            if not os.path.isabs(results_dir_env):
                results_dir = project_root / results_dir_env
            else:
                results_dir = Path(results_dir_env)
        else:
            results_dir = project_root / "results"

        # 創建股票專用目錄
        analysis_date = datetime.now().strftime('%Y-%m-%d')
        stock_dir = results_dir / stock_symbol / analysis_date
        reports_dir = stock_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        # 創建message_tool.log文件
        log_file = stock_dir / "message_tool.log"
        log_file.touch(exist_ok=True)

        state = results.get('state', {})
        saved_files = {}

        # 定義報告模塊映射（與CLI版本保持一致）
        report_modules = {
            'market_report': {
                'filename': 'market_report.md',
                'title': f'{stock_symbol} 股票技術分析報告',
                'state_key': 'market_report'
            },
            'sentiment_report': {
                'filename': 'sentiment_report.md',
                'title': f'{stock_symbol} 市場情緒分析報告',
                'state_key': 'sentiment_report'
            },
            'news_report': {
                'filename': 'news_report.md',
                'title': f'{stock_symbol} 新聞事件分析報告',
                'state_key': 'news_report'
            },
            'fundamentals_report': {
                'filename': 'fundamentals_report.md',
                'title': f'{stock_symbol} 基本面分析報告',
                'state_key': 'fundamentals_report'
            },
            'investment_plan': {
                'filename': 'investment_plan.md',
                'title': f'{stock_symbol} 投資決策報告',
                'state_key': 'investment_plan'
            },
            'trader_investment_plan': {
                'filename': 'trader_investment_plan.md',
                'title': f'{stock_symbol} 交易計劃報告',
                'state_key': 'trader_investment_plan'
            },
            'final_trade_decision': {
                'filename': 'final_trade_decision.md',
                'title': f'{stock_symbol} 最終投資決策',
                'state_key': 'final_trade_decision'
            },
            # 添加團隊決策報告模塊
            'investment_debate_state': {
                'filename': 'research_team_decision.md',
                'title': f'{stock_symbol} 研究團隊決策報告',
                'state_key': 'investment_debate_state'
            },
            'risk_debate_state': {
                'filename': 'risk_management_decision.md',
                'title': f'{stock_symbol} 風險管理團隊決策報告',
                'state_key': 'risk_debate_state'
            }
        }

        # 生成各個模塊的報告文件
        for module_key, module_info in report_modules.items():
            content = state.get(module_info['state_key'])

            if content:
                # 生成模塊報告內容
                if isinstance(content, str):
                    # 檢查內容是否已經包含標題，避免重複添加
                    if content.strip().startswith('#'):
                        report_content = content
                    else:
                        report_content = f"# {module_info['title']}\n\n{content}"
                elif isinstance(content, dict):
                    report_content = f"# {module_info['title']}\n\n"
                    # 特殊處理團隊決策報告的字典結構
                    if module_key in ['investment_debate_state', 'risk_debate_state']:
                        report_content += _format_team_decision_content(content, module_key)
                    else:
                        for sub_key, sub_value in content.items():
                            report_content += f"## {sub_key.replace('_', ' ').title()}\n\n{sub_value}\n\n"
                else:
                    report_content = f"# {module_info['title']}\n\n{str(content)}"

                # 保存文件
                file_path = reports_dir / module_info['filename']
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)

                saved_files[module_key] = str(file_path)
                logger.info(f"✅ 保存模塊報告: {file_path}")

        # 如果有決策信息，也保存最終決策報告
        decision = results.get('decision', {})
        if decision:
            decision_content = f"# {stock_symbol} 最終投資決策\n\n"

            if isinstance(decision, dict):
                decision_content += f"## 投資建議\n\n"
                decision_content += f"**行動**: {decision.get('action', 'N/A')}\n\n"
                decision_content += f"**置信度**: {decision.get('confidence', 0):.1%}\n\n"
                decision_content += f"**風險評分**: {decision.get('risk_score', 0):.1%}\n\n"
                decision_content += f"**目標價位**: {decision.get('target_price', 'N/A')}\n\n"
                decision_content += f"## 分析推理\n\n{decision.get('reasoning', '暫無分析推理')}\n\n"
            else:
                decision_content += f"{str(decision)}\n\n"

            decision_file = reports_dir / "final_trade_decision.md"
            with open(decision_file, 'w', encoding='utf-8') as f:
                f.write(decision_content)

            saved_files['final_trade_decision'] = str(decision_file)
            logger.info(f"✅ 保存最終決策: {decision_file}")

        # 保存分析元數據文件，包含研究深度等信息
        metadata = {
            'stock_symbol': stock_symbol,
            'analysis_date': analysis_date,
            'timestamp': datetime.now().isoformat(),
            'research_depth': results.get('research_depth', 1),
            'analysts': results.get('analysts', []),
            'status': 'completed',
            'reports_count': len(saved_files),
            'report_types': list(saved_files.keys())
        }

        metadata_file = reports_dir.parent / "analysis_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        logger.info(f"✅ 保存分析元數據: {metadata_file}")
        logger.info(f"✅ 分模塊報告保存完成，共保存 {len(saved_files)} 個文件")
        logger.info(f"📁 保存目錄: {os.path.normpath(str(reports_dir))}")

        # 同時保存到MongoDB
        logger.info(f"🔍 [MongoDB調試] 開始MongoDB保存流程")
        logger.info(f"🔍 [MongoDB調試] MONGODB_REPORT_AVAILABLE: {MONGODB_REPORT_AVAILABLE}")
        logger.info(f"🔍 [MongoDB調試] mongodb_report_manager存在: {mongodb_report_manager is not None}")

        if MONGODB_REPORT_AVAILABLE and mongodb_report_manager:
            logger.info(f"🔍 [MongoDB調試] MongoDB管理器連接狀態: {mongodb_report_manager.connected}")
            try:
                # 收集所有報告內容
                reports_content = {}

                logger.info(f"🔍 [MongoDB調試] 開始讀取 {len(saved_files)} 個報告文件")
                # 讀取已保存的文件內容
                for module_key, file_path in saved_files.items():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            reports_content[module_key] = content
                            logger.info(f"🔍 [MongoDB調試] 成功讀取 {module_key}: {len(content)} 字符")
                    except Exception as e:
                        logger.warning(f"⚠️ 讀取報告文件失敗 {file_path}: {e}")

                # 保存到MongoDB
                if reports_content:
                    logger.info(f"🔍 [MongoDB調試] 準備保存到MongoDB，報告數量: {len(reports_content)}")
                    logger.info(f"🔍 [MongoDB調試] 報告類型: {list(reports_content.keys())}")

                    success = mongodb_report_manager.save_analysis_report(
                        stock_symbol=stock_symbol,
                        analysis_results=results,
                        reports=reports_content
                    )

                    if success:
                        logger.info(f"✅ 分析報告已同時保存到MongoDB")
                    else:
                        logger.warning(f"⚠️ MongoDB保存失敗，但文件保存成功")
                else:
                    logger.warning(f"⚠️ 沒有報告內容可保存到MongoDB")

            except Exception as e:
                logger.error(f"❌ MongoDB保存過程出錯: {e}")
                import traceback
                logger.error(f"❌ MongoDB保存詳細錯誤: {traceback.format_exc()}")
                # 不影響文件保存的成功返回
        else:
            logger.warning(f"⚠️ MongoDB保存跳過 - AVAILABLE: {MONGODB_REPORT_AVAILABLE}, Manager: {mongodb_report_manager is not None}")

        return saved_files

    except Exception as e:
        logger.error(f"❌ 保存分模塊報告失敗: {e}")
        import traceback
        logger.error(f"❌ 詳細錯誤: {traceback.format_exc()}")
        return {}


def save_report_to_results_dir(content: bytes, filename: str, stock_symbol: str) -> str:
    """保存報告到results目錄"""
    try:
        import os
        from pathlib import Path

        # 獲取項目根目錄（Web應用在web/子目錄中運行）
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent  # web/utils/report_exporter.py -> 項目根目錄

        # 獲取results目錄配置
        results_dir_env = os.getenv("TRADINGAGENTS_RESULTS_DIR")
        if results_dir_env:
            # 如果環境變量是相對路徑，相對於項目根目錄解析
            if not os.path.isabs(results_dir_env):
                results_dir = project_root / results_dir_env
            else:
                results_dir = Path(results_dir_env)
        else:
            # 默認使用項目根目錄下的results
            results_dir = project_root / "results"

        # 創建股票專用目錄
        analysis_date = datetime.now().strftime('%Y-%m-%d')
        stock_dir = results_dir / stock_symbol / analysis_date / "reports"
        stock_dir.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path = stock_dir / filename
        with open(file_path, 'wb') as f:
            f.write(content)

        logger.info(f"✅ 報告已保存到: {file_path}")
        logger.info(f"📁 項目根目錄: {project_root}")
        logger.info(f"📁 Results目錄: {results_dir}")
        logger.info(f"📁 環境變量TRADINGAGENTS_RESULTS_DIR: {results_dir_env}")

        return str(file_path)

    except Exception as e:
        logger.error(f"❌ 保存報告到results目錄失敗: {e}")
        import traceback
        logger.error(f"❌ 詳細錯誤: {traceback.format_exc()}")
        return ""


def render_export_buttons(results: Dict[str, Any]):
    """渲染導出按鈕"""

    if not results:
        return

    st.markdown("---")
    st.subheader("📤 導出報告")

    # 檢查導出功能是否可用
    if not report_exporter.export_available:
        st.warning("⚠️ 導出功能需要安裝額外依賴包")
        st.code("pip install pypandoc markdown")
        return

    # 檢查pandoc是否可用
    if not report_exporter.pandoc_available:
        st.warning("⚠️ Word和PDF導出需要pandoc工具")
        st.info("💡 您仍可以使用Markdown格式導出")

    # 顯示Docker環境狀態
    if report_exporter.is_docker:
        if DOCKER_ADAPTER_AVAILABLE:
            docker_status = get_docker_status_info()
            if docker_status['dependencies_ok'] and docker_status['pdf_test_ok']:
                st.success("🐳 Docker環境PDF支持已啟用")
            else:
                st.warning(f"🐳 Docker環境PDF支持異常: {docker_status['dependency_message']}")
        else:
            st.warning("🐳 Docker環境檢測到，但適配器不可用")

        with st.expander("📖 如何安裝pandoc"):
            st.markdown("""
            **Windows用戶:**
            ```bash
            # 使用Chocolatey (推薦)
            choco install pandoc

            # 或下載安裝包
            # https://github.com/jgm/pandoc/releases
            ```

            **或者使用Python自動下載:**
            ```python
            import pypandoc

            pypandoc.download_pandoc()
            ```
            """)

        # 在Docker環境下，即使pandoc有問題也顯示所有按鈕，讓用戶嘗試
        pass
    
    # 生成文件名
    stock_symbol = results.get('stock_symbol', 'analysis')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 導出 Markdown", help="導出為Markdown格式"):
            logger.info(f"🖱️ [EXPORT] 用戶點擊Markdown導出按鈕 - 股票: {stock_symbol}")
            logger.info(f"🖱️ 用戶點擊Markdown導出按鈕 - 股票: {stock_symbol}")
            # 1. 保存分模塊報告（CLI格式）
            logger.info("📁 開始保存分模塊報告（CLI格式）...")
            modular_files = save_modular_reports_to_results_dir(results, stock_symbol)

            # 2. 生成彙總報告（下載用）
            content = report_exporter.export_report(results, 'markdown')
            if content:
                filename = f"{stock_symbol}_analysis_{timestamp}.md"
                logger.info(f"✅ [EXPORT] Markdown導出成功，文件名: {filename}")
                logger.info(f"✅ Markdown導出成功，文件名: {filename}")

                # 3. 保存彙總報告到results目錄
                saved_path = save_report_to_results_dir(content, filename, stock_symbol)

                # 4. 顯示保存結果
                if modular_files and saved_path:
                    st.success(f"✅ 已保存 {len(modular_files)} 個分模塊報告 + 1個彙總報告")
                    with st.expander("📁 查看保存的文件"):
                        st.write("**分模塊報告:**")
                        for module, path in modular_files.items():
                            st.write(f"- {module}: `{path}`")
                        st.write("**彙總報告:**")
                        st.write(f"- 彙總報告: `{saved_path}`")
                elif saved_path:
                    st.success(f"✅ 彙總報告已保存到: {saved_path}")

                st.download_button(
                    label="📥 下載 Markdown",
                    data=content,
                    file_name=filename,
                    mime="text/markdown"
                )
            else:
                logger.error(f"❌ [EXPORT] Markdown導出失敗，content為空")
                logger.error("❌ Markdown導出失敗，content為空")
    
    with col2:
        if st.button("📝 導出 Word", help="導出為Word文檔格式"):
            logger.info(f"🖱️ [EXPORT] 用戶點擊Word導出按鈕 - 股票: {stock_symbol}")
            logger.info(f"🖱️ 用戶點擊Word導出按鈕 - 股票: {stock_symbol}")
            with st.spinner("正在生成Word文檔，請稍候..."):
                try:
                    logger.info(f"🔄 [EXPORT] 開始Word導出流程...")
                    logger.info("🔄 開始Word導出流程...")

                    # 1. 保存分模塊報告（CLI格式）
                    logger.info("📁 開始保存分模塊報告（CLI格式）...")
                    modular_files = save_modular_reports_to_results_dir(results, stock_symbol)

                    # 2. 生成Word彙總報告
                    content = report_exporter.export_report(results, 'docx')
                    if content:
                        filename = f"{stock_symbol}_analysis_{timestamp}.docx"
                        logger.info(f"✅ [EXPORT] Word導出成功，文件名: {filename}, 大小: {len(content)} 字節")
                        logger.info(f"✅ Word導出成功，文件名: {filename}, 大小: {len(content)} 字節")

                        # 3. 保存Word彙總報告到results目錄
                        saved_path = save_report_to_results_dir(content, filename, stock_symbol)

                        # 4. 顯示保存結果
                        if modular_files and saved_path:
                            st.success(f"✅ 已保存 {len(modular_files)} 個分模塊報告 + 1個Word彙總報告")
                            with st.expander("📁 查看保存的文件"):
                                st.write("**分模塊報告:**")
                                for module, path in modular_files.items():
                                    st.write(f"- {module}: `{path}`")
                                st.write("**Word彙總報告:**")
                                st.write(f"- Word報告: `{saved_path}`")
                        elif saved_path:
                            st.success(f"✅ Word文檔已保存到: {saved_path}")
                        else:
                            st.success("✅ Word文檔生成成功！")

                        st.download_button(
                            label="📥 下載 Word",
                            data=content,
                            file_name=filename,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    else:
                        logger.error(f"❌ [EXPORT] Word導出失敗，content為空")
                        logger.error("❌ Word導出失敗，content為空")
                        st.error("❌ Word文檔生成失敗")
                except Exception as e:
                    logger.error(f"❌ [EXPORT] Word導出異常: {str(e)}")
                    logger.error(f"❌ Word導出異常: {str(e)}", exc_info=True)
                    st.error(f"❌ Word文檔生成失敗: {str(e)}")

                    # 顯示詳細錯誤信息
                    with st.expander("🔍 查看詳細錯誤信息"):
                        st.text(str(e))

                    # 提供解決方案
                    with st.expander("💡 解決方案"):
                        st.markdown("""
                        **Word導出需要pandoc工具，請檢查:**

                        1. **Docker環境**: 重新構建鏡像確保包含pandoc
                        2. **本地環境**: 安裝pandoc
                        ```bash
                        # Windows
                        choco install pandoc

                        # macOS
                        brew install pandoc

                        # Linux
                        sudo apt-get install pandoc
                        ```

                        3. **替代方案**: 使用Markdown格式導出
                        """)
    
    with col3:
        if st.button("📊 導出 PDF", help="導出為PDF格式 (需要額外工具)"):
            logger.info(f"🖱️ 用戶點擊PDF導出按鈕 - 股票: {stock_symbol}")
            with st.spinner("正在生成PDF，請稍候..."):
                try:
                    logger.info("🔄 開始PDF導出流程...")

                    # 1. 保存分模塊報告（CLI格式）
                    logger.info("📁 開始保存分模塊報告（CLI格式）...")
                    modular_files = save_modular_reports_to_results_dir(results, stock_symbol)

                    # 2. 生成PDF彙總報告
                    content = report_exporter.export_report(results, 'pdf')
                    if content:
                        filename = f"{stock_symbol}_analysis_{timestamp}.pdf"
                        logger.info(f"✅ PDF導出成功，文件名: {filename}, 大小: {len(content)} 字節")

                        # 3. 保存PDF彙總報告到results目錄
                        saved_path = save_report_to_results_dir(content, filename, stock_symbol)

                        # 4. 顯示保存結果
                        if modular_files and saved_path:
                            st.success(f"✅ 已保存 {len(modular_files)} 個分模塊報告 + 1個PDF彙總報告")
                            with st.expander("📁 查看保存的文件"):
                                st.write("**分模塊報告:**")
                                for module, path in modular_files.items():
                                    st.write(f"- {module}: `{path}`")
                                st.write("**PDF彙總報告:**")
                                st.write(f"- PDF報告: `{saved_path}`")
                        elif saved_path:
                            st.success(f"✅ PDF已保存到: {saved_path}")
                        else:
                            st.success("✅ PDF生成成功！")

                        st.download_button(
                            label="📥 下載 PDF",
                            data=content,
                            file_name=filename,
                            mime="application/pdf"
                        )
                    else:
                        logger.error("❌ PDF導出失敗，content為空")
                        st.error("❌ PDF生成失敗")
                except Exception as e:
                    logger.error(f"❌ PDF導出異常: {str(e)}", exc_info=True)
                    st.error(f"❌ PDF生成失敗")

                    # 顯示詳細錯誤信息
                    with st.expander("🔍 查看詳細錯誤信息"):
                        st.text(str(e))

                    # 提供解決方案
                    with st.expander("💡 解決方案"):
                        st.markdown("""
                        **PDF導出需要額外的工具，請選擇以下方案之一:**

                        **方案1: 安裝wkhtmltopdf (推薦)**
                        ```bash
                        # Windows
                        choco install wkhtmltopdf

                        # macOS
                        brew install wkhtmltopdf

                        # Linux
                        sudo apt-get install wkhtmltopdf
                        ```

                        **方案2: 安裝LaTeX**
                        ```bash
                        # Windows
                        choco install miktex

                        # macOS
                        brew install mactex

                        # Linux
                        sudo apt-get install texlive-full
                        ```

                        **方案3: 使用替代格式**
                        - 📄 Markdown格式 - 轻量級，兼容性好
                        - 📝 Word格式 - 適合進一步編輯
                        """)

                    # 建議使用其他格式
                    st.info("💡 建議：您可以先使用Markdown或Word格式導出，然後使用其他工具轉換為PDF")


def save_analysis_report(stock_symbol: str, analysis_results: Dict[str, Any], 
                        report_content: str = None) -> bool:
    """
    保存分析報告到MongoDB
    
    Args:
        stock_symbol: 股票代碼
        analysis_results: 分析結果字典
        report_content: 報告內容（可選，如果不提供則自動生成）
    
    Returns:
        bool: 保存是否成功
    """
    try:
        if not MONGODB_REPORT_AVAILABLE or mongodb_report_manager is None:
            logger.warning("MongoDB報告管理器不可用，無法保存報告")
            return False
        
        # 如果沒有提供報告內容，則生成Markdown報告
        if report_content is None:
            report_content = report_exporter.generate_markdown_report(analysis_results)
        
        # 調用MongoDB報告管理器保存報告
        # 將報告內容包裝成字典格式
        reports_dict = {
            "markdown": report_content,
            "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        success = mongodb_report_manager.save_analysis_report(
            stock_symbol=stock_symbol,
            analysis_results=analysis_results,
            reports=reports_dict
        )
        
        if success:
            logger.info(f"✅ 分析報告已成功保存到MongoDB - 股票: {stock_symbol}")
        else:
            logger.error(f"❌ 分析報告保存到MongoDB失敗 - 股票: {stock_symbol}")
        
        return success
        
    except Exception as e:
        logger.error(f"❌ 保存分析報告到MongoDB時發生異常 - 股票: {stock_symbol}, 錯誤: {str(e)}")
        return False
    
 