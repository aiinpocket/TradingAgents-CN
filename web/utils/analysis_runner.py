"""
股票分析執行工具
"""

import sys
import os
import uuid
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger, get_logger_manager
logger = get_logger('web')

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 確保環境變量正確加載
load_dotenv(project_root / ".env", override=True)

# 導入統一日誌系統
from tradingagents.utils.logging_init import setup_web_logging
logger = setup_web_logging()

# 添加配置管理器
try:
    from tradingagents.config.config_manager import token_tracker
    TOKEN_TRACKING_ENABLED = True
    logger.info("✅ Token跟蹤功能已啟用")
except ImportError:
    TOKEN_TRACKING_ENABLED = False
    logger.warning("⚠️ Token跟蹤功能未啟用")

def translate_analyst_labels(text):
    """将分析師的英文標簽轉換為中文"""
    if not text:
        return text

    # 分析師標簽翻譯映射
    translations = {
        'Bull Analyst:': '看涨分析師:',
        'Bear Analyst:': '看跌分析師:',
        'Risky Analyst:': '激進風險分析師:',
        'Safe Analyst:': '保守風險分析師:',
        'Neutral Analyst:': '中性風險分析師:',
        'Research Manager:': '研究經理:',
        'Portfolio Manager:': '投資組合經理:',
        'Risk Judge:': '風險管理委員會:',
        'Trader:': '交易員:'
    }

    # 替換所有英文標簽
    for english, chinese in translations.items():
        text = text.replace(english, chinese)

    return text

def extract_risk_assessment(state):
    """從分析狀態中提取風險評估數據"""
    try:
        risk_debate_state = state.get('risk_debate_state', {})

        if not risk_debate_state:
            return None

        # 提取各個風險分析師的觀點並進行中文化
        risky_analysis = translate_analyst_labels(risk_debate_state.get('risky_history', ''))
        safe_analysis = translate_analyst_labels(risk_debate_state.get('safe_history', ''))
        neutral_analysis = translate_analyst_labels(risk_debate_state.get('neutral_history', ''))
        judge_decision = translate_analyst_labels(risk_debate_state.get('judge_decision', ''))

        # 格式化風險評估報告
        risk_assessment = f"""
## ⚠️ 風險評估報告

### 🔴 激進風險分析師觀點
{risky_analysis if risky_analysis else '暂無激進風險分析'}

### 🟡 中性風險分析師觀點
{neutral_analysis if neutral_analysis else '暂無中性風險分析'}

### 🟢 保守風險分析師觀點
{safe_analysis if safe_analysis else '暂無保守風險分析'}

### 🏛️ 風險管理委員會最终決议
{judge_decision if judge_decision else '暂無風險管理決议'}

---
*風險評估基於多角度分析，請結合個人風險承受能力做出投資決策*
        """.strip()

        return risk_assessment

    except Exception as e:
        logger.info(f"提取風險評估數據時出錯: {e}")
        return None

def run_stock_analysis(stock_symbol, analysis_date, analysts, research_depth, llm_provider, llm_model, market_type="美股", progress_callback=None):
    """執行股票分析

    Args:
        stock_symbol: 股票代碼
        analysis_date: 分析日期
        analysts: 分析師列表
        research_depth: 研究深度
        llm_provider: LLM提供商 (dashscope/deepseek/google)
        llm_model: 大模型名稱
        progress_callback: 進度回調函數，用於更新UI狀態
    """

    def update_progress(message, step=None, total_steps=None):
        """更新進度"""
        if progress_callback:
            progress_callback(message, step, total_steps)
        logger.info(f"[進度] {message}")

    # 生成會話ID用於Token跟蹤和日誌關聯
    session_id = f"analysis_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 1. 數據預獲取和驗證階段
    update_progress("🔍 驗證股票代碼並預獲取數據...", 1, 10)

    try:
        from tradingagents.utils.stock_validator import prepare_stock_data

        # 預獲取股票數據（默認30天歷史數據）
        preparation_result = prepare_stock_data(
            stock_code=stock_symbol,
            market_type=market_type,
            period_days=30,  # 可以根據research_depth調整
            analysis_date=analysis_date
        )

        if not preparation_result.is_valid:
            error_msg = f"❌ 股票數據驗證失败: {preparation_result.error_message}"
            update_progress(error_msg)
            logger.error(f"[{session_id}] {error_msg}")

            return {
                'success': False,
                'error': preparation_result.error_message,
                'suggestion': preparation_result.suggestion,
                'stock_symbol': stock_symbol,
                'analysis_date': analysis_date,
                'session_id': session_id
            }

        # 數據預獲取成功
        success_msg = f"✅ 數據準备完成: {preparation_result.stock_name} ({preparation_result.market_type})"
        update_progress(success_msg)  # 使用智能檢測，不再硬編碼步骤
        logger.info(f"[{session_id}] {success_msg}")
        logger.info(f"[{session_id}] 緩存狀態: {preparation_result.cache_status}")

    except Exception as e:
        error_msg = f"❌ 數據預獲取過程中發生錯誤: {str(e)}"
        update_progress(error_msg)
        logger.error(f"[{session_id}] {error_msg}")

        return {
            'success': False,
            'error': error_msg,
            'suggestion': "請檢查網絡連接或稍後重試",
            'stock_symbol': stock_symbol,
            'analysis_date': analysis_date,
            'session_id': session_id
        }

    # 記錄分析開始的詳細日誌
    logger_manager = get_logger_manager()
    import time
    analysis_start_time = time.time()

    logger_manager.log_analysis_start(
        logger, stock_symbol, "comprehensive_analysis", session_id
    )

    logger.info(f"🚀 [分析開始] 股票分析啟動",
               extra={
                   'stock_symbol': stock_symbol,
                   'analysis_date': analysis_date,
                   'analysts': analysts,
                   'research_depth': research_depth,
                   'llm_provider': llm_provider,
                   'llm_model': llm_model,
                   'market_type': market_type,
                   'session_id': session_id,
                   'event_type': 'web_analysis_start'
               })

    update_progress("🚀 開始股票分析...")

    # 估算Token使用（用於成本預估）
    if TOKEN_TRACKING_ENABLED:
        estimated_input = 2000 * len(analysts)  # 估算每個分析師2000個輸入token
        estimated_output = 1000 * len(analysts)  # 估算每個分析師1000個輸出token
        estimated_cost = token_tracker.estimate_cost(llm_provider, llm_model, estimated_input, estimated_output)

        update_progress(f"💰 預估分析成本: ¥{estimated_cost:.4f}")

    # 驗證環境變量
    update_progress("檢查環境變量配置...")
    finnhub_key = os.getenv("FINNHUB_API_KEY")

    logger.info(f"環境變量檢查:")
    logger.info(f"  FINNHUB_API_KEY: {'已設置' if finnhub_key else '未設置'}")

    if not finnhub_key:
        logger.warning("⚠️ FINNHUB_API_KEY 未設置，部分美股數據功能可能受限")

    update_progress("環境變量驗證通過")

    try:
        # 導入必要的模塊
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        # 創建配置
        update_progress("配置分析參數...")
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = llm_provider
        config["deep_think_llm"] = llm_model
        config["quick_think_llm"] = llm_model
        # 根據研究深度調整配置
        if research_depth == 1:  # 1級 - 快速分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            # 保持內存功能啟用，因為內存操作開銷很小但能顯著提升分析质量
            config["memory_enabled"] = True

            # 統一使用在線工具，避免離線工具的各種問題
            config["online_tools"] = True  # 所有市場都使用統一工具
            logger.info(f"🔧 [快速分析] {market_type}使用統一工具，確保數據源正確和穩定性")
        elif research_depth == 2:  # 2級 - 基础分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            config["memory_enabled"] = True
            config["online_tools"] = True
        elif research_depth == 3:  # 3級 - 標準分析 (默認)
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 2
            config["memory_enabled"] = True
            config["online_tools"] = True
        elif research_depth == 4:  # 4級 - 深度分析
            config["max_debate_rounds"] = 2
            config["max_risk_discuss_rounds"] = 2
            config["memory_enabled"] = True
            config["online_tools"] = True
        else:  # 5級 - 全面分析
            config["max_debate_rounds"] = 3
            config["max_risk_discuss_rounds"] = 3
            config["memory_enabled"] = True
            config["online_tools"] = True

        # 根據LLM提供商設置不同的配置
        if llm_provider == "google":
            # Google AI不需要backend_url，使用默認的OpenAI格式
            config["backend_url"] = "https://api.openai.com/v1"
            
            # 根據研究深度優化Google模型選擇
            if research_depth == 1:  # 快速分析 - 使用最快模型
                config["quick_think_llm"] = "gemini-2.5-flash-lite-preview-06-17"  # 1.45s
                config["deep_think_llm"] = "gemini-2.0-flash"  # 1.87s
            elif research_depth == 2:  # 基础分析 - 使用快速模型
                config["quick_think_llm"] = "gemini-2.0-flash"  # 1.87s
                config["deep_think_llm"] = "gemini-1.5-pro"  # 2.25s
            elif research_depth == 3:  # 標準分析 - 平衡性能
                config["quick_think_llm"] = "gemini-1.5-pro"  # 2.25s
                config["deep_think_llm"] = "gemini-2.5-flash"  # 2.73s
            elif research_depth == 4:  # 深度分析 - 使用强大模型
                config["quick_think_llm"] = "gemini-2.5-flash"  # 2.73s
                config["deep_think_llm"] = "gemini-2.5-pro"  # 16.68s
            else:  # 全面分析 - 使用最强模型
                config["quick_think_llm"] = "gemini-2.5-pro"  # 16.68s
                config["deep_think_llm"] = "gemini-2.5-pro"  # 16.68s
            
            logger.info(f"🤖 [Google AI] 快速模型: {config['quick_think_llm']}")
            logger.info(f"🤖 [Google AI] 深度模型: {config['deep_think_llm']}")
        elif llm_provider == "openai":
            # OpenAI官方API
            config["backend_url"] = "https://api.openai.com/v1"
            logger.info(f"🤖 [OpenAI] 使用模型: {llm_model}")
            logger.info(f"🤖 [OpenAI] API端點: https://api.openai.com/v1")
        elif llm_provider == "openrouter":
            # OpenRouter使用OpenAI兼容API
            config["backend_url"] = "https://openrouter.ai/api/v1"
            logger.info(f"🌐 [OpenRouter] 使用模型: {llm_model}")
            logger.info(f"🌐 [OpenRouter] API端點: https://openrouter.ai/api/v1")
        elif llm_provider == "siliconflow":
            config["backend_url"] = "https://api.siliconflow.cn/v1"
            logger.info(f"🌐 [SiliconFlow] 使用模型: {llm_model}")
            logger.info(f"🌐 [SiliconFlow] API端點: https://api.siliconflow.cn/v1")
        elif llm_provider == "custom_openai":
            # 自定義OpenAI端點
            custom_base_url = st.session_state.get("custom_openai_base_url", "https://api.openai.com/v1")
            config["backend_url"] = custom_base_url
            config["custom_openai_base_url"] = custom_base_url
            logger.info(f"🔧 [自定義OpenAI] 使用模型: {llm_model}")
            logger.info(f"🔧 [自定義OpenAI] API端點: {custom_base_url}")

        # 修複路徑問題 - 優先使用環境變量配置
        # 數據目錄：優先使用環境變量，否則使用默認路徑
        if not config.get("data_dir") or config["data_dir"] == "./data":
            env_data_dir = os.getenv("TRADINGAGENTS_DATA_DIR")
            if env_data_dir:
                # 如果環境變量是相對路徑，相對於項目根目錄解析
                if not os.path.isabs(env_data_dir):
                    config["data_dir"] = str(project_root / env_data_dir)
                else:
                    config["data_dir"] = env_data_dir
            else:
                config["data_dir"] = str(project_root / "data")

        # 結果目錄：優先使用環境變量，否則使用默認路徑
        if not config.get("results_dir") or config["results_dir"] == "./results":
            env_results_dir = os.getenv("TRADINGAGENTS_RESULTS_DIR")
            if env_results_dir:
                # 如果環境變量是相對路徑，相對於項目根目錄解析
                if not os.path.isabs(env_results_dir):
                    config["results_dir"] = str(project_root / env_results_dir)
                else:
                    config["results_dir"] = env_results_dir
            else:
                config["results_dir"] = str(project_root / "results")

        # 緩存目錄：優先使用環境變量，否則使用默認路徑
        if not config.get("data_cache_dir"):
            env_cache_dir = os.getenv("TRADINGAGENTS_CACHE_DIR")
            if env_cache_dir:
                # 如果環境變量是相對路徑，相對於項目根目錄解析
                if not os.path.isabs(env_cache_dir):
                    config["data_cache_dir"] = str(project_root / env_cache_dir)
                else:
                    config["data_cache_dir"] = env_cache_dir
            else:
                config["data_cache_dir"] = str(project_root / "tradingagents" / "dataflows" / "data_cache")

        # 確保目錄存在
        update_progress("📁 創建必要的目錄...")
        os.makedirs(config["data_dir"], exist_ok=True)
        os.makedirs(config["results_dir"], exist_ok=True)
        os.makedirs(config["data_cache_dir"], exist_ok=True)

        logger.info(f"📁 目錄配置:")
        logger.info(f"  - 數據目錄: {config['data_dir']}")
        logger.info(f"  - 結果目錄: {config['results_dir']}")
        logger.info(f"  - 緩存目錄: {config['data_cache_dir']}")
        logger.info(f"  - 環境變量 TRADINGAGENTS_RESULTS_DIR: {os.getenv('TRADINGAGENTS_RESULTS_DIR', '未設置')}")

        logger.info(f"使用配置: {config}")
        logger.info(f"分析師列表: {analysts}")
        logger.info(f"股票代碼: {stock_symbol}")
        logger.info(f"分析日期: {analysis_date}")

        # 根據市場類型調整股票代碼格式
        logger.debug(f"🔍 [RUNNER DEBUG] ===== 股票代碼格式化 =====")
        logger.debug(f"🔍 [RUNNER DEBUG] 原始股票代碼: '{stock_symbol}'")
        logger.debug(f"🔍 [RUNNER DEBUG] 市場類型: '{market_type}'")

        if market_type == "A股":
            # A股代碼不需要特殊處理，保持原樣
            formatted_symbol = stock_symbol
            logger.debug(f"🔍 [RUNNER DEBUG] A股代碼保持原樣: '{formatted_symbol}'")
            update_progress(f"🇨🇳 準备分析A股: {formatted_symbol}")
        elif market_type == "港股":
            # 港股代碼轉為大寫，確保.HK後缀
            formatted_symbol = stock_symbol.upper()
            if not formatted_symbol.endswith('.HK'):
                # 如果是純數字，添加.HK後缀
                if formatted_symbol.isdigit():
                    formatted_symbol = f"{formatted_symbol.zfill(4)}.HK"
            update_progress(f"🇭🇰 準备分析港股: {formatted_symbol}")
        else:
            # 美股代碼轉為大寫
            formatted_symbol = stock_symbol.upper()
            logger.debug(f"🔍 [RUNNER DEBUG] 美股代碼轉大寫: '{stock_symbol}' -> '{formatted_symbol}'")
            update_progress(f"🇺🇸 準备分析美股: {formatted_symbol}")

        logger.debug(f"🔍 [RUNNER DEBUG] 最终傳遞給分析引擎的股票代碼: '{formatted_symbol}'")

        # 初始化交易圖
        update_progress("🔧 初始化分析引擎...")
        graph = TradingAgentsGraph(analysts, config=config, debug=False)

        # 執行分析
        update_progress(f"📊 開始分析 {formatted_symbol} 股票，這可能需要几分鐘時間...")
        logger.debug(f"🔍 [RUNNER DEBUG] ===== 調用graph.propagate =====")
        logger.debug(f"🔍 [RUNNER DEBUG] 傳遞給graph.propagate的參數:")
        logger.debug(f"🔍 [RUNNER DEBUG]   symbol: '{formatted_symbol}'")
        logger.debug(f"🔍 [RUNNER DEBUG]   date: '{analysis_date}'")

        state, decision = graph.propagate(formatted_symbol, analysis_date)

        # 調試信息
        logger.debug(f"🔍 [DEBUG] 分析完成，decision類型: {type(decision)}")
        logger.debug(f"🔍 [DEBUG] decision內容: {decision}")

        # 格式化結果
        update_progress("📋 分析完成，正在整理結果...")

        # 提取風險評估數據
        risk_assessment = extract_risk_assessment(state)

        # 将風險評估添加到狀態中
        if risk_assessment:
            state['risk_assessment'] = risk_assessment

        # 記錄Token使用（實际使用量，這里使用估算值）
        if TOKEN_TRACKING_ENABLED:
            # 在實际應用中，這些值應该從LLM響應中獲取
            # 這里使用基於分析師數量和研究深度的估算
            actual_input_tokens = len(analysts) * (1500 if research_depth == "快速" else 2500 if research_depth == "標準" else 4000)
            actual_output_tokens = len(analysts) * (800 if research_depth == "快速" else 1200 if research_depth == "標準" else 2000)

            usage_record = token_tracker.track_usage(
                provider=llm_provider,
                model_name=llm_model,
                input_tokens=actual_input_tokens,
                output_tokens=actual_output_tokens,
                session_id=session_id,
                analysis_type=f"{market_type}_analysis"
            )

            if usage_record:
                update_progress(f"💰 記錄使用成本: ¥{usage_record.cost:.4f}")

        results = {
            'stock_symbol': stock_symbol,
            'analysis_date': analysis_date,
            'analysts': analysts,
            'research_depth': research_depth,
            'llm_provider': llm_provider,
            'llm_model': llm_model,
            'state': state,
            'decision': decision,
            'success': True,
            'error': None,
            'session_id': session_id if TOKEN_TRACKING_ENABLED else None
        }

        # 記錄分析完成的詳細日誌
        analysis_duration = time.time() - analysis_start_time

        # 計算总成本（如果有Token跟蹤）
        total_cost = 0.0
        if TOKEN_TRACKING_ENABLED:
            try:
                total_cost = token_tracker.get_session_cost(session_id)
            except:
                pass

        logger_manager.log_analysis_complete(
            logger, stock_symbol, "comprehensive_analysis", session_id,
            analysis_duration, total_cost
        )

        logger.info(f"✅ [分析完成] 股票分析成功完成",
                   extra={
                       'stock_symbol': stock_symbol,
                       'session_id': session_id,
                       'duration': analysis_duration,
                       'total_cost': total_cost,
                       'analysts_used': analysts,
                       'success': True,
                       'event_type': 'web_analysis_complete'
                   })

        # 保存分析報告到本地和MongoDB
        try:
            update_progress("💾 正在保存分析報告...")
            from .report_exporter import save_analysis_report, save_modular_reports_to_results_dir
            
            # 1. 保存分模塊報告到本地目錄
            logger.info(f"📁 [本地保存] 開始保存分模塊報告到本地目錄")
            local_files = save_modular_reports_to_results_dir(results, stock_symbol)
            if local_files:
                logger.info(f"✅ [本地保存] 已保存 {len(local_files)} 個本地報告文件")
                for module, path in local_files.items():
                    logger.info(f"  - {module}: {path}")
            else:
                logger.warning(f"⚠️ [本地保存] 本地報告文件保存失败")
            
            # 2. 保存分析報告到MongoDB
            logger.info(f"🗄️ [MongoDB保存] 開始保存分析報告到MongoDB")
            save_success = save_analysis_report(
                stock_symbol=stock_symbol,
                analysis_results=results
            )
            
            if save_success:
                logger.info(f"✅ [MongoDB保存] 分析報告已成功保存到MongoDB")
                update_progress("✅ 分析報告已保存到數據庫和本地文件")
            else:
                logger.warning(f"⚠️ [MongoDB保存] MongoDB報告保存失败")
                if local_files:
                    update_progress("✅ 本地報告已保存，但數據庫保存失败")
                else:
                    update_progress("⚠️ 報告保存失败，但分析已完成")
                
        except Exception as save_error:
            logger.error(f"❌ [報告保存] 保存分析報告時發生錯誤: {str(save_error)}")
            update_progress("⚠️ 報告保存出錯，但分析已完成")

        update_progress("✅ 分析成功完成！")
        return results

    except Exception as e:
        # 記錄分析失败的詳細日誌
        analysis_duration = time.time() - analysis_start_time

        logger_manager.log_module_error(
            logger, "comprehensive_analysis", stock_symbol, session_id,
            analysis_duration, str(e)
        )

        logger.error(f"❌ [分析失败] 股票分析執行失败",
                    extra={
                        'stock_symbol': stock_symbol,
                        'session_id': session_id,
                        'duration': analysis_duration,
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'analysts_used': analysts,
                        'success': False,
                        'event_type': 'web_analysis_error'
                    }, exc_info=True)

        # 如果真實分析失败，返回錯誤信息而不是誤導性演示數據
        return {
            'stock_symbol': stock_symbol,
            'analysis_date': analysis_date,
            'analysts': analysts,
            'research_depth': research_depth,
            'llm_provider': llm_provider,
            'llm_model': llm_model,
            'state': {},  # 空狀態，将顯示占位符
            'decision': {},  # 空決策
            'success': False,
            'error': str(e),
            'is_demo': False,
            'error_reason': f"分析失败: {str(e)}"
        }

def format_analysis_results(results):
    """格式化分析結果用於顯示"""
    
    if not results['success']:
        return {
            'error': results['error'],
            'success': False
        }
    
    state = results['state']
    decision = results['decision']

    # 提取關键信息
    # decision 可能是字符串（如 "BUY", "SELL", "HOLD"）或字典
    if isinstance(decision, str):
        # 将英文投資建议轉換為中文
        action_translation = {
            'BUY': '买入',
            'SELL': '卖出',
            'HOLD': '持有',
            'buy': '买入',
            'sell': '卖出',
            'hold': '持有'
        }
        action = action_translation.get(decision.strip(), decision.strip())

        formatted_decision = {
            'action': action,
            'confidence': 0.7,  # 默認置信度
            'risk_score': 0.3,  # 默認風險分數
            'target_price': None,  # 字符串格式没有目標價格
            'reasoning': f'基於AI分析，建议{decision.strip().upper()}'
        }
    elif isinstance(decision, dict):
        # 處理目標價格 - 確保正確提取數值
        target_price = decision.get('target_price')
        if target_price is not None and target_price != 'N/A':
            try:
                # 嘗試轉換為浮點數
                if isinstance(target_price, str):
                    # 移除貨币符號和空格
                    clean_price = target_price.replace('$', '').replace('¥', '').replace('￥', '').strip()
                    target_price = float(clean_price) if clean_price and clean_price != 'None' else None
                elif isinstance(target_price, (int, float)):
                    target_price = float(target_price)
                else:
                    target_price = None
            except (ValueError, TypeError):
                target_price = None
        else:
            target_price = None

        # 将英文投資建议轉換為中文
        action_translation = {
            'BUY': '买入',
            'SELL': '卖出',
            'HOLD': '持有',
            'buy': '买入',
            'sell': '卖出',
            'hold': '持有'
        }
        action = decision.get('action', '持有')
        chinese_action = action_translation.get(action, action)

        formatted_decision = {
            'action': chinese_action,
            'confidence': decision.get('confidence', 0.5),
            'risk_score': decision.get('risk_score', 0.3),
            'target_price': target_price,
            'reasoning': decision.get('reasoning', '暂無分析推理')
        }
    else:
        # 處理其他類型
        formatted_decision = {
            'action': '持有',
            'confidence': 0.5,
            'risk_score': 0.3,
            'target_price': None,
            'reasoning': f'分析結果: {str(decision)}'
        }
    
    # 格式化狀態信息
    formatted_state = {}
    
    # 處理各個分析模塊的結果 - 包含完整的智能體团隊分析
    analysis_keys = [
        'market_report',
        'fundamentals_report',
        'sentiment_report',
        'news_report',
        'risk_assessment',
        'investment_plan',
        # 添加缺失的团隊決策數據，確保与CLI端一致
        'investment_debate_state',  # 研究团隊辩論（多头/空头研究員）
        'trader_investment_plan',   # 交易团隊計劃
        'risk_debate_state',        # 風險管理团隊決策
        'final_trade_decision'      # 最终交易決策
    ]
    
    for key in analysis_keys:
        if key in state:
            # 對文本內容進行中文化處理
            content = state[key]
            if isinstance(content, str):
                content = translate_analyst_labels(content)
            formatted_state[key] = content
        elif key == 'risk_assessment':
            # 特殊處理：從 risk_debate_state 生成 risk_assessment
            risk_assessment = extract_risk_assessment(state)
            if risk_assessment:
                formatted_state[key] = risk_assessment
    
    return {
        'stock_symbol': results['stock_symbol'],
        'decision': formatted_decision,
        'state': formatted_state,
        'success': True,
        # 将配置信息放在顶層，供前端直接訪問
        'analysis_date': results['analysis_date'],
        'analysts': results['analysts'],
        'research_depth': results['research_depth'],
        'llm_provider': results.get('llm_provider', 'dashscope'),
        'llm_model': results['llm_model'],
        'metadata': {
            'analysis_date': results['analysis_date'],
            'analysts': results['analysts'],
            'research_depth': results['research_depth'],
            'llm_provider': results.get('llm_provider', 'dashscope'),
            'llm_model': results['llm_model']
        }
    }

def validate_analysis_params(stock_symbol, analysis_date, analysts, research_depth, market_type="美股"):
    """驗證分析參數"""

    errors = []

    # 驗證股票代碼
    if not stock_symbol or len(stock_symbol.strip()) == 0:
        errors.append("股票代碼不能為空")
    elif len(stock_symbol.strip()) > 10:
        errors.append("股票代碼長度不能超過10個字符")
    else:
        # 根據市場類型驗證代碼格式
        symbol = stock_symbol.strip()
        if market_type == "A股":
            # A股：6位數字
            import re
            if not re.match(r'^\d{6}$', symbol):
                errors.append("A股代碼格式錯誤，應為6位數字（如：000001）")
        elif market_type == "港股":
            # 港股：4-5位數字.HK 或 純4-5位數字
            import re
            symbol_upper = symbol.upper()
            # 檢查是否為 XXXX.HK 或 XXXXX.HK 格式
            hk_format = re.match(r'^\d{4,5}\.HK$', symbol_upper)
            # 檢查是否為純4-5位數字格式
            digit_format = re.match(r'^\d{4,5}$', symbol)

            if not (hk_format or digit_format):
                errors.append("港股代碼格式錯誤，應為4位數字.HK（如：0700.HK）或4位數字（如：0700）")
        elif market_type == "美股":
            # 美股：1-5位字母
            import re
            if not re.match(r'^[A-Z]{1,5}$', symbol.upper()):
                errors.append("美股代碼格式錯誤，應為1-5位字母（如：AAPL）")
    
    # 驗證分析師列表
    if not analysts or len(analysts) == 0:
        errors.append("必须至少選擇一個分析師")
    
    valid_analysts = ['market', 'social', 'news', 'fundamentals']
    invalid_analysts = [a for a in analysts if a not in valid_analysts]
    if invalid_analysts:
        errors.append(f"無效的分析師類型: {', '.join(invalid_analysts)}")
    
    # 驗證研究深度
    if not isinstance(research_depth, int) or research_depth < 1 or research_depth > 5:
        errors.append("研究深度必须是1-5之間的整數")
    
    # 驗證分析日期
    try:
        from datetime import datetime
        datetime.strptime(analysis_date, '%Y-%m-%d')
    except ValueError:
        errors.append("分析日期格式無效，應為YYYY-MM-DD格式")
    
    return len(errors) == 0, errors

def get_supported_stocks():
    """獲取支持的股票列表"""
    
    # 常见的美股股票代碼
    popular_stocks = [
        {'symbol': 'AAPL', 'name': '苹果公司', 'sector': '科技'},
        {'symbol': 'MSFT', 'name': '微软', 'sector': '科技'},
        {'symbol': 'GOOGL', 'name': '谷歌', 'sector': '科技'},
        {'symbol': 'AMZN', 'name': '亚馬逊', 'sector': '消費'},
        {'symbol': 'TSLA', 'name': '特斯拉', 'sector': '汽車'},
        {'symbol': 'NVDA', 'name': '英伟達', 'sector': '科技'},
        {'symbol': 'META', 'name': 'Meta', 'sector': '科技'},
        {'symbol': 'NFLX', 'name': '奈飞', 'sector': '媒體'},
        {'symbol': 'AMD', 'name': 'AMD', 'sector': '科技'},
        {'symbol': 'INTC', 'name': '英特爾', 'sector': '科技'},
        {'symbol': 'SPY', 'name': 'S&P 500 ETF', 'sector': 'ETF'},
        {'symbol': 'QQQ', 'name': '纳斯達克100 ETF', 'sector': 'ETF'},
    ]
    
    return popular_stocks

def generate_demo_results_deprecated(stock_symbol, analysis_date, analysts, research_depth, llm_provider, llm_model, error_msg, market_type="美股"):
    """
    已弃用：生成演示分析結果

    註意：此函數已弃用，因為演示數據會誤導用戶。
    現在我們使用占位符來代替演示數據。
    """

    import random

    # 根據市場類型設置貨币符號和價格範围
    if market_type == "港股":
        currency_symbol = "HK$"
        price_range = (50, 500)  # 港股價格範围
        market_name = "港股"
    elif market_type == "A股":
        currency_symbol = "¥"
        price_range = (5, 100)   # A股價格範围
        market_name = "A股"
    else:  # 美股
        currency_symbol = "$"
        price_range = (50, 300)  # 美股價格範围
        market_name = "美股"

    # 生成模擬決策
    actions = ['买入', '持有', '卖出']
    action = random.choice(actions)

    demo_decision = {
        'action': action,
        'confidence': round(random.uniform(0.6, 0.9), 2),
        'risk_score': round(random.uniform(0.2, 0.7), 2),
        'target_price': round(random.uniform(*price_range), 2),
        'reasoning': f"""
基於對{market_name}{stock_symbol}的综合分析，我們的AI分析团隊得出以下結論：

**投資建议**: {action}
**目標價格**: {currency_symbol}{round(random.uniform(*price_range), 2)}

**主要分析要點**:
1. **技術面分析**: 當前價格趋势顯示{'上涨' if action == '买入' else '下跌' if action == '卖出' else '横盘'}信號
2. **基本面評估**: 公司財務狀况{'良好' if action == '买入' else '一般' if action == '持有' else '需關註'}
3. **市場情绪**: 投資者情绪{'乐觀' if action == '买入' else '中性' if action == '持有' else '谨慎'}
4. **風險評估**: 當前風險水平為{'中等' if action == '持有' else '較低' if action == '买入' else '較高'}

**註意**: 這是演示數據，實际分析需要配置正確的API密鑰。
        """
    }

    # 生成模擬狀態數據
    demo_state = {}

    if 'market' in analysts:
        current_price = round(random.uniform(*price_range), 2)
        high_price = round(current_price * random.uniform(1.2, 1.8), 2)
        low_price = round(current_price * random.uniform(0.5, 0.8), 2)

        demo_state['market_report'] = f"""
## 📈 {market_name}{stock_symbol} 技術面分析報告

### 價格趋势分析
- **當前價格**: {currency_symbol}{current_price}
- **日內變化**: {random.choice(['+', '-'])}{round(random.uniform(0.5, 5), 2)}%
- **52周高點**: {currency_symbol}{high_price}
- **52周低點**: {currency_symbol}{low_price}

### 技術指標
- **RSI (14日)**: {round(random.uniform(30, 70), 1)}
- **MACD**: {'看涨' if action == 'BUY' else '看跌' if action == 'SELL' else '中性'}
- **移動平均線**: 價格{'高於' if action == 'BUY' else '低於' if action == 'SELL' else '接近'}20日均線

### 支撑阻力位
- **支撑位**: ${round(random.uniform(80, 120), 2)}
- **阻力位**: ${round(random.uniform(250, 350), 2)}

*註意: 這是演示數據，實际分析需要配置API密鑰*
        """

    if 'fundamentals' in analysts:
        demo_state['fundamentals_report'] = f"""
## 💰 {stock_symbol} 基本面分析報告

### 財務指標
- **市盈率 (P/E)**: {round(random.uniform(15, 35), 1)}
- **市净率 (P/B)**: {round(random.uniform(1, 5), 1)}
- **净資產收益率 (ROE)**: {round(random.uniform(10, 25), 1)}%
- **毛利率**: {round(random.uniform(20, 60), 1)}%

### 盈利能力
- **營收增長**: {random.choice(['+', '-'])}{round(random.uniform(5, 20), 1)}%
- **净利润增長**: {random.choice(['+', '-'])}{round(random.uniform(10, 30), 1)}%
- **每股收益**: ${round(random.uniform(2, 15), 2)}

### 財務健康度
- **负债率**: {round(random.uniform(20, 60), 1)}%
- **流動比率**: {round(random.uniform(1, 3), 1)}
- **現金流**: {'正向' if action != 'SELL' else '需關註'}

*註意: 這是演示數據，實际分析需要配置API密鑰*
        """

    if 'social' in analysts:
        demo_state['sentiment_report'] = f"""
## 💭 {stock_symbol} 市場情绪分析報告

### 社交媒體情绪
- **整體情绪**: {'積極' if action == 'BUY' else '消極' if action == 'SELL' else '中性'}
- **情绪强度**: {round(random.uniform(0.5, 0.9), 2)}
- **討論熱度**: {'高' if random.random() > 0.5 else '中等'}

### 投資者情绪指標
- **恐慌贪婪指數**: {round(random.uniform(20, 80), 0)}
- **看涨看跌比**: {round(random.uniform(0.8, 1.5), 2)}
- **期權Put/Call比**: {round(random.uniform(0.5, 1.2), 2)}

### 機構投資者動向
- **機構持仓變化**: {random.choice(['增持', '减持', '維持'])}
- **分析師評級**: {'买入' if action == 'BUY' else '卖出' if action == 'SELL' else '持有'}

*註意: 這是演示數據，實际分析需要配置API密鑰*
        """

    if 'news' in analysts:
        demo_state['news_report'] = f"""
## 📰 {stock_symbol} 新聞事件分析報告

### 近期重要新聞
1. **財報發布**: 公司發布{'超預期' if action == 'BUY' else '低於預期' if action == 'SELL' else '符合預期'}的季度財報
2. **行業動態**: 所在行業面臨{'利好' if action == 'BUY' else '挑战' if action == 'SELL' else '穩定'}政策環境
3. **公司公告**: 管理層{'乐觀' if action == 'BUY' else '谨慎' if action == 'SELL' else '穩健'}展望未來

### 新聞情绪分析
- **正面新聞占比**: {round(random.uniform(40, 80), 0)}%
- **负面新聞占比**: {round(random.uniform(10, 40), 0)}%
- **中性新聞占比**: {round(random.uniform(20, 50), 0)}%

### 市場影響評估
- **短期影響**: {'正面' if action == 'BUY' else '负面' if action == 'SELL' else '中性'}
- **長期影響**: {'積極' if action != 'SELL' else '需觀察'}

*註意: 這是演示數據，實际分析需要配置API密鑰*
        """

    # 添加風險評估和投資建议
    demo_state['risk_assessment'] = f"""
## ⚠️ {stock_symbol} 風險評估報告

### 主要風險因素
1. **市場風險**: {'低' if action == 'BUY' else '高' if action == 'SELL' else '中等'}
2. **行業風險**: {'可控' if action != 'SELL' else '需關註'}
3. **公司特定風險**: {'較低' if action == 'BUY' else '中等'}

### 風險等級評估
- **总體風險等級**: {'低風險' if action == 'BUY' else '高風險' if action == 'SELL' else '中等風險'}
- **建议仓位**: {random.choice(['轻仓', '標準仓位', '重仓']) if action != 'SELL' else '建议减仓'}

*註意: 這是演示數據，實际分析需要配置API密鑰*
    """

    demo_state['investment_plan'] = f"""
## 📋 {stock_symbol} 投資建议

### 具體操作建议
- **操作方向**: {action}
- **建议價位**: ${round(random.uniform(90, 310), 2)}
- **止損位**: ${round(random.uniform(80, 200), 2)}
- **目標價位**: ${round(random.uniform(150, 400), 2)}

### 投資策略
- **投資期限**: {'短期' if research_depth <= 2 else '中長期'}
- **仓位管理**: {'分批建仓' if action == 'BUY' else '分批减仓' if action == 'SELL' else '維持現狀'}

*註意: 這是演示數據，實际分析需要配置API密鑰*
    """

    # 添加团隊決策演示數據，確保与CLI端一致
    demo_state['investment_debate_state'] = {
        'bull_history': f"""
## 📈 多头研究員分析

作為多头研究員，我對{stock_symbol}持乐觀態度：

### 🚀 投資亮點
1. **技術面突破**: 股價突破關键阻力位，技術形態良好
2. **基本面支撑**: 公司業绩穩健增長，財務狀况健康
3. **市場機會**: 當前估值合理，具备上涨空間

### 📊 數據支持
- 近期成交量放大，資金流入明顯
- 行業景气度提升，政策環境有利
- 機構投資者增持，市場信心增强

**建议**: 積極买入，目標價位上調15-20%

*註意: 這是演示數據*
        """.strip(),

        'bear_history': f"""
## 📉 空头研究員分析

作為空头研究員，我對{stock_symbol}持谨慎態度：

### ⚠️ 風險因素
1. **估值偏高**: 當前市盈率超過行業平均水平
2. **技術風險**: 短期涨幅過大，存在回調壓力
3. **宏觀環境**: 市場整體波動加大，不確定性增加

### 📉 擔忧點
- 成交量虽然放大，但可能是獲利盘出貨
- 行業競爭加剧，公司市場份額面臨挑战
- 政策變化可能對行業產生负面影響

**建议**: 谨慎觀望，等待更好的入場時機

*註意: 這是演示數據*
        """.strip(),

        'judge_decision': f"""
## 🎯 研究經理综合決策

經過多头和空头研究員的充分辩論，我的综合判斷如下：

### 📊 综合評估
- **多头觀點**: 技術面和基本面都顯示積極信號
- **空头觀點**: 估值和短期風險需要關註
- **平衡考慮**: 機會与風險並存，需要策略性操作

### 🎯 最终建议
基於當前市場環境和{stock_symbol}的具體情况，建议採取**{action}**策略：

1. **操作建议**: {action}
2. **仓位控制**: {'分批建仓' if action == '买入' else '分批减仓' if action == '卖出' else '維持現狀'}
3. **風險管理**: 設置止損位，控制單只股票仓位不超過10%

**決策依據**: 综合技術面、基本面和市場情绪分析

*註意: 這是演示數據*
        """.strip()
    }

    demo_state['trader_investment_plan'] = f"""
## 💼 交易团隊執行計劃

基於研究团隊的分析結果，制定如下交易執行計劃：

### 🎯 交易策略
- **交易方向**: {action}
- **目標價位**: {currency_symbol}{round(random.uniform(*price_range) * 1.1, 2)}
- **止損價位**: {currency_symbol}{round(random.uniform(*price_range) * 0.9, 2)}

### 📊 仓位管理
- **建议仓位**: {'30-50%' if action == '买入' else '减仓至20%' if action == '卖出' else '維持現有仓位'}
- **分批操作**: {'分3次建仓' if action == '买入' else '分2次减仓' if action == '卖出' else '暂不操作'}
- **時間安排**: {'1-2周內完成' if action != '持有' else '持续觀察'}

### ⚠️ 風險控制
- **止損設置**: 跌破支撑位立即止損
- **止盈策略**: 達到目標價位分批止盈
- **監控要點**: 密切關註成交量和技術指標變化

*註意: 這是演示數據，實际交易需要配置API密鑰*
    """

    demo_state['risk_debate_state'] = {
        'risky_history': f"""
## 🚀 激進分析師風險評估

從激進投資角度分析{stock_symbol}：

### 💪 風險承受能力
- **高收益機會**: 當前市場提供了難得的投資機會
- **風險可控**: 虽然存在波動，但長期趋势向好
- **時機把握**: 現在是積極布局的最佳時機

### 🎯 激進策略
- **加大仓位**: 建议将仓位提升至60-80%
- **杠杆使用**: 可適度使用杠杆放大收益
- **快速行動**: 機會稍纵即逝，需要果斷決策

**風險評級**: 中等風險，高收益潜力

*註意: 這是演示數據*
        """.strip(),

        'safe_history': f"""
## 🛡️ 保守分析師風險評估

從風險控制角度分析{stock_symbol}：

### ⚠️ 風險识別
- **市場波動**: 當前市場不確定性較高
- **估值風險**: 部分股票估值已經偏高
- **流動性風險**: 需要關註市場流動性變化

### 🔒 保守策略
- **控制仓位**: 建议仓位不超過30%
- **分散投資**: 避免過度集中於單一標的
- **安全邊际**: 確保有足夠的安全邊际

**風險評級**: 中高風險，需要谨慎操作

*註意: 這是演示數據*
        """.strip(),

        'neutral_history': f"""
## ⚖️ 中性分析師風險評估

從平衡角度分析{stock_symbol}：

### 📊 客觀評估
- **機會与風險並存**: 當前市場既有機會也有風險
- **適度參与**: 建议採取適度參与的策略
- **灵活調整**: 根據市場變化及時調整策略

### ⚖️ 平衡策略
- **中等仓位**: 建议仓位控制在40-50%
- **動態調整**: 根據市場情况動態調整仓位
- **風險監控**: 持续監控風險指標變化

**風險評級**: 中等風險，平衡收益

*註意: 這是演示數據*
        """.strip(),

        'judge_decision': f"""
## 🎯 投資組合經理最终風險決策

综合三位風險分析師的意见，最终風險管理決策如下：

### 📊 風險综合評估
- **激進觀點**: 高收益機會，建议積極參与
- **保守觀點**: 風險較高，建议谨慎操作
- **中性觀點**: 機會与風險並存，適度參与

### 🎯 最终風險決策
基於當前市場環境和{stock_symbol}的風險特征：

1. **風險等級**: 中等風險
2. **建议仓位**: 40%（平衡收益与風險）
3. **風險控制**: 嚴格執行止損策略
4. **監控頻率**: 每日監控，及時調整

**決策理由**: 在控制風險的前提下，適度參与市場機會

*註意: 這是演示數據*
        """.strip()
    }

    demo_state['final_trade_decision'] = f"""
## 🎯 最终投資決策

經過分析師团隊、研究团隊、交易团隊和風險管理团隊的全面分析，最终投資決策如下：

### 📊 決策摘要
- **投資建议**: **{action}**
- **置信度**: {confidence:.1%}
- **風險評級**: 中等風險
- **預期收益**: {'10-20%' if action == '买入' else '規避損失' if action == '卖出' else '穩健持有'}

### 🎯 執行計劃
1. **操作方向**: {action}
2. **目標仓位**: {'40%' if action == '买入' else '20%' if action == '卖出' else '維持現狀'}
3. **執行時間**: {'1-2周內分批執行' if action != '持有' else '持续觀察'}
4. **風險控制**: 嚴格執行止損止盈策略

### 📈 預期目標
- **目標價位**: {currency_symbol}{round(random.uniform(*price_range) * 1.15, 2)}
- **止損價位**: {currency_symbol}{round(random.uniform(*price_range) * 0.85, 2)}
- **投資期限**: {'3-6個月' if research_depth >= 3 else '1-3個月'}

### ⚠️ 重要提醒
這是基於當前市場環境和{stock_symbol}基本面的综合判斷。投資有風險，請根據個人風險承受能力谨慎決策。

**免责聲明**: 本分析仅供參考，不構成投資建议。

*註意: 這是演示數據，實际分析需要配置正確的API密鑰*
    """

    return {
        'stock_symbol': stock_symbol,
        'analysis_date': analysis_date,
        'analysts': analysts,
        'research_depth': research_depth,
        'llm_provider': llm_provider,
        'llm_model': llm_model,
        'state': demo_state,
        'decision': demo_decision,
        'success': True,
        'error': None,
        'is_demo': True,
        'demo_reason': f"API調用失败，顯示演示數據。錯誤信息: {error_msg}"
    }
