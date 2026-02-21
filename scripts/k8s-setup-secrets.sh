#!/bin/bash
# =============================================================
# TradingAgents-CN - K8s Secrets 初始設定腳本
# =============================================================
# 使用方式：
#   方式一（推薦）：透過 ArgoCD 注入 Helm 參數
#     ./scripts/k8s-setup-secrets.sh argocd
#
#   方式二：直接建立 K8s Secret
#     ./scripts/k8s-setup-secrets.sh kubectl
#
# 注意：執行前請先設定好環境變數或修改下方的值
# =============================================================

set -euo pipefail

NAMESPACE="app"
APP_NAME="tradingagents"

# 從環境變數讀取（如果沒有設定，會提示輸入）
read_secret() {
    local var_name="$1"
    local prompt="$2"
    local value="${!var_name:-}"
    if [ -z "$value" ] || [ "$value" = "CHANGE_ME" ]; then
        read -rsp "$prompt: " value
        echo
    fi
    echo "$value"
}

MODE="${1:-argocd}"

if [ "$MODE" = "argocd" ]; then
    echo "=== 透過 ArgoCD 注入 Secrets ==="
    echo "請確保已安裝 argocd CLI 並已登入"
    echo ""

    # LLM API 金鑰（至少需要一個）
    OPENAI_KEY=$(read_secret "OPENAI_API_KEY" "OPENAI_API_KEY")
    FINNHUB_KEY=$(read_secret "FINNHUB_API_KEY" "FINNHUB_API_KEY")
    MONGO_PASS=$(read_secret "MONGODB_PASSWORD" "MONGODB_PASSWORD")
    REDIS_PASS=$(read_secret "REDIS_PASSWORD" "REDIS_PASSWORD")
    COOKIE_KEY=$(read_secret "COOKIE_SECRET_KEY" "COOKIE_SECRET_KEY")

    argocd app set "$APP_NAME" \
        --helm-set-string "secrets.openaiApiKey=$OPENAI_KEY" \
        --helm-set-string "secrets.finnhubApiKey=$FINNHUB_KEY" \
        --helm-set-string "secrets.mongodbPassword=$MONGO_PASS" \
        --helm-set-string "secrets.redisPassword=$REDIS_PASS" \
        --helm-set-string "secrets.cookieSecretKey=$COOKIE_KEY"

    echo ""
    echo "基本 secrets 已設定完成"
    echo ""
    echo "如需設定額外的 API 金鑰，請執行："
    echo "  argocd app set $APP_NAME --helm-set-string 'secrets.anthropicApiKey=YOUR_KEY'"

elif [ "$MODE" = "kubectl" ]; then
    echo "=== 直接建立 K8s Secret ==="
    echo "請確保 kubectl 已連線到目標叢集"
    echo ""

    OPENAI_KEY=$(read_secret "OPENAI_API_KEY" "OPENAI_API_KEY")
    FINNHUB_KEY=$(read_secret "FINNHUB_API_KEY" "FINNHUB_API_KEY")
    MONGO_PASS=$(read_secret "MONGODB_PASSWORD" "MONGODB_PASSWORD")
    REDIS_PASS=$(read_secret "REDIS_PASSWORD" "REDIS_PASSWORD")
    COOKIE_KEY=$(read_secret "COOKIE_SECRET_KEY" "COOKIE_SECRET_KEY")

    kubectl create secret generic "${APP_NAME}-secret" \
        --namespace "$NAMESPACE" \
        --from-literal="OPENAI_API_KEY=$OPENAI_KEY" \
        --from-literal="FINNHUB_API_KEY=$FINNHUB_KEY" \
        --from-literal="MONGODB_PASSWORD=$MONGO_PASS" \
        --from-literal="REDIS_PASSWORD=$REDIS_PASS" \
        --from-literal="COOKIE_SECRET_KEY=$COOKIE_KEY" \
        --from-literal="ANTHROPIC_API_KEY=" \
        --dry-run=client -o yaml | kubectl apply -f -

    echo ""
    echo "K8s Secret 已建立/更新於 $NAMESPACE namespace"

else
    echo "使用方式: $0 [argocd|kubectl]"
    exit 1
fi
