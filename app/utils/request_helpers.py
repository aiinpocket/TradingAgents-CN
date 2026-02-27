# 請求相關共用工具函式

from starlette.requests import Request


def get_client_ip(request: Request) -> str:
    """從請求中提取真實客戶端 IP

    優先順序：
    1. CF-Connecting-IP（Cloudflare CDN 提供的原始客戶端 IP）
    2. X-Real-IP（Nginx Ingress 從最後一跳提取）
    3. request.client.host（直連時的 socket 對端 IP）

    並正規化 IPv4-mapped IPv6 格式（::ffff:1.2.3.4 -> 1.2.3.4）
    """
    ip = (
        request.headers.get("cf-connecting-ip")
        or request.headers.get("x-real-ip")
        or (request.client.host if request.client else "unknown")
    )
    if ip.startswith("::ffff:"):
        ip = ip[7:]
    return ip
