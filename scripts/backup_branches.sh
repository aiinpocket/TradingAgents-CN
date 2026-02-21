#!/bin/bash
# 分支備份腳本
echo "🔄 創建分支備份..."

# 創建備份分支
git checkout feature/akshare-integration 2>/dev/null && git checkout -b backup/akshare-integration-$(date +%Y%m%d)
git checkout feature/akshare-integration-clean 2>/dev/null && git checkout -b backup/akshare-integration-clean-$(date +%Y%m%d)

# 推送備份到遠程
git push origin backup/akshare-integration-$(date +%Y%m%d) 2>/dev/null
git push origin backup/akshare-integration-clean-$(date +%Y%m%d) 2>/dev/null

echo "✅ 備份完成"
