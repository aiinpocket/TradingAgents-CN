# 大語言模型配置 (v0.1.7)

## 概述

TradingAgents-CN 框架支援多種大語言模型提供商，包括 Google AI、OpenAI 和 Anthropic。本文件詳細介紹了如何配置和優化不同的 LLM 以獲得最佳效能和成本效益。

## 🎯 v0.1.7 LLM支援更新

- ✅ **智慧路由**: 根據任務自動選擇最優模型
- ✅ **成本控制**: 詳細的成本監控和限制
- ✅ **工具呼叫**: 完整的Function Calling支援

## 支援的 LLM 提供商

### 1. 🌍 Google AI (推薦)

#### 支援的模型
```python
gemini_models = {
    "gemini-1.5-pro": {
        "description": "Gemini 1.5 Pro模型",
        "context_length": 1000000,
        "cost_per_1k_tokens": {"input": 0.0035, "output": 0.0105},
        "recommended_for": ["複雜推理", "長文字處理", "多模態分析"],
        "features": ["超長上下文", "推理能力強", "多模態支援"]
    },
    "gemini-1.5-flash": {
        "description": "Gemini 1.5 Flash模型",
        "context_length": 1000000,
        "cost_per_1k_tokens": {"input": 0.00035, "output": 0.00105},
        "recommended_for": ["快速任務", "批次處理", "成本敏感"],
        "features": ["響應快速", "成本低", "效能均衡"]
    }
}
```

### 2. OpenAI

#### 支援的模型
```python
openai_models = {
    "gpt-4o": {
        "description": "最新的 GPT-4 優化版本",
        "context_length": 128000,
        "cost_per_1k_tokens": {"input": 0.005, "output": 0.015},
        "recommended_for": ["深度分析", "複雜推理", "高品質輸出"]
    },
    "gpt-4o-mini": {
        "description": "輕量級 GPT-4 版本",
        "context_length": 128000,
        "cost_per_1k_tokens": {"input": 0.00015, "output": 0.0006},
        "recommended_for": ["快速任務", "成本敏感場景", "大量API呼叫"]
    },
    "gpt-4-turbo": {
        "description": "GPT-4 Turbo 版本",
        "context_length": 128000,
        "cost_per_1k_tokens": {"input": 0.01, "output": 0.03},
        "recommended_for": ["平衡效能和成本", "標準分析任務"]
    },
    "gpt-3.5-turbo": {
        "description": "經濟實用的選擇",
        "context_length": 16385,
        "cost_per_1k_tokens": {"input": 0.0005, "output": 0.0015},
        "recommended_for": ["簡單任務", "預算有限", "快速響應"]
    }
}
```

#### 配置示例
```python
# OpenAI 配置
openai_config = {
    "llm_provider": "openai",
    "backend_url": "https://api.openai.com/v1",
    "deep_think_llm": "gpt-4o",           # 用於複雜分析
    "quick_think_llm": "gpt-4o-mini",     # 用於簡單任務
    "api_key": os.getenv("OPENAI_API_KEY"),

    # 模型參數
    "model_params": {
        "temperature": 0.1,               # 低溫度保證一致性
        "max_tokens": 2000,               # 最大輸出長度
        "top_p": 0.9,                     # 核採樣參數
        "frequency_penalty": 0.0,         # 頻率懲罰
        "presence_penalty": 0.0,          # 存在懲罰
    },

    # 速率限制
    "rate_limits": {
        "requests_per_minute": 3500,      # 每分鐘請求數
        "tokens_per_minute": 90000,       # 每分鐘token數
    },

    # 重試配置
    "retry_config": {
        "max_retries": 3,
        "backoff_factor": 2,
        "timeout": 60
    }
}
```

### 3. Anthropic Claude

#### 支援的模型
```python
anthropic_models = {
    "claude-3-opus-20240229": {
        "description": "最強大的 Claude 模型",
        "context_length": 200000,
        "cost_per_1k_tokens": {"input": 0.015, "output": 0.075},
        "recommended_for": ["最複雜的分析", "高品質推理", "創意任務"]
    },
    "claude-3-sonnet-20240229": {
        "description": "平衡效能和成本",
        "context_length": 200000,
        "cost_per_1k_tokens": {"input": 0.003, "output": 0.015},
        "recommended_for": ["標準分析任務", "平衡使用場景"]
    },
    "claude-3-haiku-20240307": {
        "description": "快速且經濟的選擇",
        "context_length": 200000,
        "cost_per_1k_tokens": {"input": 0.00025, "output": 0.00125},
        "recommended_for": ["快速任務", "大量呼叫", "成本優化"]
    }
}
```

#### 配置示例
```python
# Anthropic 配置
anthropic_config = {
    "llm_provider": "anthropic",
    "backend_url": "https://api.anthropic.com",
    "deep_think_llm": "claude-3-opus-20240229",
    "quick_think_llm": "claude-3-haiku-20240307",
    "api_key": os.getenv("ANTHROPIC_API_KEY"),

    # 模型參數
    "model_params": {
        "temperature": 0.1,
        "max_tokens": 2000,
        "top_p": 0.9,
        "top_k": 40,
    },

    # 速率限制
    "rate_limits": {
        "requests_per_minute": 1000,
        "tokens_per_minute": 40000,
    }
}
```

### 4. Google AI (Gemini)

#### 支援的模型
```python
google_models = {
    "gemini-pro": {
        "description": "Google 的主力模型",
        "context_length": 32768,
        "cost_per_1k_tokens": {"input": 0.0005, "output": 0.0015},
        "recommended_for": ["多模態任務", "程式碼分析", "推理任務"]
    },
    "gemini-pro-vision": {
        "description": "支援圖像的 Gemini 版本",
        "context_length": 16384,
        "cost_per_1k_tokens": {"input": 0.0005, "output": 0.0015},
        "recommended_for": ["圖表分析", "多模態輸入"]
    },
    "gemini-2.0-flash": {
        "description": "最新的快速版本",
        "context_length": 32768,
        "cost_per_1k_tokens": {"input": 0.0002, "output": 0.0008},
        "recommended_for": ["快速響應", "即時分析"]
    }
}
```

#### 配置示例
```python
# Google AI 配置
google_config = {
    "llm_provider": "google",
    "backend_url": "https://generativelanguage.googleapis.com/v1",
    "deep_think_llm": "gemini-pro",
    "quick_think_llm": "gemini-2.0-flash",
    "api_key": os.getenv("GOOGLE_API_KEY"),

    # 模型參數
    "model_params": {
        "temperature": 0.1,
        "max_output_tokens": 2000,
        "top_p": 0.9,
        "top_k": 40,
    }
}
```

## LLM 選擇策略

### 基於任務類型的選擇
```python
class LLMSelector:
    """LLM 選擇器 - 根據任務選擇最適合的模型"""

    def __init__(self, config: Dict):
        self.config = config
        self.task_model_mapping = self._initialize_task_mapping()

    def select_model(self, task_type: str, complexity: str = "medium") -> str:
        """根據任務類型和複雜度選擇模型"""

        task_config = self.task_model_mapping.get(task_type, {})

        if complexity == "high":
            return task_config.get("high_complexity", self.config["deep_think_llm"])
        elif complexity == "low":
            return task_config.get("low_complexity", self.config["quick_think_llm"])
        else:
            return task_config.get("medium_complexity", self.config["deep_think_llm"])

    def _initialize_task_mapping(self) -> Dict:
        """初始化任務-模型映射"""
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
                "low_complexity": "gemini-pro"
            },
            "social_sentiment": {
                "high_complexity": "claude-3-sonnet-20240229",
                "medium_complexity": "gpt-4o-mini",
                "low_complexity": "gemini-2.0-flash"
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

### 成本優化策略
```python
class CostOptimizer:
    """成本優化器 - 在效能和成本間找到平衡"""

    def __init__(self, budget_config: Dict):
        self.daily_budget = budget_config.get("daily_budget", 100)  # 美元
        self.cost_tracking = {}
        self.model_costs = self._load_model_costs()

    def get_cost_optimized_config(self, current_usage: Dict) -> Dict:
        """獲取成本優化的配置"""

        remaining_budget = self._calculate_remaining_budget(current_usage)

        if remaining_budget > 50:  # 預算充足
            return {
                "deep_think_llm": "gpt-4o",
                "quick_think_llm": "gpt-4o-mini",
                "max_debate_rounds": 3
            }
        elif remaining_budget > 20:  # 預算中等
            return {
                "deep_think_llm": "gpt-4o-mini",
                "quick_think_llm": "gpt-4o-mini",
                "max_debate_rounds": 2
            }
        else:  # 預算緊張
            return {
                "deep_think_llm": "gpt-3.5-turbo",
                "quick_think_llm": "gpt-3.5-turbo",
                "max_debate_rounds": 1
            }

    def estimate_request_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """估算請求成本"""

        model_cost = self.model_costs.get(model, {"input": 0.001, "output": 0.002})

        input_cost = (input_tokens / 1000) * model_cost["input"]
        output_cost = (output_tokens / 1000) * model_cost["output"]

        return input_cost + output_cost
```

## 效能優化

### 提示詞優化
```python
class PromptOptimizer:
    """提示詞優化器"""

    def __init__(self):
        self.prompt_templates = self._load_prompt_templates()

    def optimize_prompt(self, task_type: str, model: str, context: Dict) -> str:
        """優化提示詞"""

        base_prompt = self.prompt_templates[task_type]["base"]

        # 根據模型特點調整提示詞
        if "gpt" in model.lower():
            optimized_prompt = self._optimize_for_gpt(base_prompt, context)
        elif "claude" in model.lower():
            optimized_prompt = self._optimize_for_claude(base_prompt, context)
        elif "gemini" in model.lower():
            optimized_prompt = self._optimize_for_gemini(base_prompt, context)
        else:
            optimized_prompt = base_prompt

        return optimized_prompt

    def _optimize_for_gpt(self, prompt: str, context: Dict) -> str:
        """為 GPT 模型優化提示詞"""

        # GPT 喜歡結構化的指令
        structured_prompt = f"""
任務: {context.get('task_description', '')}

指令:
1. 仔細分析提供的資料
2. 應用相關的金融分析方法
3. 提供清晰的結論和建議
4. 包含置信度評估

資料:
{context.get('data', '')}

請按照以下格式回答:
- 分析結果: [你的分析]
- 結論: [主要結論]
- 建議: [具體建議]
- 置信度: [0-1之間的數值]
"""
        return structured_prompt

    def _optimize_for_claude(self, prompt: str, context: Dict) -> str:
        """為 Claude 模型優化提示詞"""

        # Claude 喜歡對話式的提示
        conversational_prompt = f"""
我需要你作為一個專業的金融分析師來幫助我分析以下資料。

{context.get('data', '')}

請你:
1. 深入分析這些資料的含義
2. 識別關鍵的趨勢和模式
3. 評估潛在的風險和機會
4. 給出你的專業建議

請用專業但易懂的語言回答，並解釋你的推理過程。
"""
        return conversational_prompt
```

### 並行控制
```python
class LLMConcurrencyManager:
    """LLM 並行管理器"""

    def __init__(self, config: Dict):
        self.config = config
        self.semaphores = self._initialize_semaphores()
        self.rate_limiters = self._initialize_rate_limiters()

    def _initialize_semaphores(self) -> Dict:
        """初始化信號量控制並行"""
        return {
            "openai": asyncio.Semaphore(10),      # OpenAI 最多10個並行
            "anthropic": asyncio.Semaphore(5),    # Anthropic 最多5個並行
            "google": asyncio.Semaphore(8)        # Google 最多8個並行
        }

    async def execute_with_concurrency_control(self, provider: str, llm_call: callable) -> Any:
        """在並行控制下執行LLM呼叫"""

        semaphore = self.semaphores.get(provider)
        rate_limiter = self.rate_limiters.get(provider)

        async with semaphore:
            await rate_limiter.acquire()
            try:
                result = await llm_call()
                return result
            except Exception as e:
                # 處理速率限制錯誤
                if "rate_limit" in str(e).lower():
                    await asyncio.sleep(60)  # 等待1分鐘
                    return await llm_call()
                else:
                    raise e
```

## 監控和除錯

### LLM 效能監控
```python
class LLMMonitor:
    """LLM 效能監控"""

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
        """記錄請求指標"""

        self.metrics["request_count"][model] += 1
        self.metrics["response_times"][model].append(response_time)

        if model not in self.metrics["token_usage"]:
            self.metrics["token_usage"][model] = {"input": 0, "output": 0}

        self.metrics["token_usage"][model]["input"] += input_tokens
        self.metrics["token_usage"][model]["output"] += output_tokens
        self.metrics["costs"][model] += cost

    def get_performance_report(self) -> Dict:
        """獲取效能報告"""

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

## 最佳實踐

### 1. 模型選擇建議
- **高精度任務**: 使用 GPT-4o 或 Claude-3-Opus
- **平衡場景**: 使用 GPT-4o-mini 或 Claude-3-Sonnet
- **成本敏感**: 使用 GPT-3.5-turbo 或 Claude-3-Haiku
- **快速響應**: 使用 Gemini-2.0-flash

### 2. 成本控制策略
- 設定每日預算限制
- 使用較小模型處理簡單任務
- 實施智慧快取減少重複呼叫
- 監控token使用量

### 3. 效能優化技巧
- 優化提示詞長度和結構
- 使用適當的溫度參數
- 實施並行控制避免速率限制
- 定期監控和調整配置

透過合理的LLM配置和優化，可以在保證分析品質的同時控制成本並提高系統效能。
