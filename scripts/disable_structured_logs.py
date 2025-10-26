#!/usr/bin/env python3
"""
禁用結構化日誌，只保留主日誌文件
"""

from pathlib import Path

def disable_structured_logging():
    """禁用結構化日誌"""
    print("🔧 禁用結構化日誌...")
    
    config_file = Path("config/logging_docker.toml")
    if not config_file.exists():
        print("❌ 配置文件不存在")
        return False
    
    # 讀取配置
    with open(config_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 禁用結構化日誌
    new_content = content.replace(
        '[logging.handlers.structured]\nenabled = true',
        '[logging.handlers.structured]\nenabled = false'
    )
    
    # 寫回文件
    with open(config_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ 結構化日誌已禁用")
    print("💡 現在只會生成 tradingagents.log 文件")
    print("🔄 需要重新構建Docker鏡像: docker-compose build")
    
    return True

if __name__ == "__main__":
    disable_structured_logging()
