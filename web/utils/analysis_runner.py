"""
股票分析執行工具
"""

import sys
import os
import uuid
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger, get_logger_manager
logger = get_logger('web')

# 新增項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 確保環境變數正確載入
load_dotenv(project_root / ".env", override=True)

# 新增配置管理器
try:
    from tradingagents.config.config_manager import token_tracker
    TOKEN_TRACKING_ENABLED = True
    logger.info("Token追蹤功能已啟用")
except ImportError:
    TOKEN_TRACKING_ENABLED = False
    logger.warning("Token追蹤功能未啟用")

def translate_analyst_labels(text):
    """將分析師的英文標籤轉換為中文"""
    if not text:
        return text

    # 分析師標籤翻譯映射
    translations = {
        'Bull Analyst:': '看漲分析師:',
        'Bear Analyst:': '看跌分析師:',
        'Risky Analyst:': '激進風險分析師:',
        'Safe Analyst:': '保守風險分析師:',
        'Neutral Analyst:': '中性風險分析師:',
        'Research Manager:': '研究經理:',
        'Portfolio Manager:': '投資組合經理:',
        'Risk Judge:': '風險管理委員會:',
        'Trader:': '交易員:'
    }

    # 替換所有英文標籤
    for english, chinese in translations.items():
        text = text.replace(english, chinese)

    return text

def extract_risk_assessment(state):
    """從分析狀態中提取風險評估資料"""
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
## 風險評估報告

### 激進風險分析師觀點
{risky_analysis if risky_analysis else '暫無激進風險分析'}

### 中性風險分析師觀點
{neutral_analysis if neutral_analysis else '暫無中性風險分析'}

### 保守風險分析師觀點
{safe_analysis if safe_analysis else '暫無保守風險分析'}

### 風險管理委員會最終決議
{judge_decision if judge_decision else '暫無風險管理決議'}

---
*風險評估基於多角度分析，請結合個人風險承受能力做出投資決策*
        """.strip()

        return risk_assessment

    except Exception as e:
        logger.info(f"提取風險評估資料時出錯: {e}")
        return None

def run_stock_analysis(stock_symbol, analysis_date, analysts, research_depth, llm_provider, llm_model, market_type="美股", progress_callback=None):
    """執行股票分析

    Args:
        stock_symbol: 股票代碼
        analysis_date: 分析日期
        analysts: 分析師列表
        research_depth: 研究深度
        llm_provider: LLM 提供商 (openai/anthropic)
        llm_model: 大模型名稱
        progress_callback: 進度回呼函式，用於更新UI狀態
    """

    def update_progress(message, step=None, total_steps=None):
        """更新進度"""
        if progress_callback:
            progress_callback(message, step, total_steps)
        logger.info(f"[進度] {message}")

    # 生成會話ID用於Token追蹤和日誌關聯
    session_id = f"analysis_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # 1. 資料預取得和驗證階段
    update_progress("驗證股票代碼並預取得資料...", 1, 10)

    try:
        from tradingagents.utils.stock_validator import prepare_stock_data

        # 預取得股票資料（預設30天歷史資料）
        preparation_result = prepare_stock_data(
            stock_code=stock_symbol,
            market_type=market_type,
            period_days=30,  # 可以根據research_depth調整
            analysis_date=analysis_date
        )

        if not preparation_result.is_valid:
            error_msg = f"股票資料驗證失敗: {preparation_result.error_message}"
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

        # 資料預取得成功
        success_msg = f"資料準備完成: {preparation_result.stock_name} ({preparation_result.market_type})"
        update_progress(success_msg)  # 使用智慧檢測，不再硬編碼步驟
        logger.info(f"[{session_id}] {success_msg}")
        logger.info(f"[{session_id}] 快取狀態: {preparation_result.cache_status}")

    except Exception as e:
        error_msg = f"資料預取得過程中發生錯誤: {str(e)}"
        update_progress(error_msg)
        logger.error(f"[{session_id}] {error_msg}")

        return {
            'success': False,
            'error': error_msg,
            'suggestion': "請檢查網路連接或稍後重試",
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

    logger.info(f" [分析開始] 股票分析啟動",
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

    update_progress("開始股票分析...")

    # 估算Token使用（用於成本預估）
    if TOKEN_TRACKING_ENABLED:
        estimated_input = 2000 * len(analysts)  # 估算每個分析師2000個輸入token
        estimated_output = 1000 * len(analysts)  # 估算每個分析師1000個輸出token
        estimated_cost = token_tracker.estimate_cost(llm_provider, llm_model, estimated_input, estimated_output)

        update_progress(f"預估分析成本: ${estimated_cost:.4f}")

    # 驗證環境變數
    update_progress("檢查環境變數配置...")
    finnhub_key = os.getenv("FINNHUB_API_KEY")

    logger.info("環境變數檢查:")
    logger.info(f"  FINNHUB_API_KEY: {'已設定' if finnhub_key else '未設定'}")

    if not finnhub_key:
        logger.warning("FINNHUB_API_KEY 未設定，部分美股資料功能可能受限")

    update_progress("環境變數驗證通過")

    try:
        # 匯入必要的模組
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        from tradingagents.default_config import DEFAULT_CONFIG

        # 建立配置
        update_progress("配置分析參數...")
        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = llm_provider
        config["deep_think_llm"] = llm_model
        config["quick_think_llm"] = llm_model
        # 根據研究深度調整配置
        if research_depth == 1:  # 1級 - 快速分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            # 保持記憶功能啟用，因為記憶操作開銷很小但能顯著提升分析質量
            config["memory_enabled"] = True

            # 統一使用在線工具，避免離線工具的各種問題
            config["online_tools"] = True  # 所有市場都使用統一工具
            logger.info(f" [快速分析] {market_type}使用統一工具，確保資料來源正確和穩定性")
        elif research_depth == 2:  # 2級 - 基礎分析
            config["max_debate_rounds"] = 1
            config["max_risk_discuss_rounds"] = 1
            config["memory_enabled"] = True
            config["online_tools"] = True
        elif research_depth == 3:  # 3級 - 標準分析 (預設)
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

        # 根據 LLM 提供商設定 API 端點
        if llm_provider == "openai":
            config["backend_url"] = "https://api.openai.com/v1"
            logger.info(f" [OpenAI] 使用模型: {llm_model}")
        elif llm_provider == "anthropic":
            config["backend_url"] = "https://api.anthropic.com/"
            logger.info(f" [Anthropic] 使用模型: {llm_model}")

        # 修複路徑問題 - 優先使用環境變數配置
        # 資料目錄：優先使用環境變數，否則使用預設路徑
        if not config.get("data_dir") or config["data_dir"] == "./data":
            env_data_dir = os.getenv("TRADINGAGENTS_DATA_DIR")
            if env_data_dir:
                # 如果環境變數是相對路徑，相對於項目根目錄解析
                if not os.path.isabs(env_data_dir):
                    config["data_dir"] = str(project_root / env_data_dir)
                else:
                    config["data_dir"] = env_data_dir
            else:
                config["data_dir"] = str(project_root / "data")

        # 結果目錄：優先使用環境變數，否則使用預設路徑
        if not config.get("results_dir") or config["results_dir"] == "./results":
            env_results_dir = os.getenv("TRADINGAGENTS_RESULTS_DIR")
            if env_results_dir:
                # 如果環境變數是相對路徑，相對於項目根目錄解析
                if not os.path.isabs(env_results_dir):
                    config["results_dir"] = str(project_root / env_results_dir)
                else:
                    config["results_dir"] = env_results_dir
            else:
                config["results_dir"] = str(project_root / "results")

        # 快取目錄：優先使用環境變數，否則使用預設路徑
        if not config.get("data_cache_dir"):
            env_cache_dir = os.getenv("TRADINGAGENTS_CACHE_DIR")
            if env_cache_dir:
                # 如果環境變數是相對路徑，相對於項目根目錄解析
                if not os.path.isabs(env_cache_dir):
                    config["data_cache_dir"] = str(project_root / env_cache_dir)
                else:
                    config["data_cache_dir"] = env_cache_dir
            else:
                config["data_cache_dir"] = str(project_root / "tradingagents" / "dataflows" / "data_cache")

        # 確保目錄存在
        update_progress("建立必要的目錄...")
        os.makedirs(config["data_dir"], exist_ok=True)
        os.makedirs(config["results_dir"], exist_ok=True)
        os.makedirs(config["data_cache_dir"], exist_ok=True)

        logger.info("目錄配置:")
        logger.info(f"  - 資料目錄: {config['data_dir']}")
        logger.info(f"  - 結果目錄: {config['results_dir']}")
        logger.info(f"  - 快取目錄: {config['data_cache_dir']}")
        logger.info(f"  - 環境變數 TRADINGAGENTS_RESULTS_DIR: {os.getenv('TRADINGAGENTS_RESULTS_DIR', '未設定')}")

        logger.info(f"使用配置: {config}")
        logger.info(f"分析師列表: {analysts}")
        logger.info(f"股票代碼: {stock_symbol}")
        logger.info(f"分析日期: {analysis_date}")

        # 調整股票代碼格式
        logger.debug(" ===== 股票代碼格式化 =====")
        logger.debug(f" 原始股票代碼: '{stock_symbol}'")

        # 美股代碼轉為大寫
        formatted_symbol = stock_symbol.upper()
        logger.debug(f" 美股代碼轉大寫: '{stock_symbol}' -> '{formatted_symbol}'")
        update_progress(f"準備分析美股: {formatted_symbol}")

        logger.debug(f" 最終傳遞給分析引擎的股票代碼: '{formatted_symbol}'")

        # 初始化交易圖
        update_progress("初始化分析引擎...")
        graph = TradingAgentsGraph(analysts, config=config, debug=False)

        # 執行分析
        update_progress(f"開始分析 {formatted_symbol} 股票，這可能需要几分鐘時間...")
        logger.debug(" ===== 呼叫graph.propagate =====")
        logger.debug(" 傳遞給graph.propagate的參數:")
        logger.debug(f" symbol: '{formatted_symbol}'")
        logger.debug(f" date: '{analysis_date}'")

        state, decision = graph.propagate(formatted_symbol, analysis_date)

        # 除錯資訊
        logger.debug(f" 分析完成，decision類型: {type(decision)}")
        logger.debug(f" decision內容: {decision}")

        # 格式化結果
        update_progress("分析完成，正在整理結果...")

        # 提取風險評估資料
        risk_assessment = extract_risk_assessment(state)

        # 將風險評估新增到狀態中
        if risk_assessment:
            state['risk_assessment'] = risk_assessment

        # 記錄Token使用（實際使用量，這裡使用估算值）
        if TOKEN_TRACKING_ENABLED:
            # 在實際應用中，這些值應該從LLM回應中取得
            # 這裡使用基於分析師數量和研究深度的估算
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
                update_progress(f"記錄使用成本: ${usage_record.cost:.4f}")

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

        # 計算總成本（如果有Token追蹤）
        total_cost = 0.0
        if TOKEN_TRACKING_ENABLED:
            try:
                total_cost = token_tracker.get_session_cost(session_id)
            except Exception:
                logger.debug("Token 成本查詢失敗，使用預設值 0")

        logger_manager.log_analysis_complete(
            logger, stock_symbol, "comprehensive_analysis", session_id,
            analysis_duration, total_cost
        )

        logger.info(f" [分析完成] 股票分析成功完成",
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
            update_progress("正在保存分析報告...")
            from .report_exporter import save_analysis_report, save_modular_reports_to_results_dir
            
            # 1. 保存分模組報告到本地目錄
            logger.info(" [本地保存] 開始保存分模組報告到本地目錄")
            local_files = save_modular_reports_to_results_dir(results, stock_symbol)
            if local_files:
                logger.info(f" [本地保存] 已保存 {len(local_files)} 個本地報告檔案")
                for module, path in local_files.items():
                    logger.info(f"  - {module}: {path}")
            else:
                logger.warning(" [本地保存] 本地報告檔案保存失敗")
            
            # 2. 保存分析報告到MongoDB
            logger.info(" [MongoDB保存] 開始保存分析報告到MongoDB")
            save_success = save_analysis_report(
                stock_symbol=stock_symbol,
                analysis_results=results
            )
            
            if save_success:
                logger.info(" [MongoDB保存] 分析報告已成功保存到MongoDB")
                update_progress("分析報告已保存到資料庫和本地檔案")
            else:
                logger.warning(" [MongoDB保存] MongoDB報告保存失敗")
                if local_files:
                    update_progress("本地報告已保存，但資料庫保存失敗")
                else:
                    update_progress("報告保存失敗，但分析已完成")
                
        except Exception as save_error:
            logger.error(f" [報告保存] 保存分析報告時發生錯誤: {str(save_error)}")
            update_progress("報告保存出錯，但分析已完成")

        update_progress("分析成功完成！")
        return results

    except Exception as e:
        # 記錄分析失敗的詳細日誌
        analysis_duration = time.time() - analysis_start_time

        logger_manager.log_module_error(
            logger, "comprehensive_analysis", stock_symbol, session_id,
            analysis_duration, str(e)
        )

        logger.error(f" [分析失敗] 股票分析執行失敗",
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

        # 如果真實分析失敗，返回錯誤訊息而不是誤導性演示資料
        return {
            'stock_symbol': stock_symbol,
            'analysis_date': analysis_date,
            'analysts': analysts,
            'research_depth': research_depth,
            'llm_provider': llm_provider,
            'llm_model': llm_model,
            'state': {},  # 空狀態，將顯示占位符
            'decision': {},  # 空決策
            'success': False,
            'error': str(e),
            'is_demo': False,
            'error_reason': f"分析失敗: {str(e)}"
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

    # 提取關鍵資訊
    # decision 可能是字串（如 "BUY", "SELL", "HOLD"）或字典
    if isinstance(decision, str):
        # 將英文投資建議轉換為中文
        action_translation = {
            'BUY': '買入',
            'SELL': '賣出',
            'HOLD': '持有',
            'buy': '買入',
            'sell': '賣出',
            'hold': '持有'
        }
        action = action_translation.get(decision.strip(), decision.strip())

        formatted_decision = {
            'action': action,
            'confidence': 0.7,  # 預設定信度
            'risk_score': 0.3,  # 預設風險分數
            'target_price': None,  # 字串格式沒有目標價格
            'reasoning': f'基於多維度分析，建議{decision.strip().upper()}'
        }
    elif isinstance(decision, dict):
        # 處理目標價格 - 確保正確提取數值
        target_price = decision.get('target_price')
        if target_price is not None and target_price != 'N/A':
            try:
                # 嘗試轉換為浮點數
                if isinstance(target_price, str):
                    # 移除貨幣符號和空格
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

        # 將英文投資建議轉換為中文
        action_translation = {
            'BUY': '買入',
            'SELL': '賣出',
            'HOLD': '持有',
            'buy': '買入',
            'sell': '賣出',
            'hold': '持有'
        }
        action = decision.get('action', '持有')
        chinese_action = action_translation.get(action, action)

        formatted_decision = {
            'action': chinese_action,
            'confidence': decision.get('confidence', 0.5),
            'risk_score': decision.get('risk_score', 0.3),
            'target_price': target_price,
            'reasoning': decision.get('reasoning', '暫無分析推理')
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
    
    # 格式化狀態資訊
    formatted_state = {}
    
    # 處理各個分析模組的結果 - 包含完整的智慧體團隊分析
    analysis_keys = [
        'market_report',
        'fundamentals_report',
        'sentiment_report',
        'news_report',
        'risk_assessment',
        'investment_plan',
        # 新增缺失的團隊決策資料，確保與CLI端一致
        'investment_debate_state',  # 研究團隊辯論（多頭/空頭研究員）
        'trader_investment_plan',   # 交易團隊計劃
        'risk_debate_state',        # 風險管理團隊決策
        'final_trade_decision'      # 最終交易決策
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
        # 將配置資訊放在頂層，供前端直接存取
        'analysis_date': results['analysis_date'],
        'analysts': results['analysts'],
        'research_depth': results['research_depth'],
        'llm_provider': results.get('llm_provider', 'openai'),
        'llm_model': results['llm_model'],
        'metadata': {
            'analysis_date': results['analysis_date'],
            'analysts': results['analysts'],
            'research_depth': results['research_depth'],
            'llm_provider': results.get('llm_provider', 'openai'),
            'llm_model': results['llm_model']
        }
    }

def validate_analysis_params(stock_symbol, analysis_date, analysts, research_depth):
    """驗證分析參數"""

    errors = []

    # 驗證股票代碼
    if not stock_symbol or len(stock_symbol.strip()) == 0:
        errors.append("股票代碼不能為空")
    elif len(stock_symbol.strip()) > 10:
        errors.append("股票代碼長度不能超過10個字元")
    else:
        # 驗證美股代碼格式
        symbol = stock_symbol.strip()
        import re
        if not re.match(r'^[A-Z]{1,5}$', symbol.upper()):
            errors.append("美股代碼格式錯誤，應為1-5位字母（如：AAPL）")
    
    # 驗證分析師列表
    if not analysts or len(analysts) == 0:
        errors.append("必須至少選擇一個分析師")
    
    valid_analysts = ['market', 'social', 'news', 'fundamentals']
    invalid_analysts = [a for a in analysts if a not in valid_analysts]
    if invalid_analysts:
        errors.append(f"無效的分析師類型: {', '.join(invalid_analysts)}")
    
    # 驗證研究深度
    if not isinstance(research_depth, int) or research_depth < 1 or research_depth > 5:
        errors.append("研究深度必須是1-5之間的整數")
    
    # 驗證分析日期
    try:
        from datetime import datetime
        datetime.strptime(analysis_date, '%Y-%m-%d')
    except ValueError:
        errors.append("分析日期格式無效，應為YYYY-MM-DD格式")
    
    return len(errors) == 0, errors


