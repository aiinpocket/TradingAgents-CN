#!/usr/bin/env python3
"""
創建示例分析報告
用於測試Web界面的報告顯示功能
"""

import sys
import os
from datetime import datetime

# 添加項目路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'web'))

def create_sample_report(stock_symbol: str, stock_name: str):
    """創建示例分析報告"""
    
    # 分析結果數據
    analysis_results = {
        "summary": f"{stock_name}({stock_symbol}) 综合分析顯示该股票具有良好的投資潜力，建议關註。",
        "analysts": ["market_analyst", "fundamentals_analyst", "trader_agent"]
    }
    
    # 報告內容
    reports = {
        "final_trade_decision": f"""# {stock_name}({stock_symbol}) 最终交易決策

## 📊 投資建议
**行動**: 买入
**置信度**: 85%
**風險評分**: 25%
**目標價格**: 當前價格上涨15-20%

## 🎯 關键要點
- 技術面顯示上涨趋势
- 基本面財務狀况良好
- 市場情绪積極
- 風險可控

## 💡 分析推理
基於多維度分析，该股票在技術面、基本面和市場情绪方面都表現良好。技術指標顯示突破關键阻力位，成交量放大確認上涨趋势。基本面分析顯示公司財務穩健，盈利能力强。综合評估建议买入並持有。

## ⚠️ 風險提示
- 市場整體波動風險
- 行業政策變化風險
- 建议設置止損位
""",

        "fundamentals_report": f"""# {stock_name}({stock_symbol}) 基本面分析報告

## 📈 財務指標分析
### 盈利能力
- **净利润增長率**: 15.2% (同比)
- **ROE**: 18.5%
- **ROA**: 12.3%
- **毛利率**: 35.8%

### 偿债能力
- **資產负债率**: 45.2%
- **流動比率**: 2.1
- **速動比率**: 1.8
- **利息保障倍數**: 8.5

### 運營能力
- **总資產周轉率**: 1.2
- **存貨周轉率**: 6.8
- **應收账款周轉率**: 9.2

## 🏢 公司基本情况
- **行業地位**: 行業龙头企業
- **主營業務**: 穩定增長
- **市場份額**: 持续擴大
- **競爭優势**: 技術領先，品牌知名度高

## 📊 估值分析
- **PE**: 15.2倍 (合理估值区間)
- **PB**: 2.1倍
- **PEG**: 0.8 (低於1，具有投資價值)

## 💰 投資亮點
1. 財務狀况穩健，盈利能力强
2. 行業地位穩固，競爭優势明顯
3. 估值合理，具有投資價值
4. 分红政策穩定，股东回報良好
""",

        "market_report": f"""# {stock_name}({stock_symbol}) 技術面分析報告

## 📈 價格趋势分析
### 短期趋势 (5-20日)
- **趋势方向**: 上涨
- **支撑位**: ¥45.20
- **阻力位**: ¥52.80
- **當前位置**: 突破前期高點

### 中期趋势 (20-60日)
- **趋势方向**: 上涨
- **主要支撑**: ¥42.50
- **目標位**: ¥55.00
- **趋势强度**: 强

## 📊 技術指標分析
### 趋势指標
- **MA5**: 48.50 (價格在均線上方)
- **MA20**: 46.80 (多头排列)
- **MA60**: 44.20 (長期上涨趋势)

### 動量指標
- **RSI(14)**: 68.5 (偏强，未超买)
- **MACD**: 金叉向上
- **KDJ**: K=75, D=68, J=82 (强势区域)

### 成交量分析
- **成交量**: 放量上涨
- **量價關系**: 價涨量增，健康上涨
- **換手率**: 3.2% (活躍)

## 🎯 操作建议
### 买入信號
- 突破前期高點
- 成交量配合
- 技術指標向好

### 關键位置
- **买入位**: ¥48.00-49.00
- **止損位**: ¥45.00
- **目標位**: ¥55.00

## ⚠️ 風險提示
- 註意大盘整體走势
- 關註成交量變化
- 設置合理止損位
"""
    }
    
    return analysis_results, reports

def main():
    """主函數"""
    print("🎨 創建示例分析報告...")
    
    try:
        from web.utils.mongodb_report_manager import mongodb_report_manager
        
        if not mongodb_report_manager.connected:
            print("❌ MongoDB未連接")
            return
        
        # 創建多個示例報告
        sample_stocks = [
            ("DEMO001", "示例科技股"),
            ("DEMO002", "示例銀行股"),
            ("DEMO003", "示例消費股"),
            ("000001", "平安銀行"),
            ("000002", "万科A")
        ]
        
        success_count = 0
        
        for stock_symbol, stock_name in sample_stocks:
            print(f"📝 創建 {stock_name}({stock_symbol}) 的分析報告...")
            
            analysis_results, reports = create_sample_report(stock_symbol, stock_name)
            
            success = mongodb_report_manager.save_analysis_report(
                stock_symbol=stock_symbol,
                analysis_results=analysis_results,
                reports=reports
            )
            
            if success:
                success_count += 1
                print(f"✅ {stock_name} 報告創建成功")
            else:
                print(f"❌ {stock_name} 報告創建失败")
        
        print(f"\n🎉 完成！成功創建 {success_count}/{len(sample_stocks)} 個示例報告")
        print("💡 現在可以在Web界面中查看這些報告了")
        
    except Exception as e:
        print(f"❌ 創建示例報告失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
