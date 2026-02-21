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

    # 構建詳細狀態（只顯示配置狀態，不洩露密鑰內容）
    details = {
        "FINNHUB_API_KEY": {
            "configured": bool(finnhub_key),
            "display": "已配置" if finnhub_key else "未配置",
            "required": True,
            "description": "金融資料 API 密鑰"
        },
        "OPENAI_API_KEY": {
            "configured": bool(openai_key),
            "display": "已配置" if openai_key else "未配置",
            "required": False,
            "description": "OpenAI API 密鑰"
        },
        "ANTHROPIC_API_KEY": {
            "configured": bool(anthropic_key),
            "display": "已配置" if anthropic_key else "未配置",
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

