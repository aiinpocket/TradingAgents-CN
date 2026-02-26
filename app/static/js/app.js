/**
 * TradingAgents 前端應用
 * 支援 i18n 國際化、熱門特區、股票分析
 */

// 配置常數
const CONFIG = {
  SSE_MAX_RETRIES: 3,
  SSE_BACKOFF_BASE_MS: 1000,
  SSE_BACKOFF_MAX_MS: 8000,
  POLL_MAX_RETRIES: 120, // 120 x 15s = 30 分鐘，與後端超時對齊
  POLL_BACKOFF_BASE_MS: 3000,
  POLL_BACKOFF_MAX_MS: 15000,
  PROGRESS_STEP_PERCENT: 8,
  PROGRESS_MAX_PERCENT: 95,
  TRENDING_REFRESH_MS: 300000, // 5 分鐘自動重新整理（與後端同步）
};

// 全域錯誤處理
window.onerror = function(msg, src, line) {
  console.error('JS error:', msg, src, line);
  return false;
};
window.addEventListener('unhandledrejection', function(e) {
  console.error('Unhandled promise:', e.reason);
});

function tradingApp() {
  return {
    // 狀態
    darkMode: false,
    lang: 'zh-TW',
    tab: 'trending',
    apiReady: false,
    analysisRunning: false,
    showResults: false,
    submitting: false,
    formError: null,
    reportTab: 'market',
    connectionRetries: 0,

    // 表單
    form: {
      symbol: '',
      date: new Date().toISOString().split('T')[0],
      depth: 3,
      provider: 'openai',
      model: 'o4-mini',
      analysts: ['market', 'social', 'news', 'fundamentals'],
    },

    // 資料
    availableProviders: [],
    allModels: {},
    currentModels: [],
    progressMessages: [],
    progressPercent: 0,
    result: null,
    cachedResult: false,
    historyList: [],
    configStatus: null,
    analysisId: null,
    eventSource: null,
    startTime: null,
    pollRetryCount: 0,
    elapsedText: '',
    _elapsedTimer: null,
    _scrollPending: false,

    // 熱門特區
    trendingData: { indices: [], movers: { gainers: [], losers: [] }, news: [] },
    trendingLoading: true,
    trendingError: false,
    _trendingTimer: null,

    // AI 趨勢分析
    aiAnalysis: { available: null, content: '', updated_at: '', provider: '' },
    aiAnalysisLoading: false,

    // 股票預覽快取（避免模板中重複計算）
    stockPreview: null,
    // 市場情緒快取（避免模板中 getMarketSentiment() 被重複呼叫）
    _sentiment: { label: '', cls: '', arrow: '' },
    // 共用股票查詢表（trendingData 變化時由 $watch 更新）
    _stockMap: {},

    // 個股快照
    stockContext: null,
    stockContextLoading: false,
    // 前端個股快照快取（symbol -> {data, ts}），TTL 5 分鐘，避免重複請求
    _ctxCache: {},
    _ctxPending: {},  // 正在進行的請求去重（symbol -> Promise）

    // 追蹤清單（localStorage 持久化）
    watchlist: [],

    get canSubmit() {
      return this.apiReady &&
             this.form.symbol.length > 0 &&
             this.form.analysts.length > 0 &&
             !this.submitting;
    },

    // i18n 翻譯函式
    t(key) {
      return i18n(key, this.lang);
    },

    async init() {
      // 載入語言偏好
      this.lang = getCurrentLang();
      document.documentElement.setAttribute('lang', this.lang === 'zh-TW' ? 'zh-Hant' : 'en');

      // 載入暗色模式偏好
      const saved = localStorage.getItem('theme');
      const validTheme = (saved === 'dark' || saved === 'light') ? saved : null;
      this.darkMode = validTheme === 'dark' || (!validTheme && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (this.darkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
        const meta = document.getElementById('theme-color-meta');
        if (meta) meta.content = '#161b22';
      }

      // 載入追蹤清單
      this._loadWatchlist();

      // 平行呼叫健康檢查與模型清單以縮短啟動時間
      await Promise.all([this.checkHealth(), this.loadModels()]);
      this.form.date = new Date().toISOString().split('T')[0];

      // 股票查詢表快取：trendingData 變化時重建一次，供 _computeStockPreview / getWatchlistStocks 共用
      this.$watch('trendingData', () => {
        this._rebuildStockMap();
        this.stockPreview = this._computeStockPreview();
        this._sentiment = this._computeSentiment();
      });
      this.$watch('form.symbol', () => { this.stockPreview = this._computeStockPreview(); });
      // 切換到分析 tab 時更新日期上限，避免長時間開啟頁面導致日期過時
      this.$watch('tab', (val) => {
        if (val === 'analysis') {
          const today = new Date().toISOString().split('T')[0];
          if (this.form.date > today) this.form.date = today;
        }
      });

      // 瀏覽器離線/上線事件監聽，即時更新連線狀態
      window.addEventListener('offline', () => { this.apiReady = false; });
      window.addEventListener('online', () => this.checkHealth());

      // 根據語言設定頁面標題
      document.title = this.t('meta.title');

      // SSR 預渲染：後端已將快取的趨勢資料注入 HTML，直接使用以消除 CLS
      const ssrEl = document.getElementById('ssr-trending');
      if (ssrEl) {
        try {
          const ssrData = JSON.parse(ssrEl.textContent);
          if (ssrData && ssrData.indices) {
            this.trendingData = ssrData;
            this.trendingLoading = false;
            this._trendingLoaded = true;
            this._rebuildStockMap();
            // 非同步載入 AI 分析（不阻塞渲染）
            this.loadAiAnalysis();
            // 排程下次自動重新整理（資料已存在，無需立即 fetch）
            this._trendingTimer = setTimeout(() => {
              if (this.tab === 'trending') this.loadTrending();
            }, CONFIG.TRENDING_REFRESH_MS);
          }
        } catch (e) {
          console.error('SSR trending data parse error:', e);
        }
      }

      // 無 SSR 資料時走原始 API 載入路徑
      if (this.trendingLoading) {
        this.loadTrending();
      }

      // 頁面可見性變更：隱藏時暫停重新整理，恢復時立即更新
      document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
          if (this._trendingTimer) {
            clearTimeout(this._trendingTimer);
            this._trendingTimer = null;
          }
        } else if (this.tab === 'trending') {
          this.loadTrending();
        }
      });

      // 頁面卸載時清理 EventSource，並在分析進行中顯示警告
      window.addEventListener('beforeunload', (e) => {
        if (this.eventSource) {
          this.eventSource.close();
          this.eventSource = null;
        }
        if (this.analysisRunning) {
          e.preventDefault();
          e.returnValue = '';
        }
      });
    },

    toggleTheme() {
      this.darkMode = !this.darkMode;
      const meta = document.getElementById('theme-color-meta');
      if (this.darkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        if (meta) meta.content = '#161b22';
      } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        if (meta) meta.content = '#0052cc';
      }
    },

    toggleLang() {
      this.lang = this.lang === 'zh-TW' ? 'en' : 'zh-TW';
      setLang(this.lang);
      // 同步 html lang 屬性（無障礙 + SEO）
      document.documentElement.setAttribute('lang', this.lang === 'zh-TW' ? 'zh-Hant' : 'en');
      // 同步頁面標題語言
      document.title = this.t('meta.title');
      // 情緒標籤依賴語言，需重新計算
      this._sentiment = this._computeSentiment();
      // 切換語言後先清空 AI 分析（避免短暫顯示舊語言內容），再重新載入
      if (this.tab === 'trending') {
        this.aiAnalysis = { available: null, content: '', updated_at: '', provider: '' };
        this.loadAiAnalysis(true);
      }
    },

    async checkHealth() {
      try {
        const res = await fetch('/health');
        this.apiReady = res.ok;
      } catch {
        this.apiReady = false;
      }
      // 定期健康檢查：離線時 15 秒、上線時 60 秒
      if (this._healthTimer) clearTimeout(this._healthTimer);
      const interval = this.apiReady ? 60000 : 15000;
      this._healthTimer = setTimeout(() => this.checkHealth(), interval);
    },

    async loadModels() {
      try {
        const res = await fetch('/api/config/models');
        if (!res.ok) return;
        const data = await res.json();
        this.allModels = data.models || {};
        this.availableProviders = Object.keys(this.allModels);

        if (this.availableProviders.length > 0) {
          if (!this.availableProviders.includes(this.form.provider)) {
            this.form.provider = this.availableProviders[0];
          }
          this.updateModelOptions();
        }
      } catch (e) {
        console.error('Failed to load models:', e);
      }
    },

    updateModelOptions() {
      this.currentModels = this.allModels[this.form.provider] || [];
      if (this.currentModels.length > 0) {
        const hasModel = this.currentModels.some(m => m.id === this.form.model);
        if (!hasModel) {
          this.form.model = this.currentModels[0].id;
        }
      }
    },

    // 熱門特區
    async loadTrending() {
      // trendingLoading 初始值為 true（防止 CLS），首次載入不擋
      if (this.trendingLoading && this._trendingLoaded) return;
      this._trendingLoaded = true;
      this.trendingLoading = true;
      this.trendingError = false;

      try {
        const res = await fetch('/api/trending/overview');
        if (res.ok) {
          this.trendingData = await res.json();
          this.trendingError = false;
          // 市場資料載入後，非同步載入 AI 分析
          this.loadAiAnalysis();
        } else {
          this.trendingError = true;
        }
      } catch (e) {
        console.error('Failed to load trending:', e);
        this.trendingError = true;
      } finally {
        this.trendingLoading = false;
      }

      // 設定自動重新整理（錯誤時 30 秒後重試，正常時按設定間隔）
      if (this._trendingTimer) clearTimeout(this._trendingTimer);
      const interval = this.trendingError ? 30000 : CONFIG.TRENDING_REFRESH_MS;
      this._trendingTimer = setTimeout(() => {
        if (this.tab === 'trending') this.loadTrending();
      }, interval);
    },

    // 手動重試載入熱門資料
    retryTrending() {
      this._trendingLoaded = false;
      this.trendingError = false;
      this.loadTrending();
    },

    // AI 趨勢分析
    async loadAiAnalysis(force = false) {
      if (this.aiAnalysisLoading) return;
      // 如果已有內容且非強制重新載入，略過
      if (!force && this.aiAnalysis.content) return;

      this.aiAnalysisLoading = true;
      try {
        const url = `/api/trending/ai-analysis?lang=${encodeURIComponent(this.lang)}`;
        const res = await fetch(url);
        if (res.ok) {
          this.aiAnalysis = await res.json();
        }
      } catch (e) {
        console.error('Failed to load AI analysis:', e);
      } finally {
        this.aiAnalysisLoading = false;
      }
    },

    refreshAiAnalysis() {
      this.aiAnalysis = { available: null, content: '', updated_at: '', provider: '' };
      this.loadAiAnalysis(true);
    },

    // VIX 為恐慌指數，上漲代表市場恐慌，色彩和情緒應反轉
    isPositiveForMarket(idx) {
      const up = idx.change >= 0;
      return idx.symbol === '^VIX' ? !up : up;
    },

    // 計算市場情緒（結果快取在 _sentiment，由 $watch 和 toggleLang 觸發）
    _computeSentiment() {
      const indices = this.trendingData.indices || [];
      if (indices.length === 0) return { label: '', cls: '', arrow: '' };
      const ups = indices.filter(i => this.isPositiveForMarket(i)).length;
      const ratio = ups / indices.length;
      if (ratio >= 0.7) return { label: this.t('trending.market_up'), cls: 'sentiment-up', arrow: '&#9650;' };
      if (ratio <= 0.3) return { label: this.t('trending.market_down'), cls: 'sentiment-down', arrow: '&#9660;' };
      return { label: this.t('trending.market_mixed'), cls: 'sentiment-mixed', arrow: '&#9670;' };
    },

    // 公開存取（模板使用 _sentiment 即可，此函式保留向後相容）
    getMarketSentiment() { return this._sentiment; },

    // 重建 symbol -> stock 查詢表（trendingData 變化時呼叫一次）
    _rebuildStockMap() {
      const map = {};
      const gainers = this.trendingData.movers?.gainers || [];
      const losers = this.trendingData.movers?.losers || [];
      for (const s of gainers) map[s.symbol] = s;
      for (const s of losers) map[s.symbol] = s;
      this._stockMap = map;
    },

    // 從快取查詢表中查找股票即時行情
    _computeStockPreview() {
      const sym = (this.form.symbol || '').toUpperCase().trim();
      if (!sym) return null;
      return this._stockMap[sym] || null;
    },

    quickAnalyze(symbol) {
      this.form.symbol = symbol;
      this.tab = 'analysis';
      window.scrollTo(0, 0);
      // 預載個股即時行情，讓使用者進入分析頁時立即看到股價資訊
      this.fetchStockContext(symbol);
    },

    // 指數代碼轉換為對應 ETF（可直接分析）
    indexToEtf(symbol) {
      const map = {'^GSPC': 'SPY', '^DJI': 'DIA', '^IXIC': 'QQQ', '^VIX': 'VIXY'};
      return map[symbol] || symbol.replace(/[^A-Za-z]/g, '');
    },

    navigateToAnalysis(symbol) {
      if (!symbol) return;
      // 移除 GSPC 等指數代碼的特殊字元
      const clean = symbol.replace(/[^A-Za-z]/g, '');
      this.quickAnalyze(clean);
    },

    // 追蹤清單方法
    _loadWatchlist() {
      try {
        const raw = localStorage.getItem('watchlist');
        if (raw) {
          const parsed = JSON.parse(raw);
          // 驗證格式：只接受字串陣列，限制長度
          if (Array.isArray(parsed)) {
            this.watchlist = parsed
              .filter(s => typeof s === 'string' && /^[A-Z]{1,5}$/.test(s))
              .slice(0, 20);
          }
        }
      } catch {
        this.watchlist = [];
      }
    },

    _saveWatchlist() {
      localStorage.setItem('watchlist', JSON.stringify(this.watchlist));
    },

    isInWatchlist(symbol) {
      return this.watchlist.includes(symbol);
    },

    toggleWatchlist(symbol, event) {
      if (event) event.stopPropagation();
      if (!symbol || !/^[A-Z]{1,5}$/.test(symbol)) return;
      const idx = this.watchlist.indexOf(symbol);
      if (idx >= 0) {
        this.watchlist.splice(idx, 1);
      } else {
        if (this.watchlist.length >= 20) return; // 追蹤上限
        this.watchlist.push(symbol);
      }
      this._saveWatchlist();
    },

    clearWatchlist() {
      if (!confirm(this.t('watchlist.clear_confirm'))) return;
      this.watchlist = [];
      this._saveWatchlist();
    },

    // 取得追蹤清單中的股票行情（使用 _stockMap 快取查詢表）
    getWatchlistStocks() {
      if (this.watchlist.length === 0) return [];
      return this.watchlist
        .map(sym => this._stockMap[sym] || { symbol: sym, name: '', price: null, change_pct: null })
        .filter(Boolean);
    },

    async startAnalysis() {
      this.formError = null;

      // 前端即時驗證：避免無效請求送到後端
      const sym = (this.form.symbol || '').trim().toUpperCase();
      if (!sym || !/^[A-Z]{1,5}$/.test(sym)) {
        this.formError = this.t('error.invalid_symbol');
        return;
      }
      this.form.symbol = sym;

      this.submitting = true;

      // 靜默請求桌面通知權限
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().catch(() => {});
      }

      try {
        const res = await fetch('/api/analysis/start', {
          method: 'POST',
          headers: this._langHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify({
            stock_symbol: this.form.symbol,
            analysis_date: this.form.date,
            analysts: this.form.analysts,
            research_depth: this.form.depth,
            llm_provider: this.form.provider,
            llm_model: this.form.model,
          }),
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || this.t('error.start_failed'));
        }

        const data = await res.json();

        // 快取命中：直接顯示結果，跳過 SSE 串流
        if (data.status === 'cached' && data.result) {
          this.result = data.result;
          this.showResults = true;
          this.analysisRunning = false;
          this.cachedResult = true;
          this.selectFirstTab();
          this.fetchStockContext(this.form.symbol);
          return;
        }

        // 驗證 analysis_id 格式（與後端 _validate_analysis_id 一致）
        if (!/^analysis_[A-Za-z0-9_-]{16,32}$/.test(data.analysis_id || '')) {
          throw new Error(this.t('error.start_failed'));
        }
        this.analysisId = data.analysis_id;
        this.analysisRunning = true;
        this.progressMessages = [];
        this.progressPercent = 0;
        this.startTime = Date.now();
        this.result = null;
        this.showResults = false;
        this.cachedResult = false;
        this.connectionRetries = 0;
        this.pollRetryCount = 0;

        this._startElapsedTimer();
        this.connectSSE();
        this.fetchStockContext(this.form.symbol);

      } catch (e) {
        this.formError = e.message;
      } finally {
        this.submitting = false;
      }
    },

    connectSSE() {
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
      if (this._reconnectTimer) {
        clearTimeout(this._reconnectTimer);
        this._reconnectTimer = null;
      }

      const sseLang = this.lang === 'en' ? 'en' : 'zh-TW';
      this.eventSource = new EventSource(`/api/analysis/${this.analysisId}/stream?lang=${sseLang}`);

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'progress') {
            this.progressMessages.push(data.message);
            // 限制進度訊息上限，避免長時間分析導致記憶體膨脹
            // 每次刪 10 條（而非 50），減少 DOM 批量更新的卡頓
            if (this.progressMessages.length > 200) this.progressMessages.splice(0, 10);
            const stepMatch = data.message.match(/^\[(\d+)\/(\d+)\]/);
            if (stepMatch) {
              this.progressPercent = Math.min(CONFIG.PROGRESS_MAX_PERCENT, Math.round((parseInt(stepMatch[1]) / parseInt(stepMatch[2])) * CONFIG.PROGRESS_MAX_PERCENT));
            } else {
              this.progressPercent = Math.min(CONFIG.PROGRESS_MAX_PERCENT, this.progressMessages.length * CONFIG.PROGRESS_STEP_PERCENT);
            }
            this.connectionRetries = 0;

            // 使用 requestAnimationFrame 同步瀏覽器繪製幀，避免 jank
            if (!this._scrollPending) {
              this._scrollPending = true;
              requestAnimationFrame(() => {
                this._scrollPending = false;
                const log = this.$refs.progressLog;
                if (log) log.scrollTop = log.scrollHeight;
              });
            }

          } else if (data.type === 'completed') {
            this.progressPercent = 100;
            this.analysisRunning = false;
            this.result = data.result;
            this.showResults = true;
            this.selectFirstTab();
            this.eventSource.close();
            this.eventSource = null;
            this._stopElapsedTimer();
            this._notifyCompletion(true);

          } else if (data.type === 'failed') {
            this.progressPercent = 100;
            this.progressMessages.push(this.t('error.analysis_failed') + ': ' + data.error);
            this.analysisRunning = false;
            this._stopElapsedTimer();
            this._notifyCompletion(false);
            this.formError = data.error;
            this.eventSource.close();
            this.eventSource = null;
          }
        } catch (e) {
          console.error('SSE parse error:', e);
        }
      };

      this.eventSource.onerror = () => {
        this.eventSource.close();
        this.eventSource = null;
        if (this.analysisRunning) {
          this.connectionRetries++;
          if (this.connectionRetries <= CONFIG.SSE_MAX_RETRIES) {
            // 記錄重連事件到進度日誌
            this.progressMessages.push(
              this.t('analysis.reconnecting') + ' (' + this.connectionRetries + '/' + CONFIG.SSE_MAX_RETRIES + ')'
            );
            const delay = Math.min(CONFIG.SSE_BACKOFF_BASE_MS * Math.pow(2, this.connectionRetries - 1), CONFIG.SSE_BACKOFF_MAX_MS);
            this._reconnectTimer = setTimeout(() => {
              this._reconnectTimer = null;
              if (this.analysisRunning) this.connectSSE();
            }, delay);
          } else {
            this.progressMessages.push(this.t('analysis.polling_fallback'));
            this.pollRetryCount = 0;
            this.pollStatus();
          }
        }
      };
    },

    async pollStatus() {
      while (this.analysisRunning && this.pollRetryCount < CONFIG.POLL_MAX_RETRIES) {
        try {
          const res = await fetch(`/api/analysis/${this.analysisId}/status`, {
            headers: this._langHeaders(),
          });

          if (!res.ok) {
            if (res.status === 404) {
              this.analysisRunning = false;
              this.formError = this.t('error.task_expired');
              return;
            }
            throw new Error(`HTTP ${res.status}`);
          }

          const data = await res.json();
          this.progressMessages = data.progress || [];
          this.pollRetryCount = 0;

          if (data.status === 'completed') {
            this.progressPercent = 100;
            this.analysisRunning = false;
            this.result = data.result;
            this.showResults = true;
            this.selectFirstTab();
            this._stopElapsedTimer();
            this._notifyCompletion(true);
            return;
          } else if (data.status === 'failed') {
            this.analysisRunning = false;
            this._stopElapsedTimer();
            this.formError = data.error || this.t('error.analysis_failed');
            this._notifyCompletion(false);
            return;
          }
        } catch (e) {
          this.pollRetryCount++;
          console.error(`Poll error (${this.pollRetryCount}/${CONFIG.POLL_MAX_RETRIES}):`, e);
        }

        const delay = Math.min(CONFIG.POLL_BACKOFF_BASE_MS * Math.pow(2, Math.min(this.pollRetryCount, 3)), CONFIG.POLL_BACKOFF_MAX_MS);
        await new Promise(r => setTimeout(r, delay));
      }

      if (this.analysisRunning) {
        this.analysisRunning = false;
        this._stopElapsedTimer();
        this.formError = this.t('error.connection_timeout');
      }
    },

    // 英文翻譯是否可用
    hasEnglishTranslation() {
      if (!this.result) return false;
      return !!(this.result.state_en || this.result.decision_en);
    },

    // 根據語言取得對應的 state（英文優先使用 state_en）
    getState() {
      if (!this.result) return null;
      if (this.lang === 'en' && this.result.state_en) {
        return { ...this.result.state, ...this.result.state_en };
      }
      return this.result.state;
    },

    // 根據語言取得報告內容
    getReport(key) {
      const st = this.getState();
      return st ? st[key] : null;
    },

    // 根據語言取得 decision
    getDecision() {
      if (!this.result) return null;
      if (this.lang === 'en' && this.result.decision_en) {
        return { ...this.result.decision, ...this.result.decision_en };
      }
      return this.result.decision;
    },

    selectFirstTab() {
      if (!this.result?.state) return;
      const tabs = ['market', 'fundamentals', 'news', 'sentiment', 'risk', 'debate'];
      const keys = {
        market: 'market_report',
        fundamentals: 'fundamentals_report',
        news: 'news_report',
        sentiment: 'sentiment_report',
        risk: 'risk_assessment',
        debate: 'investment_debate_state',
      };
      for (const t of tabs) {
        if (this.result.state[keys[t]]) {
          this.reportTab = t;
          return;
        }
      }
    },

    resetAnalysis() {
      // 通知後端取消進行中的分析（fire-and-forget）
      if (this.analysisId) {
        fetch(`/api/analysis/${encodeURIComponent(this.analysisId)}`, {
          method: 'DELETE',
          headers: this._langHeaders(),
        }).catch(() => {});
      }
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
      }
      if (this._reconnectTimer) {
        clearTimeout(this._reconnectTimer);
        this._reconnectTimer = null;
      }
      this.analysisRunning = false;
      this.showResults = false;
      this.result = null;
      this.progressMessages = [];
      this.progressPercent = 0;
      this.formError = null;
      this.analysisId = null;
      this.connectionRetries = 0;
      this.pollRetryCount = 0;
      this.stockContext = null;
      this.stockContextLoading = false;
      this._stopElapsedTimer();
    },

    // 取得個股即時行情快照（前端快取 5 分鐘 + 請求去重 + 自動重試）
    async fetchStockContext(symbol, _retry = 0) {
      const MAX_RETRY = 2;
      const CTX_TTL = 300000; // 5 分鐘
      // 快取命中：直接使用
      const cached = this._ctxCache[symbol];
      if (cached && Date.now() - cached.ts < CTX_TTL) {
        this.stockContext = cached.data;
        this.stockContextLoading = false;
        return;
      }
      // 請求去重：相同 symbol 的併發請求共用同一 Promise
      if (this._ctxPending[symbol]) {
        this.stockContextLoading = true;
        try {
          this.stockContext = await this._ctxPending[symbol];
        } catch { this.stockContext = { error: true }; }
        this.stockContextLoading = false;
        return;
      }
      this.stockContextLoading = true;
      if (_retry === 0) this.stockContext = null;
      // 建立請求 Promise 並註冊到去重表
      const doFetch = (async () => {
        try {
          const res = await fetch(`/api/analysis/stock-context/${encodeURIComponent(symbol)}`, {
            headers: this._langHeaders(),
          });
          if (res.ok) {
            const data = await res.json();
            this._ctxCache[symbol] = { data, ts: Date.now() };
            return data;
          } else if (res.status >= 500 && _retry < MAX_RETRY) {
            await new Promise(r => setTimeout(r, 2000 + _retry * 1000));
            delete this._ctxPending[symbol];
            return this.fetchStockContext(symbol, _retry + 1);
          }
          return { error: true };
        } catch (e) {
          console.error('Stock context fetch error:', e);
          if (_retry < MAX_RETRY) {
            await new Promise(r => setTimeout(r, 2000 + _retry * 1000));
            delete this._ctxPending[symbol];
            return this.fetchStockContext(symbol, _retry + 1);
          }
          return { error: true };
        } finally {
          delete this._ctxPending[symbol];
          this.stockContextLoading = false;
        }
      })();
      this._ctxPending[symbol] = doFetch;
      this.stockContext = await doFetch;
    },

    // 將時間戳轉為相對時間（如「剛剛」、「3 分鐘前」）
    relativeTime(dateStr) {
      if (!dateStr) return '';
      try {
        const date = new Date(dateStr.replace(' ', 'T'));
        const diff = Math.floor((Date.now() - date.getTime()) / 1000);
        if (diff < 60) return this.t('time.just_now');
        if (diff < 3600) {
          const mins = Math.floor(diff / 60);
          return mins + this.t('time.min_ago');
        }
        if (diff < 86400) {
          const hours = Math.floor(diff / 3600);
          return hours + this.t('time.hour_ago');
        }
        return dateStr;
      } catch { return dateStr; }
    },

    formatLargeNumber(num) {
      if (!num && num !== 0) return '-';
      if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
      if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
      if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
      if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
      return num.toLocaleString();
    },

    async loadHistory() {
      try {
        const res = await fetch('/api/analysis/history', { headers: this._langHeaders() });
        if (!res.ok) return;
        const data = await res.json();
        this.historyList = (data.analyses || []).reverse();
      } catch (e) {
        console.error('Failed to load history:', e);
      }
    },

    async loadAnalysisResult(analysisId) {
      try {
        const res = await fetch(`/api/analysis/${analysisId}/status`, {
          headers: this._langHeaders(),
        });
        if (!res.ok) return;
        const data = await res.json();
        if (data.result) {
          this.result = data.result;
          this.showResults = true;
          this.analysisRunning = false;
          this.tab = 'analysis';
          this.selectFirstTab();
        }
      } catch (e) {
        console.error('Failed to load result:', e);
      }
    },

    // 工具方法
    formatTime(idx) {
      if (!this.startTime) return '';
      const elapsed = Math.round((Date.now() - this.startTime) / 1000);
      const mins = Math.floor(elapsed / 60);
      const secs = elapsed % 60;
      return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    },

    formatPercent(val) {
      if (val == null) return '-';
      return (val * 100).toFixed(0) + '%';
    },

    getActionClass(action) {
      if (!action) return '';
      const a = action.toLowerCase();
      // 匹配 LLM 可能回傳的多種中英文動作詞（含台灣與大陸用語）
      if (a.includes('buy') || a.includes('買入') || a.includes('做多') || a.includes('作多') || a.includes('加倉') || a.includes('long')) return 'action-buy';
      if (a.includes('sell') || a.includes('賣出') || a.includes('做空') || a.includes('放空') || a.includes('減倉') || a.includes('short')) return 'action-sell';
      return 'action-hold';
    },

    statusText(status) {
      const key = 'history.status_' + status;
      return this.t(key);
    },

    exportResult() {
      if (!this.result) return;
      const data = JSON.stringify(this.result, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${this.result.stock_symbol || 'analysis'}_${this.result.analysis_date || 'report'}.json`;
      a.click();
      // 延遲釋放 blob URL，避免 Safari 下載前尚未讀取完成
      setTimeout(() => URL.revokeObjectURL(url), 1000);
    },

    _startElapsedTimer() {
      this._stopElapsedTimer();
      this.elapsedText = this.t('analysis.elapsed') + ' 00:00';
      this._elapsedTimer = setInterval(() => {
        if (!this.startTime) return;
        const sec = Math.floor((Date.now() - this.startTime) / 1000);
        const m = String(Math.floor(sec / 60)).padStart(2, '0');
        const s = String(sec % 60).padStart(2, '0');
        this.elapsedText = `${this.t('analysis.elapsed')} ${m}:${s}`;
      }, 1000);
    },

    _stopElapsedTimer() {
      if (this._elapsedTimer) {
        clearInterval(this._elapsedTimer);
        this._elapsedTimer = null;
      }
      this.elapsedText = '';
    },

    _notifyCompletion(success) {
      const symbol = this.form.symbol || '';
      const title = success
        ? `${symbol} ${this.t('analysis.completed')}`
        : `${symbol} ${this.t('analysis.failed')}`;
      document.title = title + ' - TradingAgents';
      setTimeout(() => { document.title = this.t('meta.title'); }, 5000);
      if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
        new Notification('TradingAgents', { body: title, icon: '/static/favicon.svg' });
      }
    },

    // 產生帶有語言偏好的 HTTP headers
    _langHeaders(extra = {}) {
      return { 'Accept-Language': this.lang === 'en' ? 'en' : 'zh-TW', ...extra };
    },

    // 驗證 URL 協議，防止 javascript: 等注入
    safeUrl(url) {
      if (!url) return '#';
      try {
        const parsed = new URL(url, window.location.origin);
        return ['http:', 'https:'].includes(parsed.protocol) ? url : '#';
      } catch { return '#'; }
    },

    // DOMPurify 白名單配置（僅允許 Markdown 渲染所需標籤與屬性）
    _purifyConfig: {
      ALLOWED_TAGS: [
        'p', 'h2', 'h3', 'h4', 'h5', 'strong', 'em', 'code', 'pre',
        'ul', 'ol', 'li', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'br', 'hr', 'blockquote', 'div', 'a', 'span'
      ],
      ALLOWED_ATTR: ['class', 'scope', 'href', 'target', 'rel']
    },

    _sanitize(html) {
      if (typeof DOMPurify !== 'undefined') {
        return DOMPurify.sanitize(html, this._purifyConfig);
      }
      // DOMPurify 未載入時，直接做字元跳脫，避免使用 innerHTML 造成 XSS
      console.warn('DOMPurify not loaded, falling back to character escaping');
      const escaped = String(html)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
      return `<pre style="white-space:pre-wrap">${escaped}</pre>`;
    },

    renderMarkdown(text) {
      if (!text) return '<p class="empty-state">' + this._sanitize(this.t('common.no_data')) + '</p>';

      let html = text;

      // 單次掃描的 HTML 實體編碼函式（避免對同一字串掃描 3 次）
      const escHtml = s => s.replace(/[&<>]/g, c => c === '&' ? '&amp;' : c === '<' ? '&lt;' : '&gt;');

      // 先提取多行代碼塊，避免後續處理破壞其內容
      const codeBlocks = [];
      html = html.replace(/```(\w*)\n([\s\S]*?)```/gm, (_, lang, code) => {
        const safeCode = escHtml(code.trimEnd());
        const placeholder = `\x00CB${codeBlocks.length}\x00`;
        codeBlocks.push(`<pre><code class="language-${lang || 'text'}">${safeCode}</code></pre>`);
        return placeholder;
      });

      // HTML 實體編碼（代碼塊已單獨處理，單次掃描取代三次鏈式 replace）
      html = escHtml(html);

      // 標題（結果區域容器為 h2，Markdown 標題從 h3 開始以維持正確層級）
      html = html
        .replace(/^#{1,6}\s*$/gm, '')
        .replace(/^#{4,6} (\S.*)$/gm, (_, g) => `<h6>${g.trim()}</h6>`)
        .replace(/^### (\S.*)$/gm, (_, g) => `<h5>${g.trim()}</h5>`)
        .replace(/^## (\S.*)$/gm, (_, g) => `<h4>${g.trim()}</h4>`)
        .replace(/^# (\S.*)$/gm, (_, g) => `<h3>${g.trim()}</h3>`)
        .replace(/^---$/gm, '<hr>');

      // 行內格式
      html = html
        .replace(/\*\*(.+?)\*\*/g, (_, g) => `<strong>${g}</strong>`)
        .replace(/\*(.+?)\*/g, (_, g) => `<em>${g}</em>`)
        .replace(/`([^`]+)`/g, (_, g) => `<code>${g}</code>`);

      // Markdown 連結（僅允許 http/https 協議，在新分頁開啟）
      html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/g,
        (_, label, url) => `<a href="${url}" target="_blank" rel="noopener noreferrer">${label}</a>`);

      // 引用區塊（支援連續 > 行）
      html = html.replace(/(?:^&gt; .+$\n?)+/gm, (match) => {
        const content = match.trim().split('\n')
          .map(line => line.replace(/^&gt; /, ''))
          .join('<br>');
        return `<blockquote>${content}</blockquote>`;
      });

      // 合併被空行分隔的列表項（LLM 常在項目間插入空行）
      html = html.replace(/^(\d+\. .+)$(\n\n)(?=\d+\. )/gm, '$1\n');

      html = html.replace(/(?:^- .+$\n?)+/gm, (match) => {
        const items = match.trim().split('\n')
          .filter(line => line.trim())
          .map(line => `<li>${line.replace(/^- /, '')}</li>`)
          .join('');
        return `<ul>${items}</ul>`;
      });

      html = html.replace(/(?:^\d+\. .+$\n?)+/gm, (match) => {
        const items = match.trim().split('\n')
          .filter(line => line.trim())
          .map(line => `<li>${line.replace(/^\d+\. /, '')}</li>`)
          .join('');
        return `<ol>${items}</ol>`;
      });

      // Markdown 表格解析（支援 LLM 常見的對齊標記變體）
      html = html.replace(/(?:^\|.+\|$\n?)+/gm, (block) => {
        const rows = block.trim().split('\n').filter(r => r.trim());
        if (rows.length < 2) return block;
        const sepTest = rows[1].replace(/\s/g, '');
        if (!/^\|[:|-]+\|$/.test(sepTest)) return block;
        const sepCells = rows[1].replace(/^\|/, '').replace(/\|$/, '').split('|');
        if (!sepCells.every(c => c.trim().replace(/:/g, '').includes('-'))) return block;
        const parseRow = (row) =>
          row.replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim());
        const headers = parseRow(rows[0]);
        const thead = '<thead><tr>' + headers.map(h => `<th scope="col">${h}</th>`).join('') + '</tr></thead>';
        const bodyRows = rows.slice(2);
        const tbody = '<tbody>' + bodyRows.map(row => {
          const cells = parseRow(row);
          return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
        }).join('') + '</tbody>';
        return `<div class="table-scroll"><table>${thead}${tbody}</table></div>`;
      });

      // 段落與換行
      html = html.replace(/\n\n/g, '</p><p>');
      html = html.replace(/\n/g, '<br>');
      html = `<div class="markdown-body"><p>${html}</p></div>`;

      // 還原代碼塊佔位符
      codeBlocks.forEach((block, i) => {
        html = html.replace(`\x00CB${i}\x00`, block);
      });

      return this._sanitize(html);
    },

    renderDebate(debateState) {
      const emptyHtml = '<p class="empty-state">' + this._sanitize(this.t('common.no_data')) + '</p>';
      if (!debateState) return emptyHtml;

      if (typeof debateState === 'string') {
        return this.renderMarkdown(debateState);
      }

      // 所有欄位皆為空時顯示空狀態
      if (!debateState.bull_history && !debateState.bear_history && !debateState.judge_decision) {
        return emptyHtml;
      }

      let html = '<div class="debate-content">';

      if (debateState.bull_history) {
        const bullLabel = this.t('debate.bull_label');
        html += `<div class="debate-section debate-bull">
          <h3>${bullLabel}</h3>
          <div>${this.renderMarkdown(debateState.bull_history)}</div>
        </div>`;
      }

      if (debateState.bear_history) {
        const bearLabel = this.t('debate.bear_label');
        html += `<div class="debate-section debate-bear">
          <h3>${bearLabel}</h3>
          <div>${this.renderMarkdown(debateState.bear_history)}</div>
        </div>`;
      }

      if (debateState.judge_decision) {
        const judgeLabel = this.t('debate.judge_label');
        html += `<div class="debate-section debate-judge">
          <h3>${judgeLabel}</h3>
          <div>${this.renderMarkdown(debateState.judge_decision)}</div>
        </div>`;
      }

      html += '</div>';
      // renderMarkdown 內部已呼叫 _sanitize()，外層不需重複清理
      // 雙重 _sanitize 在 DOMPurify fallback 路徑下會破壞已生成的 HTML 標籤
      return html;
    },
  };
}
