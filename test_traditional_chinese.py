#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試繁體中文輸出
產生一個簡單的股票分析報告並檢查簡體字
"""

import os
import sys
import re
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 確保項目目錄在Python路徑中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 簡體字檢測函數
def find_simplified_chinese(text):
    """
    檢測文本中的簡體字
    返回: [(簡體字, 位置), ...]
    """
    # 常見簡體字對應繁體字的映射
    simplified_to_traditional = {
        '数': '數', '据': '據', '营': '營', '业': '業', '币': '幣',
        '为': '為', '时': '時', '间': '間', '应': '應', '该': '該',
        '领': '領', '导': '導', '过': '過', '对': '對', '说': '說',
        '软': '軟', '硬': '硬', '历': '歷', '压': '壓', '态': '態',
        '岁': '歲', '规': '規', '则': '則', '选': '選', '择': '擇',
        '义': '義', '尽': '盡', '丽': '麗', '么': '麼', '广': '廣',
        '产': '產', '从': '從', '两': '兩', '严': '嚴', '丧': '喪',
        '个': '個', '临': '臨', '为': '為', '举': '舉', '乐': '樂',
        '习': '習', '书': '書', '买': '買', '乱': '亂', '争': '爭',
        '于': '於', '亏': '虧', '云': '雲', '亚': '亞', '产': '產',
        '亩': '畝', '享': '享', '亮': '亮', '亲': '親', '億': '億',
        '仅': '僅', '从': '從', '仑': '崙', '仓': '倉', '仪': '儀',
        '们': '們', '价': '價', '众': '眾', '优': '優', '伙': '夥',
        '会': '會', '伟': '偉', '传': '傳', '伤': '傷', '伦': '倫',
        '伪': '偽', '伫': '佇', '体': '體', '余': '餘', '佣': '傭',
        '佥': '僉', '侠': '俠', '侣': '侶', '侥': '僥', '侦': '偵',
        '侧': '側', '侨': '僑', '侩': '儈', '侪': '儕', '侬': '儂',
        '俣': '俁', '俦': '儔', '俨': '儼', '俩': '倆', '俪': '儷',
        '俭': '儉', '债': '債', '倾': '傾', '偬': '傯', '偻': '僂',
        '偾': '僨', '偿': '償', '傥': '儻', '傧': '儐', '储': '儲',
        '催': '催', '傻': '傻', '像': '像', '僵': '僵', '僻': '僻',
    }

    results = []
    for i, char in enumerate(text):
        if char in simplified_to_traditional:
            results.append((char, i, simplified_to_traditional[char]))

    return results

def test_simple_analysis():
    """
    執行簡單的測試分析
    """
    print("=" * 60)
    print("開始測試繁體中文輸出")
    print("=" * 60)

    try:
        # 測試配置
        from tradingagents.config.config_manager import ConfigManager
        config_manager = ConfigManager()

        # 檢查API密鑰
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        print(f"\n檢查API密鑰配置:")
        print(f"  OpenAI: {'✓ 已配置' if openai_key else '✗ 未配置'}")
        print(f"  Google: {'✓ 已配置' if google_key else '✗ 未配置'}")
        print(f"  Anthropic: {'✓ 已配置' if anthropic_key else '✗ 未配置'}")

        if not (openai_key or google_key or anthropic_key):
            print("\n⚠️ 警告：沒有配置任何LLM API密鑰，無法執行完整測試")
            print("將進行系統提示詞檢查...")
            return test_prompts_only()

        # 執行簡單的LLM測試
        print("\n正在執行簡單的LLM測試...")

        # 使用可用的LLM
        if openai_key:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                api_key=openai_key
            )
            provider = "OpenAI"
        elif google_key:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-exp",
                temperature=0.3,
                google_api_key=google_key
            )
            provider = "Google"
        elif anthropic_key:
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.3,
                anthropic_api_key=anthropic_key
            )
            provider = "Anthropic"

        print(f"使用LLM提供商: {provider}")

        # 測試提示詞
        test_prompt = """你是一位專業的股票分析師。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**

請對台積電（股票代碼：2330）進行一個簡短的技術分析。包括：
1. 公司概況
2. 技術指標分析
3. 投資建議

請用繁體中文回答，不超過300字。"""

        print("\n發送測試提示詞到LLM...")
        response = llm.invoke(test_prompt)

        # 獲取回應內容
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)

        print("\n" + "=" * 60)
        print("LLM回應內容:")
        print("=" * 60)
        print(content)
        print("=" * 60)

        # 檢查簡體字
        print("\n檢查簡體字...")
        simplified_chars = find_simplified_chinese(content)

        if simplified_chars:
            print(f"\n❌ 發現 {len(simplified_chars)} 個簡體字:")
            for char, pos, traditional in simplified_chars[:20]:  # 只顯示前20個
                # 顯示簡體字及其上下文
                start = max(0, pos - 10)
                end = min(len(content), pos + 10)
                context = content[start:end]
                print(f"  位置 {pos}: '{char}' → 應為 '{traditional}'")
                print(f"    上下文: ...{context}...")

            if len(simplified_chars) > 20:
                print(f"  ... 還有 {len(simplified_chars) - 20} 個簡體字")
        else:
            print("\n✓ 未發現簡體字，LLM正確使用繁體中文！")

        return len(simplified_chars) == 0

    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_prompts_only():
    """
    只測試系統提示詞中是否包含繁體中文要求
    """
    print("\n檢查系統提示詞配置...")

    # 檢查所有agent文件
    agent_files = [
        "tradingagents/agents/analysts/market_analyst.py",
        "tradingagents/agents/analysts/fundamentals_analyst.py",
        "tradingagents/agents/analysts/news_analyst.py",
        "tradingagents/agents/analysts/social_media_analyst.py",
        "tradingagents/agents/researchers/bull_researcher.py",
        "tradingagents/agents/researchers/bear_researcher.py",
        "tradingagents/agents/trader/trader.py",
        "tradingagents/agents/risk_mgmt/aggresive_debator.py",
        "tradingagents/agents/risk_mgmt/conservative_debator.py",
        "tradingagents/agents/risk_mgmt/neutral_debator.py",
        "tradingagents/agents/managers/research_manager.py",
        "tradingagents/agents/managers/risk_manager.py",
    ]

    required_text = "**重要：你必須使用繁體中文回答，絕對不可使用簡體字"

    all_pass = True
    for file_path in agent_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if required_text in content:
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ {file_path} - 缺少繁體中文要求")
                all_pass = False
        else:
            print(f"  ? {file_path} - 文件不存在")
            all_pass = False

    return all_pass

if __name__ == "__main__":
    success = test_simple_analysis()

    if success:
        print("\n" + "=" * 60)
        print("✓ 所有測試通過！")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ 測試失敗，請檢查上述問題")
        print("=" * 60)
        sys.exit(1)
