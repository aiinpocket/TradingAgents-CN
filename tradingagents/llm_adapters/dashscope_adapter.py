"""
阿里百炼大模型 (DashScope) 適配器
為 TradingAgents 提供阿里百炼大模型的 LangChain 兼容接口
"""

import os
import json
from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator, Sequence
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks.manager import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field, SecretStr
import dashscope
from dashscope import Generation
from ..config.config_manager import token_tracker

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')



class ChatDashScope(BaseChatModel):
    """阿里百炼大模型的 LangChain 適配器"""
    
    # 模型配置
    model: str = Field(default="qwen-turbo", description="DashScope 模型名稱")
    api_key: Optional[SecretStr] = Field(default=None, description="DashScope API 密鑰")
    temperature: float = Field(default=0.1, description="生成溫度")
    max_tokens: int = Field(default=2000, description="最大生成token數")
    top_p: float = Field(default=0.9, description="核採樣參數")
    
    # 內部屬性
    _client: Any = None
    
    def __init__(self, **kwargs):
        """初始化 DashScope 客戶端"""
        super().__init__(**kwargs)
        
        # 設置API密鑰
        api_key = self.api_key
        if api_key is None:
            api_key = os.getenv("DASHSCOPE_API_KEY")
        
        if api_key is None:
            raise ValueError(
                "DashScope API key not found. Please set DASHSCOPE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # 配置 DashScope
        if isinstance(api_key, SecretStr):
            dashscope.api_key = api_key.get_secret_value()
        else:
            dashscope.api_key = api_key
    
    @property
    def _llm_type(self) -> str:
        """返回LLM類型"""
        return "dashscope"
    
    def _convert_messages_to_dashscope_format(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """将 LangChain 消息格式轉換為 DashScope 格式"""
        dashscope_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                role = "system"
            elif isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                # 默認作為用戶消息處理
                role = "user"
            
            content = message.content
            if isinstance(content, list):
                # 處理多模態內容，目前只提取文本
                text_content = ""
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_content += item.get("text", "")
                content = text_content
            
            dashscope_messages.append({
                "role": role,
                "content": str(content)
            })
        
        return dashscope_messages
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """生成聊天回複"""
        
        # 轉換消息格式
        dashscope_messages = self._convert_messages_to_dashscope_format(messages)
        
        # 準备請求參數
        request_params = {
            "model": self.model,
            "messages": dashscope_messages,
            "result_format": "message",
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }
        
        # 添加停止詞
        if stop:
            request_params["stop"] = stop
        
        # 合並額外參數
        request_params.update(kwargs)
        
        try:
            # 調用 DashScope API
            response = Generation.call(**request_params)
            
            if response.status_code == 200:
                # 解析響應
                output = response.output
                message_content = output.choices[0].message.content
                
                # 提取token使用量信息
                input_tokens = 0
                output_tokens = 0
                
                # DashScope API響應中包含usage信息
                if hasattr(response, 'usage') and response.usage:
                    usage = response.usage
                    # 根據API文档，usage可能包含input_tokens和output_tokens
                    if hasattr(usage, 'input_tokens'):
                        input_tokens = usage.input_tokens
                    if hasattr(usage, 'output_tokens'):
                        output_tokens = usage.output_tokens
                    # 有些情况下可能是total_tokens
                    elif hasattr(usage, 'total_tokens'):
                        # 估算輸入和輸出token（如果没有分別提供）
                        total_tokens = usage.total_tokens
                        # 簡單估算：假設輸入占30%，輸出占70%
                        input_tokens = int(total_tokens * 0.3)
                        output_tokens = int(total_tokens * 0.7)
                
                # 記錄token使用量
                if input_tokens > 0 or output_tokens > 0:
                    try:
                        # 生成會話ID（如果没有提供）
                        session_id = kwargs.get('session_id', f"dashscope_{hash(str(messages))%10000}")
                        analysis_type = kwargs.get('analysis_type', 'stock_analysis')
                        
                        # 使用TokenTracker記錄使用量
                        token_tracker.track_usage(
                            provider="dashscope",
                            model_name=self.model,
                            input_tokens=input_tokens,
                            output_tokens=output_tokens,
                            session_id=session_id,
                            analysis_type=analysis_type
                        )
                    except Exception as track_error:
                        # 記錄失败不應该影響主要功能
                        logger.info(f"Token tracking failed: {track_error}")
                
                # 創建 AI 消息
                ai_message = AIMessage(content=message_content)
                
                # 創建生成結果
                generation = ChatGeneration(message=ai_message)
                
                return ChatResult(generations=[generation])
            else:
                raise Exception(f"DashScope API error: {response.code} - {response.message}")
                
        except Exception as e:
            raise Exception(f"Error calling DashScope API: {str(e)}")
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """異步生成聊天回複"""
        # 目前使用同步方法，後续可以實現真正的異步
        return self._generate(messages, stop, run_manager, **kwargs)
    
    def bind_tools(
        self,
        tools: Sequence[Union[Dict[str, Any], type, BaseTool]],
        **kwargs: Any,
    ) -> "ChatDashScope":
        """绑定工具到模型"""
        # 註意：DashScope 目前不直接支持工具調用
        # 這里我們返回一個新的實例，但實际上工具調用需要在應用層處理
        formatted_tools = []
        for tool in tools:
            if hasattr(tool, "name") and hasattr(tool, "description"):
                # 這是一個 BaseTool 實例
                formatted_tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": getattr(tool, "args_schema", {})
                })
            elif isinstance(tool, dict):
                formatted_tools.append(tool)
            else:
                # 嘗試轉換為 OpenAI 工具格式
                try:
                    formatted_tools.append(convert_to_openai_tool(tool))
                except Exception:
                    pass

        # 創建新實例，保存工具信息
        new_instance = self.__class__(
            model=self.model,
            api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            top_p=self.top_p,
            **kwargs
        )
        new_instance._tools = formatted_tools
        return new_instance

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回標识參數"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
        }


# 支持的模型列表
DASHSCOPE_MODELS = {
    # 通義千問系列
    "qwen-turbo": {
        "description": "通義千問 Turbo - 快速響應，適合日常對話",
        "context_length": 8192,
        "recommended_for": ["快速任務", "日常對話", "簡單分析"]
    },
    "qwen-plus": {
        "description": "通義千問 Plus - 平衡性能和成本",
        "context_length": 32768,
        "recommended_for": ["複雜分析", "專業任務", "深度思考"]
    },
    "qwen-max": {
        "description": "通義千問 Max - 最强性能",
        "context_length": 32768,
        "recommended_for": ["最複雜任務", "專業分析", "高质量輸出"]
    },
    "qwen-max-longcontext": {
        "description": "通義千問 Max 長文本版 - 支持超長上下文",
        "context_length": 1000000,
        "recommended_for": ["長文档分析", "大量數據處理", "複雜推理"]
    },
}


def get_available_models() -> Dict[str, Dict[str, Any]]:
    """獲取可用的 DashScope 模型列表"""
    return DASHSCOPE_MODELS


def create_dashscope_llm(
    model: str = "qwen-plus",
    api_key: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 2000,
    **kwargs
) -> ChatDashScope:
    """創建 DashScope LLM 實例的便捷函數"""
    
    return ChatDashScope(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )
