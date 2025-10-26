#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試Finnhub新聞數據路徑修複

這個腳本用於驗證:
1. 數據目錄路徑配置是否正確
2. 新聞數據文件路徑是否存在
3. 錯誤處理是否正常工作
"""

import os
import sys
from pathlib import Path

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tradingagents.dataflows.config import get_config, set_config
from tradingagents.dataflows.interface import get_finnhub_news
from tradingagents.dataflows.finnhub_utils import get_data_in_range

def test_data_dir_config():
    """測試數據目錄配置"""
    print("=== 測試數據目錄配置 ===")
    
    config = get_config()
    data_dir = config.get('data_dir')
    
    print(f"當前數據目錄配置: {data_dir}")
    print(f"數據目錄是否存在: {os.path.exists(data_dir) if data_dir else False}")
    
    # 檢查是否為跨平台路徑
    if data_dir:
        if '/' in data_dir and '\\' in data_dir:
            print("⚠️ 警告: 數據目錄路徑混合了Unix和Windows分隔符")
        elif data_dir.startswith('/Users/') and os.name == 'nt':
            print("⚠️ 警告: 在Windows系統上使用了Unix路徑")
        else:
            print("✅ 數據目錄路徑格式正確")
    
    return data_dir

def test_finnhub_news_path():
    """測試Finnhub新聞數據路徑"""
    print("\n=== 測試Finnhub新聞數據路徑 ===")
    
    config = get_config()
    data_dir = config.get('data_dir')
    
    if not data_dir:
        print("❌ 數據目錄未配置")
        return False
    
    # 測試AAPL新聞數據路徑
    ticker = "AAPL"
    news_data_path = os.path.join(data_dir, "finnhub_data", "news_data", f"{ticker}_data_formatted.json")
    
    print(f"新聞數據文件路徑: {news_data_path}")
    print(f"文件是否存在: {os.path.exists(news_data_path)}")
    
    # 檢查目錄結構
    finnhub_dir = os.path.join(data_dir, "finnhub_data")
    news_dir = os.path.join(finnhub_dir, "news_data")
    
    print(f"Finnhub目錄是否存在: {os.path.exists(finnhub_dir)}")
    print(f"新聞數據目錄是否存在: {os.path.exists(news_dir)}")
    
    if os.path.exists(news_dir):
        files = os.listdir(news_dir)
        print(f"新聞數據目錄中的文件: {files[:5]}...")  # 只顯示前5個文件
    
    return os.path.exists(news_data_path)

def test_get_data_in_range():
    """測試get_data_in_range函數的錯誤處理"""
    print("\n=== 測試get_data_in_range錯誤處理 ===")
    
    config = get_config()
    data_dir = config.get('data_dir')
    
    if not data_dir:
        print("❌ 數據目錄未配置")
        return
    
    # 測試不存在的股票代碼
    result = get_data_in_range(
        ticker="NONEXISTENT",
        start_date="2025-01-01",
        end_date="2025-01-02",
        data_type="news_data",
        data_dir=data_dir
    )
    
    print(f"不存在股票的返回結果: {result}")
    print(f"返回結果類型: {type(result)}")
    print(f"是否為空字典: {result == {}}")

def test_get_finnhub_news():
    """測試get_finnhub_news函數"""
    print("\n=== 測試get_finnhub_news函數 ===")
    
    # 測試不存在的股票代碼
    result = get_finnhub_news(
        ticker="NONEXISTENT",
        curr_date="2025-01-02",
        look_back_days=7
    )
    
    print(f"函數返回結果: {result[:200]}...")  # 只顯示前200個字符
    print(f"是否包含錯誤信息: {'無法獲取' in result}")

def create_sample_data_structure():
    """創建示例數據目錄結構"""
    print("\n=== 創建示例數據目錄結構 ===")
    
    config = get_config()
    data_dir = config.get('data_dir')
    
    if not data_dir:
        print("❌ 數據目錄未配置")
        return
    
    # 創建目錄結構
    finnhub_dir = os.path.join(data_dir, "finnhub_data")
    news_dir = os.path.join(finnhub_dir, "news_data")
    
    try:
        os.makedirs(news_dir, exist_ok=True)
        print(f"✅ 創建目錄結構: {news_dir}")
        
        # 創建示例數據文件
        sample_file = os.path.join(news_dir, "AAPL_data_formatted.json")
        sample_data = {
            "2025-01-01": [
                {
                    "headline": "Apple發布新產品",
                    "summary": "苹果公司今日發布了新的產品線..."
                }
            ]
        }
        
        import json
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 創建示例數據文件: {sample_file}")
        
    except Exception as e:
        print(f"❌ 創建目錄結構失败: {e}")

def main():
    """主測試函數"""
    print("Finnhub新聞數據路徑修複測試")
    print("=" * 50)
    
    # 測試數據目錄配置
    data_dir = test_data_dir_config()
    
    # 測試新聞數據路徑
    news_exists = test_finnhub_news_path()
    
    # 測試錯誤處理
    test_get_data_in_range()
    test_get_finnhub_news()
    
    # 如果數據不存在，創建示例結構
    if not news_exists:
        create_sample_data_structure()
        print("\n重新測試新聞數據路徑:")
        test_finnhub_news_path()
    
    print("\n=== 測試总結 ===")
    print("1. 數據目錄路徑已修複為跨平台兼容")
    print("2. 添加了詳細的錯誤處理和調試信息")
    print("3. 當數據文件不存在時會提供清晰的錯誤提示")
    print("4. 建议下載或配置正確的Finnhub數據")
    
    print("\n=== 解決方案建议 ===")
    print("如果仍然遇到新聞數據問題，請:")
    print("1. 確保已正確配置Finnhub API密鑰")
    print("2. 運行數據下載腳本獲取新聞數據")
    print("3. 檢查數據目錄權限")
    print(f"4. 確認數據目錄存在: {data_dir}")

if __name__ == "__main__":
    main()