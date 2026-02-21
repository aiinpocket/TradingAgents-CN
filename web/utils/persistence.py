"""
持久化工具
使用URL參數和session state結合的方式來持久化用戶選擇
"""

import streamlit as st

# 日誌模組
try:
    from tradingagents.utils.logging_manager import get_logger
    logger = get_logger('web')
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

class ModelPersistence:
    """模型選擇持久化管理器"""
    
    def __init__(self):
        self.storage_key = "model_config"
    
    def save_config(self, provider, category, model):
        """保存配置到session state和URL"""
        config = {
            'provider': provider,
            'category': category,
            'model': model
        }
        
        # 保存到session state
        st.session_state[self.storage_key] = config
        
        # 保存到URL參數（通過query_params）
        try:
            st.query_params.update({
                'provider': provider,
                'category': category,
                'model': model
            })
            logger.debug(f"[Persistence] 配置已保存: {config}")
        except Exception as e:
            logger.warning(f"[Persistence] URL參數保存失敗: {e}")
    
    def load_config(self):
        """從session state或URL載入配置"""
        # 首先嘗試從URL參數載入
        try:
            query_params = st.query_params
            if 'provider' in query_params:
                config = {
                    'provider': query_params.get('provider', 'openai'),
                    'category': query_params.get('category', 'openai'),
                    'model': query_params.get('model', '')
                }
                logger.debug(f"[Persistence] 從URL載入配置: {config}")
                return config
        except Exception as e:
            logger.warning(f"[Persistence] URL參數載入失敗: {e}")
        
        # 然後嘗試從session state載入
        if self.storage_key in st.session_state:
            config = st.session_state[self.storage_key]
            logger.debug(f"[Persistence] 從Session State載入配置: {config}")
            return config
        
        # 返回預設配置
        default_config = {
            'provider': 'openai',
            'category': 'openai',
            'model': ''
        }
        logger.debug(f"[Persistence] 使用預設配置: {default_config}")
        return default_config
    
    def clear_config(self):
        """清除配置"""
        if self.storage_key in st.session_state:
            del st.session_state[self.storage_key]
        
        try:
            st.query_params.clear()
            logger.info("[Persistence] 配置已清除")
        except Exception as e:
            logger.warning(f"[Persistence] 清除失敗: {e}")

# 全局實例
persistence = ModelPersistence()

def save_model_selection(provider, category="", model=""):
    """保存模型選擇"""
    persistence.save_config(provider, category, model)

def load_model_selection():
    """載入模型選擇"""
    return persistence.load_config()

