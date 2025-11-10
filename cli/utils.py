import questionary
from typing import List, Optional, Tuple, Dict
from rich.console import Console

from cli.models import AnalystType
from tradingagents.utils.logging_manager import get_logger
from tradingagents.utils.stock_utils import StockUtils

logger = get_logger('cli')
console = Console()

ANALYST_ORDER = [
    ("市場分析師 | Market Analyst", AnalystType.MARKET),
    ("社交媒體分析師 | Social Media Analyst", AnalystType.SOCIAL),
    ("新聞分析師 | News Analyst", AnalystType.NEWS),
    ("基本面分析師 | Fundamentals Analyst", AnalystType.FUNDAMENTALS),
]


def get_ticker() -> str:
    """Prompt the user to enter a ticker symbol."""
    ticker = questionary.text(
        "請輸入要分析的股票代碼 | Enter the ticker symbol to analyze:",
        validate=lambda x: len(x.strip()) > 0 or "請輸入有效的股票代碼 | Please enter a valid ticker symbol.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not ticker:
        logger.info(f"\n[red]未提供股票代碼，退出程序... | No ticker symbol provided. Exiting...[/red]")
        exit(1)

    return ticker.strip().upper()


def get_analysis_date() -> str:
    """Prompt the user to enter a date in YYYY-MM-DD format."""
    import re
    from datetime import datetime

    def validate_date(date_str: str) -> bool:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            return False
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    date = questionary.text(
        "請輸入分析日期 (YYYY-MM-DD) | Enter the analysis date (YYYY-MM-DD):",
        validate=lambda x: validate_date(x.strip())
        or "請輸入有效的日期格式 YYYY-MM-DD | Please enter a valid date in YYYY-MM-DD format.",
        style=questionary.Style(
            [
                ("text", "fg:green"),
                ("highlighted", "noinherit"),
            ]
        ),
    ).ask()

    if not date:
        logger.info(f"\n[red]未提供日期，退出程序... | No date provided. Exiting...[/red]")
        exit(1)

    return date.strip()


def select_analysts(ticker: str = None) -> List[AnalystType]:
    """Select analysts using an interactive checkbox."""

    available_analysts = ANALYST_ORDER.copy()

    choices = questionary.checkbox(
        "選擇您的分析師團隊 | Select Your [Analysts Team]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in available_analysts
        ],
        instruction="\n- 按空格鍵選擇/取消選擇分析師 | Press Space to select/unselect analysts\n- 按 'a' 鍵全選/取消全選 | Press 'a' to select/unselect all\n- 按回車鍵完成選擇 | Press Enter when done",
        validate=lambda x: len(x) > 0 or "您必须至少選擇一個分析師 | You must select at least one analyst.",
        style=questionary.Style(
            [
                ("checkbox-selected", "fg:green"),
                ("selected", "fg:green noinherit"),
                ("highlighted", "noinherit"),
                ("pointer", "noinherit"),
            ]
        ),
    ).ask()

    if not choices:
        logger.info(f"\n[red]未選擇分析師，退出程序... | No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("浅層 - 快速研究，少量辩論和策略討論 | Shallow - Quick research, few debate rounds", 1),
        ("中等 - 中等程度，適度的辩論和策略討論 | Medium - Moderate debate and strategy discussion", 3),
        ("深度 - 全面研究，深入的辩論和策略討論 | Deep - Comprehensive research, in-depth debate", 5),
    ]

    choice = questionary.select(
        "選擇您的研究深度 | Select Your [Research Depth]:",
        choices=[
            questionary.Choice(display, value=value) for display, value in DEPTH_OPTIONS
        ],
        instruction="\n- 使用方向鍵導航 | Use arrow keys to navigate\n- 按回車鍵選擇 | Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:yellow noinherit"),
                ("highlighted", "fg:yellow noinherit"),
                ("pointer", "fg:yellow noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        logger.info(f"\n[red]未選擇研究深度，退出程序... | No research depth selected. Exiting...[/red]")
        exit(1)

    return choice


def select_shallow_thinking_agent(provider) -> str:
    """Select shallow thinking llm engine using an interactive selection."""

    # Define shallow thinking llm engine options with their corresponding model names
    SHALLOW_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4o-mini - Fast and efficient for quick tasks", "gpt-4o-mini"),
            ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
            ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
            ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Fast inference and standard capabilities", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5 - Highly capable standard model", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7 - Exceptional hybrid reasoning and agentic capabilities", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4 - High performance and excellent reasoning", "claude-sonnet-4-0"),
        ],
        "google": [
            ("Gemini 2.5 Pro - 🚀 最新旗舰模型", "gemini-2.5-pro"),
            ("Gemini 2.5 Flash - ⚡ 最新快速模型", "gemini-2.5-flash"),
            ("Gemini 2.5 Flash Lite - 💡 轻量快速", "gemini-2.5-flash-lite"),
            ("Gemini 2.5 Pro-002 - 🔧 優化版本", "gemini-2.5-pro-002"),
            ("Gemini 2.5 Flash-002 - ⚡ 優化快速版", "gemini-2.5-flash-002"),
            ("Gemini 2.5 Flash - Adaptive thinking, cost efficiency", "gemini-2.5-flash-preview-05-20"),
            ("Gemini 2.5 Pro Preview - 預覽版本", "gemini-2.5-pro-preview-06-05"),
            ("Gemini 2.0 Flash Lite - 轻量版本", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - 推薦使用", "gemini-2.0-flash"),
            ("Gemini 1.5 Pro - 强大性能", "gemini-1.5-pro"),
            ("Gemini 1.5 Flash - 快速響應", "gemini-1.5-flash"),
        ],
        "openrouter": [
            ("Meta: Llama 4 Scout", "meta-llama/llama-4-scout:free"),
            ("Meta: Llama 3.3 8B Instruct - A lightweight and ultra-fast variant of Llama 3.3 70B", "meta-llama/llama-3.3-8b-instruct:free"),
            ("google/gemini-2.0-flash-exp:free - Gemini Flash 2.0 offers a significantly faster time to first token", "google/gemini-2.0-flash-exp:free"),
        ],
        "ollama": [
            ("llama3.1 local", "llama3.1"),
            ("llama3.2 local", "llama3.2"),
        ],
        "阿里百炼 (dashscope)": [
            ("通義千問 Turbo - 快速響應，適合日常對話", "qwen-turbo"),
            ("通義千問 Plus - 平衡性能和成本", "qwen-plus"),
            ("通義千問 Max - 最强性能", "qwen-max"),
        ],
        "deepseek v3": [
            ("DeepSeek Chat - 通用對話模型，適合股票投資分析", "deepseek-chat"),
        ],
        "🔧 自定義openai端點": [
            ("GPT-4o-mini - Fast and efficient for quick tasks", "gpt-4o-mini"),
            ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
            ("GPT-3.5-turbo - Cost-effective option", "gpt-3.5-turbo"),
            ("Claude-3-haiku - Fast Anthropic model", "claude-3-haiku-20240307"),
            ("Llama-3.1-8B - Open source model", "meta-llama/llama-3.1-8b-instruct"),
            ("Qwen2.5-7B - Chinese optimized model", "qwen/qwen-2.5-7b-instruct"),
            ("自定義模型 - 手動輸入模型名稱", "custom"),
        ]
    }

    # 獲取選項列表
    options = SHALLOW_AGENT_OPTIONS[provider.lower()]

    # 為國產LLM設置默認選擇
    default_choice = None
    if "阿里百炼" in provider:
        default_choice = options[0][1]  # 通義千問 Turbo
    elif "deepseek" in provider.lower():
        default_choice = options[0][1]  # DeepSeek Chat (推薦選擇)

    choice = questionary.select(
        "選擇您的快速思考LLM引擎 | Select Your [Quick-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in options
        ],
        default=default_choice,
        instruction="\n- 使用方向鍵導航 | Use arrow keys to navigate\n- 按回車鍵選擇 | Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:green noinherit"),
                ("highlighted", "fg:green noinherit"),
                ("pointer", "fg:green noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        console.print(
            "\n[red]未選擇快速思考LLM引擎，退出程序... | No shallow thinking llm engine selected. Exiting...[/red]"
        )
        exit(1)

    return choice


def select_deep_thinking_agent(provider) -> str:
    """Select deep thinking llm engine using an interactive selection."""

    # Define deep thinking llm engine options with their corresponding model names
    DEEP_AGENT_OPTIONS = {
        "openai": [
            ("GPT-4.1-nano - Ultra-lightweight model for basic operations", "gpt-4.1-nano"),
            ("GPT-4.1-mini - Compact model with good performance", "gpt-4.1-mini"),
            ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
            ("o4-mini - Specialized reasoning model (compact)", "o4-mini"),
            ("o3-mini - Advanced reasoning model (lightweight)", "o3-mini"),
            ("o3 - Full advanced reasoning model", "o3"),
            ("o1 - Premier reasoning and problem-solving model", "o1"),
        ],
        "anthropic": [
            ("Claude Haiku 3.5 - Fast inference and standard capabilities", "claude-3-5-haiku-latest"),
            ("Claude Sonnet 3.5 - Highly capable standard model", "claude-3-5-sonnet-latest"),
            ("Claude Sonnet 3.7 - Exceptional hybrid reasoning and agentic capabilities", "claude-3-7-sonnet-latest"),
            ("Claude Sonnet 4 - High performance and excellent reasoning", "claude-sonnet-4-0"),
            ("Claude Opus 4 - Most powerful Anthropic model", "	claude-opus-4-0"),
        ],
        "google": [
            ("Gemini 2.5 Pro - 🚀 最新旗舰模型", "gemini-2.5-pro"),
            ("Gemini 2.5 Flash - ⚡ 最新快速模型", "gemini-2.5-flash"),
            ("Gemini 2.5 Flash Lite - 💡 轻量快速", "gemini-2.5-flash-lite"),
            ("Gemini 2.5 Pro-002 - 🔧 優化版本", "gemini-2.5-pro-002"),
            ("Gemini 2.5 Flash-002 - ⚡ 優化快速版", "gemini-2.5-flash-002"),
            ("Gemini 2.5 Flash - Adaptive thinking, cost efficiency", "gemini-2.5-flash-preview-05-20"),
            ("Gemini 2.5 Pro Preview - 預覽版本", "gemini-2.5-pro-preview-06-05"),
            ("Gemini 2.0 Flash Lite - 轻量版本", "gemini-2.0-flash-lite"),
            ("Gemini 2.0 Flash - 推薦使用", "gemini-2.0-flash"),
            ("Gemini 1.5 Pro - 强大性能", "gemini-1.5-pro"),
            ("Gemini 1.5 Flash - 快速響應", "gemini-1.5-flash"),
        ],
        "openrouter": [
            ("DeepSeek V3 - a 685B-parameter, mixture-of-experts model", "deepseek/deepseek-chat-v3-0324:free"),
            ("Deepseek - latest iteration of the flagship chat model family from the DeepSeek team.", "deepseek/deepseek-chat-v3-0324:free"),
        ],
        "ollama": [
            ("llama3.1 local", "llama3.1"),
            ("qwen3", "qwen3"),
        ],
        "阿里百炼 (dashscope)": [
            ("通義千問 Turbo - 快速響應，適合日常對話", "qwen-turbo"),
            ("通義千問 Plus - 平衡性能和成本", "qwen-plus"),
            ("通義千問 Max - 最强性能", "qwen-max"),
            ("通義千問 Max 長文本版 - 支持超長上下文", "qwen-max-longcontext"),
        ],
        "deepseek v3": [
            ("DeepSeek Chat - 通用對話模型，適合股票投資分析", "deepseek-chat"),
        ],
        "🔧 自定義openai端點": [
            ("GPT-4o - Standard model with solid capabilities", "gpt-4o"),
            ("GPT-4o-mini - Fast and efficient for quick tasks", "gpt-4o-mini"),
            ("o1-preview - Advanced reasoning model", "o1-preview"),
            ("o1-mini - Compact reasoning model", "o1-mini"),
            ("Claude-3-sonnet - Balanced Anthropic model", "claude-3-sonnet-20240229"),
            ("Claude-3-opus - Most capable Anthropic model", "claude-3-opus-20240229"),
            ("Llama-3.1-70B - Large open source model", "meta-llama/llama-3.1-70b-instruct"),
            ("Qwen2.5-72B - Chinese optimized model", "qwen/qwen-2.5-72b-instruct"),
            ("自定義模型 - 手動輸入模型名稱", "custom"),
        ]
    }
    
    # 獲取選項列表
    options = DEEP_AGENT_OPTIONS[provider.lower()]

    # 為國產LLM設置默認選擇
    default_choice = None
    if "阿里百炼" in provider:
        default_choice = options[0][1]  # 通義千問 Turbo
    elif "deepseek" in provider.lower():
        default_choice = options[0][1]  # DeepSeek Chat

    choice = questionary.select(
        "選擇您的深度思考LLM引擎 | Select Your [Deep-Thinking LLM Engine]:",
        choices=[
            questionary.Choice(display, value=value)
            for display, value in options
        ],
        default=default_choice,
        instruction="\n- 使用方向鍵導航 | Use arrow keys to navigate\n- 按回車鍵選擇 | Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:green noinherit"),
                ("highlighted", "fg:green noinherit"),
                ("pointer", "fg:green noinherit"),
            ]
        ),
    ).ask()

    if choice is None:
        logger.info(f"\n[red]未選擇深度思考LLM引擎，退出程序... | No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice

def select_llm_provider() -> tuple[str, str]:
    """Select the LLM provider using interactive selection."""
    # Define LLM provider options with their corresponding endpoints
    # 國產LLM作為默認推薦選項放在前面
    BASE_URLS = [
        ("阿里百炼 (DashScope)", "https://dashscope.aliyuncs.com/api/v1"),
        ("DeepSeek V3", "https://api.deepseek.com"),
        ("OpenAI", "https://api.openai.com/v1"),
        ("🔧 自定義OpenAI端點", "custom"),
        ("Anthropic", "https://api.anthropic.com/"),
        ("Google", "https://generativelanguage.googleapis.com/v1"),
        ("Openrouter", "https://openrouter.ai/api/v1"),
        ("Ollama", "http://localhost:11434/v1"),
    ]
    
    choice = questionary.select(
        "選擇您的LLM提供商 | Select your LLM Provider:",
        choices=[
            questionary.Choice(display, value=(display, value))
            for display, value in BASE_URLS
        ],
        default=(BASE_URLS[0][0], BASE_URLS[0][1]),
        instruction="\n- 使用方向鍵導航 | Use arrow keys to navigate\n- 按回車鍵選擇 | Press Enter to select",
        style=questionary.Style(
            [
                ("selected", "fg:green noinherit"),
                ("highlighted", "fg:green noinherit"),
                ("pointer", "fg:green noinherit"),
            ]
        ),
    ).ask()
    
    if choice is None:
        logger.info(f"\n[red]未選擇LLM提供商，退出程序... | No LLM provider selected. Exiting...[/red]")
        exit(1)
    
    display_name, url = choice
    
    # 如果選擇了自定義OpenAI端點，詢問用戶輸入URL
    if url == "custom":
        custom_url = questionary.text(
            "請輸入自定義OpenAI端點URL | Please enter custom OpenAI endpoint URL:",
            default="https://api.openai.com/v1",
            instruction="例如: https://api.openai.com/v1 或 http://localhost:8000/v1"
        ).ask()
        
        if custom_url is None:
            logger.info(f"\n[red]未輸入自定義URL，退出程序... | No custom URL entered. Exiting...[/red]")
            exit(1)
            
        url = custom_url
        logger.info(f"您選擇了 | You selected: {display_name}\tURL: {url}")
        
        # 設置環境變量以便後续使用
        os.environ['CUSTOM_OPENAI_BASE_URL'] = url
    else:
        logger.info(f"您選擇了 | You selected: {display_name}\tURL: {url}")

    return display_name, url
