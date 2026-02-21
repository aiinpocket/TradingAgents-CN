"""
基於檔案的會話管理器 - 不依賴Redis的可靠方案
適用於沒有Redis或Redis連接失敗的情況
"""

import re
import streamlit as st
import json
import time
import uuid
from typing import Optional, Dict, Any
from pathlib import Path

class FileSessionManager:
    """基於檔案的會話管理器"""
    
    def __init__(self):
        self.data_dir = Path("./data/sessions")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.max_age_hours = 24  # 會話有效期24小時
        
    def _get_browser_fingerprint(self) -> str:
        """生成瀏覽器指紋"""
        try:
            # 方法1：使用固定的session標識符
            # 檢查是否已經有session標識符保存在session_state中
            if hasattr(st.session_state, 'file_session_fingerprint'):
                return st.session_state.file_session_fingerprint

            # 方法2：查找最近的session檔案（24小時內）
            current_time = time.time()
            recent_files = []

            for session_file in self.data_dir.glob("*.json"):
                try:
                    file_age = current_time - session_file.stat().st_mtime
                    if file_age < (24 * 3600):  # 24小時內的檔案
                        recent_files.append((session_file, file_age))
                except Exception as e:
                    continue

            if recent_files:
                # 使用最新的session檔案
                recent_files.sort(key=lambda x: x[1])  # 按檔案年齡排序
                newest_file = recent_files[0][0]
                fingerprint = newest_file.stem
                # 保存到session_state以便後續使用
                st.session_state.file_session_fingerprint = fingerprint
                return fingerprint

            # 方法3：建立新的session
            fingerprint = f"session_{uuid.uuid4().hex[:12]}"
            st.session_state.file_session_fingerprint = fingerprint
            return fingerprint

        except Exception as e:
            # 方法4：最後的fallback
            fingerprint = f"fallback_{uuid.uuid4().hex[:8]}"
            if hasattr(st, 'session_state'):
                st.session_state.file_session_fingerprint = fingerprint
            return fingerprint
    
    def _get_session_file_path(self, fingerprint: str) -> Path:
        """取得會話檔案路徑（含路徑遍歷防護）"""
        # 驗證 fingerprint 只包含安全字元
        if not re.match(r'^[a-zA-Z0-9_-]+$', fingerprint):
            raise ValueError("無效的會話指紋格式")

        file_path = self.data_dir / f"{fingerprint}.json"

        # 確保最終路徑在預期目錄內，防止路徑遍歷
        if not file_path.resolve().is_relative_to(self.data_dir.resolve()):
            raise ValueError("會話檔案路徑驗證失敗")

        return file_path
    
    def _cleanup_old_sessions(self):
        """清理過期的會話檔案"""
        try:
            current_time = time.time()
            max_age_seconds = self.max_age_hours * 3600
            
            for session_file in self.data_dir.glob("*.json"):
                try:
                    # 檢查檔案修改時間
                    file_age = current_time - session_file.stat().st_mtime
                    if file_age > max_age_seconds:
                        session_file.unlink()
                except OSError:
                    continue

        except OSError as e:
            import logging
            logging.getLogger(__name__).debug(f"清理過期會話時發生錯誤: {e}")
    
    def save_analysis_state(self, analysis_id: str, status: str = "running",
                           stock_symbol: str = "", market_type: str = "",
                           form_config: Dict[str, Any] = None):
        """保存分析狀態和表單配置"""
        try:
            # 清理過期檔案
            self._cleanup_old_sessions()

            fingerprint = self._get_browser_fingerprint()
            session_file = self._get_session_file_path(fingerprint)

            session_data = {
                "analysis_id": analysis_id,
                "status": status,
                "stock_symbol": stock_symbol,
                "market_type": market_type,
                "timestamp": time.time(),
                "last_update": time.time(),
                "fingerprint": fingerprint
            }

            # 新增表單配置
            if form_config:
                session_data["form_config"] = form_config
            
            # 保存到檔案
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)

            # 同時保存到session state
            st.session_state.current_analysis_id = analysis_id
            st.session_state.analysis_running = (status == 'running')
            st.session_state.last_stock_symbol = stock_symbol
            st.session_state.last_market_type = market_type
            st.session_state.session_fingerprint = fingerprint

            return True
            
        except Exception as e:
            st.warning(f"保存會話狀態失敗: {e}")
            return False
    
    def load_analysis_state(self) -> Optional[Dict[str, Any]]:
        """載入分析狀態"""
        try:
            fingerprint = self._get_browser_fingerprint()
            session_file = self._get_session_file_path(fingerprint)

            # 檢查檔案是否存在
            if not session_file.exists():
                return None

            # 讀取會話資料
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # 檢查是否過期
            timestamp = session_data.get("timestamp", 0)
            if time.time() - timestamp > (self.max_age_hours * 3600):
                # 過期了，刪除檔案
                session_file.unlink()
                return None

            return session_data
            
        except Exception as e:
            st.warning(f"載入會話狀態失敗: {e}")
            return None
    
    def clear_analysis_state(self):
        """清除分析狀態"""
        try:
            fingerprint = self._get_browser_fingerprint()
            session_file = self._get_session_file_path(fingerprint)
            
            # 刪除檔案
            if session_file.exists():
                session_file.unlink()
            
            # 清除session state
            keys_to_remove = ['current_analysis_id', 'analysis_running', 'last_stock_symbol', 'last_market_type', 'session_fingerprint']
            for key in keys_to_remove:
                if key in st.session_state:
                    del st.session_state[key]
            
        except Exception as e:
            st.warning(f"清除會話狀態失敗: {e}")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """取得除錯資訊"""
        try:
            fingerprint = self._get_browser_fingerprint()
            session_file = self._get_session_file_path(fingerprint)
            
            debug_info = {
                "fingerprint": fingerprint,
                "session_file": str(session_file),
                "file_exists": session_file.exists(),
                "data_dir": str(self.data_dir),
                "session_state_keys": [k for k in st.session_state.keys() if 'analysis' in k.lower() or 'session' in k.lower()]
            }
            
            # 統計會話檔案數量
            session_files = list(self.data_dir.glob("*.json"))
            debug_info["total_session_files"] = len(session_files)
            debug_info["session_files"] = [f.name for f in session_files]
            
            if session_file.exists():
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    debug_info["session_data"] = session_data
                    debug_info["age_hours"] = (time.time() - session_data.get("timestamp", 0)) / 3600
                except Exception as e:
                    debug_info["file_error"] = str(e)
            
            return debug_info
            
        except Exception as e:
            return {"error": str(e)}

# 全域檔案會話管理器實例（由 SmartSessionManager 使用）
file_session_manager = FileSessionManager()
