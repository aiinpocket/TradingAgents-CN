import questionary
from typing import List, Optional, Tuple, Dict
from rich.console import Console

from cli.models import AnalystType
from tradingagents.utils.logging_manager import get_logger
from tradingagents.utils.stock_utils import get_stock_market_info

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
        logger.info(f"\n[red]未提供股票代碼，退出程式... | No ticker symbol provided. Exiting...[/red]")
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
        logger.info(f"\n[red]未提供日期，退出程式... | No date provided. Exiting...[/red]")
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
        validate=lambda x: len(x) > 0 or "您必須至少選擇一個分析師 | You must select at least one analyst.",
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
        logger.info(f"\n[red]未選擇分析師，退出程式... | No analysts selected. Exiting...[/red]")
        exit(1)

    return choices


def select_research_depth() -> int:
    """Select research depth using an interactive selection."""

    # Define research depth options with their corresponding values
    DEPTH_OPTIONS = [
        ("淺層 - 快速研究，少量辯論和策略討論 | Shallow - Quick research, few debate rounds", 1),
        ("中等 - 中等程度，適度的辯論和策略討論 | Medium - Moderate debate and strategy discussion", 3),
        ("深度 - 全面研究，深入的辯論和策略討論 | Deep - Comprehensive research, in-depth debate", 5),
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
        logger.info(f"\n[red]未選擇研究深度，退出程式... | No research depth selected. Exiting...[/red]")
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
    }

    # 取得選項列表
    options = SHALLOW_AGENT_OPTIONS[provider.lower()]

    default_choice = None

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
            "\n[red]未選擇快速思考LLM引擎，退出程式... | No shallow thinking llm engine selected. Exiting...[/red]"
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
            ("Claude Opus 4 - Most powerful Anthropic model", "claude-opus-4-0"),
        ],
    }

    # 取得選項列表
    options = DEEP_AGENT_OPTIONS[provider.lower()]

    default_choice = None

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
        logger.info(f"\n[red]未選擇深度思考LLM引擎，退出程式... | No deep thinking llm engine selected. Exiting...[/red]")
        exit(1)

    return choice

def select_llm_provider() -> tuple[str, str]:
    """Select the LLM provider using interactive selection."""
    # 定義 LLM 提供商選項及其對應端點
    BASE_URLS = [
        ("OpenAI", "https://api.openai.com/v1"),
        ("Anthropic", "https://api.anthropic.com/"),
    ]

    choice = questionary.select(
        "選擇您的 LLM 提供商 | Select your LLM Provider:",
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
        logger.info(f"\n[red]未選擇 LLM 提供商，退出程式... | No LLM provider selected. Exiting...[/red]")
        exit(1)

    display_name, url = choice
    logger.info(f"您選擇了 | You selected: {display_name}\tURL: {url}")

    return display_name, url
