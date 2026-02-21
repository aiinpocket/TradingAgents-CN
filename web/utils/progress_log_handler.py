"""
進度日誌處理器
將日誌系統中的模塊完成訊息轉發給進度跟蹤器
"""


import logging
import threading
from typing import Dict, Optional

class ProgressLogHandler(logging.Handler):
    """
    自定義日誌處理器，將模塊開始/完成訊息轉發給進度跟蹤器
    """
    
    # 類級別的跟蹤器註冊表
    _trackers: Dict[str, 'AsyncProgressTracker'] = {}
    _lock = threading.Lock()
    
    @classmethod
    def register_tracker(cls, analysis_id: str, tracker):
        """註冊進度跟蹤器"""
        try:
            with cls._lock:
                cls._trackers[analysis_id] = tracker
            # 在鎖外面打印，避免死鎖
            print(f"📊 [進度集成] 註冊跟蹤器: {analysis_id}")
        except Exception as e:
            print(f"❌ [進度集成] 註冊跟蹤器失敗: {e}")

    @classmethod
    def unregister_tracker(cls, analysis_id: str):
        """註銷進度跟蹤器"""
        try:
            removed = False
            with cls._lock:
                if analysis_id in cls._trackers:
                    del cls._trackers[analysis_id]
                    removed = True
            # 在鎖外面打印，避免死鎖
            if removed:
                print(f"📊 [進度集成] 註銷跟蹤器: {analysis_id}")
        except Exception as e:
            print(f"❌ [進度集成] 註銷跟蹤器失敗: {e}")
    
    def emit(self, record):
        """處理日誌記錄"""
        try:
            message = record.getMessage()
            
            # 只處理模塊開始和完成的訊息
            if "[模塊開始]" in message or "[模塊完成]" in message:
                # 嘗試從訊息中提取股票代碼來匹配分析
                stock_symbol = self._extract_stock_symbol(message)
                
                # 查找匹配的跟蹤器（減少鎖持有時間）
                trackers_copy = {}
                with self._lock:
                    trackers_copy = self._trackers.copy()

                # 在鎖外面處理跟蹤器更新
                for analysis_id, tracker in trackers_copy.items():
                    # 簡單匹配：如果跟蹤器存在且狀態為running，就更新
                    if hasattr(tracker, 'progress_data') and tracker.progress_data.get('status') == 'running':
                        try:
                            tracker.update_progress(message)
                            print(f"📊 [進度集成] 轉發訊息到 {analysis_id}: {message[:50]}...")
                            break  # 只更新第一個匹配的跟蹤器
                        except Exception as e:
                            print(f"❌ [進度集成] 更新失敗: {e}")
                        
        except Exception as e:
            # 不要讓日誌處理器的錯誤影響主程序
            print(f"❌ [進度集成] 日誌處理錯誤: {e}")
    
    def _extract_stock_symbol(self, message: str) -> Optional[str]:
        """從訊息中提取股票代碼"""
        import re
        
        # 嘗試匹配 "股票: XXXXX" 格式
        match = re.search(r'股票:\s*([A-Za-z0-9]+)', message)
        if match:
            return match.group(1)
        
        return None

# 全局日誌處理器實例
_progress_handler = None

def setup_progress_log_integration():
    """設置進度日誌集成"""
    global _progress_handler
    
    if _progress_handler is None:
        _progress_handler = ProgressLogHandler()
        _progress_handler.setLevel(logging.INFO)
        
        # 添加到tools日誌器（模組完成訊息來自這裡）
        tools_logger = logging.getLogger('tools')
        tools_logger.addHandler(_progress_handler)
        
        print("✅ [進度集成] 日誌處理器已設置")
    
    return _progress_handler

def register_analysis_tracker(analysis_id: str, tracker):
    """註冊分析跟蹤器"""
    handler = setup_progress_log_integration()
    ProgressLogHandler.register_tracker(analysis_id, tracker)

def unregister_analysis_tracker(analysis_id: str):
    """註銷分析跟蹤器"""
    ProgressLogHandler.unregister_tracker(analysis_id)
