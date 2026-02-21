# 

## 

 TradingAgents 

## 1: 

### 
```python
from tradingagents.agents.analysts.base_analyst import BaseAnalyst
import numpy as np
import pandas as pd

class QuantitativeAnalyst(BaseAnalyst):
 """ - """

 def __init__(self, llm, config):
 super().__init__(llm, config)
 self.models = self._initialize_quant_models()

 def _initialize_quant_models(self):
 """"""
 return {
 "mean_reversion": MeanReversionModel(),
 "momentum": MomentumModel(),
 "volatility": VolatilityModel(),
 "correlation": CorrelationModel()
 }

 def perform_analysis(self, data: Dict) -> Dict:
 """"""

 price_data = data.get("price_data", {})
 historical_data = data.get("historical_data", pd.DataFrame())

 if historical_data.empty:
 return {"error": "No historical data available"}

 # 1. 
 stat_arb_signals = self._statistical_arbitrage_analysis(historical_data)

 # 2. 
 momentum_signals = self._momentum_factor_analysis(historical_data)

 # 3. 
 mean_reversion_signals = self._mean_reversion_analysis(historical_data)

 # 4. 
 volatility_analysis = self._volatility_analysis(historical_data)

 # 5. 
 risk_adjusted_metrics = self._risk_adjusted_analysis(historical_data)

 # 6. 
 quant_score = self._calculate_quant_score({
 "stat_arb": stat_arb_signals,
 "momentum": momentum_signals,
 "mean_reversion": mean_reversion_signals,
 "volatility": volatility_analysis,
 "risk_adjusted": risk_adjusted_metrics
 })

 return {
 "statistical_arbitrage": stat_arb_signals,
 "momentum_analysis": momentum_signals,
 "mean_reversion": mean_reversion_signals,
 "volatility_analysis": volatility_analysis,
 "risk_metrics": risk_adjusted_metrics,
 "quantitative_score": quant_score,
 "model_confidence": self._calculate_model_confidence(quant_score),
 "trading_signals": self._generate_trading_signals(quant_score)
 }

 def _statistical_arbitrage_analysis(self, data: pd.DataFrame) -> Dict:
 """"""

 returns = data['Close'].pct_change().dropna()

 # Z-Score 
 rolling_mean = returns.rolling(window=20).mean()
 rolling_std = returns.rolling(window=20).std()
 z_score = (returns - rolling_mean) / rolling_std

 # 
 adf_statistic, adf_pvalue = self._adf_test(data['Close'])

 # 
 half_life = self._calculate_half_life(returns)

 return {
 "current_z_score": z_score.iloc[-1] if not z_score.empty else 0,
 "z_score_percentile": self._calculate_percentile(z_score.iloc[-1], z_score),
 "adf_statistic": adf_statistic,
 "adf_pvalue": adf_pvalue,
 "is_stationary": adf_pvalue < 0.05,
 "half_life_days": half_life,
 "signal_strength": abs(z_score.iloc[-1]) if not z_score.empty else 0
 }

 def _momentum_factor_analysis(self, data: pd.DataFrame) -> Dict:
 """"""

 # 
 momentum_1m = self._calculate_momentum(data, 21) # 1
 momentum_3m = self._calculate_momentum(data, 63) # 3
 momentum_6m = self._calculate_momentum(data, 126) # 6
 momentum_12m = self._calculate_momentum(data, 252) # 12

 # 
 momentum_strength = self._calculate_momentum_strength(data)

 # 
 momentum_persistence = self._calculate_momentum_persistence(data)

 return {
 "momentum_1m": momentum_1m,
 "momentum_3m": momentum_3m,
 "momentum_6m": momentum_6m,
 "momentum_12m": momentum_12m,
 "momentum_strength": momentum_strength,
 "momentum_persistence": momentum_persistence,
 "momentum_score": (momentum_1m + momentum_3m + momentum_6m) / 3,
 "momentum_trend": "bullish" if momentum_3m > 0.05 else "bearish" if momentum_3m < -0.05 else "neutral"
 }
```

## 2: 

### 
```python
class PortfolioOptimizer:
 """ - """

 def __init__(self, config: Dict):
 self.config = config
 self.risk_models = self._initialize_risk_models()
 self.optimization_methods = self._initialize_optimization_methods()

 def optimize_portfolio(self, symbols: List[str], target_date: str,
 constraints: Dict = None) -> Dict:
 """"""

 # 1. 
 assets_data = self._collect_multi_asset_data(symbols, target_date)

 # 2. 
 expected_returns = self._calculate_expected_returns(assets_data)

 # 3. 
 covariance_matrix = self._build_covariance_matrix(assets_data)

 # 4. 
 risk_analysis = self._analyze_portfolio_risk(assets_data, covariance_matrix)

 # 5. 
 optimization_results = self._multi_objective_optimization(
 expected_returns, covariance_matrix, constraints
 )

 # 6. 
 scenario_analysis = self._perform_scenario_analysis(
 optimization_results, assets_data
 )

 return {
 "assets_analysis": assets_data,
 "expected_returns": expected_returns,
 "risk_analysis": risk_analysis,
 "optimal_weights": optimization_results["weights"],
 "portfolio_metrics": optimization_results["metrics"],
 "scenario_analysis": scenario_analysis,
 "rebalancing_schedule": self._generate_rebalancing_schedule(optimization_results)
 }

 def _collect_multi_asset_data(self, symbols: List[str], target_date: str) -> Dict:
 """"""

 assets_data = {}

 # 
 with ThreadPoolExecutor(max_workers=len(symbols)) as executor:
 future_to_symbol = {
 executor.submit(self._analyze_single_asset, symbol, target_date): symbol
 for symbol in symbols
 }

 for future in as_completed(future_to_symbol):
 symbol = future_to_symbol[future]
 try:
 asset_analysis = future.result()
 assets_data[symbol] = asset_analysis
 except Exception as e:
 print(f"Error analyzing {symbol}: {e}")
 assets_data[symbol] = {"error": str(e)}

 return assets_data

 def _analyze_single_asset(self, symbol: str, target_date: str) -> Dict:
 """"""

 # TradingAgents 
 ta = TradingAgentsGraph(debug=False, config=self.config)
 state, decision = ta.propagate(symbol, target_date)

 # 
 return {
 "symbol": symbol,
 "decision": decision,
 "fundamental_score": state.analyst_reports.get("fundamentals", {}).get("overall_score", 0.5),
 "technical_score": state.analyst_reports.get("technical", {}).get("technical_score", 0.5),
 "sentiment_score": (
 state.analyst_reports.get("news", {}).get("news_score", 0.5) +
 state.analyst_reports.get("social", {}).get("social_score", 0.5)
 ) / 2,
 "risk_score": decision.get("risk_score", 0.5),
 "confidence": decision.get("confidence", 0.5)
 }

 def _multi_objective_optimization(self, expected_returns: np.ndarray,
 cov_matrix: np.ndarray, constraints: Dict) -> Dict:
 """"""

 from scipy.optimize import minimize

 n_assets = len(expected_returns)

 # 
 def objective(weights):
 portfolio_return = np.sum(weights * expected_returns)
 portfolio_risk = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
 sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
 return -sharpe_ratio # 

 # 
 constraints_list = [
 {'type': 'eq', 'fun': lambda x: np.sum(x) - 1} # 1
 ]

 # 
 if constraints:
 if 'max_weight' in constraints:
 for i in range(n_assets):
 constraints_list.append({
 'type': 'ineq',
 'fun': lambda x, i=i: constraints['max_weight'] - x[i]
 })

 if 'min_weight' in constraints:
 for i in range(n_assets):
 constraints_list.append({
 'type': 'ineq',
 'fun': lambda x, i=i: x[i] - constraints['min_weight']
 })

 # 
 bounds = tuple((0, 1) for _ in range(n_assets))

 # 
 x0 = np.array([1/n_assets] * n_assets)

 # 
 result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints_list)

 if result.success:
 optimal_weights = result.x
 portfolio_return = np.sum(optimal_weights * expected_returns)
 portfolio_risk = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
 sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0

 return {
 "weights": optimal_weights,
 "metrics": {
 "expected_return": portfolio_return,
 "expected_risk": portfolio_risk,
 "sharpe_ratio": sharpe_ratio,
 "optimization_success": True
 }
 }
 else:
 # 
 equal_weights = np.array([1/n_assets] * n_assets)
 return {
 "weights": equal_weights,
 "metrics": {
 "expected_return": np.sum(equal_weights * expected_returns),
 "expected_risk": np.sqrt(np.dot(equal_weights.T, np.dot(cov_matrix, equal_weights))),
 "sharpe_ratio": 0,
 "optimization_success": False,
 "error": result.message
 }
 }
```

## 3: 

### 
```python
class RealTimeTradingSystem:
 """"""

 def __init__(self, config: Dict):
 self.config = config
 self.trading_agents = {}
 self.position_manager = PositionManager()
 self.risk_monitor = RealTimeRiskMonitor()
 self.execution_engine = ExecutionEngine()
 self.market_data_feed = MarketDataFeed()

 async def start_real_time_trading(self, watchlist: List[str]):
 """"""

 print(f" {len(watchlist)} ...")

 # 
 for symbol in watchlist:
 self.trading_agents[symbol] = TradingAgentsGraph(
 debug=False,
 config=self.config
 )

 # 
 await self.market_data_feed.subscribe(watchlist)

 # 
 await self._main_trading_loop(watchlist)

 async def _main_trading_loop(self, watchlist: List[str]):
 """"""

 while True:
 try:
 # 
 market_updates = await self.market_data_feed.get_updates()

 # 
 tasks = []
 for symbol in watchlist:
 if symbol in market_updates:
 task = self._process_symbol_update(symbol, market_updates[symbol])
 tasks.append(task)

 if tasks:
 await asyncio.gather(*tasks, return_exceptions=True)

 # 
 await self._perform_risk_checks()

 # 
 await asyncio.sleep(1)

 except Exception as e:
 print(f": {e}")
 await asyncio.sleep(5)

 async def _process_symbol_update(self, symbol: str, market_data: Dict):
 """"""

 try:
 # 
 if self._should_reanalyze(symbol, market_data):

 # 
 analysis_result = await self._quick_analysis(symbol, market_data)

 # 
 trading_signals = self._extract_trading_signals(analysis_result)

 # 
 if trading_signals["action"] != "hold":
 await self._execute_trading_decision(symbol, trading_signals)

 # 
 await self._update_position_monitoring(symbol, analysis_result)

 except Exception as e:
 print(f" {symbol} : {e}")

 def _should_reanalyze(self, symbol: str, market_data: Dict) -> bool:
 """"""

 # 
 price_change_threshold = 0.02 # 2%

 current_price = market_data.get("price", 0)
 last_analysis_price = self.trading_agents[symbol].last_analysis_price if hasattr(self.trading_agents[symbol], 'last_analysis_price') else 0

 if last_analysis_price == 0:
 return True

 price_change = abs(current_price - last_analysis_price) / last_analysis_price

 # 
 time_threshold = 300 # 5
 last_analysis_time = getattr(self.trading_agents[symbol], 'last_analysis_time', 0)
 time_since_last = time.time() - last_analysis_time

 return price_change > price_change_threshold or time_since_last > time_threshold

 async def _quick_analysis(self, symbol: str, market_data: Dict) -> Dict:
 """"""

 # 
 quick_config = self.config.copy()
 quick_config.update({
 "max_debate_rounds": 1,
 "max_risk_discuss_rounds": 1,
 "quick_think_llm": "gpt-4o-mini" # 
 })

 # 
 quick_agent = TradingAgentsGraph(
 selected_analysts=["market", "news"], # 
 debug=False,
 config=quick_config
 )

 # 
 current_date = datetime.now().strftime("%Y-%m-%d")
 state, decision = quick_agent.propagate(symbol, current_date)

 # 
 self.trading_agents[symbol].last_analysis_time = time.time()
 self.trading_agents[symbol].last_analysis_price = market_data.get("price", 0)

 return {
 "state": state,
 "decision": decision,
 "market_data": market_data,
 "analysis_timestamp": time.time()
 }
```

## 4: 

### 
```python
class AdvancedBacktester:
 """"""

 def __init__(self, config: Dict):
 self.config = config
 self.performance_analyzer = PerformanceAnalyzer()
 self.risk_analyzer = RiskAnalyzer()
 self.transaction_cost_model = TransactionCostModel()

 def run_comprehensive_backtest(self, strategy_config: Dict,
 start_date: str, end_date: str,
 universe: List[str]) -> Dict:
 """"""

 print(f": {start_date} {end_date}, : {len(universe)} ")

 # 1. 
 historical_data = self._prepare_historical_data(universe, start_date, end_date)

 # 2. 
 trading_history = self._execute_strategy(strategy_config, historical_data)

 # 3. 
 performance_metrics = self._analyze_performance(trading_history)

 # 4. 
 risk_metrics = self._analyze_risk(trading_history)

 # 5. 
 attribution_analysis = self._perform_attribution_analysis(trading_history)

 # 6. 
 sensitivity_analysis = self._perform_sensitivity_analysis(strategy_config, historical_data)

 return {
 "strategy_config": strategy_config,
 "backtest_period": {"start": start_date, "end": end_date},
 "universe": universe,
 "trading_history": trading_history,
 "performance_metrics": performance_metrics,
 "risk_metrics": risk_metrics,
 "attribution_analysis": attribution_analysis,
 "sensitivity_analysis": sensitivity_analysis,
 "summary": self._generate_backtest_summary(performance_metrics, risk_metrics)
 }

 def _execute_strategy(self, strategy_config: Dict, historical_data: Dict) -> List[Dict]:
 """"""

 trading_history = []
 portfolio = Portfolio(initial_capital=strategy_config.get("initial_capital", 1000000))

 # 
 dates = sorted(historical_data.keys())

 for date in dates:
 daily_data = historical_data[date]

 # 
 daily_signals = {}
 for symbol in daily_data:
 try:
 # TradingAgents 
 signal = self._generate_trading_signal(symbol, date, daily_data[symbol])
 daily_signals[symbol] = signal
 except Exception as e:
 print(f" {symbol} : {e}")
 continue

 # 
 portfolio_changes = self._rebalance_portfolio(
 portfolio, daily_signals, daily_data, strategy_config
 )

 # 
 if portfolio_changes:
 trading_history.extend(portfolio_changes)

 # 
 portfolio.update_value(daily_data)

 return trading_history

 def _analyze_performance(self, trading_history: List[Dict]) -> Dict:
 """"""

 # 
 returns = self._calculate_returns(trading_history)

 # 
 total_return = self._calculate_total_return(returns)
 annualized_return = self._calculate_annualized_return(returns)
 volatility = self._calculate_volatility(returns)
 sharpe_ratio = self._calculate_sharpe_ratio(returns)

 # 
 sortino_ratio = self._calculate_sortino_ratio(returns)
 calmar_ratio = self._calculate_calmar_ratio(returns)
 max_drawdown = self._calculate_max_drawdown(returns)

 # 
 win_rate = self._calculate_win_rate(trading_history)
 profit_factor = self._calculate_profit_factor(trading_history)

 return {
 "total_return": total_return,
 "annualized_return": annualized_return,
 "volatility": volatility,
 "sharpe_ratio": sharpe_ratio,
 "sortino_ratio": sortino_ratio,
 "calmar_ratio": calmar_ratio,
 "max_drawdown": max_drawdown,
 "win_rate": win_rate,
 "profit_factor": profit_factor,
 "total_trades": len(trading_history),
 "avg_holding_period": self._calculate_avg_holding_period(trading_history)
 }
```

 TradingAgents 