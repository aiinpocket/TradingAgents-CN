#!/bin/bash
# 分支备份腳本
echo "🔄 創建分支备份..."

# 創建备份分支
git checkout feature/akshare-integration 2>/dev/null && git checkout -b backup/akshare-integration-$(date +%Y%m%d)
git checkout feature/akshare-integration-clean 2>/dev/null && git checkout -b backup/akshare-integration-clean-$(date +%Y%m%d)

# 推送备份到远程
git push origin backup/akshare-integration-$(date +%Y%m%d) 2>/dev/null
git push origin backup/akshare-integration-clean-$(date +%Y%m%d) 2>/dev/null

echo "✅ 备份完成"
