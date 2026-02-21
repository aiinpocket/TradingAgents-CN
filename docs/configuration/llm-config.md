# (v0.1.7)

## 

TradingAgents-CN OpenAI Anthropic LLM 

## v0.1.7 LLM

- ****: 
- ****: 
- ****: Function Calling

## LLM 

### 1. OpenAI

#### 
```python
openai_models = {
 "gpt-4o": {
 "description": " GPT-4 ",
 "context_length": 128000,
 "cost_per_1k_tokens": {"input": 0.005, "output": 0.015},
 "recommended_for": ["", "", ""]
 },
 "gpt-4o-mini": {
 "description": " GPT-4 ",
 "context_length": 128000,
 "cost_per_1k_tokens": {"input": 0.00015, "output": 0.0006},
 "recommended_for": ["", "", "API"]
 },
 "gpt-4-turbo": {
 "description": "GPT-4 Turbo ",
 "context_length": 128000,
 "cost_per_1k_tokens": {"input": 0.01, "output": 0.03},
 "recommended_for": ["", ""]
 },
 "gpt-3.5-turbo": {
 "description": "",
 "context_length": 16385,
 "cost_per_1k_tokens": {"input": 0.0005, "output": 0.0015},
 "recommended_for": ["", "", ""]
 }
}
```

#### 
```python
# OpenAI 
openai_config = {
 "llm_provider": "openai",
 "backend_url": "https://api.openai.com/v1",
 "deep_think_llm": "gpt-4o", # 
 "quick_think_llm": "gpt-4o-mini", # 
 "api_key": os.getenv("OPENAI_API_KEY"),

 # 
 "model_params": {
 "temperature": 0.1, # 
 "max_tokens": 2000, # 
 "top_p": 0.9, # 
 "frequency_penalty": 0.0, # 
 "presence_penalty": 0.0, # 
 },

 # 
 "rate_limits": {
 "requests_per_minute": 3500, # 
 "tokens_per_minute": 90000, # token
 },

 # 
 "retry_config": {
 "max_retries": 3,
 "backoff_factor": 2,
 "timeout": 60
 }
}
```

### 2. Anthropic Claude

#### 
```python
anthropic_models = {
 "claude-3-opus-20240229": {
 "description": " Claude ",
 "context_length": 200000,
 "cost_per_1k_tokens": {"input": 0.015, "output": 0.075},
 "recommended_for": ["", "", ""]
 },
 "claude-3-sonnet-20240229": {
 "description": "",
 "context_length": 200000,
 "cost_per_1k_tokens": {"input": 0.003, "output": 0.015},
 "recommended_for": ["", ""]
 },
 "claude-3-haiku-20240307": {
 "description": "",
 "context_length": 200000,
 "cost_per_1k_tokens": {"input": 0.00025, "output": 0.00125},
 "recommended_for": ["", "", ""]
 }
}
```

#### 
```python
# Anthropic 
anthropic_config = {
 "llm_provider": "anthropic",
 "backend_url": "https://api.anthropic.com",
 "deep_think_llm": "claude-3-opus-20240229",
 "quick_think_llm": "claude-3-haiku-20240307",
 "api_key": os.getenv("ANTHROPIC_API_KEY"),

 # 
 "model_params": {
 "temperature": 0.1,
 "max_tokens": 2000,
 "top_p": 0.9,
 "top_k": 40,
 },

 # 
 "rate_limits": {
 "requests_per_minute": 1000,
 "tokens_per_minute": 40000,
 }
}
```

## LLM 

### 
```python
class LLMSelector:
 """LLM - """

 def __init__(self, config: Dict):
 self.config = config
 self.task_model_mapping = self._initialize_task_mapping()

 def select_model(self, task_type: str, complexity: str = "medium") -> str:
 """"""

 task_config = self.task_model_mapping.get(task_type, {})

 if complexity == "high":
 return task_config.get("high_complexity", self.config["deep_think_llm"])
 elif complexity == "low":
 return task_config.get("low_complexity", self.config["quick_think_llm"])
 else:
 return task_config.get("medium_complexity", self.config["deep_think_llm"])

 def _initialize_task_mapping(self) -> Dict:
 """-"""
 return {
 "fundamental_analysis": {
 "high_complexity": "gpt-4o",
 "medium_complexity": "gpt-4o-mini",
 "low_complexity": "gpt-3.5-turbo"
 },
 "technical_analysis": {
 "high_complexity": "claude-3-opus-20240229",
 "medium_complexity": "claude-3-sonnet-20240229",
 "low_complexity": "claude-3-haiku-20240307"
 },
 "news_analysis": {
 "high_complexity": "gpt-4o",
 "medium_complexity": "gpt-4o-mini",
 "low_complexity": "gpt-4o-mini"
 },
 "social_sentiment": {
 "high_complexity": "claude-3-sonnet-20240229",
 "medium_complexity": "gpt-4o-mini",
 "low_complexity": "gpt-4o-mini"
 },
 "risk_assessment": {
 "high_complexity": "gpt-4o",
 "medium_complexity": "claude-3-sonnet-20240229",
 "low_complexity": "gpt-4o-mini"
 },
 "trading_decision": {
 "high_complexity": "gpt-4o",
 "medium_complexity": "gpt-4o",
 "low_complexity": "claude-3-sonnet-20240229"
 }
 }
```

### 
```python
class CostOptimizer:
 """ - """

 def __init__(self, budget_config: Dict):
 self.daily_budget = budget_config.get("daily_budget", 100) # 
 self.cost_tracking = {}
 self.model_costs = self._load_model_costs()

 def get_cost_optimized_config(self, current_usage: Dict) -> Dict:
 """"""

 remaining_budget = self._calculate_remaining_budget(current_usage)

 if remaining_budget > 50: # 
 return {
 "deep_think_llm": "gpt-4o",
 "quick_think_llm": "gpt-4o-mini",
 "max_debate_rounds": 3
 }
 elif remaining_budget > 20: # 
 return {
 "deep_think_llm": "gpt-4o-mini",
 "quick_think_llm": "gpt-4o-mini",
 "max_debate_rounds": 2
 }
 else: # 
 return {
 "deep_think_llm": "gpt-3.5-turbo",
 "quick_think_llm": "gpt-3.5-turbo",
 "max_debate_rounds": 1
 }

 def estimate_request_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
 """"""

 model_cost = self.model_costs.get(model, {"input": 0.001, "output": 0.002})

 input_cost = (input_tokens / 1000) * model_cost["input"]
 output_cost = (output_tokens / 1000) * model_cost["output"]

 return input_cost + output_cost
```

## 

### 
```python
class PromptOptimizer:
 """"""

 def __init__(self):
 self.prompt_templates = self._load_prompt_templates()

 def optimize_prompt(self, task_type: str, model: str, context: Dict) -> str:
 """"""

 base_prompt = self.prompt_templates[task_type]["base"]

 # 
 if "gpt" in model.lower():
 optimized_prompt = self._optimize_for_gpt(base_prompt, context)
 elif "claude" in model.lower():
 optimized_prompt = self._optimize_for_claude(base_prompt, context)
 else:
 optimized_prompt = base_prompt

 return optimized_prompt

 def _optimize_for_gpt(self, prompt: str, context: Dict) -> str:
 """ GPT """

 # GPT 
 structured_prompt = f"""
: {context.get('task_description', '')}

:
1. 
2. 
3. 
4. 

:
{context.get('data', '')}

:
- : []
- : []
- : []
- : [0-1]
"""
 return structured_prompt

 def _optimize_for_claude(self, prompt: str, context: Dict) -> str:
 """ Claude """

 # Claude 
 conversational_prompt = f"""


{context.get('data', '')}

:
1. 
2. 
3. 
4. 


"""
 return conversational_prompt
```

### 
```python
class LLMConcurrencyManager:
 """LLM """

 def __init__(self, config: Dict):
 self.config = config
 self.semaphores = self._initialize_semaphores()
 self.rate_limiters = self._initialize_rate_limiters()

 def _initialize_semaphores(self) -> Dict:
 """"""
 return {
 "openai": asyncio.Semaphore(10), # OpenAI 10
 "anthropic": asyncio.Semaphore(5), # Anthropic 5
 }

 async def execute_with_concurrency_control(self, provider: str, llm_call: callable) -> Any:
 """LLM"""

 semaphore = self.semaphores.get(provider)
 rate_limiter = self.rate_limiters.get(provider)

 async with semaphore:
 await rate_limiter.acquire()
 try:
 result = await llm_call()
 return result
 except Exception as e:
 # 
 if "rate_limit" in str(e).lower():
 await asyncio.sleep(60) # 1
 return await llm_call()
 else:
 raise e
```

## 

### LLM 
```python
class LLMMonitor:
 """LLM """

 def __init__(self):
 self.metrics = {
 "request_count": defaultdict(int),
 "response_times": defaultdict(list),
 "token_usage": defaultdict(dict),
 "error_rates": defaultdict(float),
 "costs": defaultdict(float)
 }

 def record_request(self, model: str, response_time: float,
 input_tokens: int, output_tokens: int, cost: float):
 """"""

 self.metrics["request_count"][model] += 1
 self.metrics["response_times"][model].append(response_time)

 if model not in self.metrics["token_usage"]:
 self.metrics["token_usage"][model] = {"input": 0, "output": 0}

 self.metrics["token_usage"][model]["input"] += input_tokens
 self.metrics["token_usage"][model]["output"] += output_tokens
 self.metrics["costs"][model] += cost

 def get_performance_report(self) -> Dict:
 """"""

 report = {}

 for model in self.metrics["request_count"]:
 response_times = self.metrics["response_times"][model]

 report[model] = {
 "total_requests": self.metrics["request_count"][model],
 "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
 "total_input_tokens": self.metrics["token_usage"][model].get("input", 0),
 "total_output_tokens": self.metrics["token_usage"][model].get("output", 0),
 "total_cost": self.metrics["costs"][model],
 "avg_cost_per_request": self.metrics["costs"][model] / self.metrics["request_count"][model] if self.metrics["request_count"][model] > 0 else 0
 }

 return report
```

## 

### 1. 
- ****: GPT-4o Claude-3-Opus
- ****: GPT-4o-mini Claude-3-Sonnet
- ****: GPT-3.5-turbo Claude-3-Haiku

### 2. 
- 
- 
- 
- token

### 3. 
- 
- 
- 
- 

LLM
