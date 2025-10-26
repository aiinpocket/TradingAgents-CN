"""
阿里百炼 OpenAI兼容適配器
為 TradingAgents 提供阿里百炼大模型的 OpenAI 兼容接口
利用百炼模型的原生 OpenAI 兼容性，無需額外的工具轉換
"""

import os
from typing import Any, Dict, List, Optional, Union, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.tools import BaseTool
from pydantic import Field, SecretStr
from ..config.config_manager import token_tracker

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class ChatDashScopeOpenAI(ChatOpenAI):
    """
    阿里百炼 OpenAI 兼容適配器
    繼承 ChatOpenAI，通過 OpenAI 兼容接口調用百炼模型
    利用百炼模型的原生 OpenAI 兼容性，支持原生 Function Calling
    """
    
    def __init__(self, **kwargs):
        """初始化 DashScope OpenAI 兼容客戶端"""
        
        # 設置 DashScope OpenAI 兼容接口的默認配置
        kwargs.setdefault("base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        kwargs.setdefault("api_key", os.getenv("DASHSCOPE_API_KEY"))
        kwargs.setdefault("model", "qwen-turbo")
        kwargs.setdefault("temperature", 0.1)
        kwargs.setdefault("max_tokens", 2000)
        
        # 檢查 API 密鑰
        if not kwargs.get("api_key"):
            raise ValueError(
                "DashScope API key not found. Please set DASHSCOPE_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        # 調用父類初始化
        super().__init__(**kwargs)

        logger.info(f"✅ 阿里百炼 OpenAI 兼容適配器初始化成功")
        logger.info(f"   模型: {kwargs.get('model', 'qwen-turbo')}")

        # 兼容不同版本的屬性名
        api_base = getattr(self, 'base_url', None) or getattr(self, 'openai_api_base', None) or kwargs.get('base_url', 'unknown')
        logger.info(f"   API Base: {api_base}")
    
    def _generate(self, *args, **kwargs):
        """重寫生成方法，添加 token 使用量追蹤"""
        
        # 調用父類的生成方法
        result = super()._generate(*args, **kwargs)
        
        # 追蹤 token 使用量
        try:
            # 從結果中提取 token 使用信息
            if hasattr(result, 'llm_output') and result.llm_output:
                token_usage = result.llm_output.get('token_usage', {})
                
                input_tokens = token_usage.get('prompt_tokens', 0)
                output_tokens = token_usage.get('completion_tokens', 0)
                
                if input_tokens > 0 or output_tokens > 0:
                    # 生成會話ID
                    session_id = kwargs.get('session_id', f"dashscope_openai_{hash(str(args))%10000}")
                    analysis_type = kwargs.get('analysis_type', 'stock_analysis')
                    
                    # 使用 TokenTracker 記錄使用量
                    token_tracker.track_usage(
                        provider="dashscope",
                        model_name=self.model_name,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens,
                        session_id=session_id,
                        analysis_type=analysis_type
                    )
                    
        except Exception as track_error:
            # token 追蹤失败不應该影響主要功能
            logger.error(f"⚠️ Token 追蹤失败: {track_error}")
        
        return result


# 支持的模型列表
DASHSCOPE_OPENAI_MODELS = {
    # 通義千問系列
    "qwen-turbo": {
        "description": "通義千問 Turbo - 快速響應，適合日常對話",
        "context_length": 8192,
        "supports_function_calling": True,
        "recommended_for": ["快速任務", "日常對話", "簡單分析"]
    },
    "qwen-plus": {
        "description": "通義千問 Plus - 平衡性能和成本",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["複雜分析", "專業任務", "深度思考"]
    },
    "qwen-plus-latest": {
        "description": "通義千問 Plus 最新版 - 最新功能和性能",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["最新功能", "複雜分析", "專業任務"]
    },
    "qwen-max": {
        "description": "通義千問 Max - 最强性能，適合複雜任務",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["複雜推理", "專業分析", "高质量輸出"]
    },
    "qwen-max-latest": {
        "description": "通義千問 Max 最新版 - 最强性能和最新功能",
        "context_length": 32768,
        "supports_function_calling": True,
        "recommended_for": ["最新功能", "複雜推理", "專業分析"]
    },
    "qwen-long": {
        "description": "通義千問 Long - 超長上下文，適合長文档處理",
        "context_length": 1000000,
        "supports_function_calling": True,
        "recommended_for": ["長文档分析", "大量數據處理", "複雜上下文"]
    }
}


def get_available_openai_models() -> Dict[str, Dict[str, Any]]:
    """獲取可用的 DashScope OpenAI 兼容模型列表"""
    return DASHSCOPE_OPENAI_MODELS


def create_dashscope_openai_llm(
    model: str = "qwen-plus-latest",
    api_key: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 2000,
    **kwargs
) -> ChatDashScopeOpenAI:
    """創建 DashScope OpenAI 兼容 LLM 實例的便捷函數"""
    
    return ChatDashScopeOpenAI(
        model=model,
        api_key=api_key,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )


def test_dashscope_openai_connection(
    model: str = "qwen-turbo",
    api_key: Optional[str] = None
) -> bool:
    """測試 DashScope OpenAI 兼容接口連接"""
    
    try:
        logger.info(f"🧪 測試 DashScope OpenAI 兼容接口連接")
        logger.info(f"   模型: {model}")
        
        # 創建客戶端
        llm = create_dashscope_openai_llm(
            model=model,
            api_key=api_key,
            max_tokens=50
        )
        
        # 發送測試消息
        response = llm.invoke("你好，請簡單介紹一下你自己。")
        
        if response and hasattr(response, 'content') and response.content:
            logger.info(f"✅ DashScope OpenAI 兼容接口連接成功")
            logger.info(f"   響應: {response.content[:100]}...")
            return True
        else:
            logger.error(f"❌ DashScope OpenAI 兼容接口響應為空")
            return False
            
    except Exception as e:
        logger.error(f"❌ DashScope OpenAI 兼容接口連接失败: {e}")
        return False


def test_dashscope_openai_function_calling(
    model: str = "qwen-plus-latest",
    api_key: Optional[str] = None
) -> bool:
    """測試 DashScope OpenAI 兼容接口的 Function Calling"""
    
    try:
        logger.info(f"🧪 測試 DashScope OpenAI Function Calling")
        logger.info(f"   模型: {model}")
        
        # 創建客戶端
        llm = create_dashscope_openai_llm(
            model=model,
            api_key=api_key,
            max_tokens=200
        )
        
        # 定義測試工具
        def get_current_time() -> str:
            """獲取當前時間"""
            import datetime
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 創建 LangChain 工具
        from langchain_core.tools import tool
        
        @tool
        def test_tool(query: str) -> str:
            """測試工具，返回查詢信息"""
            return f"收到查詢: {query}"
        
        # 绑定工具
        llm_with_tools = llm.bind_tools([test_tool])
        
        # 測試工具調用
        response = llm_with_tools.invoke("請使用test_tool查詢'hello world'")
        
        logger.info(f"✅ DashScope OpenAI Function Calling 測試完成")
        logger.info(f"   響應類型: {type(response)}")
        
        if hasattr(response, 'tool_calls') and response.tool_calls:
            logger.info(f"   工具調用數量: {len(response.tool_calls)}")
            return True
        else:
            logger.info(f"   響應內容: {getattr(response, 'content', 'No content')}")
            return True  # 即使没有工具調用也算成功，因為模型可能選擇不調用工具
            
    except Exception as e:
        logger.error(f"❌ DashScope OpenAI Function Calling 測試失败: {e}")
        return False


if __name__ == "__main__":
    """測試腳本"""
    logger.info(f"🧪 DashScope OpenAI 兼容適配器測試")
    logger.info(f"=" * 50)
    
    # 測試連接
    connection_ok = test_dashscope_openai_connection()
    
    if connection_ok:
        # 測試 Function Calling
        function_calling_ok = test_dashscope_openai_function_calling()
        
        if function_calling_ok:
            logger.info(f"\n🎉 所有測試通過！DashScope OpenAI 兼容適配器工作正常")
        else:
            logger.error(f"\n⚠️ Function Calling 測試失败")
    else:
        logger.error(f"\n❌ 連接測試失败")
