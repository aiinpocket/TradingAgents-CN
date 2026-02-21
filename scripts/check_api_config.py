#!/usr/bin/env python3
"""
API 配置檢查工具
檢查各種 API 密鑰的配置狀態和可用性
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 新增專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_env_file():
    """檢查 .env 檔案是否存在"""
    env_file = project_root / ".env"
    if env_file.exists():
        print("  .env file exists")
        load_dotenv(env_file)
        return True
    else:
        print("  .env file not found")
        print("  Please copy .env.example to .env and configure API keys")
        return False


def check_api_keys():
    """檢查各 API 密鑰配置狀態"""
    print("\n  Checking API key configuration...")

    apis = {
        'FINNHUB_API_KEY': 'FinnHub (Financial Data)',
        'OPENAI_API_KEY': 'OpenAI',
        'ANTHROPIC_API_KEY': 'Anthropic',
    }

    configured_apis = []
    missing_apis = []

    for env_var, name in apis.items():
        value = os.getenv(env_var)
        if value and value.strip() and not value.startswith("your_"):
            print(f"  [OK] {name}: Configured")
            configured_apis.append(name)
        else:
            print(f"  [--] {name}: Not configured")
            missing_apis.append(name)

    return configured_apis, missing_apis


def check_memory_functionality():
    """檢查記憶功能是否可用"""
    print("\n  Checking memory functionality...")

    try:
        from tradingagents.agents.utils.memory import FinancialSituationMemory
        from tradingagents.default_config import DEFAULT_CONFIG

        config = DEFAULT_CONFIG.copy()
        config["llm_provider"] = "openai"

        memory = FinancialSituationMemory("test_memory", config)

        embedding = memory.get_embedding("Test text for embedding")

        if all(x == 0.0 for x in embedding):
            print("  Memory disabled (returning zero vectors)")
            print("  Reason: OPENAI_API_KEY not configured")
            return False
        else:
            print(f"  Memory functional (vector dimension: {len(embedding)})")
            return True

    except Exception as e:
        print(f"  Memory test failed: {e}")
        return False


def provide_recommendations(configured_apis, missing_apis):
    """提供配置建議"""
    print("\n  Configuration Recommendations:")
    print("=" * 50)

    if len(configured_apis) == 0:
        print("  WARNING: No API keys configured")
        print("  System may not function properly")
        print("  Please configure at least one LLM API key")
        print()

    print("  Minimum configuration:")
    print("    1. At least one LLM API key (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
    print("    2. FINNHUB_API_KEY for financial data")
    print()

    print("  Recommended configuration:")
    print("    - OPENAI_API_KEY: OpenAI (recommended)")
    print("    - FINNHUB_API_KEY: Financial data (free tier available)")
    print("    - ANTHROPIC_API_KEY: Anthropic (optional)")


def main():
    """主函式"""
    print("  TradingAgents API Configuration Checker")
    print("=" * 60)

    # 檢查 .env 檔案
    if not check_env_file():
        return

    # 檢查 API 密鑰
    configured_apis, missing_apis = check_api_keys()

    # 檢查記憶功能
    memory_ok = check_memory_functionality()

    # 摘要
    print("\n  Configuration Summary:")
    print("=" * 30)
    print(f"  Memory: {'Available' if memory_ok else 'Disabled'}")
    print(f"  Configured APIs: {len(configured_apis)}")
    print(f"  Missing APIs: {len(missing_apis)}")

    # 提供建議
    provide_recommendations(configured_apis, missing_apis)

    # 系統狀態評估
    if len(configured_apis) >= 2:
        print("\n  System configured properly, all features available!")
    elif len(configured_apis) >= 1:
        print("\n  System can run with limited features. Consider adding more API keys.")
    else:
        print("\n  System configuration insufficient. Please configure required API keys.")


if __name__ == "__main__":
    main()
