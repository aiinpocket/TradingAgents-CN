#!/usr/bin/env python3
"""
DeepSeek直接適配器，不依賴langchain_openai，避免DefaultHttpxClient兼容性問題
"""

import os
import json
from typing import Any, Dict, List, Optional, Union
from openai import OpenAI
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

import logging
logger = logging.getLogger(__name__)

class DeepSeekDirectAdapter:
    """DeepSeek直接適配器，使用OpenAI庫直接調用DeepSeek API"""
    
    def __init__(
        self,
        model: str = "deepseek-chat",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepseek.com"
    ):
        """
        初始化DeepSeek直接適配器
        
        Args:
            model: 模型名稱
            temperature: 溫度參數
            max_tokens: 最大token數
            api_key: API密鑰，如果不提供則從環境變量獲取
            base_url: API基础URL
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 獲取API密鑰
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("未找到DEEPSEEK_API_KEY，請在.env文件中配置或通過參數傳入")
        
        # 創建OpenAI客戶端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        
        logger.info(f"✅ DeepSeek直接適配器初始化成功，模型: {model}")
    
    def invoke(self, messages: Union[str, List[Dict[str, str]]]) -> str:
        """
        調用DeepSeek API
        
        Args:
            messages: 消息內容，可以是字符串或消息列表
            
        Returns:
            str: 模型響應
        """
        try:
            # 處理輸入消息格式
            if isinstance(messages, str):
                formatted_messages = [{"role": "user", "content": messages}]
            elif isinstance(messages, list):
                formatted_messages = messages
            else:
                raise ValueError(f"不支持的消息格式: {type(messages)}")
            
            # 調用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            result = response.choices[0].message.content
            logger.debug(f"DeepSeek API調用成功，響應長度: {len(result)}")
            return result
            
        except Exception as e:
            logger.error(f"DeepSeek API調用失败: {e}")
            raise
    
    def chat(self, message: str) -> str:
        """
        簡單聊天接口
        
        Args:
            message: 用戶消息
            
        Returns:
            str: 模型響應
        """
        return self.invoke(message)
    
    def analyze_with_tools(self, query: str, tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        使用工具進行分析
        
        Args:
            query: 查詢內容
            tools: 可用工具列表
            
        Returns:
            Dict: 分析結果
        """
        try:
            # 構建包含工具信息的提示
            tools_description = "\n".join([
                f"- {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}"
                for tool in tools
            ])
            
            prompt = f"""
你是一個專業的股票分析師。請根據以下查詢進行分析：

查詢：{query}

可用工具：
{tools_description}

請提供詳細的分析結果，包括：
1. 分析思路
2. 關键發現
3. 投資建议
4. 風險提示

請用中文回答。
"""
            
            response = self.invoke(prompt)
            
            return {
                "query": query,
                "analysis": response,
                "tools_used": [tool.get('name') for tool in tools],
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"工具分析失败: {e}")
            return {
                "query": query,
                "analysis": f"分析失败: {str(e)}",
                "tools_used": [],
                "status": "error"
            }

def create_deepseek_direct_adapter(
    model: str = "deepseek-chat",
    temperature: float = 0.1,
    max_tokens: int = 1000,
    **kwargs
) -> DeepSeekDirectAdapter:
    """
    創建DeepSeek直接適配器的便捷函數
    
    Args:
        model: 模型名稱
        temperature: 溫度參數
        max_tokens: 最大token數
        **kwargs: 其他參數
        
    Returns:
        DeepSeekDirectAdapter: 適配器實例
    """
    return DeepSeekDirectAdapter(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        **kwargs
    )