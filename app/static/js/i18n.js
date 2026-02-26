/**
 * TradingAgents 國際化（i18n）模組
 * 支援繁體中文（zh-TW）與英文（en）
 */

const I18N_MESSAGES = {
  'zh-TW': {
    // 導覽列
    'nav.analysis': '分析',
    'nav.trending': '熱門',
    'nav.history': '歷史',
    'nav.brand': 'TradingAgents',

    // 狀態
    'status.online': '已連線',
    'status.offline': '離線',

    // 分析頁面
    'analysis.title': '股票分析',
    'analysis.desc': '輸入美股代碼，啟動多代理協作分析。',
    'analysis.symbol': '股票代碼',
    'analysis.date': '分析日期',
    'analysis.provider': 'LLM 提供商',
    'analysis.model': '模型',
    'analysis.depth': '研究深度',
    'analysis.modules': '分析模組',
    'analysis.module_market': '市場技術',
    'analysis.module_fundamentals': '基本面',
    'analysis.module_news': '新聞輿情',
    'analysis.module_social': '社群情緒',
    'analysis.start': '開始分析',
    'analysis.submitting': '提交中',
    'analysis.submit_hint': 'Ctrl+Enter 快速提交',
    'analysis.running': '分析進行中',
    'analysis.reconnecting': '重新連線...',
    'analysis.polling_fallback': '即時串流已斷線，已切換為輪詢模式。',
    'analysis.retry': '重試',
    'analysis.in_progress': '進行中',
    'analysis.waiting': '等待分析引擎啟動...',
    'analysis.time_hint': '分析通常需要 1-10 分鐘，取決於研究深度。',
    'analysis.cancel': '取消',
    'analysis.elapsed': '已用時',
    'analysis.progress_log': '分析進度日誌',
    'analysis.new': '新分析',
    'analysis.from_cache': '快取結果',
    'analysis.export': '匯出',
    'analysis.report': '分析報告',

    // 深度等級
    'depth.1': '快速',
    'depth.2': '基礎',
    'depth.3': '標準',
    'depth.4': '深度',
    'depth.5': '全面',
    'depth.time.1': '約 1-2 分鐘',
    'depth.time.2': '約 2-3 分鐘',
    'depth.time.3': '約 3-5 分鐘',
    'depth.time.4': '約 3-6 分鐘',
    'depth.time.5': '約 5-10 分鐘',

    // 分析流程
    'workflow.title': '多代理協作分析流程',
    'workflow.step1_title': '市場技術分析',
    'workflow.step1_desc': '分析價格走勢、技術指標與交易量模式',
    'workflow.step2_title': '基本面研究',
    'workflow.step2_desc': '評估財報數據、營收成長與估值指標',
    'workflow.step3_title': '新聞與輿情',
    'workflow.step3_desc': '掃描即時新聞、社群媒體與分析師評論',
    'workflow.step4_title': '多空辯論',
    'workflow.step4_desc': '多頭與空頭研究員進行觀點交鋒',
    'workflow.step5_title': '風險評估',
    'workflow.step5_desc': '穩健型、積極型與中立型觀點綜合評估',
    'workflow.step6_title': '最終決策',
    'workflow.step6_desc': '綜合所有分析產出投資建議與信心度',

    // 結果
    'result.suggestion': '建議',
    'result.confidence': '信心度',
    'result.risk': '風險',
    'result.target_price': '目標價',
    'result.tab_market': '市場技術',
    'result.tab_fundamentals': '基本面',
    'result.tab_news': '新聞輿情',
    'result.tab_sentiment': '社群情緒',
    'result.tab_risk': '風險評估',
    'result.tab_debate': '投資辯論',
    'result.disclaimer': '分析結果僅供研究參考，不構成投資建議。請結合個人風險承受能力做出投資決策。',

    // 個股快照
    'context.market_cap': '市值',
    'context.volume': '成交量',
    'context.pe_ratio': '本益比',
    'context.week52': '52 週區間',
    'context.news_title': '近期新聞',
    'context.beta': 'Beta',
    'context.snapshot': '個股快照',
    'context.fetch_failed': '無法載入個股行情，請稍後再試',

    // API 密鑰提示
    'api.not_configured': 'API 密鑰未配置',
    'api.config_hint': '請在伺服器端的 .env 檔案中配置至少一個 LLM 提供商的密鑰，然後重啟應用。',

    // 歷史頁面
    'history.title': '分析歷史',
    'history.refresh': '重新整理',
    'history.empty': '尚無分析記錄',
    'history.empty_desc': '使用 AI 多代理系統分析美股，完成後結果會顯示在這裡。',
    'history.go_analyze': '前往分析',
    'history.col_symbol': '代碼',
    'history.col_date': '日期',
    'history.col_provider': '提供商',
    'history.col_status': '狀態',
    'history.status_pending': '待處理',
    'history.status_running': '進行中',
    'history.status_completed': '已完成',
    'history.status_failed': '失敗',

    // 熱門特區
    'trending.refresh_hint': '每 5 分鐘自動更新',
    'time.just_now': '剛剛更新',
    'time.min_ago': ' 分鐘前',
    'time.hour_ago': ' 小時前',
    'trending.indices': '主要指數',
    'trending.gainers': '漲幅排行',
    'trending.losers': '跌幅排行',
    'trending.news': '市場新聞',
    'trending.updated': '最後更新',
    'trending.analyze': '分析',
    'trending.no_data': '暫無資料',
    'trending.load_error': '市場資料載入失敗，請稍後再試',
    'trending.retry': '重新載入',
    'trending.ai_title': 'AI 趨勢分析',
    'trending.ai_desc': '基於宏觀經濟、國際趨勢與市場新聞的每日綜合分析',
    'trending.ai_loading': '正在生成 AI 分析...',
    'trending.ai_no_key': 'AI 分析功能需要配置 LLM API 密鑰（OPENAI_API_KEY 或 ANTHROPIC_API_KEY）。',
    'trending.ai_refresh': '重新分析',
    'trending.ai_powered_by': '由 AI 生成',
    'trending.ai_error': 'AI 分析生成失敗，請稍後重試',
    'trending.market_pulse': '市場脈動',
    'trending.market_up': '偏多',
    'trending.market_down': '偏空',
    'trending.market_mixed': '震盪',
    'trending.quick_analyze': '快速分析',
    'trending.sectors': '板塊表現',
    'trending.sectors_desc': 'S&P 500 各板塊 ETF 當日漲跌',

    // 追蹤清單
    'watchlist.title': '我的追蹤',
    'watchlist.add': '加入追蹤',
    'watchlist.remove': '移除追蹤',
    'watchlist.clear': '清除全部',
    'watchlist.clear_confirm': '確定清除所有追蹤？',

    // 頁面標題
    'meta.title': 'TradingAgents - AI 股票分析',

    // 頁尾
    'footer.version': 'v0.4.5',
    'footer.open_source': '開源專案',

    // 主題
    'theme.to_dark': '切換深色模式',
    'theme.to_light': '切換淺色模式',

    // 翻譯進度
    'analysis.translating': '正在生成英文版本...',

    // 通知
    'analysis.completed': '分析完成',
    'analysis.en_unavailable': '英文版本暫時不可用，以下顯示中文分析結果。',
    'analysis.failed': '分析失敗',

    // 錯誤訊息
    'error.invalid_symbol': '請輸入有效的美股代碼（1-5 個英文字母）',
    'error.start_failed': '無法啟動分析',
    'error.analysis_failed': '分析失敗',
    'error.task_expired': '分析任務已過期，請重新開始',
    'error.connection_timeout': '連線逾時，請檢查網路連線',

    // 辯論標籤
    'debate.bull_label': '多頭研究員',
    'debate.bear_label': '空頭研究員',
    'debate.judge_label': '研究經理決議',

    // 無障礙
    'a11y.analyze_stock': '分析股票',
    'a11y.view_analysis': '查看分析結果',
    'a11y.switch_lang': '切換至英文',
    'a11y.main_nav': '主選單',
    'a11y.loading': '載入中',
    'a11y.skip_to_content': '跳至主要內容',
    'a11y.history_table': '分析歷史記錄',
    'a11y.refresh_ai': '重新整理 AI 趨勢分析',
    'a11y.export_result': '匯出分析結果',
    'a11y.refresh_history': '重新整理歷史記錄',

    // 通用
    'common.no_data': '暫無資料',
    'common.close': '關閉',
    'common.retry': '重試',
  },

  'en': {
    // Navigation
    'nav.analysis': 'Analysis',
    'nav.trending': 'Trending',
    'nav.history': 'History',
    'nav.brand': 'TradingAgents',

    // Status
    'status.online': 'Online',
    'status.offline': 'Offline',

    // Analysis page
    'analysis.title': 'Stock Analysis',
    'analysis.desc': 'Enter a US stock ticker to start multi-agent analysis.',
    'analysis.symbol': 'Ticker',
    'analysis.date': 'Date',
    'analysis.provider': 'LLM Provider',
    'analysis.model': 'Model',
    'analysis.depth': 'Depth',
    'analysis.modules': 'Modules',
    'analysis.module_market': 'Technical',
    'analysis.module_fundamentals': 'Fundamentals',
    'analysis.module_news': 'News',
    'analysis.module_social': 'Sentiment',
    'analysis.start': 'Start Analysis',
    'analysis.submitting': 'Submitting',
    'analysis.submit_hint': 'Ctrl+Enter to submit',
    'analysis.running': 'Analysis in Progress',
    'analysis.reconnecting': 'Reconnecting...',
    'analysis.polling_fallback': 'Live stream disconnected, switched to polling mode.',
    'analysis.retry': 'Retry',
    'analysis.in_progress': 'In Progress',
    'analysis.waiting': 'Waiting for analysis engine...',
    'analysis.time_hint': 'Analysis usually takes 1-10 minutes depending on depth.',
    'analysis.cancel': 'Cancel',
    'analysis.elapsed': 'Elapsed',
    'analysis.progress_log': 'Analysis progress log',
    'analysis.new': 'New Analysis',
    'analysis.from_cache': 'Cached',
    'analysis.export': 'Export',
    'analysis.report': 'Report',

    // Depth levels
    'depth.1': 'Quick',
    'depth.2': 'Basic',
    'depth.3': 'Standard',
    'depth.4': 'Deep',
    'depth.5': 'Full',
    'depth.time.1': '~1-2 min',
    'depth.time.2': '~2-3 min',
    'depth.time.3': '~3-5 min',
    'depth.time.4': '~3-6 min',
    'depth.time.5': '~5-10 min',

    // Workflow
    'workflow.title': 'Multi-Agent Analysis Pipeline',
    'workflow.step1_title': 'Technical Analysis',
    'workflow.step1_desc': 'Analyze price trends, indicators, and volume patterns',
    'workflow.step2_title': 'Fundamentals',
    'workflow.step2_desc': 'Evaluate earnings, revenue growth, and valuation metrics',
    'workflow.step3_title': 'News & Sentiment',
    'workflow.step3_desc': 'Scan real-time news, social media, and analyst opinions',
    'workflow.step4_title': 'Bull vs Bear Debate',
    'workflow.step4_desc': 'Bull and bear researchers debate opposing viewpoints',
    'workflow.step5_title': 'Risk Assessment',
    'workflow.step5_desc': 'Conservative, aggressive, and neutral perspectives combined',
    'workflow.step6_title': 'Final Decision',
    'workflow.step6_desc': 'Synthesize all analyses into recommendation with confidence',

    // Results
    'result.suggestion': 'Suggestion',
    'result.confidence': 'Confidence',
    'result.risk': 'Risk',
    'result.target_price': 'Target',
    'result.tab_market': 'Technical',
    'result.tab_fundamentals': 'Fundamentals',
    'result.tab_news': 'News',
    'result.tab_sentiment': 'Sentiment',
    'result.tab_risk': 'Risk',
    'result.tab_debate': 'Debate',
    'result.disclaimer': 'Analysis results are for research only and do not constitute investment advice. Please make investment decisions based on your own risk tolerance.',

    // Stock context
    'context.market_cap': 'Market Cap',
    'context.volume': 'Volume',
    'context.pe_ratio': 'P/E Ratio',
    'context.week52': '52W Range',
    'context.news_title': 'Recent News',
    'context.beta': 'Beta',
    'context.snapshot': 'Snapshot',
    'context.fetch_failed': 'Failed to load stock snapshot. Please try again.',

    // API key notice
    'api.not_configured': 'API Key Not Configured',
    'api.config_hint': 'Please configure at least one LLM provider API key in the server .env file, then restart the app.',

    // History page
    'history.title': 'Analysis History',
    'history.refresh': 'Refresh',
    'history.empty': 'No analysis records yet',
    'history.empty_desc': 'Analyze US stocks with AI multi-agent system. Results will appear here after completion.',
    'history.go_analyze': 'Go to Analysis',
    'history.col_symbol': 'Ticker',
    'history.col_date': 'Date',
    'history.col_provider': 'Provider',
    'history.col_status': 'Status',
    'history.status_pending': 'Pending',
    'history.status_running': 'Running',
    'history.status_completed': 'Completed',
    'history.status_failed': 'Failed',

    // Trending
    'trending.refresh_hint': 'Auto-refresh every 5 min',
    'time.just_now': 'Just updated',
    'time.min_ago': ' min ago',
    'time.hour_ago': 'h ago',
    'trending.indices': 'Major Indices',
    'trending.gainers': 'Top Gainers',
    'trending.losers': 'Top Losers',
    'trending.news': 'Market News',
    'trending.updated': 'Last updated',
    'trending.analyze': 'Analyze',
    'trending.no_data': 'No data available',
    'trending.load_error': 'Failed to load market data. Please try again later.',
    'trending.retry': 'Reload',
    'trending.ai_title': 'AI Trend Analysis',
    'trending.ai_desc': 'Daily comprehensive analysis based on macro economics, global trends, and market news',
    'trending.ai_loading': 'Generating AI analysis...',
    'trending.ai_no_key': 'AI analysis requires an LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY).',
    'trending.ai_refresh': 'Re-analyze',
    'trending.ai_powered_by': 'AI Generated',
    'trending.ai_error': 'Failed to generate AI analysis, please try again later',
    'trending.market_pulse': 'Market Pulse',
    'trending.market_up': 'Bullish',
    'trending.market_down': 'Bearish',
    'trending.market_mixed': 'Mixed',
    'trending.quick_analyze': 'Analyze',
    'trending.sectors': 'Sector Performance',
    'trending.sectors_desc': 'S&P 500 sector ETF daily changes',

    // Watchlist
    'watchlist.title': 'My Watchlist',
    'watchlist.add': 'Add to watchlist',
    'watchlist.remove': 'Remove from watchlist',
    'watchlist.clear': 'Clear all',
    'watchlist.clear_confirm': 'Clear all tracked stocks?',

    // Page title
    'meta.title': 'TradingAgents - AI Stock Analysis',

    // Footer
    'footer.version': 'v0.4.5',
    'footer.open_source': 'Open Source',

    // Theme
    'theme.to_dark': 'Switch to dark mode',
    'theme.to_light': 'Switch to light mode',

    // Translation progress
    'analysis.translating': 'Generating English version...',

    // Notifications
    'analysis.completed': 'analysis completed',
    'analysis.en_unavailable': 'English version is temporarily unavailable. Showing Chinese analysis results.',
    'analysis.failed': 'analysis failed',

    // Error messages
    'error.invalid_symbol': 'Please enter a valid US stock ticker (1-5 letters)',
    'error.start_failed': 'Failed to start analysis',
    'error.analysis_failed': 'Analysis failed',
    'error.task_expired': 'Analysis task expired, please restart',
    'error.connection_timeout': 'Connection timeout, please check your network',

    // Debate labels
    'debate.bull_label': 'Bull Researcher',
    'debate.bear_label': 'Bear Researcher',
    'debate.judge_label': 'Research Manager',

    // Accessibility
    'a11y.analyze_stock': 'Analyze stock',
    'a11y.view_analysis': 'View analysis for',
    'a11y.switch_lang': 'Switch to Chinese',
    'a11y.main_nav': 'Main navigation',
    'a11y.loading': 'Loading',
    'a11y.skip_to_content': 'Skip to content',
    'a11y.history_table': 'Analysis history',
    'a11y.refresh_ai': 'Refresh AI trend analysis',
    'a11y.export_result': 'Export analysis result',
    'a11y.refresh_history': 'Refresh history',

    // Common
    'common.no_data': 'No data',
    'common.close': 'Close',
    'common.retry': 'Retry',
  }
};

/**
 * 取得翻譯文字
 * @param {string} key - 翻譯鍵
 * @param {string} [lang] - 語言代碼，預設從 localStorage 讀取
 * @returns {string} 翻譯結果
 */
function i18n(key, lang) {
  const currentLang = lang || localStorage.getItem('lang') || 'zh-TW';
  const messages = I18N_MESSAGES[currentLang] || I18N_MESSAGES['zh-TW'];
  return messages[key] || key;
}

/**
 * 取得當前語言
 * @returns {string}
 */
function getCurrentLang() {
  const saved = localStorage.getItem('lang');
  // 驗證語言代碼，防止注入
  if (saved === 'zh-TW' || saved === 'en') return saved;
  return 'zh-TW';
}

/**
 * 設定語言
 * @param {string} lang
 */
function setLang(lang) {
  if (lang !== 'zh-TW' && lang !== 'en') return;
  localStorage.setItem('lang', lang);
  document.documentElement.setAttribute('lang', lang === 'zh-TW' ? 'zh-Hant' : 'en');
}
