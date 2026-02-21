#!/usr/bin/env python3
"""
數據目錄重新組織遷移腳本
Data Directory Reorganization Migration Script

此腳本將項目中分散的數據目錄重新組織為統一的結構
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataDirectoryMigrator:
    """數據目錄遷移器"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.backup_dir = self.project_root / f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 新的目錄結構
        self.new_structure = {
            'data': {
                'cache': ['stock_data', 'news_data', 'fundamentals', 'metadata'],
                'analysis_results': ['summary', 'detailed', 'exports'],
                'databases': ['mongodb', 'redis'],
                'sessions': ['web_sessions', 'cli_sessions'],
                'logs': ['application', 'operations', 'user_activities'],
                'config': ['user_configs', 'system_configs'],
                'temp': ['downloads', 'processing']
            }
        }
        
        # 遷移映射：(源路徑, 目標路徑)
        self.migration_map = [
            # 緩存數據遷移
            ('tradingagents/dataflows/data_cache', 'data/cache'),
            
            # 分析結果遷移
            ('results', 'data/analysis_results/detailed'),
            ('web/data/analysis_results', 'data/analysis_results/summary'),
            
            # 數據庫數據遷移
            ('data/mongodb', 'data/databases/mongodb'),
            ('data/redis', 'data/databases/redis'),
            
            # 會話數據遷移
            ('data/sessions', 'data/sessions/cli_sessions'),
            ('web/data/sessions', 'data/sessions/web_sessions'),
            
            # 日誌數據遷移
            ('web/data/operation_logs', 'data/logs/operations'),
            ('web/data/user_activities', 'data/logs/user_activities'),
            
            # 報告數據遷移（如果存在）
            ('data/reports', 'data/analysis_results/exports'),
        ]
    
    def create_backup(self) -> bool:
        """創建數據備份"""
        try:
            logger.info(f"🔄 開始創建數據備份到: {self.backup_dir}")
            self.backup_dir.mkdir(exist_ok=True)
            
            # 備份現有數據目錄
            backup_paths = ['data', 'web/data', 'results', 'tradingagents/dataflows/data_cache']
            
            for path in backup_paths:
                source = self.project_root / path
                if source.exists():
                    target = self.backup_dir / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    if source.is_dir():
                        shutil.copytree(source, target, dirs_exist_ok=True)
                    else:
                        shutil.copy2(source, target)
                    
                    logger.info(f"  ✅ 已備份: {path}")
            
            logger.info(f"✅ 數據備份完成: {self.backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 備份失敗: {e}")
            return False
    
    def create_new_structure(self) -> bool:
        """創建新的目錄結構"""
        try:
            logger.info("🔄 創建新的目錄結構...")
            
            for root_dir, subdirs in self.new_structure.items():
                root_path = self.project_root / root_dir
                root_path.mkdir(exist_ok=True)
                
                if isinstance(subdirs, dict):
                    for subdir, sub_subdirs in subdirs.items():
                        subdir_path = root_path / subdir
                        subdir_path.mkdir(exist_ok=True)
                        
                        for sub_subdir in sub_subdirs:
                            (subdir_path / sub_subdir).mkdir(exist_ok=True)
                            
                        logger.info(f"  ✅ 創建目錄: {subdir_path.relative_to(self.project_root)}")
                elif isinstance(subdirs, list):
                    for subdir in subdirs:
                        subdir_path = root_path / subdir
                        subdir_path.mkdir(exist_ok=True)
                        logger.info(f"  ✅ 創建目錄: {subdir_path.relative_to(self.project_root)}")
            
            logger.info("✅ 新目錄結構創建完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 創建目錄結構失敗: {e}")
            return False
    
    def migrate_data(self) -> bool:
        """遷移數據"""
        try:
            logger.info("🔄 開始數據遷移...")
            
            for source_path, target_path in self.migration_map:
                source = self.project_root / source_path
                target = self.project_root / target_path
                
                if not source.exists():
                    logger.info(f"  ⏭️ 跳過不存在的路徑: {source_path}")
                    continue
                
                # 確保目標目錄存在
                target.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    if source.is_dir():
                        # 如果目標已存在，合並內容
                        if target.exists():
                            self._merge_directories(source, target)
                        else:
                            shutil.copytree(source, target)
                    else:
                        shutil.copy2(source, target)
                    
                    logger.info(f"  ✅ 遷移完成: {source_path} → {target_path}")
                    
                except Exception as e:
                    logger.error(f"  ❌ 遷移失敗: {source_path} → {target_path}, 錯誤: {e}")
            
            logger.info("✅ 數據遷移完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 數據遷移失敗: {e}")
            return False
    
    def _merge_directories(self, source: Path, target: Path):
        """合並目錄內容"""
        for item in source.rglob('*'):
            if item.is_file():
                relative_path = item.relative_to(source)
                target_file = target / relative_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 如果目標文件已存在，重命名
                if target_file.exists():
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    target_file = target_file.with_name(f"{target_file.stem}_{timestamp}{target_file.suffix}")
                
                shutil.copy2(item, target_file)
    
    def update_env_file(self) -> bool:
        """更新.env文件"""
        try:
            logger.info("🔄 更新.env文件...")
            
            env_file = self.project_root / '.env'
            if not env_file.exists():
                logger.warning("⚠️ .env文件不存在，跳過更新")
                return True
            
            # 讀取現有內容
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 添加新的環境變量配置
            new_config = """
# ===== 數據目錄配置 (重新組織後) =====
# 統一數據根目錄
TRADINGAGENTS_DATA_DIR=./data

# 子目錄配置（可選，使用默認值）
TRADINGAGENTS_CACHE_DIR=${TRADINGAGENTS_DATA_DIR}/cache
TRADINGAGENTS_SESSIONS_DIR=${TRADINGAGENTS_DATA_DIR}/sessions
TRADINGAGENTS_LOGS_DIR=${TRADINGAGENTS_DATA_DIR}/logs
TRADINGAGENTS_CONFIG_DIR=${TRADINGAGENTS_DATA_DIR}/config
TRADINGAGENTS_TEMP_DIR=${TRADINGAGENTS_DATA_DIR}/temp

# 更新結果目錄配置
TRADINGAGENTS_RESULTS_DIR=${TRADINGAGENTS_DATA_DIR}/analysis_results
"""
            
            # 如果還沒有這些配置，則添加
            if 'TRADINGAGENTS_DATA_DIR' not in content:
                content += new_config
                
                with open(env_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info("✅ .env文件更新完成")
            else:
                logger.info("ℹ️ .env文件已包含數據目錄配置")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 更新.env文件失敗: {e}")
            return False
    
    def create_migration_report(self) -> bool:
        """創建遷移報告"""
        try:
            report = {
                'migration_date': datetime.now().isoformat(),
                'project_root': str(self.project_root),
                'backup_location': str(self.backup_dir),
                'new_structure': self.new_structure,
                'migration_map': self.migration_map,
                'status': 'completed'
            }
            
            report_file = self.project_root / 'data_migration_report.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ 遷移報告已保存: {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 創建遷移報告失敗: {e}")
            return False
    
    def cleanup_old_directories(self, confirm: bool = False) -> bool:
        """清理舊目錄（可選）"""
        if not confirm:
            logger.info("⚠️ 跳過清理舊目錄（需要手動確認）")
            return True
        
        try:
            logger.info("🔄 清理舊目錄...")
            
            # 要清理的舊目錄
            old_dirs = [
                'web/data',
                'tradingagents/dataflows/data_cache'
            ]
            
            for old_dir in old_dirs:
                old_path = self.project_root / old_dir
                if old_path.exists():
                    shutil.rmtree(old_path)
                    logger.info(f"  ✅ 已刪除: {old_dir}")
            
            logger.info("✅ 舊目錄清理完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 清理舊目錄失敗: {e}")
            return False
    
    def run_migration(self, cleanup_old: bool = False) -> bool:
        """運行完整的遷移流程"""
        logger.info("🚀 開始數據目錄重新組織遷移...")
        
        steps = [
            ("創建備份", self.create_backup),
            ("創建新目錄結構", self.create_new_structure),
            ("遷移數據", self.migrate_data),
            ("更新環境變量", self.update_env_file),
            ("創建遷移報告", self.create_migration_report),
        ]
        
        if cleanup_old:
            steps.append(("清理舊目錄", lambda: self.cleanup_old_directories(True)))
        
        for step_name, step_func in steps:
            logger.info(f"\n📋 執行步驟: {step_name}")
            if not step_func():
                logger.error(f"❌ 步驟失敗: {step_name}")
                return False
        
        logger.info("\n🎉 數據目錄重新組織完成！")
        logger.info(f"📁 備份位置: {self.backup_dir}")
        logger.info(f"📊 新數據目錄: {self.project_root / 'data'}")
        
        return True


def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description='數據目錄重新組織遷移腳本')
    parser.add_argument('--project-root', help='項目根目錄路徑')
    parser.add_argument('--cleanup-old', action='store_true', help='遷移後清理舊目錄')
    parser.add_argument('--dry-run', action='store_true', help='僅顯示遷移計劃，不執行實際遷移')
    
    args = parser.parse_args()
    
    migrator = DataDirectoryMigrator(args.project_root)
    
    if args.dry_run:
        logger.info("🔍 遷移計劃預覽:")
        logger.info(f"📁 項目根目錄: {migrator.project_root}")
        logger.info(f"📁 備份目錄: {migrator.backup_dir}")
        logger.info("\n📋 遷移映射:")
        for source, target in migrator.migration_map:
            logger.info(f"  {source} → {target}")
        return
    
    # 執行遷移
    success = migrator.run_migration(cleanup_old=args.cleanup_old)
    
    if success:
        logger.info("\n✅ 遷移成功完成！")
        logger.info("\n📝 後續步驟:")
        logger.info("1. 驗證新目錄結構是否正確")
        logger.info("2. 測試應用程序功能")
        logger.info("3. 確認無誤後可刪除備份目錄")
    else:
        logger.error("\n❌ 遷移失敗！請檢查日誌並從備份恢復")


if __name__ == '__main__':
    main()