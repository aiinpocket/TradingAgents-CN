/**
 * TradingAgents 前端應用
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
    tab: 'analysis',
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

    get canSubmit() {
      return this.apiReady &&
             this.form.symbol.length > 0 &&
             this.form.analysts.length > 0 &&
             !this.submitting;
    },

    async init() {
      // 載入暗色模式偏好
      const saved = localStorage.getItem('theme');
      this.darkMode = saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
      if (this.darkMode) document.documentElement.setAttribute('data-theme', 'dark');

      await this.checkHealth();
      await this.loadModels();
      this.form.date = new Date().toISOString().split('T')[0];
    },

    toggleTheme() {
      this.darkMode = !this.darkMode;
      if (this.darkMode) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
      } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
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
        console.error('載入模型失敗:', e);
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

    async startAnalysis() {
      this.formError = null;
      this.submitting = true;

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
          throw new Error(err.detail || '啟動分析失敗');
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
            // 解析步驟前綴 [N/M] 來計算精確進度
            const stepMatch = data.message.match(/^\[(\d+)\/(\d+)\]/);
            if (stepMatch) {
              this.progressPercent = Math.min(CONFIG.PROGRESS_MAX_PERCENT, Math.round((parseInt(stepMatch[1]) / parseInt(stepMatch[2])) * CONFIG.PROGRESS_MAX_PERCENT));
            } else {
              this.progressPercent = Math.min(CONFIG.PROGRESS_MAX_PERCENT, this.progressMessages.length * CONFIG.PROGRESS_STEP_PERCENT);
            }
            this.connectionRetries = 0;

            // 自動捲動到最新
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

          } else if (data.type === 'failed') {
            this.progressPercent = 100;
            this.progressMessages.push('分析失敗: ' + data.error);
            this.analysisRunning = false;
            this.formError = data.error;
            this.eventSource.close();
          }
        } catch (e) {
          console.error('SSE 解析錯誤:', e);
        }
      };

      this.eventSource.onerror = () => {
        this.eventSource.close();
        if (this.analysisRunning) {
          this.connectionRetries++;
          if (this.connectionRetries <= CONFIG.SSE_MAX_RETRIES) {
            // 短暫延遲後重試 SSE
            const delay = Math.min(CONFIG.SSE_BACKOFF_BASE_MS * Math.pow(2, this.connectionRetries - 1), CONFIG.SSE_BACKOFF_MAX_MS);
            setTimeout(() => {
              if (this.analysisRunning) this.connectSSE();
            }, delay);
          } else {
            // SSE 重試失敗，改用輪詢
            this.progressMessages.push('即時連線中斷，已切換至輪詢模式，分析仍在進行中...');
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
              this.formError = '分析任務已失效，請重新開始';
              return;
            }
            throw new Error(`HTTP ${res.status}`);
          }

          const data = await res.json();
          this.progressMessages = data.progress || [];
          this.pollRetryCount = 0;  // 成功時重設重試計數

          if (data.status === 'completed') {
            this.progressPercent = 100;
            this.analysisRunning = false;
            this.result = data.result;
            this.showResults = true;
            this.selectFirstTab();
            return;
          } else if (data.status === 'failed') {
            this.analysisRunning = false;
            this.formError = data.error || '分析失敗';
            return;
          }
        } catch (e) {
          this.pollRetryCount++;
          console.error(`輪詢錯誤 (${this.pollRetryCount}/${CONFIG.POLL_MAX_RETRIES}):`, e);
        }

        // 指數退避
        const delay = Math.min(CONFIG.POLL_BACKOFF_BASE_MS * Math.pow(2, Math.min(this.pollRetryCount, 3)), CONFIG.POLL_BACKOFF_MAX_MS);
        await new Promise(r => setTimeout(r, delay));
      }

      if (this.analysisRunning) {
        this.analysisRunning = false;
        this.formError = '連線逾時，請檢查網路後重試';
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
    },

    async loadHistory() {
      try {
        const res = await fetch('/api/analysis/history');
        if (!res.ok) return;
        const data = await res.json();
        this.historyList = (data.analyses || []).reverse();
      } catch (e) {
        console.error('載入歷史失敗:', e);
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
        console.error('載入結果失敗:', e);
      }
    },

    async loadConfig() {
      try {
        const res = await fetch('/api/config/status');
        if (!res.ok) return;
        this.configStatus = await res.json();
      } catch (e) {
        console.error('載入配置失敗:', e);
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
      const map = { pending: '待處理', running: '進行中', completed: '已完成', failed: '失敗' };
      return map[status] || status;
    },

    _sanitize(html) {
      if (typeof DOMPurify !== 'undefined') {
        return DOMPurify.sanitize(html);
      }
      // 降級：移除所有 HTML 標籤，顯示純文字
      const text = html.replace(/<[^>]*>/g, '');
      return `<pre style="white-space:pre-wrap">${text}</pre>`;
    },

    renderMarkdown(text) {
      if (!text) return '<p class="empty-state">暫無資料</p>';

      // 轉義 HTML 特殊字元
      let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      // 區塊元素
      html = html
        .replace(/^### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^## (.+)$/gm, '<h3>$1</h3>')
        .replace(/^# (.+)$/gm, '<h2>$1</h2>')
        .replace(/^---$/gm, '<hr>');

      // 行內格式
      html = html
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');

      // 清單：將連續的 - 項目包裝為 <ul>
      html = html.replace(/(?:^- .+$\n?)+/gm, (match) => {
        const items = match.trim().split('\n')
          .map(line => `<li>${line.replace(/^- /, '')}</li>`)
          .join('');
        return `<ul>${items}</ul>`;
      });

      // 有序清單：將連續的 1. 2. 項目包裝為 <ol>
      html = html.replace(/(?:^\d+\. .+$\n?)+/gm, (match) => {
        const items = match.trim().split('\n')
          .map(line => `<li>${line.replace(/^\d+\. /, '')}</li>`)
          .join('');
        return `<ol>${items}</ol>`;
      });

      // 段落分隔
      html = html.replace(/\n\n/g, '</p><p>');
      html = html.replace(/\n/g, '<br>');
      html = `<div class="markdown-body"><p>${html}</p></div>`;

      return this._sanitize(html);
    },

    renderDebate(debateState) {
      if (!debateState) return '<p class="empty-state">暫無辯論資料</p>';

      if (typeof debateState === 'string') {
        return this.renderMarkdown(debateState);
      }

      let html = '<div class="debate-content">';

      if (debateState.bull_history) {
        html += `<div class="debate-section debate-bull">
          <h4>多頭研究員</h4>
          <div>${this.renderMarkdown(debateState.bull_history)}</div>
        </div>`;
      }

      if (debateState.bear_history) {
        html += `<div class="debate-section debate-bear">
          <h4>空頭研究員</h4>
          <div>${this.renderMarkdown(debateState.bear_history)}</div>
        </div>`;
      }

      if (debateState.judge_decision) {
        html += `<div class="debate-section debate-judge">
          <h4>研究經理決議</h4>
          <div>${this.renderMarkdown(debateState.judge_decision)}</div>
        </div>`;
      }

      html += '</div>';
      return this._sanitize(html);
    },
  };
}
