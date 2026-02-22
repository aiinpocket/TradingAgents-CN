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
    'status.api_label': 'API 伺服器狀態',

    // 分析頁面
    'analysis.title': '股票分析',
    'analysis.desc': '輸入美股代碼，啟動多代理協作分析。',
    'analysis.symbol': '股票代碼',
    'analysis.symbol_placeholder': 'AAPL',
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
    'analysis.in_progress': '進行中',
    'analysis.waiting': '等待分析引擎啟動...',
    'analysis.time_hint': '分析通常需要 2-8 分鐘，取決於研究深度。',
    'analysis.cancel': '取消',
    'analysis.elapsed': '已用時',
    'analysis.new': '新分析',
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
    'depth.time.4': '約 5-8 分鐘',
    'depth.time.5': '約 8-15 分鐘',

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

    // API 密鑰提示
    'api.not_configured': 'API 密鑰未配置',
    'api.config_hint': '請在伺服器端的 .env 檔案中配置至少一個 LLM 提供商的密鑰，然後重啟應用。',

    // 歷史頁面
    'history.title': '分析歷史',
    'history.refresh': '重新整理',
    'history.empty': '尚無分析記錄',
    'history.col_symbol': '代碼',
    'history.col_date': '日期',
    'history.col_provider': '提供商',
    'history.col_status': '狀態',
    'history.status_pending': '待處理',
    'history.status_running': '進行中',
    'history.status_completed': '已完成',
    'history.status_failed': '失敗',

    // 熱門特區
    'trending.title': '市場動態',
    'trending.subtitle': '美股即時行情與熱門話題',
    'trending.indices': '主要指數',
    'trending.gainers': '漲幅排行',
    'trending.losers': '跌幅排行',
    'trending.news': '市場新聞',
    'trending.loading': '載入中...',
    'trending.updated': '最後更新',
    'trending.analyze': '分析',
    'trending.view_more': '查看更多',
    'trending.no_data': '暫無資料',
    'trending.error': '載入失敗，請稍後重試',
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
    'trending.rank': '#',

    // 頁尾
    'footer.version': 'v0.2.9',

    // 主題
    'theme.to_dark': '切換深色模式',
    'theme.to_light': '切換淺色模式',

    // 通知
    'analysis.completed': '分析完成',
    'analysis.failed': '分析失敗',

    // 無障礙
    'a11y.analyze_stock': '分析股票',
    'a11y.switch_lang': '切換至英文',

    // 通用
    'common.no_data': '暫無資料',
    'common.error': '發生錯誤',
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
    'status.api_label': 'API Server Status',

    // Analysis page
    'analysis.title': 'Stock Analysis',
    'analysis.desc': 'Enter a US stock ticker to start multi-agent analysis.',
    'analysis.symbol': 'Ticker',
    'analysis.symbol_placeholder': 'AAPL',
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
    'analysis.in_progress': 'In Progress',
    'analysis.waiting': 'Waiting for analysis engine...',
    'analysis.time_hint': 'Analysis usually takes 2-8 minutes depending on depth.',
    'analysis.cancel': 'Cancel',
    'analysis.elapsed': 'Elapsed',
    'analysis.new': 'New Analysis',
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
    'depth.time.4': '~5-8 min',
    'depth.time.5': '~8-15 min',

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

    // API key notice
    'api.not_configured': 'API Key Not Configured',
    'api.config_hint': 'Please configure at least one LLM provider API key in the server .env file, then restart the app.',

    // History page
    'history.title': 'Analysis History',
    'history.refresh': 'Refresh',
    'history.empty': 'No analysis records yet',
    'history.col_symbol': 'Ticker',
    'history.col_date': 'Date',
    'history.col_provider': 'Provider',
    'history.col_status': 'Status',
    'history.status_pending': 'Pending',
    'history.status_running': 'Running',
    'history.status_completed': 'Completed',
    'history.status_failed': 'Failed',

    // Trending
    'trending.title': 'Market Overview',
    'trending.subtitle': 'Real-time US stock market data and trending topics',
    'trending.indices': 'Major Indices',
    'trending.gainers': 'Top Gainers',
    'trending.losers': 'Top Losers',
    'trending.news': 'Market News',
    'trending.loading': 'Loading...',
    'trending.updated': 'Last updated',
    'trending.analyze': 'Analyze',
    'trending.view_more': 'View more',
    'trending.no_data': 'No data available',
    'trending.error': 'Failed to load, please try again later',
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
    'trending.rank': '#',

    // Footer
    'footer.version': 'v0.2.9',

    // Theme
    'theme.to_dark': 'Switch to dark mode',
    'theme.to_light': 'Switch to light mode',

    // Notifications
    'analysis.completed': 'analysis completed',
    'analysis.failed': 'analysis failed',

    // Accessibility
    'a11y.analyze_stock': 'Analyze stock',
    'a11y.switch_lang': 'Switch to Chinese',

    // Common
    'common.no_data': 'No data',
    'common.error': 'Error occurred',
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
