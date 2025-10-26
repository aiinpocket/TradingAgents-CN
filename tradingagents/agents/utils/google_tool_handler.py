#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google模型工具調用統一處理器

解決Google模型在工具調用時result.content為空的問題，
提供統一的工具調用處理逻辑供所有分析師使用。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

logger = logging.getLogger(__name__)

class GoogleToolCallHandler:
    """Google模型工具調用統一處理器"""
    
    @staticmethod
    def is_google_model(llm) -> bool:
        """檢查是否為Google模型"""
        return 'Google' in llm.__class__.__name__ or 'ChatGoogleOpenAI' in llm.__class__.__name__
    
    @staticmethod
    def handle_google_tool_calls(
        result: AIMessage,
        llm: Any,
        tools: List[Any],
        state: Dict[str, Any],
        analysis_prompt_template: str,
        analyst_name: str = "分析師"
    ) -> Tuple[str, List[Any]]:
        """
        統一處理Google模型的工具調用
        
        Args:
            result: LLM的第一次調用結果
            llm: 語言模型實例
            tools: 可用工具列表
            state: 當前狀態
            analysis_prompt_template: 分析提示詞模板
            analyst_name: 分析師名稱
            
        Returns:
            Tuple[str, List[Any]]: (分析報告, 消息列表)
        """
        
        # 驗證輸入參數
        logger.info(f"[{analyst_name}] 🔍 開始Google工具調用處理...")
        logger.debug(f"[{analyst_name}] 🔍 LLM類型: {llm.__class__.__name__}")
        logger.debug(f"[{analyst_name}] 🔍 工具數量: {len(tools) if tools else 0}")
        logger.debug(f"[{analyst_name}] 🔍 狀態類型: {type(state).__name__ if state else None}")
        
        if not GoogleToolCallHandler.is_google_model(llm):
            logger.warning(f"[{analyst_name}] ⚠️ 非Google模型，跳過特殊處理")
            logger.debug(f"[{analyst_name}] 🔍 模型檢查失败: {llm.__class__.__name__}")
            # 非Google模型，返回原始內容
            return result.content, [result]
        
        logger.info(f"[{analyst_name}] ✅ 確認為Google模型")
        logger.debug(f"[{analyst_name}] 🔍 結果類型: {type(result).__name__}")
        logger.debug(f"[{analyst_name}] 🔍 結果屬性: {[attr for attr in dir(result) if not attr.startswith('_')]}")
        
        # 檢查API調用是否成功
        if not hasattr(result, 'content'):
            logger.error(f"[{analyst_name}] ❌ Google模型API調用失败，無返回內容")
            logger.debug(f"[{analyst_name}] 🔍 結果對象缺少content屬性")
            return "Google模型API調用失败", []
        
        # 檢查是否有工具調用
        if not hasattr(result, 'tool_calls'):
            logger.warning(f"[{analyst_name}] ⚠️ 結果對象没有tool_calls屬性")
            logger.debug(f"[{analyst_name}] 🔍 可用屬性: {[attr for attr in dir(result) if not attr.startswith('_')]}")
            return result.content, [result]
        
        if not result.tool_calls:
            # 改進：提供更詳細的診斷信息
            logger.info(f"[{analyst_name}] ℹ️ Google模型未調用工具，可能原因：")
            logger.info(f"[{analyst_name}]   - 輸入消息為空或格式不正確")
            logger.info(f"[{analyst_name}]   - 模型認為不需要調用工具")
            logger.info(f"[{analyst_name}]   - 工具绑定可能存在問題")
            
            # 檢查輸入消息
            if "messages" in state:
                messages = state["messages"]
                if not messages:
                    logger.warning(f"[{analyst_name}] ⚠️ 輸入消息列表為空")
                else:
                    logger.info(f"[{analyst_name}] 📝 輸入消息數量: {len(messages)}")
                    for i, msg in enumerate(messages):
                        msg_type = type(msg).__name__
                        content_preview = str(msg.content)[:100] if hasattr(msg, 'content') else "無內容"
                        logger.info(f"[{analyst_name}]   消息 {i+1}: {msg_type} - {content_preview}...")
            
            # 檢查內容是否為分析報告
            content = result.content
            logger.info(f"[{analyst_name}] 🔍 檢查返回內容是否為分析報告...")
            logger.debug(f"[{analyst_name}] 🔍 內容類型: {type(content)}")
            logger.debug(f"[{analyst_name}] 🔍 內容長度: {len(content) if content else 0}")
            
            # 檢查內容是否包含分析報告的特征
            is_analysis_report = False
            analysis_keywords = ["分析", "報告", "总結", "評估", "建议", "風險", "趋势", "市場", "股票", "投資"]
            
            if content:
                # 檢查內容長度和關键詞
                if len(content) > 200:  # 假設分析報告至少有200個字符
                    keyword_count = sum(1 for keyword in analysis_keywords if keyword in content)
                    is_analysis_report = keyword_count >= 3  # 至少包含3個關键詞
                
                logger.info(f"[{analyst_name}] 🔍 內容判斷為{'分析報告' if is_analysis_report else '非分析報告'}")
                
                if is_analysis_report:
                    logger.info(f"[{analyst_name}] ✅ Google模型直接返回了分析報告，長度: {len(content)} 字符")
                    return content, [result]
            
            # 返回原始內容，但添加說明
            return result.content, [result]
        
        logger.info(f"[{analyst_name}] 🔧 Google模型調用了 {len(result.tool_calls)} 個工具")
        
        # 記錄工具調用詳情
        for i, tool_call in enumerate(result.tool_calls):
            logger.info(f"[{analyst_name}] 工具 {i+1}:")
            logger.info(f"[{analyst_name}]   ID: {tool_call.get('id', 'N/A')}")
            logger.info(f"[{analyst_name}]   名稱: {tool_call.get('name', 'N/A')}")
            logger.info(f"[{analyst_name}]   參數: {tool_call.get('args', {})}")
        
        try:
            # 執行工具調用
            tool_messages = []
            tool_results = []
            executed_tools = set()  # 防止重複調用同一工具
            
            logger.info(f"[{analyst_name}] 🔧 開始執行 {len(result.tool_calls)} 個工具調用...")
            
            # 驗證工具調用格式
            valid_tool_calls = []
            for i, tool_call in enumerate(result.tool_calls):
                if GoogleToolCallHandler._validate_tool_call(tool_call, i, analyst_name):
                    valid_tool_calls.append(tool_call)
                else:
                    # 嘗試修複工具調用
                    fixed_tool_call = GoogleToolCallHandler._fix_tool_call(tool_call, i, analyst_name)
                    if fixed_tool_call:
                        valid_tool_calls.append(fixed_tool_call)
            
            logger.info(f"[{analyst_name}] 🔧 有效工具調用: {len(valid_tool_calls)}/{len(result.tool_calls)}")
            
            for i, tool_call in enumerate(valid_tool_calls):
                tool_name = tool_call.get('name')
                tool_args = tool_call.get('args', {})
                tool_id = tool_call.get('id')
                
                # 防止重複調用同一工具（特別是統一市場數據工具）
                tool_signature = f"{tool_name}_{hash(str(tool_args))}"
                if tool_signature in executed_tools:
                    logger.warning(f"[{analyst_name}] ⚠️ 跳過重複工具調用: {tool_name}")
                    continue
                executed_tools.add(tool_signature)
                
                logger.info(f"[{analyst_name}] 🛠️ 執行工具 {i+1}/{len(valid_tool_calls)}: {tool_name}")
                logger.info(f"[{analyst_name}] 參數: {tool_args}")
                logger.debug(f"[{analyst_name}] 🔧 工具調用詳情: {tool_call}")
                
                # 找到對應的工具並執行
                tool_result = None
                available_tools = []
                
                for tool in tools:
                    current_tool_name = GoogleToolCallHandler._get_tool_name(tool)
                    available_tools.append(current_tool_name)
                    
                    if current_tool_name == tool_name:
                        try:
                            logger.debug(f"[{analyst_name}] 🔧 找到工具: {tool.__class__.__name__}")
                            logger.debug(f"[{analyst_name}] 🔧 工具類型檢查...")
                            
                            # 檢查工具類型並相應調用
                            if hasattr(tool, 'invoke'):
                                # LangChain工具，使用invoke方法
                                logger.info(f"[{analyst_name}] 🚀 正在調用LangChain工具.invoke()...")
                                tool_result = tool.invoke(tool_args)
                                logger.info(f"[{analyst_name}] ✅ LangChain工具執行成功，結果長度: {len(str(tool_result))} 字符")
                                logger.debug(f"[{analyst_name}] 🔧 工具結果類型: {type(tool_result)}")
                            elif callable(tool):
                                # 普通Python函數，直接調用
                                logger.info(f"[{analyst_name}] 🚀 正在調用Python函數工具...")
                                tool_result = tool(**tool_args)
                                logger.info(f"[{analyst_name}] ✅ Python函數工具執行成功，結果長度: {len(str(tool_result))} 字符")
                                logger.debug(f"[{analyst_name}] 🔧 工具結果類型: {type(tool_result)}")
                            else:
                                logger.error(f"[{analyst_name}] ❌ 工具類型不支持: {type(tool)}")
                                tool_result = f"工具類型不支持: {type(tool)}"
                            break
                        except Exception as tool_error:
                            logger.error(f"[{analyst_name}] ❌ 工具執行失败: {tool_error}")
                            logger.error(f"[{analyst_name}] ❌ 異常類型: {type(tool_error).__name__}")
                            logger.error(f"[{analyst_name}] ❌ 異常詳情: {str(tool_error)}")
                            
                            # 記錄詳細的異常堆棧
                            import traceback
                            error_traceback = traceback.format_exc()
                            logger.error(f"[{analyst_name}] ❌ 工具執行異常堆棧:\n{error_traceback}")
                            
                            tool_result = f"工具執行失败: {str(tool_error)}"
                
                logger.debug(f"[{analyst_name}] 🔧 可用工具列表: {available_tools}")
                
                if tool_result is None:
                    tool_result = f"未找到工具: {tool_name}"
                    logger.warning(f"[{analyst_name}] ⚠️ 未找到工具: {tool_name}")
                    logger.debug(f"[{analyst_name}] ⚠️ 工具名稱不匹配，期望: {tool_name}, 可用: {available_tools}")
                
                # 創建工具消息
                tool_message = ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_id
                )
                tool_messages.append(tool_message)
                tool_results.append(tool_result)
                logger.debug(f"[{analyst_name}] 🔧 創建工具消息，ID: {tool_message.tool_call_id}")
            
            logger.info(f"[{analyst_name}] 🔧 工具調用完成，成功: {len(tool_results)}, 总計: {len(result.tool_calls)}")
            
            # 第二次調用模型生成最终分析報告
            logger.info(f"[{analyst_name}] 🚀 基於工具結果生成最终分析報告...")
            
            # 安全地構建消息序列，確保所有消息都是有效的LangChain消息類型
            safe_messages = []
            
            # 添加歷史消息（只保留有效的LangChain消息）
            if "messages" in state and state["messages"]:
                for msg in state["messages"]:
                    try:
                        if hasattr(msg, 'content') and hasattr(msg, '__class__'):
                            # 檢查是否是有效的LangChain消息類型
                            msg_class_name = msg.__class__.__name__
                            if msg_class_name in ['HumanMessage', 'AIMessage', 'SystemMessage', 'ToolMessage']:
                                safe_messages.append(msg)
                            else:
                                # 轉換為HumanMessage
                                logger.warning(f"[{analyst_name}] ⚠️ 轉換非標準消息類型: {msg_class_name}")
                                safe_messages.append(HumanMessage(content=str(msg.content)))
                    except Exception as msg_error:
                        logger.warning(f"[{analyst_name}] ⚠️ 跳過無效消息: {msg_error}")
                        continue
            
            # 添加當前結果（確保是AIMessage）
            if hasattr(result, 'content'):
                safe_messages.append(result)
            
            # 添加工具消息
            safe_messages.extend(tool_messages)
            
            # 添加分析提示
            safe_messages.append(HumanMessage(content=analysis_prompt_template))
            
            # 檢查消息序列長度，避免過長
            total_length = sum(len(str(msg.content)) for msg in safe_messages if hasattr(msg, 'content'))
            if total_length > 50000:
                logger.warning(f"[{analyst_name}] ⚠️ 消息序列過長 ({total_length} 字符)，進行優化...")
                
                # 優化策略：保留最重要的消息
                optimized_messages = []
                
                # 保留最後的用戶消息
                if safe_messages and isinstance(safe_messages[0], HumanMessage):
                    optimized_messages.append(safe_messages[0])
                
                # 保留工具調用結果
                optimized_messages.append(result)
                
                # 保留工具消息（截斷過長的內容）
                for tool_msg in tool_messages:
                    if len(tool_msg.content) > 5000:
                        truncated_content = tool_msg.content[:5000] + "\n\n[註：數據已截斷以確保處理效率]"
                        optimized_tool_msg = ToolMessage(
                            content=truncated_content,
                            tool_call_id=tool_msg.tool_call_id
                        )
                        optimized_messages.append(optimized_tool_msg)
                    else:
                        optimized_messages.append(tool_msg)
                
                # 保留分析提示
                optimized_messages.append(HumanMessage(content=analysis_prompt_template))
                
                safe_messages = optimized_messages
                logger.info(f"[{analyst_name}] ✅ 消息序列優化完成，新長度: {sum(len(str(msg.content)) for msg in safe_messages)} 字符")
            
            logger.info(f"[{analyst_name}] 📊 最终消息序列: {len(safe_messages)} 條消息")
            
            # 檢查消息序列是否為空
            if not safe_messages:
                logger.error(f"[{analyst_name}] ❌ 消息序列為空，無法生成分析報告")
                tool_summary = "\n\n".join([f"工具結果 {i+1}:\n{str(result)}" for i, result in enumerate(tool_results)])
                report = f"{analyst_name}工具調用完成，獲得以下數據：\n\n{tool_summary}"
                return report, [result] + tool_messages
            
            # 生成最终分析報告
            try:
                logger.info(f"[{analyst_name}] 🔄 開始調用Google模型生成最终分析報告...")
                logger.debug(f"[{analyst_name}] 📋 LLM類型: {llm.__class__.__name__}")
                logger.debug(f"[{analyst_name}] 📋 消息數量: {len(safe_messages)}")
                
                # 記錄每個消息的類型和長度
                for i, msg in enumerate(safe_messages):
                    msg_type = msg.__class__.__name__
                    msg_length = len(str(msg.content)) if hasattr(msg, 'content') else 0
                    logger.debug(f"[{analyst_name}] 📋 消息 {i+1}: {msg_type}, 長度: {msg_length}")
                
                # 記錄分析提示的內容（前200字符）
                analysis_msg = safe_messages[-1] if safe_messages else None
                if analysis_msg and hasattr(analysis_msg, 'content'):
                    prompt_preview = str(analysis_msg.content)[:200] + "..." if len(str(analysis_msg.content)) > 200 else str(analysis_msg.content)
                    logger.debug(f"[{analyst_name}] 📋 分析提示預覽: {prompt_preview}")
                
                logger.info(f"[{analyst_name}] 🚀 正在調用LLM.invoke()...")
                final_result = llm.invoke(safe_messages)
                logger.info(f"[{analyst_name}] ✅ LLM.invoke()調用完成")
                
                # 詳細檢查返回結果
                logger.debug(f"[{analyst_name}] 🔍 檢查LLM返回結果...")
                logger.debug(f"[{analyst_name}] 🔍 返回結果類型: {type(final_result)}")
                logger.debug(f"[{analyst_name}] 🔍 返回結果屬性: {dir(final_result)}")
                
                if hasattr(final_result, 'content'):
                    content = final_result.content
                    logger.debug(f"[{analyst_name}] 🔍 內容類型: {type(content)}")
                    logger.debug(f"[{analyst_name}] 🔍 內容長度: {len(content) if content else 0}")
                    logger.debug(f"[{analyst_name}] 🔍 內容是否為空: {not content}")
                    
                    if content:
                        content_preview = content[:200] + "..." if len(content) > 200 else content
                        logger.debug(f"[{analyst_name}] 🔍 內容預覽: {content_preview}")
                        
                        report = content
                        logger.info(f"[{analyst_name}] ✅ Google模型最终分析報告生成成功，長度: {len(report)} 字符")
                        
                        # 返回完整的消息序列
                        all_messages = [result] + tool_messages + [final_result]
                        return report, all_messages
                    else:
                        logger.warning(f"[{analyst_name}] ⚠️ Google模型返回內容為空")
                        logger.debug(f"[{analyst_name}] 🔍 空內容詳情: repr={repr(content)}")
                else:
                    logger.warning(f"[{analyst_name}] ⚠️ Google模型返回結果没有content屬性")
                    logger.debug(f"[{analyst_name}] 🔍 可用屬性: {[attr for attr in dir(final_result) if not attr.startswith('_')]}")
                
                # 如果到這里，說明內容為空或没有content屬性
                logger.warning(f"[{analyst_name}] ⚠️ Google模型最终分析報告生成失败 - 內容為空")
                # 降級處理：基於工具結果生成簡單報告
                tool_summary = "\n\n".join([f"工具結果 {i+1}:\n{str(result)}" for i, result in enumerate(tool_results)])
                report = f"{analyst_name}工具調用完成，獲得以下數據：\n\n{tool_summary}"
                logger.info(f"[{analyst_name}] 🔄 使用降級報告，長度: {len(report)} 字符")
                return report, [result] + tool_messages
                
            except Exception as final_error:
                logger.error(f"[{analyst_name}] ❌ 最终分析報告生成失败: {final_error}")
                logger.error(f"[{analyst_name}] ❌ 異常類型: {type(final_error).__name__}")
                logger.error(f"[{analyst_name}] ❌ 異常詳情: {str(final_error)}")
                
                # 記錄詳細的異常堆棧
                import traceback
                error_traceback = traceback.format_exc()
                logger.error(f"[{analyst_name}] ❌ 異常堆棧:\n{error_traceback}")
                
                # 降級處理：基於工具結果生成簡單報告
                tool_summary = "\n\n".join([f"工具結果 {i+1}:\n{str(result)}" for i, result in enumerate(tool_results)])
                report = f"{analyst_name}工具調用完成，獲得以下數據：\n\n{tool_summary}"
                logger.info(f"[{analyst_name}] 🔄 異常後使用降級報告，長度: {len(report)} 字符")
                return report, [result] + tool_messages
                
        except Exception as e:
            logger.error(f"[{analyst_name}] ❌ Google模型工具調用處理失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 降級處理：返回工具調用信息
            tool_names = [tc.get('name', 'unknown') for tc in result.tool_calls]
            report = f"{analyst_name}調用了工具 {tool_names} 但處理失败: {str(e)}"
            return report, [result]
    
    @staticmethod
    def _get_tool_name(tool):
        """獲取工具名稱"""
        if hasattr(tool, 'name'):
            return tool.name
        elif hasattr(tool, '__name__'):
            return tool.__name__
        else:
            return str(tool)
    
    @staticmethod
    def _validate_tool_call(tool_call, index, analyst_name):
        """驗證工具調用格式"""
        try:
            if not isinstance(tool_call, dict):
                logger.warning(f"[{analyst_name}] ⚠️ 工具調用 {index} 不是字典格式: {type(tool_call)}")
                return False
            
            # 檢查必需字段
            required_fields = ['name', 'args', 'id']
            for field in required_fields:
                if field not in tool_call:
                    logger.warning(f"[{analyst_name}] ⚠️ 工具調用 {index} 缺少字段 '{field}': {tool_call}")
                    return False
            
            # 檢查工具名稱
            tool_name = tool_call.get('name')
            if not isinstance(tool_name, str) or not tool_name.strip():
                logger.warning(f"[{analyst_name}] ⚠️ 工具調用 {index} 工具名稱無效: {tool_name}")
                return False
            
            # 檢查參數
            tool_args = tool_call.get('args')
            if not isinstance(tool_args, dict):
                logger.warning(f"[{analyst_name}] ⚠️ 工具調用 {index} 參數不是字典格式: {type(tool_args)}")
                return False
            
            # 檢查ID
            tool_id = tool_call.get('id')
            if not isinstance(tool_id, str) or not tool_id.strip():
                logger.warning(f"[{analyst_name}] ⚠️ 工具調用 {index} ID無效: {tool_id}")
                return False
            
            logger.debug(f"[{analyst_name}] ✅ 工具調用 {index} 驗證通過: {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"[{analyst_name}] ❌ 工具調用 {index} 驗證異常: {e}")
            return False
    
    @staticmethod
    def _fix_tool_call(tool_call, index, analyst_name):
        """嘗試修複工具調用格式"""
        try:
            logger.info(f"[{analyst_name}] 🔧 嘗試修複工具調用 {index}: {tool_call}")
            
            if not isinstance(tool_call, dict):
                logger.warning(f"[{analyst_name}] ❌ 無法修複非字典格式的工具調用: {type(tool_call)}")
                return None
            
            fixed_tool_call = tool_call.copy()
            
            # 修複工具名稱
            if 'name' not in fixed_tool_call or not isinstance(fixed_tool_call['name'], str):
                if 'function' in fixed_tool_call and isinstance(fixed_tool_call['function'], dict):
                    # OpenAI格式轉換
                    function_data = fixed_tool_call['function']
                    if 'name' in function_data:
                        fixed_tool_call['name'] = function_data['name']
                        if 'arguments' in function_data:
                            import json
                            try:
                                if isinstance(function_data['arguments'], str):
                                    fixed_tool_call['args'] = json.loads(function_data['arguments'])
                                else:
                                    fixed_tool_call['args'] = function_data['arguments']
                            except json.JSONDecodeError:
                                fixed_tool_call['args'] = {}
                else:
                    logger.warning(f"[{analyst_name}] ❌ 無法確定工具名稱")
                    return None
            
            # 修複參數
            if 'args' not in fixed_tool_call:
                fixed_tool_call['args'] = {}
            elif not isinstance(fixed_tool_call['args'], dict):
                try:
                    import json
                    if isinstance(fixed_tool_call['args'], str):
                        fixed_tool_call['args'] = json.loads(fixed_tool_call['args'])
                    else:
                        fixed_tool_call['args'] = {}
                except:
                    fixed_tool_call['args'] = {}
            
            # 修複ID
            if 'id' not in fixed_tool_call or not isinstance(fixed_tool_call['id'], str):
                import uuid
                fixed_tool_call['id'] = f"call_{uuid.uuid4().hex[:8]}"
            
            # 驗證修複後的工具調用
            if GoogleToolCallHandler._validate_tool_call(fixed_tool_call, index, analyst_name):
                logger.info(f"[{analyst_name}] ✅ 工具調用 {index} 修複成功: {fixed_tool_call['name']}")
                return fixed_tool_call
            else:
                logger.warning(f"[{analyst_name}] ❌ 工具調用 {index} 修複失败")
                return None
                
        except Exception as e:
            logger.error(f"[{analyst_name}] ❌ 工具調用 {index} 修複異常: {e}")
            return None
    
    @staticmethod
    def handle_simple_google_response(
        result: AIMessage,
        llm: Any,
        analyst_name: str = "分析師"
    ) -> str:
        """
        處理簡單的Google模型響應（無工具調用）
        
        Args:
            result: LLM調用結果
            llm: 語言模型實例
            analyst_name: 分析師名稱
            
        Returns:
            str: 分析報告
        """
        
        if not GoogleToolCallHandler.is_google_model(llm):
            return result.content
        
        logger.info(f"[{analyst_name}] 📝 Google模型直接回複，長度: {len(result.content)} 字符")
        
        # 檢查內容長度，如果過長進行處理
        if len(result.content) > 15000:
            logger.warning(f"[{analyst_name}] ⚠️ Google模型輸出過長，進行截斷處理...")
            return result.content[:10000] + "\n\n[註：內容已截斷以確保可讀性]"
        
        return result.content
    
    @staticmethod
    def generate_final_analysis_report(llm, messages: List, analyst_name: str) -> str:
        """
        生成最终分析報告 - 增强版，支持重試和模型切換
        
        Args:
            llm: LLM實例
            messages: 消息列表
            analyst_name: 分析師名稱
            
        Returns:
            str: 分析報告
        """
        if not GoogleToolCallHandler.is_google_model(llm):
            logger.warning(f"⚠️ [{analyst_name}] 非Google模型，跳過Google工具處理器")
            return ""
        
        # 重試配置
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"🔍 [{analyst_name}] ===== 最终分析報告生成開始 (嘗試 {attempt + 1}/{max_retries}) =====")
                logger.debug(f"🔍 [{analyst_name}] LLM類型: {type(llm).__name__}")
                logger.debug(f"🔍 [{analyst_name}] LLM模型: {getattr(llm, 'model', 'unknown')}")
                logger.debug(f"🔍 [{analyst_name}] 消息數量: {len(messages)}")
                
                # 記錄消息類型和長度
                for i, msg in enumerate(messages):
                    msg_type = type(msg).__name__
                    if hasattr(msg, 'content'):
                        content_length = len(str(msg.content)) if msg.content else 0
                        logger.debug(f"🔍 [{analyst_name}] 消息{i+1}: {msg_type}, 長度: {content_length}")
                    else:
                        logger.debug(f"🔍 [{analyst_name}] 消息{i+1}: {msg_type}, 無content屬性")
                
                # 構建分析提示 - 根據嘗試次數調整
                if attempt == 0:
                    analysis_prompt = f"""
                    基於以上工具調用的結果，請為{analyst_name}生成一份詳細的分析報告。
                    
                    要求：
                    1. 综合分析所有工具返回的數據
                    2. 提供清晰的投資建议和風險評估
                    3. 報告應该結構化且易於理解
                    4. 包含具體的數據支撑和分析逻辑
                    
                    請生成完整的分析報告：
                    """
                elif attempt == 1:
                    analysis_prompt = f"""
                    請簡要分析{analyst_name}的工具調用結果並提供投資建议。
                    要求：簡潔明了，包含關键數據和建议。
                    """
                else:
                    analysis_prompt = f"""
                    請為{analyst_name}提供一個簡短的分析总結。
                    """
                
                logger.debug(f"🔍 [{analyst_name}] 分析提示預覽: {analysis_prompt[:100]}...")
                
                # 優化消息序列
                optimized_messages = GoogleToolCallHandler._optimize_message_sequence(messages, analysis_prompt)
                
                logger.info(f"[{analyst_name}] 🚀 正在調用LLM.invoke() (嘗試 {attempt + 1}/{max_retries})...")
                
                # 調用LLM生成報告
                import time
                start_time = time.time()
                result = llm.invoke(optimized_messages)
                end_time = time.time()
                
                logger.info(f"[{analyst_name}] ✅ LLM.invoke()調用完成 (耗時: {end_time - start_time:.2f}秒)")
                
                # 詳細檢查返回結果
                logger.debug(f"🔍 [{analyst_name}] 返回結果類型: {type(result).__name__}")
                logger.debug(f"🔍 [{analyst_name}] 返回結果屬性: {dir(result)}")
                
                if hasattr(result, 'content'):
                    content = result.content
                    logger.debug(f"🔍 [{analyst_name}] 內容類型: {type(content)}")
                    logger.debug(f"🔍 [{analyst_name}] 內容長度: {len(content) if content else 0}")
                    
                    if not content or len(content.strip()) == 0:
                        logger.warning(f"[{analyst_name}] ⚠️ Google模型返回內容為空 (嘗試 {attempt + 1}/{max_retries})")
                        
                        if attempt < max_retries - 1:
                            logger.info(f"[{analyst_name}] 🔄 等待{retry_delay}秒後重試...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            logger.warning(f"[{analyst_name}] ⚠️ Google模型最终分析報告生成失败 - 所有重試均返回空內容")
                            # 使用降級報告
                            fallback_report = GoogleToolCallHandler._generate_fallback_report(messages, analyst_name)
                            logger.info(f"[{analyst_name}] 🔄 使用降級報告，長度: {len(fallback_report)} 字符")
                            return fallback_report
                    else:
                        logger.info(f"[{analyst_name}] ✅ 成功生成分析報告，長度: {len(content)} 字符")
                        return content
                else:
                    logger.error(f"[{analyst_name}] ❌ 返回結果没有content屬性 (嘗試 {attempt + 1}/{max_retries})")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"[{analyst_name}] 🔄 等待{retry_delay}秒後重試...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        fallback_report = GoogleToolCallHandler._generate_fallback_report(messages, analyst_name)
                        logger.info(f"[{analyst_name}] 🔄 使用降級報告，長度: {len(fallback_report)} 字符")
                        return fallback_report
                        
            except Exception as e:
                logger.error(f"[{analyst_name}] ❌ LLM調用異常 (嘗試 {attempt + 1}/{max_retries}): {e}")
                logger.error(f"[{analyst_name}] ❌ 異常類型: {type(e).__name__}")
                logger.error(f"[{analyst_name}] ❌ 完整異常信息:\n{traceback.format_exc()}")
                
                if attempt < max_retries - 1:
                    logger.info(f"[{analyst_name}] 🔄 等待{retry_delay}秒後重試...")
                    time.sleep(retry_delay)
                    continue
                else:
                    # 使用降級報告
                    fallback_report = GoogleToolCallHandler._generate_fallback_report(messages, analyst_name)
                    logger.info(f"[{analyst_name}] 🔄 使用降級報告，長度: {len(fallback_report)} 字符")
                    return fallback_report
        
        # 如果所有重試都失败，返回降級報告
        fallback_report = GoogleToolCallHandler._generate_fallback_report(messages, analyst_name)
        logger.info(f"[{analyst_name}] 🔄 所有重試失败，使用降級報告，長度: {len(fallback_report)} 字符")
        return fallback_report
    
    @staticmethod
    def _optimize_message_sequence(messages: List, analysis_prompt: str) -> List:
        """
        優化消息序列，確保在合理長度內
        
        Args:
            messages: 原始消息列表
            analysis_prompt: 分析提示
            
        Returns:
            List: 優化後的消息列表
        """
        from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
        
        # 計算总長度
        total_length = sum(len(str(msg.content)) for msg in messages if hasattr(msg, 'content'))
        total_length += len(analysis_prompt)
        
        if total_length <= 50000:
            # 長度合理，直接添加分析提示
            return messages + [HumanMessage(content=analysis_prompt)]
        
        # 需要優化：保留關键消息
        optimized_messages = []
        
        # 保留最後的用戶消息
        for msg in messages:
            if isinstance(msg, HumanMessage):
                optimized_messages = [msg]
                break
        
        # 保留AI消息和工具消息，但截斷過長內容
        for msg in messages:
            if isinstance(msg, (AIMessage, ToolMessage)):
                if hasattr(msg, 'content') and len(str(msg.content)) > 5000:
                    # 截斷過長內容
                    truncated_content = str(msg.content)[:5000] + "\n\n[註：數據已截斷以確保處理效率]"
                    if isinstance(msg, AIMessage):
                        optimized_msg = AIMessage(content=truncated_content)
                    else:
                        optimized_msg = ToolMessage(
                            content=truncated_content,
                            tool_call_id=getattr(msg, 'tool_call_id', 'unknown')
                        )
                    optimized_messages.append(optimized_msg)
                else:
                    optimized_messages.append(msg)
        
        # 添加分析提示
        optimized_messages.append(HumanMessage(content=analysis_prompt))
        
        return optimized_messages
    
    @staticmethod
    def _generate_fallback_report(messages: List, analyst_name: str) -> str:
        """
        生成降級報告
        
        Args:
            messages: 消息列表
            analyst_name: 分析師名稱
            
        Returns:
            str: 降級報告
        """
        from langchain_core.messages import ToolMessage
        
        # 提取工具結果
        tool_results = []
        for msg in messages:
            if isinstance(msg, ToolMessage) and hasattr(msg, 'content'):
                content = str(msg.content)
                if len(content) > 1000:
                    content = content[:1000] + "\n\n[註：數據已截斷]"
                tool_results.append(content)
        
        if tool_results:
            tool_summary = "\n\n".join([f"工具結果 {i+1}:\n{result}" for i, result in enumerate(tool_results)])
            report = f"{analyst_name}工具調用完成，獲得以下數據：\n\n{tool_summary}\n\n註：由於模型響應異常，此為基於工具數據的簡化報告。"
        else:
            report = f"{analyst_name}分析完成，但未能獲取到有效的工具數據。建议檢查數據源或重新嘗試分析。"
        
        return report
    
    @staticmethod
    def create_analysis_prompt(
        ticker: str,
        company_name: str,
        analyst_type: str,
        specific_requirements: str = ""
    ) -> str:
        """
        創建標準的分析提示詞
        
        Args:
            ticker: 股票代碼
            company_name: 公司名稱
            analyst_type: 分析師類型（如"技術分析"、"基本面分析"等）
            specific_requirements: 特定要求
            
        Returns:
            str: 分析提示詞
        """
        
        base_prompt = f"""現在請基於上述工具獲取的數據，生成詳細的{analyst_type}報告。

**股票信息：**
- 公司名稱：{company_name}
- 股票代碼：{ticker}

**分析要求：**
1. 報告必须基於工具返回的真實數據進行分析
2. 包含具體的數值和專業分析
3. 提供明確的投資建议和風險提示
4. 報告長度不少於800字
5. 使用中文撰寫
6. 確保在分析中正確使用公司名稱"{company_name}"和股票代碼"{ticker}"

{specific_requirements}

請生成專業、詳細的{analyst_type}報告。"""
        
        return base_prompt