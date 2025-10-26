#!/usr/bin/env python3
"""
Tushare配置管理
專門處理Tushare相關的環境變量配置，兼容Python 3.13+
"""

import os
from typing import Dict, Any, Optional
from .env_utils import parse_bool_env, parse_str_env, get_env_info, validate_required_env_vars


class TushareConfig:
    """Tushare配置管理器"""
    
    def __init__(self):
        """初始化Tushare配置"""
        self.load_config()
    
    def load_config(self):
        """加載Tushare配置"""
        # 嘗試加載python-dotenv
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # 解析配置
        self.token = parse_str_env("TUSHARE_TOKEN", "")
        self.enabled = parse_bool_env("TUSHARE_ENABLED", False)
        self.default_source = parse_str_env("DEFAULT_CHINA_DATA_SOURCE", "akshare")
        
        # 緩存配置
        self.cache_enabled = parse_bool_env("ENABLE_DATA_CACHE", True)
        self.cache_ttl_hours = parse_str_env("TUSHARE_CACHE_TTL_HOURS", "24")
        
        # 調試信息
        self._debug_config()
    
    def _debug_config(self):
        """輸出調試配置信息"""
        print(f"🔍 Tushare配置調試信息:")
        print(f"   TUSHARE_TOKEN: {'已設置' if self.token else '未設置'} ({len(self.token)}字符)")
        print(f"   TUSHARE_ENABLED: {self.enabled} (原始值: {os.getenv('TUSHARE_ENABLED', 'None')})")
        print(f"   DEFAULT_CHINA_DATA_SOURCE: {self.default_source}")
        print(f"   ENABLE_DATA_CACHE: {self.cache_enabled}")
    
    def is_valid(self) -> bool:
        """檢查配置是否有效"""
        if not self.enabled:
            return False
        
        if not self.token:
            return False
        
        # 檢查token格式（Tushare token通常是40字符的十六進制字符串）
        if len(self.token) < 30:
            return False
        
        return True
    
    def get_validation_result(self) -> Dict[str, Any]:
        """獲取詳細的驗證結果"""
        result = {
            'valid': False,
            'enabled': self.enabled,
            'token_set': bool(self.token),
            'token_length': len(self.token),
            'issues': [],
            'suggestions': []
        }
        
        # 檢查啟用狀態
        if not self.enabled:
            result['issues'].append("TUSHARE_ENABLED未啟用")
            result['suggestions'].append("在.env文件中設置 TUSHARE_ENABLED=true")
        
        # 檢查token
        if not self.token:
            result['issues'].append("TUSHARE_TOKEN未設置")
            result['suggestions'].append("在.env文件中設置 TUSHARE_TOKEN=your_token_here")
        elif len(self.token) < 30:
            result['issues'].append("TUSHARE_TOKEN格式可能不正確")
            result['suggestions'].append("檢查token是否完整（通常為40字符）")
        
        # 如果没有問題，標記為有效
        if not result['issues']:
            result['valid'] = True
        
        return result
    
    def get_env_debug_info(self) -> Dict[str, Any]:
        """獲取環境變量調試信息"""
        env_vars = [
            "TUSHARE_TOKEN",
            "TUSHARE_ENABLED", 
            "DEFAULT_CHINA_DATA_SOURCE",
            "ENABLE_DATA_CACHE"
        ]
        
        debug_info = {}
        for var in env_vars:
            debug_info[var] = get_env_info(var)
        
        return debug_info
    
    def test_boolean_parsing(self) -> Dict[str, Any]:
        """測試布爾值解析的兼容性"""
        test_cases = [
            ("true", True),
            ("True", True), 
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
            ("off", False),
            ("", False),  # 空值
            ("invalid", False)  # 無效值
        ]
        
        results = {}
        for test_value, expected in test_cases:
            # 臨時設置環境變量
            original_value = os.getenv("TEST_BOOL_VAR")
            os.environ["TEST_BOOL_VAR"] = test_value
            
            # 測試解析
            parsed = parse_bool_env("TEST_BOOL_VAR", False)
            results[test_value] = {
                'expected': expected,
                'parsed': parsed,
                'correct': parsed == expected
            }
            
            # 恢複原始值
            if original_value is not None:
                os.environ["TEST_BOOL_VAR"] = original_value
            else:
                os.environ.pop("TEST_BOOL_VAR", None)
        
        return results
    
    def fix_common_issues(self) -> Dict[str, str]:
        """修複常见配置問題"""
        fixes = {}
        
        # 檢查TUSHARE_ENABLED的常见問題
        enabled_raw = os.getenv("TUSHARE_ENABLED", "")
        if enabled_raw.lower() in ["true", "1", "yes", "on"] and not self.enabled:
            fixes["TUSHARE_ENABLED"] = f"檢測到 '{enabled_raw}'，但解析為False，可能存在兼容性問題"
        
        return fixes


def get_tushare_config() -> TushareConfig:
    """獲取Tushare配置實例"""
    return TushareConfig()


def check_tushare_compatibility() -> Dict[str, Any]:
    """檢查Tushare配置兼容性"""
    config = get_tushare_config()
    
    return {
        'config_valid': config.is_valid(),
        'validation_result': config.get_validation_result(),
        'env_debug_info': config.get_env_debug_info(),
        'boolean_parsing_test': config.test_boolean_parsing(),
        'common_fixes': config.fix_common_issues()
    }


def diagnose_tushare_issues():
    """診斷Tushare配置問題"""
    print("🔍 Tushare配置診斷")
    print("=" * 60)
    
    compatibility = check_tushare_compatibility()
    
    # 顯示配置狀態
    print(f"\n📊 配置狀態:")
    validation = compatibility['validation_result']
    print(f"   配置有效: {'✅' if validation['valid'] else '❌'}")
    print(f"   Tushare啟用: {'✅' if validation['enabled'] else '❌'}")
    print(f"   Token設置: {'✅' if validation['token_set'] else '❌'}")
    
    # 顯示問題
    if validation['issues']:
        print(f"\n⚠️ 發現問題:")
        for issue in validation['issues']:
            print(f"   - {issue}")
    
    # 顯示建议
    if validation['suggestions']:
        print(f"\n💡 修複建议:")
        for suggestion in validation['suggestions']:
            print(f"   - {suggestion}")
    
    # 顯示環境變量詳情
    print(f"\n🔍 環境變量詳情:")
    for var, info in compatibility['env_debug_info'].items():
        status = "✅" if info['exists'] and not info['empty'] else "❌"
        print(f"   {var}: {status} {info['value']}")
    
    # 顯示布爾值解析測試
    print(f"\n🧪 布爾值解析測試:")
    bool_tests = compatibility['boolean_parsing_test']
    failed_tests = [k for k, v in bool_tests.items() if not v['correct']]
    
    if failed_tests:
        print(f"   ❌ 失败的測試: {failed_tests}")
        print(f"   ⚠️ 可能存在Python版本兼容性問題")
    else:
        print(f"   ✅ 所有布爾值解析測試通過")
    
    # 顯示修複建议
    fixes = compatibility['common_fixes']
    if fixes:
        print(f"\n🔧 自動修複建议:")
        for var, fix in fixes.items():
            print(f"   {var}: {fix}")


if __name__ == "__main__":
    diagnose_tushare_issues()
