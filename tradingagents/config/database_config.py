#!/usr/bin/env python3
"""
數據庫配置管理模塊
統一管理MongoDB和Redis的連接配置
"""

import os
from typing import Dict, Any, Optional


class DatabaseConfig:
    """數據庫配置管理類"""
    
    @staticmethod
    def get_mongodb_config() -> Dict[str, Any]:
        """
        獲取MongoDB配置
        
        Returns:
            Dict[str, Any]: MongoDB配置字典
            
        Raises:
            ValueError: 當必要的配置未設置時
        """
        connection_string = os.getenv('MONGODB_CONNECTION_STRING')
        if not connection_string:
            raise ValueError(
                "MongoDB連接字符串未配置。請設置環境變量 MONGODB_CONNECTION_STRING\n"
                "例如: MONGODB_CONNECTION_STRING=mongodb://localhost:27017/"
            )
        
        return {
            'connection_string': connection_string,
            'database': os.getenv('MONGODB_DATABASE', 'tradingagents'),
            'auth_source': os.getenv('MONGODB_AUTH_SOURCE', 'admin')
        }
    
    @staticmethod
    def get_redis_config() -> Dict[str, Any]:
        """
        獲取Redis配置
        
        Returns:
            Dict[str, Any]: Redis配置字典
            
        Raises:
            ValueError: 當必要的配置未設置時
        """
        # 優先使用連接字符串
        connection_string = os.getenv('REDIS_CONNECTION_STRING')
        if connection_string:
            return {
                'connection_string': connection_string,
                'database': int(os.getenv('REDIS_DATABASE', 0))
            }
        
        # 使用分離的配置參數
        host = os.getenv('REDIS_HOST')
        port = os.getenv('REDIS_PORT')
        
        if not host or not port:
            raise ValueError(
                "Redis連接配置未完整設置。請設置以下環境變量之一：\n"
                "1. REDIS_CONNECTION_STRING=redis://localhost:6379/0\n"
                "2. REDIS_HOST + REDIS_PORT (例如: REDIS_HOST=localhost, REDIS_PORT=6379)"
            )
        
        return {
            'host': host,
            'port': int(port),
            'password': os.getenv('REDIS_PASSWORD'),
            'database': int(os.getenv('REDIS_DATABASE', 0))
        }
    
    @staticmethod
    def validate_config() -> Dict[str, bool]:
        """
        驗證數據庫配置是否完整
        
        Returns:
            Dict[str, bool]: 驗證結果
        """
        result = {
            'mongodb_valid': False,
            'redis_valid': False
        }
        
        try:
            DatabaseConfig.get_mongodb_config()
            result['mongodb_valid'] = True
        except ValueError:
            pass
        
        try:
            DatabaseConfig.get_redis_config()
            result['redis_valid'] = True
        except ValueError:
            pass
        
        return result
    
    @staticmethod
    def get_config_status() -> str:
        """
        獲取配置狀態的友好描述
        
        Returns:
            str: 配置狀態描述
        """
        validation = DatabaseConfig.validate_config()
        
        if validation['mongodb_valid'] and validation['redis_valid']:
            return "✅ 所有數據庫配置正常"
        elif validation['mongodb_valid']:
            return "⚠️ MongoDB配置正常，Redis配置缺失"
        elif validation['redis_valid']:
            return "⚠️ Redis配置正常，MongoDB配置缺失"
        else:
            return "❌ 數據庫配置缺失，請檢查環境變量"