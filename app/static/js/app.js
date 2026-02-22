/**
 * TradingAgents 前端應用
 * 支援 i18n 國際化、熱門特區、股票分析
 */

// 配置常數
const CONFIG = {
  SSE_MAX_RETRIES: 3,
  SSE_BACKOFF_BASE_MS: 1000,
  SSE_BACKOFF_MAX_MS: 8000,
  POLL_MAX_RETRIES: 60,
  POLL_BACKOFF_BASE_MS: 3000,
  POLL_BACKOFF_MAX_MS: 15000,
  PROGRESS_STEP_PERCENT: 8,
  PROGRESS_MAX_PERCENT: 95,
  TRENDING_REFRESH_MS: 600000, // 10 分鐘自動重新整理
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
    historyList: [],
    configStatus: null,
    analysisId: null,
    eventSource: null,
    startTime: null,
    pollRetryCount: 0,
    elapsedText: '',
    _elapsedTimer: null,

    // 熱門特區
    trendingData: { indices: [], movers: { gainers: [], losers: [] }, news: [] },
    trendingLoading: false,
    _trendingTimer: null,

    // AI 趨勢分析
    aiAnalysis: { available: null, content: '', updated_at: '', provider: '' },
    aiAnalysisLoading: false,

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

      await this.checkHealth();
      await this.loadModels();
      this.form.date = new Date().toISOString().split('T')[0];

      // 預設載入熱門特區
      this.loadTrending();

      // 分析進行中離開頁面時警告
      window.addEventListener('beforeunload', (e) => {
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
      // 切換語言後重新載入 AI 分析（使用新語言）
      if (this.tab === 'trending' && this.aiAnalysis.content) {
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
      if (this.trendingLoading) return;
      this.trendingLoading = true;

      try {
        const res = await fetch('/api/trending/overview');
        if (res.ok) {
          this.trendingData = await res.json();
          // 市場資料載入後，非同步載入 AI 分析
          this.loadAiAnalysis();
        }
      } catch (e) {
        console.error('Failed to load trending:', e);
      } finally {
        this.trendingLoading = false;
      }

      // 設定自動重新整理
      if (this._trendingTimer) clearTimeout(this._trendingTimer);
      this._trendingTimer = setTimeout(() => {
        if (this.tab === 'trending') this.loadTrending();
      }, CONFIG.TRENDING_REFRESH_MS);
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

    getMarketSentiment() {
      const indices = this.trendingData.indices || [];
      if (indices.length === 0) return { label: '', cls: '', arrow: '' };
      const ups = indices.filter(i => i.change >= 0).length;
      const ratio = ups / indices.length;
      if (ratio >= 0.7) return { label: this.t('trending.market_up'), cls: 'sentiment-up', arrow: '&#9650;' };
      if (ratio <= 0.3) return { label: this.t('trending.market_down'), cls: 'sentiment-down', arrow: '&#9660;' };
      return { label: this.t('trending.market_mixed'), cls: 'sentiment-mixed', arrow: '&#9670;' };
    },

    // 從已載入的熱門資料中查找股票即時行情
    getStockPreview() {
      const sym = (this.form.symbol || '').toUpperCase().trim();
      if (!sym) return null;
      const all = [
        ...(this.trendingData.movers?.gainers || []),
        ...(this.trendingData.movers?.losers || []),
      ];
      return all.find(s => s.symbol === sym) || null;
    },

    quickAnalyze(symbol) {
      this.form.symbol = symbol;
      this.tab = 'analysis';
      window.scrollTo(0, 0);
    },

    // 指數代碼轉換為對應 ETF（可直接分析）
    indexToEtf(symbol) {
      const map = {'^GSPC': 'SPY', '^DJI': 'DIA', '^IXIC': 'QQQ', '^VIX': 'VIXY'};
      return map[symbol] || symbol.replace(/[^A-Za-z0-9.-]/g, '');
    },

    navigateToAnalysis(symbol) {
      if (!symbol) return;
      // 移除 GSPC 等指數代碼的特殊字元
      const clean = symbol.replace(/[^A-Za-z0-9.-]/g, '');
      this.quickAnalyze(clean);
    },

    async startAnalysis() {
      this.formError = null;
      this.submitting = true;

      // 靜默請求桌面通知權限
      if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
      }

      try {
        const res = await fetch('/api/analysis/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
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
        this.analysisId = data.analysis_id;
        this.analysisRunning = true;
        this.progressMessages = [];
        this.progressPercent = 0;
        this.startTime = Date.now();
        this.result = null;
        this.showResults = false;
        this.connectionRetries = 0;
        this.pollRetryCount = 0;

        this._startElapsedTimer();
        this.connectSSE();

      } catch (e) {
        this.formError = e.message;
      } finally {
        this.submitting = false;
      }
    },

    connectSSE() {
      if (this.eventSource) {
        this.eventSource.close();
      }

      this.eventSource = new EventSource(`/api/analysis/${this.analysisId}/stream`);

      this.eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'progress') {
            this.progressMessages.push(data.message);
            const stepMatch = data.message.match(/^\[(\d+)\/(\d+)\]/);
            if (stepMatch) {
              this.progressPercent = Math.min(CONFIG.PROGRESS_MAX_PERCENT, Math.round((parseInt(stepMatch[1]) / parseInt(stepMatch[2])) * CONFIG.PROGRESS_MAX_PERCENT));
            } else {
              this.progressPercent = Math.min(CONFIG.PROGRESS_MAX_PERCENT, this.progressMessages.length * CONFIG.PROGRESS_STEP_PERCENT);
            }
            this.connectionRetries = 0;

            this.$nextTick(() => {
              const log = this.$refs.progressLog;
              if (log) log.scrollTop = log.scrollHeight;
            });

          } else if (data.type === 'completed') {
            this.progressPercent = 100;
            this.analysisRunning = false;
            this.result = data.result;
            this.showResults = true;
            this.selectFirstTab();
            this.eventSource.close();
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
          }
        } catch (e) {
          console.error('SSE parse error:', e);
        }
      };

      this.eventSource.onerror = () => {
        this.eventSource.close();
        if (this.analysisRunning) {
          this.connectionRetries++;
          if (this.connectionRetries <= CONFIG.SSE_MAX_RETRIES) {
            const delay = Math.min(CONFIG.SSE_BACKOFF_BASE_MS * Math.pow(2, this.connectionRetries - 1), CONFIG.SSE_BACKOFF_MAX_MS);
            setTimeout(() => {
              if (this.analysisRunning) this.connectSSE();
            }, delay);
          } else {
            this.progressMessages.push(this.t('analysis.reconnecting'));
            this.pollRetryCount = 0;
            this.pollStatus();
          }
        }
      };
    },

    async pollStatus() {
      while (this.analysisRunning && this.pollRetryCount < CONFIG.POLL_MAX_RETRIES) {
        try {
          const res = await fetch(`/api/analysis/${this.analysisId}/status`);

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
      if (this.eventSource) {
        this.eventSource.close();
        this.eventSource = null;
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
      this._stopElapsedTimer();
    },

    async loadHistory() {
      try {
        const res = await fetch('/api/analysis/history');
        if (!res.ok) return;
        const data = await res.json();
        this.historyList = (data.analyses || []).reverse();
      } catch (e) {
        console.error('Failed to load history:', e);
      }
    },

    async loadAnalysisResult(analysisId) {
      try {
        const res = await fetch(`/api/analysis/${analysisId}/status`);
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
      if (a.includes('buy') || a.includes('買入')) return 'action-buy';
      if (a.includes('sell') || a.includes('賣出')) return 'action-sell';
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
      URL.revokeObjectURL(url);
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
      setTimeout(() => { document.title = 'TradingAgents - AI Stock Analysis'; }, 5000);
      if (document.hidden && 'Notification' in window && Notification.permission === 'granted') {
        new Notification('TradingAgents', { body: title, icon: '/static/favicon.svg' });
      }
    },

    _sanitize(html) {
      if (typeof DOMPurify !== 'undefined') {
        return DOMPurify.sanitize(html);
      }
      const tmp = document.createElement('div');
      tmp.innerHTML = html;
      const text = tmp.textContent || tmp.innerText || '';
      return `<pre style="white-space:pre-wrap">${text.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</pre>`;
    },

    renderMarkdown(text) {
      if (!text) return '<p class="empty-state">' + this.t('common.no_data') + '</p>';

      let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      html = html
        .replace(/^### (.+)$/gm, (_, g) => `<h4>${g}</h4>`)
        .replace(/^## (.+)$/gm, (_, g) => `<h3>${g}</h3>`)
        .replace(/^# (.+)$/gm, (_, g) => `<h2>${g}</h2>`)
        .replace(/^---$/gm, '<hr>')
        .replace(/^#{1,6}\s*$/gm, '');

      html = html
        .replace(/\*\*(.+?)\*\*/g, (_, g) => `<strong>${g}</strong>`)
        .replace(/\*(.+?)\*/g, (_, g) => `<em>${g}</em>`)
        .replace(/`([^`]+)`/g, (_, g) => `<code>${g}</code>`);

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

      // Markdown 表格解析
      html = html.replace(/(?:^\|.+\|$\n?)+/gm, (block) => {
        const rows = block.trim().split('\n').filter(r => r.trim());
        if (rows.length < 2) return block;
        // 檢查第二行是否為分隔線（|---|---|）
        const sepTest = rows[1].replace(/\s/g, '');
        if (!/^\|[-:|]+\|$/.test(sepTest)) return block;
        const parseRow = (row) =>
          row.replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim());
        const headers = parseRow(rows[0]);
        const thead = '<thead><tr>' + headers.map(h => `<th>${h}</th>`).join('') + '</tr></thead>';
        const bodyRows = rows.slice(2);
        const tbody = '<tbody>' + bodyRows.map(row => {
          const cells = parseRow(row);
          return '<tr>' + cells.map(c => `<td>${c}</td>`).join('') + '</tr>';
        }).join('') + '</tbody>';
        return `<table>${thead}${tbody}</table>`;
      });

      html = html.replace(/\n\n/g, '</p><p>');
      html = html.replace(/\n/g, '<br>');
      html = `<div class="markdown-body"><p>${html}</p></div>`;

      return this._sanitize(html);
    },

    renderDebate(debateState) {
      if (!debateState) return '<p class="empty-state">' + this.t('common.no_data') + '</p>';

      if (typeof debateState === 'string') {
        return this.renderMarkdown(debateState);
      }

      let html = '<div class="debate-content">';

      if (debateState.bull_history) {
        const bullLabel = this.t('debate.bull_label');
        html += `<div class="debate-section debate-bull">
          <h4>${bullLabel}</h4>
          <div>${this.renderMarkdown(debateState.bull_history)}</div>
        </div>`;
      }

      if (debateState.bear_history) {
        const bearLabel = this.t('debate.bear_label');
        html += `<div class="debate-section debate-bear">
          <h4>${bearLabel}</h4>
          <div>${this.renderMarkdown(debateState.bear_history)}</div>
        </div>`;
      }

      if (debateState.judge_decision) {
        const judgeLabel = this.t('debate.judge_label');
        html += `<div class="debate-section debate-judge">
          <h4>${judgeLabel}</h4>
          <div>${this.renderMarkdown(debateState.judge_decision)}</div>
        </div>`;
      }

      html += '</div>';
      return this._sanitize(html);
    },
  };
}
