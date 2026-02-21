#!/usr/bin/env python3
"""
統一數據目錄配置管理器
Unified Data Directory Configuration Manager

提供統一的數據目錄配置管理功能
"""

import os
from pathlib import Path
from typing import Dict, Optional, Union
import logging

logger = logging.getLogger(__name__)

class UnifiedDataDirectoryManager:
    """統一數據目錄管理器"""
    
    def __init__(self, project_root: Optional[Union[str, Path]] = None):
        """
        初始化數據目錄管理器
        
        Args:
            project_root: 項目根目錄，默認為當前文件的上級目錄
        """
        if project_root is None:
            # 假設此文件在 scripts/ 目錄下
            self.project_root = Path(__file__).parent.parent
        else:
            self.project_root = Path(project_root)
        
        # 默認數據目錄配置
        self._default_config = {
            'data_root': 'data',
            'cache': 'data/cache',
            'analysis_results': 'data/analysis_results',
            'databases': 'data/databases',
            'sessions': 'data/sessions',
            'logs': 'data/logs',
            'config': 'data/config',
            'temp': 'data/temp',
            
            # 子目錄
            'cache_stock_data': 'data/cache/stock_data',
            'cache_news_data': 'data/cache/news_data',
            'cache_fundamentals': 'data/cache/fundamentals',
            'cache_metadata': 'data/cache/metadata',
            
            'results_summary': 'data/analysis_results/summary',
            'results_detailed': 'data/analysis_results/detailed',
            'results_exports': 'data/analysis_results/exports',
            
            'db_mongodb': 'data/databases/mongodb',
            'db_redis': 'data/databases/redis',
            
            'sessions_web': 'data/sessions/web_sessions',
            'sessions_cli': 'data/sessions/cli_sessions',
            
            'logs_application': 'data/logs/application',
            'logs_operations': 'data/logs/operations',
            'logs_user_activities': 'data/logs/user_activities',
            
            'config_user': 'data/config/user_configs',
            'config_system': 'data/config/system_configs',
            
            'temp_downloads': 'data/temp/downloads',
            'temp_processing': 'data/temp/processing',
        }
        
        # 環境變量映射
        self._env_mapping = {
            'data_root': 'TRADINGAGENTS_DATA_DIR',
            'cache': 'TRADINGAGENTS_CACHE_DIR',
            'analysis_results': 'TRADINGAGENTS_RESULTS_DIR',
            'sessions': 'TRADINGAGENTS_SESSIONS_DIR',
            'logs': 'TRADINGAGENTS_LOGS_DIR',
            'config': 'TRADINGAGENTS_CONFIG_DIR',
            'temp': 'TRADINGAGENTS_TEMP_DIR',
        }
    
    def get_path(self, key: str, create: bool = True) -> Path:
        """
        獲取指定數據目錄的路徑
        
        Args:
            key: 目錄鍵名
            create: 是否自動創建目錄
            
        Returns:
            Path: 目錄路徑對象
        """
        # 首先檢查環境變量
        env_key = self._env_mapping.get(key)
        if env_key and os.getenv(env_key):
            path_str = os.getenv(env_key)
        else:
            # 使用默認配置
            path_str = self._default_config.get(key)
            if not path_str:
                raise ValueError(f"未知的目錄鍵: {key}")
        
        # 處理路徑
        if os.path.isabs(path_str):
            path = Path(path_str)
        else:
            path = self.project_root / path_str
        
        # 創建目錄
        if create:
            path.mkdir(parents=True, exist_ok=True)
        
        return path
    
    def get_all_paths(self, create: bool = True) -> Dict[str, Path]:
        """
        獲取所有數據目錄路徑
        
        Args:
            create: 是否自動創建目錄
            
        Returns:
            Dict[str, Path]: 所有目錄路徑的字典
        """
        paths = {}
        for key in self._default_config.keys():
            try:
                paths[key] = self.get_path(key, create=create)
            except Exception as e:
                logger.warning(f"獲取路徑失敗 {key}: {e}")
        
        return paths
    
    def create_all_directories(self) -> bool:
        """
        創建所有數據目錄
        
        Returns:
            bool: 是否成功創建所有目錄
        """
        try:
            logger.info("🔄 創建統一數據目錄結構...")
            
            paths = self.get_all_paths(create=True)
            
            for key, path in paths.items():
                logger.info(f"  ✅ {key}: {path}")
            
            logger.info("✅ 統一數據目錄結構創建完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 創建目錄結構失敗: {e}")
            return False
    
    def get_config_summary(self) -> Dict[str, str]:
        """
        獲取配置摘要
        
        Returns:
            Dict[str, str]: 配置摘要
        """
        summary = {
            'project_root': str(self.project_root),
            'data_root': str(self.get_path('data_root', create=False)),
        }
        
        # 添加環境變量狀態
        for key, env_key in self._env_mapping.items():
            env_value = os.getenv(env_key)
            summary[f'env_{key}'] = env_value if env_value else '未設置'
        
        return summary
    
    def validate_structure(self) -> Dict[str, bool]:
        """
        驗證目錄結構
        
        Returns:
            Dict[str, bool]: 驗證結果
        """
        results = {}
        
        for key in self._default_config.keys():
            try:
                path = self.get_path(key, create=False)
                results[key] = path.exists()
            except Exception:
                results[key] = False
        
        return results
    
    def print_structure(self):
        """打印目錄結構"""
        print("📁 統一數據目錄結構:")
        print(f"📂 項目根目錄: {self.project_root}")
        print()
        
        # 按層級組織顯示
        structure = {
            '📊 數據根目錄': ['data_root'],
            '💾 緩存目錄': ['cache', 'cache_stock_data', 'cache_news_data', 'cache_fundamentals', 'cache_metadata'],
            '📈 分析結果': ['analysis_results', 'results_summary', 'results_detailed', 'results_exports'],
            '🗄️ 數據庫': ['databases', 'db_mongodb', 'db_redis'],
            '📝 會話數據': ['sessions', 'sessions_web', 'sessions_cli'],
            '📋 日誌文件': ['logs', 'logs_application', 'logs_operations', 'logs_user_activities'],
            '🔧 配置文件': ['config', 'config_user', 'config_system'],
            '📦 臨時文件': ['temp', 'temp_downloads', 'temp_processing'],
        }
        
        for category, keys in structure.items():
            print(f"{category}:")
            for key in keys:
                try:
                    path = self.get_path(key, create=False)
                    exists = "✅" if path.exists() else "❌"
                    relative_path = path.relative_to(self.project_root)
                    print(f"  {exists} {key}: {relative_path}")
                except Exception as e:
                    print(f"  ❌ {key}: 錯誤 - {e}")
            print()


# 全局實例
_data_manager = None

def get_data_manager(project_root: Optional[Union[str, Path]] = None) -> UnifiedDataDirectoryManager:
    """
    獲取全局數據目錄管理器實例
    
    Args:
        project_root: 項目根目錄
        
    Returns:
        UnifiedDataDirectoryManager: 數據目錄管理器實例
    """
    global _data_manager
    if _data_manager is None:
        _data_manager = UnifiedDataDirectoryManager(project_root)
    return _data_manager

def get_data_path(key: str, create: bool = True) -> Path:
    """
    便捷函數：獲取數據目錄路徑
    
    Args:
        key: 目錄鍵名
        create: 是否自動創建目錄
        
    Returns:
        Path: 目錄路徑
    """
    return get_data_manager().get_path(key, create=create)

def main():
    """命令行工具主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='統一數據目錄配置管理器')
    parser.add_argument('--project-root', help='項目根目錄路徑')
    parser.add_argument('--create', action='store_true', help='創建所有目錄')
    parser.add_argument('--validate', action='store_true', help='驗證目錄結構')
    parser.add_argument('--show-config', action='store_true', help='顯示配置摘要')
    parser.add_argument('--show-structure', action='store_true', help='顯示目錄結構')
    
    args = parser.parse_args()
    
    # 設置日誌
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    manager = UnifiedDataDirectoryManager(args.project_root)
    
    if args.create:
        manager.create_all_directories()
    
    if args.validate:
        print("🔍 驗證目錄結構:")
        results = manager.validate_structure()
        for key, exists in results.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {key}")
        
        total = len(results)
        existing = sum(results.values())
        print(f"\n📊 統計: {existing}/{total} 個目錄存在")
    
    if args.show_config:
        print("⚙️ 配置摘要:")
        config = manager.get_config_summary()
        for key, value in config.items():
            print(f"  {key}: {value}")
    
    if args.show_structure:
        manager.print_structure()
    
    # 如果沒有指定任何操作，顯示幫助
    if not any([args.create, args.validate, args.show_config, args.show_structure]):
        parser.print_help()


if __name__ == '__main__':
    main()