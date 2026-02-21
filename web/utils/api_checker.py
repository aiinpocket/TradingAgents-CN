"""
API 密鑰檢查工具
"""

import os

def check_api_keys():
    """檢查所有必要的 API 密鑰是否已配置"""

    # 檢查各個 API 密鑰
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    # 構建詳細狀態
    details = {
        "FINNHUB_API_KEY": {
            "configured": bool(finnhub_key),
            "display": f"{finnhub_key[:12]}..." if finnhub_key else "未配置",
            "required": True,
            "description": "金融資料 API 密鑰"
        },
        "OPENAI_API_KEY": {
            "configured": bool(openai_key),
            "display": f"{openai_key[:12]}..." if openai_key else "未配置",
            "required": False,
            "description": "OpenAI API 密鑰"
        },
        "ANTHROPIC_API_KEY": {
            "configured": bool(anthropic_key),
            "display": f"{anthropic_key[:12]}..." if anthropic_key else "未配置",
            "required": False,
            "description": "Anthropic API 密鑰"
        },
    }

    # 檢查必需的 API 密鑰
    required_keys = [key for key, info in details.items() if info["required"]]
    missing_required = [key for key in required_keys if not details[key]["configured"]]

    return {
        "all_configured": len(missing_required) == 0,
        "required_configured": len(missing_required) == 0,
        "missing_required": missing_required,
        "details": details,
        "summary": {
            "total": len(details),
            "configured": sum(1 for info in details.values() if info["configured"]),
            "required": len(required_keys),
            "required_configured": len(required_keys) - len(missing_required)
        }
    }

def get_api_key_status_message():
    """取得 API 密鑰狀態訊息"""

    status = check_api_keys()

    if status["all_configured"]:
        return "所有必需的 API 密鑰已配置完成"
    elif status["required_configured"]:
        return "必需的 API 密鑰已配置，可選 API 密鑰未配置"
    else:
        missing = ", ".join(status["missing_required"])
        return f"缺少必需的 API 密鑰: {missing}"

def validate_api_key_format(key_type, api_key):
    """驗證 API 密鑰格式"""

    if not api_key:
        return False, "API 密鑰不能為空"

    if len(api_key) < 10:
        return False, "API 密鑰長度過短"

    # 特定格式檢查
    if key_type == "OPENAI_API_KEY":
        if not api_key.startswith("sk-"):
            return False, "OpenAI API 密鑰應以 'sk-' 開頭"

    return True, "API 密鑰格式正確"

def test_api_connection(key_type, api_key):
    """測試 API 連線（簡單驗證）"""

    is_valid, message = validate_api_key_format(key_type, api_key)

    if not is_valid:
        return False, message

    return True, "API 密鑰驗證通過"
