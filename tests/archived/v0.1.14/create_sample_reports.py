#!/usr/bin/env python3
"""
建立示例分析報告
用於測試Web介面的報告顯示功能
"""

import sys
import os
from datetime import datetime

# 新增項目路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

def create_sample_report(stock_symbol: str, stock_name: str):
    """建立示例分析報告"""
    
    # 分析結果資料
    analysis_results = {
        "summary": f"{stock_name}({stock_symbol}) 綜合分析顯示該股票具有良好的投資潛力，建議關注。",
        "analysts": ["market_analyst", "fundamentals_analyst", "trader_agent"]
    }
    
    # 報告內容
    reports = {
        "final_trade_decision": f"""# {stock_name}({stock_symbol}) 最終交易決策

##  投資建議
**行動**: 買入
**置信度**: 85%
**風險評分**: 25%
**目標價格**: 當前價格上漲15-20%

##  關鍵要點
- 技術面顯示上漲趨勢
- 基本面財務狀況良好
- 市場情緒積極
- 風險可控

##  分析推理
基於多維度分析，該股票在技術面、基本面和市場情緒方面都表現良好。技術指標顯示突破關鍵阻力位，成交量放大確認上漲趨勢。基本面分析顯示公司財務穩健，盈利能力強。綜合評估建議買入並持有。

##  風險提示
- 市場整體波動風險
- 行業政策變化風險
- 建議設定止損位
""",

        "fundamentals_report": f"""# {stock_name}({stock_symbol}) 基本面分析報告

##  財務指標分析
### 盈利能力
- **淨利潤增長率**: 15.2% (同比)
- **ROE**: 18.5%
- **ROA**: 12.3%
- **毛利率**: 35.8%

### 償債能力
- **資產負債率**: 45.2%
- **流動比率**: 2.1
- **速動比率**: 1.8
- **利息保障倍數**: 8.5

### 運營能力
- **總資產周轉率**: 1.2
- **存貨周轉率**: 6.8
- **應收帳款周轉率**: 9.2

##  公司基本情況
- **行業地位**: 行業龍頭企業
- **主營業務**: 穩定增長
- **市場份額**: 持續擴大
- **競爭優勢**: 技術領先，品牌知名度高

##  估值分析
- **PE**: 15.2倍 (合理估值區間)
- **PB**: 2.1倍
- **PEG**: 0.8 (低於1，具有投資價值)

##  投資亮點
1. 財務狀況穩健，盈利能力強
2. 行業地位穩固，競爭優勢明顯
3. 估值合理，具有投資價值
4. 分紅政策穩定，股東回報良好
""",

        "market_report": f"""# {stock_name}({stock_symbol}) 技術面分析報告

##  價格趨勢分析
### 短期趨勢 (5-20日)
- **趨勢方向**: 上漲
- **支撐位**: ¥45.20
- **阻力位**: ¥52.80
- **當前位置**: 突破前期高點

### 中期趨勢 (20-60日)
- **趨勢方向**: 上漲
- **主要支撐**: ¥42.50
- **目標位**: ¥55.00
- **趨勢強度**: 強

##  技術指標分析
### 趨勢指標
- **MA5**: 48.50 (價格在均線上方)
- **MA20**: 46.80 (多頭排列)
- **MA60**: 44.20 (長期上漲趨勢)

### 動量指標
- **RSI(14)**: 68.5 (偏強，未超買)
- **MACD**: 金叉向上
- **KDJ**: K=75, D=68, J=82 (強勢區域)

### 成交量分析
- **成交量**: 放量上漲
- **量價關系**: 價漲量增，健康上漲
- **換手率**: 3.2% (活躍)

##  操作建議
### 買入訊號
- 突破前期高點
- 成交量配合
- 技術指標向好

### 關鍵位置
- **買入位**: ¥48.00-49.00
- **止損位**: ¥45.00
- **目標位**: ¥55.00

##  風險提示
- 注意大盤整體走勢
- 關注成交量變化
- 設定合理止損位
"""
    }
    
    return analysis_results, reports

def main():
    """主函式"""
    print(" 建立示例分析報告...")
    
    try:
        from web.utils.mongodb_report_manager import mongodb_report_manager
        
        if not mongodb_report_manager.connected:
            print(" MongoDB未連接")
            return
        
        # 建立多個示例報告
        sample_stocks = [
            ("DEMO001", "示例科技股"),
            ("DEMO002", "示例銀行股"),
            ("DEMO003", "示例消費股"),
            ("AAPL", "Apple Inc."),
            ("MSFT", "Microsoft Corp.")
        ]
        
        success_count = 0
        
        for stock_symbol, stock_name in sample_stocks:
            print(f" 建立 {stock_name}({stock_symbol}) 的分析報告...")
            
            analysis_results, reports = create_sample_report(stock_symbol, stock_name)
            
            success = mongodb_report_manager.save_analysis_report(
                stock_symbol=stock_symbol,
                analysis_results=analysis_results,
                reports=reports
            )
            
            if success:
                success_count += 1
                print(f" {stock_name} 報告建立成功")
            else:
                print(f" {stock_name} 報告建立失敗")
        
        print(f"\n 完成！成功建立 {success_count}/{len(sample_stocks)} 個示例報告")
        print(" 現在可以在Web介面中查看這些報告了")
        
    except Exception as e:
        print(f" 建立示例報告失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
