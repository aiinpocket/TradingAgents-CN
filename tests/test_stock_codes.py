#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試從通達信獲取股票代碼和名稱
"""

from enhanced_stock_list_fetcher import enhanced_fetch_stock_list

def test_get_stock_codes():
    """
    測試獲取股票代碼和名稱
    """
    print("=" * 60)
    print("📊 測試從通達信獲取股票代碼和名稱")
    print("=" * 60)
    
    try:
        # 獲取股票數據
        print("\n🔄 正在獲取股票數據...")
        stock_data = enhanced_fetch_stock_list(
            type_='stock',  # 只獲取股票
            enable_server_failover=True,  # 啟用故障轉移
            max_retries=3
        )
        
        if stock_data is not None and not stock_data.empty:
            print(f"\n✅ 成功獲取到 {len(stock_data)} 只股票")
            
            # 顯示前20只股票的代碼和名稱
            print("\n📋 前20只股票代碼和名稱:")
            print("-" * 40)
            print(f"{'股票代碼':<10} {'股票名稱':<15} {'市場'}")
            print("-" * 40)
            
            for i, (idx, row) in enumerate(stock_data.head(20).iterrows()):
                market = "深圳" if row['sse'] == 'sz' else "上海"
                print(f"{row['code']:<10} {row['name']:<15} {market}")
            
            # 統計信息
            print("\n📊 統計信息:")
            print("-" * 30)
            sz_count = len(stock_data[stock_data['sse'] == 'sz'])
            sh_count = len(stock_data[stock_data['sse'] == 'sh'])
            print(f"深圳市場股票: {sz_count} 只")
            print(f"上海市場股票: {sh_count} 只")
            print(f"總計股票數量: {len(stock_data)} 只")
            
            # 保存到文件
            output_file = "stock_codes_list.csv"
            stock_codes_df = stock_data[['code', 'name', 'sse']].copy()
            stock_codes_df['market'] = stock_codes_df['sse'].apply(lambda x: '深圳' if x == 'sz' else '上海')
            stock_codes_df = stock_codes_df[['code', 'name', 'market']]
            stock_codes_df.to_csv(output_file, index=False, encoding='utf-8-sig')
            print(f"\n💾 股票代碼列表已保存到: {output_file}")
            
        else:
            print("❌ 未能獲取到股票數據")
            
    except Exception as e:
        print(f"❌ 獲取股票數據時發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_get_stock_codes()