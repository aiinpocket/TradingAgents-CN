#!/usr/bin/env python3
"""
Git分支管理工具
幫助管理TradingAgents-CN項目的分支
"""

import subprocess
import sys
from typing import List, Dict
import argparse

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('scripts')


class BranchManager:
    def __init__(self):
        self.current_branch = self.get_current_branch()
        
    def run_git_command(self, command: List[str]) -> tuple:
        """運行Git命令"""
        try:
            result = subprocess.run(
                ['git'] + command, 
                capture_output=True, 
                text=True, 
                check=True
            )
            return True, result.stdout.strip(), result.stderr.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stdout, e.stderr
    
    def get_current_branch(self) -> str:
        """獲取當前分支"""
        success, stdout, _ = self.run_git_command(['branch', '--show-current'])
        return stdout if success else "unknown"
    
    def get_all_branches(self) -> Dict[str, List[str]]:
        """獲取所有分支"""
        branches = {'local': [], 'remote': []}
        
        # 本地分支
        success, stdout, _ = self.run_git_command(['branch'])
        if success:
            for line in stdout.split('\n'):
                branch = line.strip().replace('* ', '')
                if branch:
                    branches['local'].append(branch)
        
        # 远程分支
        success, stdout, _ = self.run_git_command(['branch', '-r'])
        if success:
            for line in stdout.split('\n'):
                branch = line.strip()
                if branch and not branch.startswith('origin/HEAD'):
                    branches['remote'].append(branch)
        
        return branches
    
    def get_merged_branches(self, target_branch: str = 'main') -> List[str]:
        """獲取已合並到目標分支的分支"""
        success, stdout, _ = self.run_git_command(['branch', '--merged', target_branch])
        if not success:
            return []
        
        merged = []
        for line in stdout.split('\n'):
            branch = line.strip().replace('* ', '')
            if branch and branch != target_branch:
                merged.append(branch)
        
        return merged
    
    def get_unmerged_branches(self, target_branch: str = 'main') -> List[str]:
        """獲取未合並到目標分支的分支"""
        success, stdout, _ = self.run_git_command(['branch', '--no-merged', target_branch])
        if not success:
            return []
        
        unmerged = []
        for line in stdout.split('\n'):
            branch = line.strip().replace('* ', '')
            if branch and branch != target_branch:
                unmerged.append(branch)
        
        return unmerged
    
    def check_status(self):
        """檢查Git狀態"""
        logger.debug(f"🔍 Git分支狀態檢查")
        logger.info(f"=")
        
        # 當前分支
        logger.info(f"📍 當前分支: {self.current_branch}")
        
        # 未提交的更改
        success, stdout, _ = self.run_git_command(['status', '--porcelain'])
        if success:
            if stdout:
                logger.warning(f"⚠️ 未提交的更改: {len(stdout.split())} 個文件")
                for line in stdout.split('\n')[:5]:  # 只顯示前5個
                    if line:
                        logger.info(f"   {line}")
                lines = stdout.split('\n')
                if len(lines) > 5:
                    logger.info(f"   ... 还有 {len(lines) - 5} 個文件")
            else:
                logger.info(f"✅ 工作目錄干净")
        
        # 分支信息
        branches = self.get_all_branches()
        logger.info(f"\n📋 本地分支 ({len(branches['local'])}個):")
        for branch in branches['local']:
            marker = "👉 " if branch == self.current_branch else "   "
            logger.info(f"{marker}{branch}")
        
        logger.info(f"\n🌐 远程分支 ({len(branches['remote'])}個):")
        for branch in branches['remote'][:10]:  # 只顯示前10個
            logger.info(f"   {branch}")
        if len(branches['remote']) > 10:
            logger.info(f"   ... 还有 {len(branches['remote']) - 10} 個远程分支")
        
        # 合並狀態
        merged = self.get_merged_branches()
        unmerged = self.get_unmerged_branches()
        
        logger.info(f"\n✅ 已合並到main ({len(merged)}個):")
        for branch in merged:
            logger.info(f"   {branch}")
        
        logger.warning(f"\n⚠️ 未合並到main ({len(unmerged)}個):")
        for branch in unmerged:
            logger.info(f"   {branch}")
    
    def release_version(self, version: str):
        """發布版本"""
        logger.info(f"🚀 發布版本 {version}")
        logger.info(f"=")
        
        # 檢查當前狀態
        success, stdout, _ = self.run_git_command(['status', '--porcelain'])
        if success and stdout:
            logger.error(f"❌ 工作目錄不干净，請先提交所有更改")
            return False
        
        # 切換到main分支
        logger.info(f"📍 切換到main分支...")
        success, _, stderr = self.run_git_command(['checkout', 'main'])
        if not success:
            logger.error(f"❌ 切換到main分支失败: {stderr}")
            return False
        
        # 拉取最新代碼
        logger.info(f"📥 拉取最新代碼...")
        success, _, stderr = self.run_git_command(['pull', 'origin', 'main'])
        if not success:
            logger.error(f"❌ 拉取代碼失败: {stderr}")
            return False
        
        # 合並當前功能分支（如果不是main）
        if self.current_branch != 'main':
            logger.info(f"🔀 合並分支 {self.current_branch}...")
            success, _, stderr = self.run_git_command(['merge', self.current_branch])
            if not success:
                logger.error(f"❌ 合並失败: {stderr}")
                return False
        
        # 創建標簽
        logger.info(f"🏷️ 創建版本標簽 {version}...")
        success, _, stderr = self.run_git_command(['tag', '-a', version, '-m', f'Release {version}'])
        if not success:
            logger.error(f"❌ 創建標簽失败: {stderr}")
            return False
        
        # 推送到远程
        logger.info(f"📤 推送到远程...")
        success, _, stderr = self.run_git_command(['push', 'origin', 'main', '--tags'])
        if not success:
            logger.error(f"❌ 推送失败: {stderr}")
            return False
        
        logger.info(f"✅ 版本 {version} 發布成功！")
        return True
    
    def cleanup_branches(self, dry_run: bool = True):
        """清理已合並的分支"""
        logger.info(f"🧹 清理已合並的分支")
        logger.info(f"=")
        
        merged = self.get_merged_branches()
        feature_branches = [b for b in merged if b.startswith(('feature/', 'hotfix/'))]
        
        if not feature_branches:
            logger.info(f"✅ 没有需要清理的功能分支")
            return
        
        logger.info(f"📋 發現 {len(feature_branches)} 個已合並的功能分支:")
        for branch in feature_branches:
            logger.info(f"   {branch}")
        
        if dry_run:
            logger.info(f"\n💡 這是預覽模式，使用 --no-dry-run 執行實际刪除")
            return
        
        # 確認刪除
        confirm = input(f"\n❓ 確認刪除這 {len(feature_branches)} 個分支? (y/N): ")
        if confirm.lower() != 'y':
            logger.error(f"❌ 取消刪除操作")
            return
        
        # 刪除分支
        deleted_count = 0
        for branch in feature_branches:
            logger.info(f"🗑️ 刪除分支: {branch}")
            success, _, stderr = self.run_git_command(['branch', '-d', branch])
            if success:
                deleted_count += 1
                # 嘗試刪除远程分支
                self.run_git_command(['push', 'origin', '--delete', branch])
            else:
                logger.error(f"   ❌ 刪除失败: {stderr}")
        
        logger.info(f"✅ 成功刪除 {deleted_count} 個分支")
    
    def create_feature_branch(self, branch_name: str, base_branch: str = 'main'):
        """創建功能分支"""
        logger.info(f"🌱 創建功能分支: {branch_name}")
        logger.info(f"=")
        
        # 切換到基础分支
        logger.info(f"📍 切換到基础分支: {base_branch}")
        success, _, stderr = self.run_git_command(['checkout', base_branch])
        if not success:
            logger.error(f"❌ 切換失败: {stderr}")
            return False
        
        # 拉取最新代碼
        logger.info(f"📥 拉取最新代碼...")
        success, _, stderr = self.run_git_command(['pull', 'origin', base_branch])
        if not success:
            logger.error(f"❌ 拉取失败: {stderr}")
            return False
        
        # 創建新分支
        logger.info(f"🌱 創建新分支: {branch_name}")
        success, _, stderr = self.run_git_command(['checkout', '-b', branch_name])
        if not success:
            logger.error(f"❌ 創建分支失败: {stderr}")
            return False
        
        logger.info(f"✅ 功能分支 {branch_name} 創建成功！")
        return True

def main():
    parser = argparse.ArgumentParser(description='Git分支管理工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 狀態檢查
    subparsers.add_parser('status', help='檢查分支狀態')
    
    # 版本發布
    release_parser = subparsers.add_parser('release', help='發布版本')
    release_parser.add_argument('version', help='版本號 (如: v0.1.6)')
    
    # 分支清理
    cleanup_parser = subparsers.add_parser('cleanup', help='清理已合並的分支')
    cleanup_parser.add_argument('--no-dry-run', action='store_true', help='執行實际刪除')
    
    # 創建功能分支
    create_parser = subparsers.add_parser('create', help='創建功能分支')
    create_parser.add_argument('name', help='分支名稱')
    create_parser.add_argument('--base', default='main', help='基础分支 (默認: main)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = BranchManager()
    
    if args.command == 'status':
        manager.check_status()
    elif args.command == 'release':
        manager.release_version(args.version)
    elif args.command == 'cleanup':
        manager.cleanup_branches(dry_run=not args.no_dry_run)
    elif args.command == 'create':
        manager.create_feature_branch(args.name, args.base)

if __name__ == '__main__':
    main()
