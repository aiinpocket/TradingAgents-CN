#!/usr/bin/env python3
"""
工具呼叫日誌裝飾器
為所有工具呼叫添加統一的日誌記錄
"""

import time
import functools
from typing import Optional, Callable
from datetime import datetime

from tradingagents.utils.logging_init import get_logger

# 匯入日誌模組
from tradingagents.utils.logging_manager import get_logger, get_logger_manager
logger = get_logger('agents')

# 工具呼叫日誌器
tool_logger = get_logger("tools")


def log_tool_call(tool_name: Optional[str] = None, log_args: bool = True, log_result: bool = False):
    """
    工具呼叫日誌裝飾器
    
    Args:
        tool_name: 工具名稱，如果不提供則使用函數名
        log_args: 是否記錄參數
        log_result: 是否記錄返回結果（註意：可能包含大量資料）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 確定工具名稱
            name = tool_name or getattr(func, '__name__', 'unknown_tool')
            
            # 記錄開始時間
            start_time = time.time()
            
            # 準備參數資訊
            args_info = {}
            if log_args:
                # 記錄位置參數
                if args:
                    args_info['args'] = [str(arg)[:100] + '...' if len(str(arg)) > 100 else str(arg) for arg in args]
                
                # 記錄關鍵字參數
                if kwargs:
                    args_info['kwargs'] = {
                        k: str(v)[:100] + '...' if len(str(v)) > 100 else str(v) 
                        for k, v in kwargs.items()
                    }
            
            # 記錄工具呼叫開始
            tool_logger.info(
                f"[工具呼叫] {name} - 開始",
                extra={
                    'tool_name': name,
                    'event_type': 'tool_call_start',
                    'timestamp': datetime.now().isoformat(),
                    'args_info': args_info if log_args else None
                }
            )
            
            try:
                # 執行工具函數
                result = func(*args, **kwargs)
                
                # 計算執行時間
                duration = time.time() - start_time
                
                # 準備結果資訊
                result_info = None
                if log_result and result is not None:
                    result_str = str(result)
                    result_info = result_str[:200] + '...' if len(result_str) > 200 else result_str
                
                # 記錄工具呼叫成功
                tool_logger.info(
                    f"[工具呼叫] {name} - 完成 (耗時: {duration:.2f}s)",
                    extra={
                        'tool_name': name,
                        'event_type': 'tool_call_success',
                        'duration': duration,
                        'result_info': result_info if log_result else None,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                return result
                
            except Exception as e:
                # 計算執行時間
                duration = time.time() - start_time
                
                # 記錄工具呼叫失敗
                tool_logger.error(
                    f"[工具呼叫] {name} - 失敗 (耗時: {duration:.2f}s): {str(e)}",
                    extra={
                        'tool_name': name,
                        'event_type': 'tool_call_error',
                        'duration': duration,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    },
                    exc_info=True
                )
                
                # 重新拋出異常
                raise
        
        return wrapper
    return decorator


def log_data_source_call(source_name: str):
    """
    資料來源呼叫專用日誌裝飾器
    
    Args:
        source_name: 資料來源名稱（如：yfinance、finnhub、googlenews 等）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 提取股票代碼（通常是第一個參數）
            symbol = args[0] if args else kwargs.get('symbol', kwargs.get('ticker', 'unknown'))
            
            # 記錄資料來源呼叫開始
            tool_logger.info(
                f"[資料來源] {source_name} - 取得 {symbol} 資料",
                extra={
                    'data_source': source_name,
                    'symbol': symbol,
                    'event_type': 'data_source_call',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                # 檢查結果是否成功
                success = result and "錯誤" not in str(result)
                
                if success:
                    tool_logger.info(
                        f"[資料來源] {source_name} - {symbol} 資料取得成功 (耗時: {duration:.2f}s)",
                        extra={
                            'data_source': source_name,
                            'symbol': symbol,
                            'event_type': 'data_source_success',
                            'duration': duration,
                            'data_size': len(str(result)) if result else 0,
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                else:
                    tool_logger.warning(
                        f"[資料來源] {source_name} - {symbol} 資料取得失敗 (耗時: {duration:.2f}s)",
                        extra={
                            'data_source': source_name,
                            'symbol': symbol,
                            'event_type': 'data_source_failure',
                            'duration': duration,
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                tool_logger.error(
                    f"[資料來源] {source_name} - {symbol} 資料取得異常 (耗時: {duration:.2f}s): {str(e)}",
                    extra={
                        'data_source': source_name,
                        'symbol': symbol,
                        'event_type': 'data_source_error',
                        'duration': duration,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    },
                    exc_info=True
                )
                
                raise
        
        return wrapper
    return decorator


def log_llm_call(provider: str, model: str):
    """
    LLM呼叫專用日誌裝飾器
    
    Args:
        provider: LLM 提供商（如：openai、anthropic）
        model: 模型名稱
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # 記錄LLM呼叫開始
            tool_logger.info(
                f"[LLM呼叫] {provider}/{model} - 開始",
                extra={
                    'llm_provider': provider,
                    'llm_model': model,
                    'event_type': 'llm_call_start',
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                tool_logger.info(
                    f"[LLM呼叫] {provider}/{model} - 完成 (耗時: {duration:.2f}s)",
                    extra={
                        'llm_provider': provider,
                        'llm_model': model,
                        'event_type': 'llm_call_success',
                        'duration': duration,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                
                tool_logger.error(
                    f"[LLM呼叫] {provider}/{model} - 失敗 (耗時: {duration:.2f}s): {str(e)}",
                    extra={
                        'llm_provider': provider,
                        'llm_model': model,
                        'event_type': 'llm_call_error',
                        'duration': duration,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    },
                    exc_info=True
                )
                
                raise
        
        return wrapper
    return decorator


# 便捷函數
def log_tool_usage(tool_name: str, symbol: str = None, **extra_data):
    """
    記錄工具使用情況的便捷函數
    
    Args:
        tool_name: 工具名稱
        symbol: 股票代碼（可選）
        **extra_data: 額外的資料
    """
    extra = {
        'tool_name': tool_name,
        'event_type': 'tool_usage',
        'timestamp': datetime.now().isoformat(),
        **extra_data
    }
    
    if symbol:
        extra['symbol'] = symbol
    
    tool_logger.info(f"[工具使用] {tool_name}", extra=extra)


def log_analysis_step(step_name: str, symbol: str, **extra_data):
    """
    記錄分析步驟的便捷函數

    Args:
        step_name: 步驟名稱
        symbol: 股票代碼
        **extra_data: 額外的資料
    """
    extra = {
        'step_name': step_name,
        'symbol': symbol,
        'event_type': 'analysis_step',
        'timestamp': datetime.now().isoformat(),
        **extra_data
    }

    tool_logger.info(f"[分析步驟] {step_name} - {symbol}", extra=extra)


def log_analysis_module(module_name: str, session_id: str = None):
    """
    分析模組日誌裝飾器
    自動記錄模組的開始和結束

    Args:
        module_name: 模組名稱（如：market_analyst、fundamentals_analyst等）
        session_id: 會話ID（可選）
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 嘗試從參數中提取股票代碼
            symbol = None

            # 特殊處理：信號處理模組的參數結構
            if module_name == "graph_signal_processing":
                # 信號處理模組：process_signal(self, full_signal, stock_symbol=None)
                if len(args) >= 3:  # self, full_signal, stock_symbol
                    symbol = str(args[2]) if args[2] else None
                elif 'stock_symbol' in kwargs:
                    symbol = str(kwargs['stock_symbol']) if kwargs['stock_symbol'] else None
            else:
                if args:
                    # 檢查第一個參數是否是state字典（分析師節點的情況）
                    first_arg = args[0]
                    if isinstance(first_arg, dict) and 'company_of_interest' in first_arg:
                        symbol = str(first_arg['company_of_interest'])
                    # 檢查第一個參數是否是股票代碼
                    elif isinstance(first_arg, str) and len(first_arg) <= 10:
                        symbol = first_arg

            # 從kwargs中查找股票代碼
            if not symbol:
                for key in ['symbol', 'ticker', 'stock_code', 'stock_symbol', 'company_of_interest']:
                    if key in kwargs:
                        symbol = str(kwargs[key])
                        break

            # 如果還是沒找到，使用預設值
            if not symbol:
                symbol = 'unknown'

            # 生成會話ID
            actual_session_id = session_id or f"session_{int(time.time())}"

            # 記錄模組開始
            logger_manager = get_logger_manager()

            start_time = time.time()

            logger_manager.log_module_start(
                tool_logger, module_name, symbol, actual_session_id,
                function_name=func.__name__,
                args_count=len(args),
                kwargs_keys=list(kwargs.keys())
            )

            try:
                # 執行分析函數
                result = func(*args, **kwargs)

                # 計算執行時間
                duration = time.time() - start_time

                # 記錄模組完成
                result_length = len(str(result)) if result else 0
                logger_manager.log_module_complete(
                    tool_logger, module_name, symbol, actual_session_id,
                    duration, success=True, result_length=result_length,
                    function_name=func.__name__
                )

                return result

            except Exception as e:
                # 計算執行時間
                duration = time.time() - start_time

                # 記錄模組錯誤
                logger_manager.log_module_error(
                    tool_logger, module_name, symbol, actual_session_id,
                    duration, str(e),
                    function_name=func.__name__
                )

                # 重新拋出異常
                raise

        return wrapper
    return decorator


def log_analyst_module(analyst_type: str):
    """
    分析師模組專用裝飾器

    Args:
        analyst_type: 分析師類型（如：market、fundamentals、technical、sentiment等）
    """
    return log_analysis_module(f"{analyst_type}_analyst")


def log_graph_module(graph_type: str):
    """
    圖處理模組專用裝飾器

    Args:
        graph_type: 圖處理類型（如：signal_processing、workflow等）
    """
    return log_analysis_module(f"graph_{graph_type}")


def log_dataflow_module(dataflow_type: str):
    """
    資料流模組專用裝飾器

    Args:
        dataflow_type: 資料流類型（如：cache、interface、provider等）
    """
    return log_analysis_module(f"dataflow_{dataflow_type}")
