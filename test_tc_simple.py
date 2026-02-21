#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的繁體中文測試 - 不導入tradingagents模組
"""

import os
import sys
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 簡體字檢測函數
def find_simplified_chinese(text):
    """檢測文本中的簡體字"""
    # 擴展的簡體字映射表
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
        '亩': '畝', '价': '價', '优': '優', '传': '傳', '会': '會',
        '债': '債', '伤': '傷', '倾': '傾', '储': '儲', '党': '黨',
        '军': '軍', '写': '寫', '农': '農', '冬': '冬', '况': '況',
        '准': '準', '减': '減', '击': '擊', '几': '幾', '处': '處',
        '凤': '鳳', '凭': '憑', '凯': '凱', '务': '務', '动': '動',
        '励': '勵', '劲': '勁', '劳': '勞', '势': '勢', '协': '協',
        '区': '區', '华': '華', '协': '協', '单': '單', '卖': '賣',
        '南': '南', '卫': '衛', '厂': '廠', '厉': '厲', '压': '壓',
        '厢': '廂', '县': '縣', '参': '參', '戏': '戲', '叹': '嘆',
        '变': '變', '让': '讓', '讯': '訊', '计': '計', '记': '記',
        '认': '認', '队': '隊', '务': '務', '议': '議', '讲': '講',
        '许': '許', '论': '論', '设': '設', '访': '訪', '证': '證',
        '评': '評', '识': '識', '诉': '訴', '词': '詞', '译': '譯',
        '试': '試', '诗': '詩', '话': '話', '询': '詢', '详': '詳',
        '语': '語', '误': '誤', '说': '說', '请': '請', '诸': '諸',
        '读': '讀', '课': '課', '调': '調', '谁': '誰', '谈': '談',
        '谊': '誼', '谋': '謀', '谓': '謂', '谢': '謝', '谣': '謠',
        '谦': '謙', '讲': '講', '诉': '訴', '词': '詞', '译': '譯',
        '试': '試', '诗': '詩', '话': '話', '询': '詢', '详': '詳',
        '语': '語', '误': '誤', '说': '說', '请': '請', '诸': '諸',
        '读': '讀', '课': '課', '调': '調', '谁': '誰', '谈': '談',
    }

    results = []
    for i, char in enumerate(text):
        if char in simplified_to_traditional:
            results.append((char, i, simplified_to_traditional[char]))

    return results

def test_llm_output():
    """測試LLM輸出是否使用繁體中文"""
    print("=" * 60)
    print("測試繁體中文輸出")
    print("=" * 60)

    # 檢查API密鑰
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    print(f"\nAPI密鑰檢查:")
    print(f"  OpenAI: {'✓' if openai_key else '✗'}")
    print(f"  Anthropic: {'✓' if anthropic_key else '✗'}")

    if not (openai_key or anthropic_key):
        print("\n沒有配置任何LLM API密鑰")
        print("跳過LLM測試，只檢查agent文件配置...")
        return check_agent_files()

    # 選擇可用的LLM
    try:
        if openai_key:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.3,
                api_key=openai_key
            )
            provider = "OpenAI (gpt-4o-mini)"
        elif anthropic_key:
            from langchain_anthropic import ChatAnthropic
            llm = ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0.3,
                anthropic_api_key=anthropic_key
            )
            provider = "Anthropic (claude-3-5-sonnet)"

        print(f"\n使用LLM: {provider}")

        # 測試提示詞
        test_prompt = """你是一位專業的股票分析師。

**重要：你必須使用繁體中文回答，絕對不可使用簡體字。所有分析、建議、評估都必須用繁體中文撰寫。**

請對蘋果公司（AAPL）進行一個簡短的技術分析。包括：
1. 公司概況
2. 近期股價表現
3. 投資建議

請用繁體中文回答，不超過250字。"""

        print("\n發送測試提示詞...")
        response = llm.invoke(test_prompt)

        content = response.content if hasattr(response, 'content') else str(response)

        print("\n" + "=" * 60)
        print("LLM回應:")
        print("=" * 60)
        print(content)
        print("=" * 60)

        # 檢查簡體字
        print("\n檢查簡體字...")
        simplified_chars = find_simplified_chinese(content)

        if simplified_chars:
            print(f"\n❌ 發現 {len(simplified_chars)} 個簡體字:")
            unique_chars = {}
            for char, pos, traditional in simplified_chars:
                if char not in unique_chars:
                    unique_chars[char] = traditional

            for char, traditional in sorted(unique_chars.items()):
                count = sum(1 for c, _, _ in simplified_chars if c == char)
                print(f"  '{char}' (應為 '{traditional}') - 出現 {count} 次")

            print("\n位置示例:")
            for char, pos, traditional in simplified_chars[:5]:
                start = max(0, pos - 15)
                end = min(len(content), pos + 15)
                context = content[start:end]
                highlight = context.replace(char, f"【{char}】")
                print(f"  位置 {pos}: ...{highlight}...")

            return False
        else:
            print("\n✅ 未發現簡體字！LLM正確使用繁體中文。")
            return True

    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_agent_files():
    """檢查agent文件是否包含繁體中文要求"""
    print("\n" + "=" * 60)
    print("檢查agent文件配置")
    print("=" * 60)

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
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if required_text in content:
                print(f"  ✓ {os.path.basename(file_path)}")
            else:
                print(f"  ✗ {os.path.basename(file_path)} - 缺少繁體中文要求")
                all_pass = False
        else:
            print(f"  ? {os.path.basename(file_path)} - 文件不存在")
            all_pass = False

    return all_pass

if __name__ == "__main__":
    print("\n🔍 開始繁體中文檢查\n")

    # 先檢查文件配置
    config_ok = check_agent_files()

    # 再測試LLM輸出
    llm_ok = test_llm_output()

    print("\n" + "=" * 60)
    if config_ok and llm_ok:
        print("✅ 所有測試通過！")
        sys.exit(0)
    elif config_ok:
        print("⚠️ 文件配置正確，但LLM測試失敗或未執行")
        sys.exit(1)
    else:
        print("❌ 測試失敗")
        sys.exit(1)
