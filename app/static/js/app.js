/**
 * TradingAgents 前端應用
 */

function tradingApp() {
  return {
    // 狀態
    tab: 'analysis',
    apiReady: false,
    analysisRunning: false,
    showResults: false,
    submitting: false,
    formError: null,
    reportTab: 'market',

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

    get canSubmit() {
      return this.form.symbol.length > 0 &&
             this.form.analysts.length > 0 &&
             !this.submitting;
    },

    async init() {
      await this.checkHealth();
      await this.loadModels();
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
          const err = await res.json();
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
            this.progressPercent = Math.min(95, this.progressMessages.length * 8);

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
        // 如果連線斷開，改用輪詢
        this.eventSource.close();
        if (this.analysisRunning) {
          this.pollStatus();
        }
      };
    },

    async pollStatus() {
      while (this.analysisRunning) {
        try {
          const res = await fetch(`/api/analysis/${this.analysisId}/status`);
          const data = await res.json();

          this.progressMessages = data.progress || [];

          if (data.status === 'completed') {
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
          console.error('輪詢錯誤:', e);
        }

        await new Promise(r => setTimeout(r, 3000));
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
      this.analysisRunning = false;
      this.showResults = false;
      this.result = null;
      this.progressMessages = [];
      this.progressPercent = 0;
      this.formError = null;
      this.analysisId = null;
    },

    async loadHistory() {
      try {
        const res = await fetch('/api/analysis/history');
        const data = await res.json();
        this.historyList = (data.analyses || []).reverse();
      } catch (e) {
        console.error('載入歷史失敗:', e);
      }
    },

    async loadAnalysisResult(analysisId) {
      try {
        const res = await fetch(`/api/analysis/${analysisId}/status`);
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

    renderMarkdown(text) {
      if (!text) return '<p class="empty-state">暫無資料</p>';
      // 簡易 Markdown 渲染（先轉義，再轉為 HTML 結構）
      let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/^### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^## (.+)$/gm, '<h3>$1</h3>')
        .replace(/^# (.+)$/gm, '<h2>$1</h2>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/^---$/gm, '<hr>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

      html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
      html = `<div class="markdown-body"><p>${html}</p></div>`;
      // DOMPurify 淨化，防止 XSS
      return typeof DOMPurify !== 'undefined' ? DOMPurify.sanitize(html) : html;
    },

    renderDebate(debateState) {
      if (!debateState) return '<p class="empty-state">暫無辯論資料</p>';

      let html = '<div class="debate-content">';

      if (typeof debateState === 'string') {
        return this.renderMarkdown(debateState);
      }

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
      return typeof DOMPurify !== 'undefined' ? DOMPurify.sanitize(html) : html;
    },
  };
}
