"""
API密鑰檢查工具
"""

import os

def check_api_keys():
    """檢查所有必要的API密鑰是否已配置"""

    # 檢查各個API密鑰
    dashscope_key = os.getenv("DASHSCOPE_API_KEY")
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    qianfan_key = os.getenv("QIANFAN_API_KEY")

    
    # 構建詳細狀態
    details = {
        "DASHSCOPE_API_KEY": {
            "configured": bool(dashscope_key),
            "display": f"{dashscope_key[:12]}..." if dashscope_key else "未配置",
            "required": True,
            "description": "阿里百炼API密鑰"
        },
        "FINNHUB_API_KEY": {
            "configured": bool(finnhub_key),
            "display": f"{finnhub_key[:12]}..." if finnhub_key else "未配置",
            "required": True,
            "description": "金融數據API密鑰"
        },
        "OPENAI_API_KEY": {
            "configured": bool(openai_key),
            "display": f"{openai_key[:12]}..." if openai_key else "未配置",
            "required": False,
            "description": "OpenAI API密鑰"
        },
        "ANTHROPIC_API_KEY": {
            "configured": bool(anthropic_key),
            "display": f"{anthropic_key[:12]}..." if anthropic_key else "未配置",
            "required": False,
            "description": "Anthropic API密鑰"
        },
        "GOOGLE_API_KEY": {
            "configured": bool(google_key),
            "display": f"{google_key[:12]}..." if google_key else "未配置",
            "required": False,
            "description": "Google AI API密鑰"
        },
        "QIANFAN_ACCESS_KEY": {
            "configured": bool(qianfan_key),
            "display": f"{qianfan_key[:16]}..." if qianfan_key else "未配置",
            "required": False,
            "description": "文心一言（千帆）API Key（OpenAI兼容），一般以 bce-v3/ 開头"
        },
        # QIANFAN_SECRET_KEY 不再用於OpenAI兼容路徑，仅保留給腳本示例使用
        # "QIANFAN_SECRET_KEY": {
        #     "configured": bool(qianfan_sk),
        #     "display": f"{qianfan_sk[:12]}..." if qianfan_sk else "未配置",
        #     "required": False,
        #     "description": "文心一言（千帆）Secret Key (仅腳本示例)"
        # },
    }
    
    # 檢查必需的API密鑰
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
    """獲取API密鑰狀態消息"""
    
    status = check_api_keys()
    
    if status["all_configured"]:
        return "✅ 所有必需的API密鑰已配置完成"
    elif status["required_configured"]:
        return "✅ 必需的API密鑰已配置，可選API密鑰未配置"
    else:
        missing = ", ".join(status["missing_required"])
        return f"❌ 缺少必需的API密鑰: {missing}"

def validate_api_key_format(key_type, api_key):
    """驗證API密鑰格式"""
    
    if not api_key:
        return False, "API密鑰不能為空"
    
    # 基本長度檢查
    if len(api_key) < 10:
        return False, "API密鑰長度過短"
    
    # 特定格式檢查
    if key_type == "DASHSCOPE_API_KEY":
        if not api_key.startswith("sk-"):
            return False, "阿里百炼API密鑰應以'sk-'開头"
    elif key_type == "OPENAI_API_KEY":
        if not api_key.startswith("sk-"):
            return False, "OpenAI API密鑰應以'sk-'開头"
    elif key_type == "QIANFAN_API_KEY":
        if not api_key.startswith("bce-v3/"):
            return False, "千帆 API Key（OpenAI兼容）應以 'bce-v3/' 開头"
    
    return True, "API密鑰格式正確"

def test_api_connection(key_type, api_key):
    """測試API連接（簡單驗證）"""
    
    # 這里可以添加實际的API連接測試
    # 為了簡化，現在只做格式驗證
    
    is_valid, message = validate_api_key_format(key_type, api_key)
    
    if not is_valid:
        return False, message
    
    # 可以在這里添加實际的API調用測試
    # 例如：調用一個簡單的API端點驗證密鑰有效性
    
    return True, "API密鑰驗證通過"
