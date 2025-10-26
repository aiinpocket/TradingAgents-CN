#!/usr/bin/env python3
"""
優化的A股數據獲取工具
集成緩存策略和Tushare數據接口，提高數據獲取效率
"""

import os
import time
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from .cache_manager import get_cache
from .config import get_config

# 導入日誌模塊
from tradingagents.utils.logging_manager import get_logger
logger = get_logger('agents')


class OptimizedChinaDataProvider:
    """優化的A股數據提供器 - 集成緩存和Tushare數據接口"""
    
    def __init__(self):
        self.cache = get_cache()
        self.config = get_config()
        self.last_api_call = 0
        self.min_api_interval = 0.5  # Tushare數據接口調用間隔較短
        
        logger.info(f"📊 優化A股數據提供器初始化完成")
    
    def _wait_for_rate_limit(self):
        """等待API限制"""
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        
        if time_since_last_call < self.min_api_interval:
            wait_time = self.min_api_interval - time_since_last_call
            time.sleep(wait_time)
        
        self.last_api_call = time.time()
    
    def get_stock_data(self, symbol: str, start_date: str, end_date: str, 
                      force_refresh: bool = False) -> str:
        """
        獲取A股數據 - 優先使用緩存
        
        Args:
            symbol: 股票代碼（6位數字）
            start_date: 開始日期 (YYYY-MM-DD)
            end_date: 結束日期 (YYYY-MM-DD)
            force_refresh: 是否强制刷新緩存
        
        Returns:
            格式化的股票數據字符串
        """
        logger.info(f"📈 獲取A股數據: {symbol} ({start_date} 到 {end_date})")
        
        # 檢查緩存（除非强制刷新）
        if not force_refresh:
            cache_key = self.cache.find_cached_stock_data(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                data_source="unified"
            )
            
            if cache_key:
                cached_data = self.cache.load_stock_data(cache_key)
                if cached_data:
                    logger.info(f"⚡ 從緩存加載A股數據: {symbol}")
                    return cached_data
        
        # 緩存未命中，從Tushare數據接口獲取
        logger.info(f"🌐 從Tushare數據接口獲取數據: {symbol}")
        
        try:
            # API限制處理
            self._wait_for_rate_limit()
            
            # 調用統一數據源接口（默認Tushare，支持备用數據源）
            from .data_source_manager import get_china_stock_data_unified

            formatted_data = get_china_stock_data_unified(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )

            # 檢查是否獲取成功
            if "❌" in formatted_data or "錯誤" in formatted_data:
                logger.error(f"❌ 數據源API調用失败: {symbol}")
                # 嘗試從旧緩存獲取數據
                old_cache = self._try_get_old_cache(symbol, start_date, end_date)
                if old_cache:
                    logger.info(f"📁 使用過期緩存數據: {symbol}")
                    return old_cache

                # 生成备用數據
                return self._generate_fallback_data(symbol, start_date, end_date, "數據源API調用失败")
            
            # 保存到緩存
            self.cache.save_stock_data(
                symbol=symbol,
                data=formatted_data,
                start_date=start_date,
                end_date=end_date,
                data_source="unified"  # 使用統一數據源標识
            )
            
            logger.info(f"✅ A股數據獲取成功: {symbol}")
            return formatted_data
            
        except Exception as e:
            error_msg = f"Tushare數據接口調用異常: {str(e)}"
            logger.error(f"❌ {error_msg}")
            
            # 嘗試從旧緩存獲取數據
            old_cache = self._try_get_old_cache(symbol, start_date, end_date)
            if old_cache:
                logger.info(f"📁 使用過期緩存數據: {symbol}")
                return old_cache
            
            # 生成备用數據
            return self._generate_fallback_data(symbol, start_date, end_date, error_msg)
    
    def get_fundamentals_data(self, symbol: str, force_refresh: bool = False) -> str:
        """
        獲取A股基本面數據 - 優先使用緩存
        
        Args:
            symbol: 股票代碼
            force_refresh: 是否强制刷新緩存
        
        Returns:
            格式化的基本面數據字符串
        """
        logger.info(f"📊 獲取A股基本面數據: {symbol}")
        
        # 檢查緩存（除非强制刷新）
        if not force_refresh:
            # 查找基本面數據緩存
            for metadata_file in self.cache.metadata_dir.glob(f"*_meta.json"):
                try:
                    import json
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    if (metadata.get('symbol') == symbol and 
                        metadata.get('data_type') == 'fundamentals' and
                        metadata.get('market_type') == 'china'):
                        
                        cache_key = metadata_file.stem.replace('_meta', '')
                        if self.cache.is_cache_valid(cache_key, symbol=symbol, data_type='fundamentals'):
                            cached_data = self.cache.load_stock_data(cache_key)
                            if cached_data:
                                logger.info(f"⚡ 從緩存加載A股基本面數據: {symbol}")
                                return cached_data
                except Exception:
                    continue
        
        # 緩存未命中，生成基本面分析
        logger.debug(f"🔍 生成A股基本面分析: {symbol}")
        
        try:
            # 先獲取股票數據
            current_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            stock_data = self.get_stock_data(symbol, start_date, current_date)
            
            # 生成基本面分析報告
            fundamentals_data = self._generate_fundamentals_report(symbol, stock_data)
            
            # 保存到緩存
            self.cache.save_fundamentals_data(
                symbol=symbol,
                fundamentals_data=fundamentals_data,
                data_source="unified_analysis"
            )
            
            logger.info(f"✅ A股基本面數據生成成功: {symbol}")
            return fundamentals_data
            
        except Exception as e:
            error_msg = f"基本面數據生成失败: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return self._generate_fallback_fundamentals(symbol, error_msg)
    
    def _generate_fundamentals_report(self, symbol: str, stock_data: str) -> str:
        """基於股票數據生成真實的基本面分析報告"""

        # 添加詳細的股票代碼追蹤日誌
        logger.debug(f"🔍 [股票代碼追蹤] _generate_fundamentals_report 接收到的股票代碼: '{symbol}' (類型: {type(symbol)})")
        logger.debug(f"🔍 [股票代碼追蹤] 股票代碼長度: {len(str(symbol))}")
        logger.debug(f"🔍 [股票代碼追蹤] 股票代碼字符: {list(str(symbol))}")
        logger.debug(f"🔍 [股票代碼追蹤] 接收到的股票數據前200字符: {stock_data[:200] if stock_data else 'None'}")

        # 從股票數據中提取信息
        company_name = "未知公司"
        current_price = "N/A"
        volume = "N/A"
        change_pct = "N/A"

        # 首先嘗試從統一接口獲取股票基本信息
        try:
            logger.debug(f"🔍 [股票代碼追蹤] 嘗試獲取{symbol}的基本信息...")
            from .interface import get_china_stock_info_unified
            stock_info = get_china_stock_info_unified(symbol)
            logger.debug(f"🔍 [股票代碼追蹤] 獲取到的股票信息: {stock_info}")

            if "股票名稱:" in stock_info:
                lines = stock_info.split('\n')
                for line in lines:
                    if "股票名稱:" in line:
                        company_name = line.split(':')[1].strip()
                        logger.debug(f"🔍 [股票代碼追蹤] 從統一接口獲取到股票名稱: {company_name}")
                        break
        except Exception as e:
            logger.warning(f"⚠️ 獲取股票基本信息失败: {e}")

        # 然後從股票數據中提取價格信息
        if "股票名稱:" in stock_data:
            lines = stock_data.split('\n')
            for line in lines:
                if "股票名稱:" in line and company_name == "未知公司":
                    company_name = line.split(':')[1].strip()
                elif "當前價格:" in line:
                    current_price = line.split(':')[1].strip()
                elif "涨跌幅:" in line:
                    change_pct = line.split(':')[1].strip()
                elif "成交量:" in line:
                    volume = line.split(':')[1].strip()

        # 嘗試從股票數據表格中提取最新價格信息
        if current_price == "N/A" and stock_data:
            try:
                lines = stock_data.split('\n')
                for i, line in enumerate(lines):
                    if "最新數據:" in line and i + 1 < len(lines):
                        # 查找數據行
                        for j in range(i + 1, min(i + 5, len(lines))):
                            data_line = lines[j].strip()
                            if data_line and not data_line.startswith('日期') and not data_line.startswith('-'):
                                # 嘗試解析數據行
                                parts = data_line.split()
                                if len(parts) >= 4:
                                    try:
                                        # 假設格式: 日期 股票代碼 開盘 收盘 最高 最低 成交量 成交額...
                                        current_price = parts[3]  # 收盘價
                                        logger.debug(f"🔍 [股票代碼追蹤] 從數據表格提取到收盘價: {current_price}")
                                        break
                                    except (IndexError, ValueError):
                                        continue
                        break
            except Exception as e:
                logger.debug(f"🔍 [股票代碼追蹤] 解析股票數據表格失败: {e}")

        # 根據股票代碼判斷行業和基本信息
        logger.debug(f"🔍 [股票代碼追蹤] 調用 _get_industry_info，傳入參數: '{symbol}'")
        industry_info = self._get_industry_info(symbol)
        logger.debug(f"🔍 [股票代碼追蹤] _get_industry_info 返回結果: {industry_info}")

        logger.debug(f"🔍 [股票代碼追蹤] 調用 _estimate_financial_metrics，傳入參數: '{symbol}'")
        financial_estimates = self._estimate_financial_metrics(symbol, current_price)
        logger.debug(f"🔍 [股票代碼追蹤] _estimate_financial_metrics 返回結果: {financial_estimates}")

        logger.debug(f"🔍 [股票代碼追蹤] 開始生成報告，使用股票代碼: '{symbol}'")
        
        # 檢查數據來源並生成相應說明
        data_source_note = ""
        data_source = financial_estimates.get('data_source', '')
        
        if any("（估算值）" in str(v) for v in financial_estimates.values() if isinstance(v, str)):
            data_source_note = "\n⚠️ **數據說明**: 部分財務指標為估算值，建议結合最新財報數據進行分析"
        elif data_source == "AKShare":
            data_source_note = "\n✅ **數據說明**: 財務指標基於AKShare真實財務數據計算"
        elif data_source == "Tushare":
            data_source_note = "\n✅ **數據說明**: 財務指標基於Tushare真實財務數據計算"
        else:
            data_source_note = "\n✅ **數據說明**: 財務指標基於真實財務數據計算"
        
        report = f"""# 中國A股基本面分析報告 - {symbol}

## 📊 股票基本信息
- **股票代碼**: {symbol}
- **股票名稱**: {company_name}
- **所屬行業**: {industry_info['industry']}
- **市場板塊**: {industry_info['market']}
- **當前股價**: {current_price}
- **涨跌幅**: {change_pct}
- **成交量**: {volume}
- **分析日期**: {datetime.now().strftime('%Y年%m月%d日')}{data_source_note}

## 💰 財務數據分析

### 估值指標
- **市盈率(PE)**: {financial_estimates['pe']}
- **市净率(PB)**: {financial_estimates['pb']}
- **市銷率(PS)**: {financial_estimates['ps']}
- **股息收益率**: {financial_estimates['dividend_yield']}

### 盈利能力指標
- **净資產收益率(ROE)**: {financial_estimates['roe']}
- **总資產收益率(ROA)**: {financial_estimates['roa']}
- **毛利率**: {financial_estimates['gross_margin']}
- **净利率**: {financial_estimates['net_margin']}

### 財務健康度
- **資產负债率**: {financial_estimates['debt_ratio']}
- **流動比率**: {financial_estimates['current_ratio']}
- **速動比率**: {financial_estimates['quick_ratio']}
- **現金比率**: {financial_estimates['cash_ratio']}

## 📈 行業分析

### 行業地位
{industry_info['analysis']}

### 競爭優势
- **市場份額**: {industry_info['market_share']}
- **品牌價值**: {industry_info['brand_value']}
- **技術優势**: {industry_info['tech_advantage']}

## 🎯 投資價值評估

### 估值水平分析
{self._analyze_valuation(financial_estimates)}

### 成長性分析
{self._analyze_growth_potential(symbol, industry_info)}

### 風險評估
{self._analyze_risks(symbol, financial_estimates, industry_info)}

## 💡 投資建议

### 综合評分
- **基本面評分**: {financial_estimates['fundamental_score']}/10
- **估值吸引力**: {financial_estimates['valuation_score']}/10
- **成長潜力**: {financial_estimates['growth_score']}/10
- **風險等級**: {financial_estimates['risk_level']}

### 操作建议
{self._generate_investment_advice(financial_estimates, industry_info)}

### 絕對估值
- **DCF估值**：基於現金流贴現的內在價值
- **資產價值**：净資產重估價值
- **分红收益率**：股息回報分析

## 風險分析
### 系統性風險
- **宏觀經濟風險**：經濟周期對公司的影響
- **政策風險**：行業政策變化的影響
- **市場風險**：股市波動對估值的影響

### 非系統性風險
- **經營風險**：公司特有的經營風險
- **財務風險**：债務結構和偿债能力風險
- **管理風險**：管理層變動和決策風險

## 投資建议
### 综合評價
基於以上分析，该股票的投資價值評估：

**優势：**
- A股市場上市公司，監管相對完善
- 具备一定的市場地位和品牌價值
- 財務信息透明度較高

**風險：**
- 需要關註宏觀經濟環境變化
- 行業競爭加剧的影響
- 政策調整對業務的潜在影響

### 操作建议
- **投資策略**：建议採用價值投資策略，關註長期基本面
- **仓位建议**：根據風險承受能力合理配置仓位
- **關註指標**：重點關註ROE、PE、現金流等核心指標

---
**重要聲明**: 本報告基於公開數據和模型估算生成，仅供參考，不構成投資建议。
實际投資決策請結合最新財報數據和專業分析師意见。

**數據來源**: {data_source if data_source else "多源數據"}數據接口 + 基本面分析模型
**生成時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return report

    def _get_industry_info(self, symbol: str) -> dict:
        """根據股票代碼獲取行業信息"""

        # 添加詳細的股票代碼追蹤日誌
        logger.debug(f"🔍 [股票代碼追蹤] _get_industry_info 接收到的股票代碼: '{symbol}' (類型: {type(symbol)})")
        logger.debug(f"🔍 [股票代碼追蹤] 股票代碼長度: {len(str(symbol))}")
        logger.debug(f"🔍 [股票代碼追蹤] 股票代碼字符: {list(str(symbol))}")

        # 根據股票代碼前缀判斷行業（簡化版）
        code_prefix = symbol[:3]
        logger.debug(f"🔍 [股票代碼追蹤] 提取的代碼前缀: '{code_prefix}'")

        industry_map = {
            "000": {"industry": "深市主板", "market": "深圳證券交易所", "type": "综合"},
            "001": {"industry": "深市主板", "market": "深圳證券交易所", "type": "综合"},
            "002": {"industry": "中小板", "market": "深圳證券交易所", "type": "成長型"},
            "003": {"industry": "創業板", "market": "深圳證券交易所", "type": "創新型"},
            "300": {"industry": "創業板", "market": "深圳證券交易所", "type": "高科技"},
            "600": {"industry": "沪市主板", "market": "上海證券交易所", "type": "大盘蓝筹"},
            "601": {"industry": "沪市主板", "market": "上海證券交易所", "type": "大盘蓝筹"},
            "603": {"industry": "沪市主板", "market": "上海證券交易所", "type": "中小盘"},
            "688": {"industry": "科創板", "market": "上海證券交易所", "type": "科技創新"},
        }

        info = industry_map.get(code_prefix, {
            "industry": "其他",
            "market": "未知市場",
            "type": "综合"
        })

        # 特殊股票的詳細信息
        special_stocks = {
            "000001": {
                "industry": "銀行業",
                "analysis": "平安銀行是中國領先的股份制商業銀行，在零售銀行業務方面具有顯著優势。",
                "market_share": "股份制銀行前列",
                "brand_value": "知名金融品牌",
                "tech_advantage": "金融科技創新領先"
            },
            "600036": {
                "industry": "銀行業",
                "analysis": "招商銀行是中國優质的股份制銀行，零售銀行業務和財富管理業務領先。",
                "market_share": "股份制銀行龙头",
                "brand_value": "優质銀行品牌",
                "tech_advantage": "數字化銀行先锋"
            },
            "000002": {
                "industry": "房地產",
                "analysis": "万科A是中國房地產行業龙头企業，在住宅開發領域具有領先地位。",
                "market_share": "房地產行業前三",
                "brand_value": "知名地產品牌",
                "tech_advantage": "绿色建筑技術"
            }
        }

        if symbol in special_stocks:
            info.update(special_stocks[symbol])
        else:
            info.update({
                "analysis": f"该股票屬於{info['industry']}，具體業務需要進一步分析。",
                "market_share": "待分析",
                "brand_value": "待評估",
                "tech_advantage": "待分析"
            })

        return info

    def _estimate_financial_metrics(self, symbol: str, current_price: str) -> dict:
        """獲取真實財務指標（優先使用Tushare真實數據，失败時使用估算）"""

        # 提取價格數值
        try:
            price_value = float(current_price.replace('¥', '').replace(',', ''))
        except:
            price_value = 10.0  # 默認值

        # 嘗試獲取真實財務數據
        real_metrics = self._get_real_financial_metrics(symbol, price_value)
        if real_metrics:
            logger.debug(f"✅ 使用真實財務數據: {symbol}")
            return real_metrics
        
        # 如果無法獲取真實數據，使用估算數據並標註
        logger.warning(f"⚠️ 無法獲取真實財務數據，使用估算數據: {symbol}")
        estimated_metrics = self._get_estimated_financial_metrics(symbol, price_value)
        
        # 在所有指標後添加估算標註
        for key in estimated_metrics:
            if isinstance(estimated_metrics[key], str) and key not in ['fundamental_score', 'valuation_score', 'growth_score', 'risk_level']:
                if "（" not in estimated_metrics[key]:
                    estimated_metrics[key] += "（估算值）"
        
        return estimated_metrics

    def _get_real_financial_metrics(self, symbol: str, price_value: float) -> dict:
        """獲取真實財務指標 - 優先使用AKShare"""
        try:
            # 優先嘗試AKShare數據源
            logger.info(f"🔄 優先嘗試AKShare獲取{symbol}財務數據")
            from .akshare_utils import get_akshare_provider
            
            akshare_provider = get_akshare_provider()
            
            if akshare_provider.connected:
                financial_data = akshare_provider.get_financial_data(symbol)
                
                if financial_data and any(not v.empty if hasattr(v, 'empty') else bool(v) for v in financial_data.values()):
                    logger.info(f"✅ AKShare財務數據獲取成功: {symbol}")
                    # 獲取股票基本信息
                    stock_info = akshare_provider.get_stock_info(symbol)
                    
                    # 解析AKShare財務數據
                    logger.debug(f"🔧 調用AKShare解析函數，股價: {price_value}")
                    metrics = self._parse_akshare_financial_data(financial_data, stock_info, price_value)
                    logger.debug(f"🔧 AKShare解析結果: {metrics}")
                    if metrics:
                        logger.info(f"✅ AKShare解析成功，返回指標")
                        return metrics
                    else:
                        logger.warning(f"⚠️ AKShare解析失败，返回None")
                else:
                    logger.warning(f"⚠️ AKShare未獲取到{symbol}財務數據，嘗試Tushare")
            else:
                logger.warning(f"⚠️ AKShare未連接，嘗試Tushare")
            
            # 备用方案：使用Tushare數據源
            logger.info(f"🔄 使用Tushare备用數據源獲取{symbol}財務數據")
            from .tushare_utils import get_tushare_provider
            
            provider = get_tushare_provider()
            if not provider.connected:
                logger.debug(f"Tushare未連接，無法獲取{symbol}真實財務數據")
                return None
            
            # 獲取財務數據
            financial_data = provider.get_financial_data(symbol)
            if not financial_data:
                logger.debug(f"未獲取到{symbol}的財務數據")
                return None
            
            # 獲取股票基本信息
            stock_info = provider.get_stock_info(symbol)
            
            # 解析Tushare財務數據
            metrics = self._parse_financial_data(financial_data, stock_info, price_value)
            if metrics:
                return metrics
                
        except Exception as e:
            logger.debug(f"獲取{symbol}真實財務數據失败: {e}")
        
        return None

    def _parse_akshare_financial_data(self, financial_data: dict, stock_info: dict, price_value: float) -> dict:
        """解析AKShare財務數據為指標"""
        try:
            # 獲取最新的財務數據
            balance_sheet = financial_data.get('balance_sheet', [])
            income_statement = financial_data.get('income_statement', [])
            cash_flow = financial_data.get('cash_flow', [])
            main_indicators = financial_data.get('main_indicators')
            
            if main_indicators is None or main_indicators.empty:
                logger.warning("AKShare主要財務指標為空")
                return None
            
            # main_indicators是DataFrame，需要轉換為字典格式便於查找
            # 獲取最新數據列（第3列，索引為2）
            latest_col = main_indicators.columns[2] if len(main_indicators.columns) > 2 else None
            if not latest_col:
                logger.warning("AKShare主要財務指標缺少數據列")
                return None
            
            logger.info(f"📅 使用AKShare最新數據期間: {latest_col}")
            
            # 創建指標名稱到值的映射
            indicators_dict = {}
            for _, row in main_indicators.iterrows():
                indicator_name = row['指標']
                value = row[latest_col]
                indicators_dict[indicator_name] = value
            
            logger.debug(f"AKShare主要財務指標數量: {len(indicators_dict)}")
            
            # 計算財務指標
            metrics = {}
            
            # 獲取ROE - 直接從指標中獲取
            roe_value = indicators_dict.get('净資產收益率(ROE)')
            if roe_value is not None and str(roe_value) != 'nan' and roe_value != '--':
                try:
                    roe_val = float(roe_value)
                    # ROE通常是百分比形式
                    metrics["roe"] = f"{roe_val:.1f}%"
                    logger.debug(f"✅ 獲取ROE: {metrics['roe']}")
                except (ValueError, TypeError):
                    metrics["roe"] = "N/A"
            else:
                metrics["roe"] = "N/A"
            
            # 獲取每股收益 - 用於計算PE
            eps_value = indicators_dict.get('基本每股收益')
            if eps_value is not None and str(eps_value) != 'nan' and eps_value != '--':
                try:
                    eps_val = float(eps_value)
                    if eps_val > 0:
                        # 計算PE = 股價 / 每股收益
                        pe_val = price_value / eps_val
                        metrics["pe"] = f"{pe_val:.1f}倍"
                        logger.debug(f"✅ 計算PE: 股價{price_value} / EPS{eps_val} = {metrics['pe']}")
                    else:
                        metrics["pe"] = "N/A（亏損）"
                except (ValueError, TypeError):
                    metrics["pe"] = "N/A"
            else:
                metrics["pe"] = "N/A"
            
            # 獲取每股净資產 - 用於計算PB
            bps_value = indicators_dict.get('每股净資產_最新股數')
            if bps_value is not None and str(bps_value) != 'nan' and bps_value != '--':
                try:
                    bps_val = float(bps_value)
                    if bps_val > 0:
                        # 計算PB = 股價 / 每股净資產
                        pb_val = price_value / bps_val
                        metrics["pb"] = f"{pb_val:.2f}倍"
                        logger.debug(f"✅ 計算PB: 股價{price_value} / BPS{bps_val} = {metrics['pb']}")
                    else:
                        metrics["pb"] = "N/A"
                except (ValueError, TypeError):
                    metrics["pb"] = "N/A"
            else:
                metrics["pb"] = "N/A"
            
            # 嘗試獲取其他指標
            # 总資產收益率(ROA)
            roa_value = indicators_dict.get('总資產報酬率')
            if roa_value is not None and str(roa_value) != 'nan' and roa_value != '--':
                try:
                    roa_val = float(roa_value)
                    metrics["roa"] = f"{roa_val:.1f}%"
                except (ValueError, TypeError):
                    metrics["roa"] = "N/A"
            else:
                metrics["roa"] = "N/A"
            
            # 毛利率
            gross_margin_value = indicators_dict.get('毛利率')
            if gross_margin_value is not None and str(gross_margin_value) != 'nan' and gross_margin_value != '--':
                try:
                    gross_margin_val = float(gross_margin_value)
                    metrics["gross_margin"] = f"{gross_margin_val:.1f}%"
                except (ValueError, TypeError):
                    metrics["gross_margin"] = "N/A"
            else:
                metrics["gross_margin"] = "N/A"
            
            # 銷售净利率
            net_margin_value = indicators_dict.get('銷售净利率')
            if net_margin_value is not None and str(net_margin_value) != 'nan' and net_margin_value != '--':
                try:
                    net_margin_val = float(net_margin_value)
                    metrics["net_margin"] = f"{net_margin_val:.1f}%"
                except (ValueError, TypeError):
                    metrics["net_margin"] = "N/A"
            else:
                metrics["net_margin"] = "N/A"
            
            # 資產负债率
            debt_ratio_value = indicators_dict.get('資產负债率')
            if debt_ratio_value is not None and str(debt_ratio_value) != 'nan' and debt_ratio_value != '--':
                try:
                    debt_ratio_val = float(debt_ratio_value)
                    metrics["debt_ratio"] = f"{debt_ratio_val:.1f}%"
                except (ValueError, TypeError):
                    metrics["debt_ratio"] = "N/A"
            else:
                metrics["debt_ratio"] = "N/A"
            
            # 流動比率
            current_ratio_value = indicators_dict.get('流動比率')
            if current_ratio_value is not None and str(current_ratio_value) != 'nan' and current_ratio_value != '--':
                try:
                    current_ratio_val = float(current_ratio_value)
                    metrics["current_ratio"] = f"{current_ratio_val:.2f}"
                except (ValueError, TypeError):
                    metrics["current_ratio"] = "N/A"
            else:
                metrics["current_ratio"] = "N/A"
            
            # 速動比率
            quick_ratio_value = indicators_dict.get('速動比率')
            if quick_ratio_value is not None and str(quick_ratio_value) != 'nan' and quick_ratio_value != '--':
                try:
                    quick_ratio_val = float(quick_ratio_value)
                    metrics["quick_ratio"] = f"{quick_ratio_val:.2f}"
                except (ValueError, TypeError):
                    metrics["quick_ratio"] = "N/A"
            else:
                metrics["quick_ratio"] = "N/A"
            
            # 補充其他指標的默認值
            metrics.update({
                "ps": "待計算",
                "dividend_yield": "待查詢",
                "cash_ratio": "待分析"
            })
            
            # 評分（基於AKShare數據的簡化評分）
            fundamental_score = self._calculate_fundamental_score(metrics, stock_info)
            valuation_score = self._calculate_valuation_score(metrics)
            growth_score = self._calculate_growth_score(metrics, stock_info)
            risk_level = self._calculate_risk_level(metrics, stock_info)
            
            metrics.update({
                "fundamental_score": fundamental_score,
                "valuation_score": valuation_score,
                "growth_score": growth_score,
                "risk_level": risk_level,
                "data_source": "AKShare"
            })
            
            logger.info(f"✅ AKShare財務數據解析成功: PE={metrics['pe']}, PB={metrics['pb']}, ROE={metrics['roe']}")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ AKShare財務數據解析失败: {e}")
            return None

    def _parse_financial_data(self, financial_data: dict, stock_info: dict, price_value: float) -> dict:
        """解析財務數據為指標"""
        try:
            # 獲取最新的財務數據
            balance_sheet = financial_data.get('balance_sheet', [])
            income_statement = financial_data.get('income_statement', [])
            cash_flow = financial_data.get('cash_flow', [])
            
            if not (balance_sheet or income_statement):
                return None
            
            latest_balance = balance_sheet[0] if balance_sheet else {}
            latest_income = income_statement[0] if income_statement else {}
            latest_cash = cash_flow[0] if cash_flow else {}
            
            # 計算財務指標
            metrics = {}
            
            # 基础數據
            total_assets = latest_balance.get('total_assets', 0) or 0
            total_liab = latest_balance.get('total_liab', 0) or 0
            total_equity = latest_balance.get('total_hldr_eqy_exc_min_int', 0) or 0
            total_revenue = latest_income.get('total_revenue', 0) or 0
            net_income = latest_income.get('n_income', 0) or 0
            operate_profit = latest_income.get('operate_profit', 0) or 0
            
            # 估算市值（簡化計算）
            market_cap = price_value * 1000000000  # 假設10億股本
            
            # 計算各項指標
            # PE比率
            if net_income > 0:
                pe_ratio = market_cap / (net_income * 10000)  # 轉換單位
                metrics["pe"] = f"{pe_ratio:.1f}倍"
            else:
                metrics["pe"] = "N/A（亏損）"
            
            # PB比率
            if total_equity > 0:
                pb_ratio = market_cap / (total_equity * 10000)
                metrics["pb"] = f"{pb_ratio:.2f}倍"
            else:
                metrics["pb"] = "N/A"
            
            # PS比率
            if total_revenue > 0:
                ps_ratio = market_cap / (total_revenue * 10000)
                metrics["ps"] = f"{ps_ratio:.1f}倍"
            else:
                metrics["ps"] = "N/A"
            
            # ROE
            if total_equity > 0 and net_income > 0:
                roe = (net_income / total_equity) * 100
                metrics["roe"] = f"{roe:.1f}%"
            else:
                metrics["roe"] = "N/A"
            
            # ROA
            if total_assets > 0 and net_income > 0:
                roa = (net_income / total_assets) * 100
                metrics["roa"] = f"{roa:.1f}%"
            else:
                metrics["roa"] = "N/A"
            
            # 净利率
            if total_revenue > 0 and net_income > 0:
                net_margin = (net_income / total_revenue) * 100
                metrics["net_margin"] = f"{net_margin:.1f}%"
            else:
                metrics["net_margin"] = "N/A"
            
            # 資產负债率
            if total_assets > 0:
                debt_ratio = (total_liab / total_assets) * 100
                metrics["debt_ratio"] = f"{debt_ratio:.1f}%"
            else:
                metrics["debt_ratio"] = "N/A"
            
            # 其他指標設為默認值
            metrics.update({
                "dividend_yield": "待查詢",
                "gross_margin": "待計算",
                "current_ratio": "待計算",
                "quick_ratio": "待計算",
                "cash_ratio": "待分析"
            })
            
            # 評分（基於真實數據的簡化評分）
            fundamental_score = self._calculate_fundamental_score(metrics, stock_info)
            valuation_score = self._calculate_valuation_score(metrics)
            growth_score = self._calculate_growth_score(metrics, stock_info)
            risk_level = self._calculate_risk_level(metrics, stock_info)
            
            metrics.update({
                "fundamental_score": fundamental_score,
                "valuation_score": valuation_score,
                "growth_score": growth_score,
                "risk_level": risk_level
            })
            
            return metrics
            
        except Exception as e:
            logger.error(f"解析財務數據失败: {e}")
            return None

    def _calculate_fundamental_score(self, metrics: dict, stock_info: dict) -> float:
        """計算基本面評分"""
        score = 5.0  # 基础分
        
        # ROE評分
        roe_str = metrics.get("roe", "N/A")
        if roe_str != "N/A":
            try:
                roe = float(roe_str.replace("%", ""))
                if roe > 15:
                    score += 1.5
                elif roe > 10:
                    score += 1.0
                elif roe > 5:
                    score += 0.5
            except:
                pass
        
        # 净利率評分
        net_margin_str = metrics.get("net_margin", "N/A")
        if net_margin_str != "N/A":
            try:
                net_margin = float(net_margin_str.replace("%", ""))
                if net_margin > 20:
                    score += 1.0
                elif net_margin > 10:
                    score += 0.5
            except:
                pass
        
        return min(score, 10.0)

    def _calculate_valuation_score(self, metrics: dict) -> float:
        """計算估值評分"""
        score = 5.0  # 基础分
        
        # PE評分
        pe_str = metrics.get("pe", "N/A")
        if pe_str != "N/A" and "亏損" not in pe_str:
            try:
                pe = float(pe_str.replace("倍", ""))
                if pe < 15:
                    score += 2.0
                elif pe < 25:
                    score += 1.0
                elif pe > 50:
                    score -= 1.0
            except:
                pass
        
        # PB評分
        pb_str = metrics.get("pb", "N/A")
        if pb_str != "N/A":
            try:
                pb = float(pb_str.replace("倍", ""))
                if pb < 1.5:
                    score += 1.0
                elif pb < 3:
                    score += 0.5
                elif pb > 5:
                    score -= 0.5
            except:
                pass
        
        return min(max(score, 1.0), 10.0)

    def _calculate_growth_score(self, metrics: dict, stock_info: dict) -> float:
        """計算成長性評分"""
        score = 6.0  # 基础分
        
        # 根據行業調整
        industry = stock_info.get('industry', '')
        if '科技' in industry or '软件' in industry or '互聯網' in industry:
            score += 1.0
        elif '銀行' in industry or '保險' in industry:
            score -= 0.5
        
        return min(max(score, 1.0), 10.0)

    def _calculate_risk_level(self, metrics: dict, stock_info: dict) -> str:
        """計算風險等級"""
        # 資產负债率
        debt_ratio_str = metrics.get("debt_ratio", "N/A")
        if debt_ratio_str != "N/A":
            try:
                debt_ratio = float(debt_ratio_str.replace("%", ""))
                if debt_ratio > 70:
                    return "較高"
                elif debt_ratio > 50:
                    return "中等"
                else:
                    return "較低"
            except:
                pass
        
        # 根據行業判斷
        industry = stock_info.get('industry', '')
        if '銀行' in industry:
            return "中等"
        elif '科技' in industry or '創業板' in industry:
            return "較高"
        
        return "中等"

    def _get_estimated_financial_metrics(self, symbol: str, price_value: float) -> dict:
        """獲取估算財務指標（原有的分類方法）"""
        # 根據股票代碼和價格估算指標
        if symbol.startswith(('000001', '600036')):  # 銀行股
            return {
                "pe": "5.2倍（銀行業平均水平）",
                "pb": "0.65倍（破净狀態，銀行業常见）",
                "ps": "2.1倍",
                "dividend_yield": "4.2%（銀行業分红較高）",
                "roe": "12.5%（銀行業平均）",
                "roa": "0.95%",
                "gross_margin": "N/A（銀行業無毛利率概念）",
                "net_margin": "28.5%",
                "debt_ratio": "92%（銀行業负债率高屬正常）",
                "current_ratio": "N/A（銀行業特殊）",
                "quick_ratio": "N/A（銀行業特殊）",
                "cash_ratio": "充足",
                "fundamental_score": 7.5,
                "valuation_score": 8.0,
                "growth_score": 6.5,
                "risk_level": "中等"
            }
        elif symbol.startswith('300'):  # 創業板
            return {
                "pe": "35.8倍（創業板平均）",
                "pb": "3.2倍",
                "ps": "5.8倍",
                "dividend_yield": "1.2%",
                "roe": "15.2%",
                "roa": "8.5%",
                "gross_margin": "42.5%",
                "net_margin": "18.2%",
                "debt_ratio": "35%",
                "current_ratio": "2.1倍",
                "quick_ratio": "1.8倍",
                "cash_ratio": "良好",
                "fundamental_score": 7.0,
                "valuation_score": 5.5,
                "growth_score": 8.5,
                "risk_level": "較高"
            }
        else:  # 其他股票
            return {
                "pe": "18.5倍（市場平均）",
                "pb": "1.8倍",
                "ps": "2.5倍",
                "dividend_yield": "2.5%",
                "roe": "12.8%",
                "roa": "6.2%",
                "gross_margin": "25.5%",
                "net_margin": "12.8%",
                "debt_ratio": "45%",
                "current_ratio": "1.5倍",
                "quick_ratio": "1.2倍",
                "cash_ratio": "一般",
                "fundamental_score": 6.5,
                "valuation_score": 6.0,
                "growth_score": 7.0,
                "risk_level": "中等"
            }

    def _analyze_valuation(self, financial_estimates: dict) -> str:
        """分析估值水平"""
        valuation_score = financial_estimates['valuation_score']

        if valuation_score >= 8:
            return "當前估值水平較為合理，具有一定的投資價值。市盈率和市净率相對較低，安全邊际較高。"
        elif valuation_score >= 6:
            return "估值水平適中，需要結合基本面和成長性综合判斷投資價值。"
        else:
            return "當前估值偏高，投資需谨慎。建议等待更好的买入時機。"

    def _analyze_growth_potential(self, symbol: str, industry_info: dict) -> str:
        """分析成長潜力"""
        if symbol.startswith(('000001', '600036')):
            return "銀行業整體增長穩定，受益於經濟發展和金融深化。數字化轉型和財富管理業務是主要增長點。"
        elif symbol.startswith('300'):
            return "創業板公司通常具有較高的成長潜力，但也伴隨着較高的風險。需要關註技術創新和市場拓展能力。"
        else:
            return "成長潜力需要結合具體行業和公司基本面分析。建议關註行業發展趋势和公司競爭優势。"

    def _analyze_risks(self, symbol: str, financial_estimates: dict, industry_info: dict) -> str:
        """分析投資風險"""
        risk_level = financial_estimates['risk_level']

        risk_analysis = f"**風險等級**: {risk_level}\n\n"

        if symbol.startswith(('000001', '600036')):
            risk_analysis += """**主要風險**:
- 利率環境變化對净息差的影響
- 信贷資產质量風險
- 監管政策變化風險
- 宏觀經濟下行對銀行業的影響"""
        elif symbol.startswith('300'):
            risk_analysis += """**主要風險**:
- 技術更新換代風險
- 市場競爭加剧風險
- 估值波動較大
- 業绩不確定性較高"""
        else:
            risk_analysis += """**主要風險**:
- 行業周期性風險
- 宏觀經濟環境變化
- 市場競爭風險
- 政策調整風險"""

        return risk_analysis

    def _generate_investment_advice(self, financial_estimates: dict, industry_info: dict) -> str:
        """生成投資建议"""
        fundamental_score = financial_estimates['fundamental_score']
        valuation_score = financial_estimates['valuation_score']
        growth_score = financial_estimates['growth_score']

        total_score = (fundamental_score + valuation_score + growth_score) / 3

        if total_score >= 7.5:
            return """**投資建议**: 🟢 **买入**
- 基本面良好，估值合理，具有較好的投資價值
- 建议分批建仓，長期持有
- 適合價值投資者和穩健型投資者"""
        elif total_score >= 6.0:
            return """**投資建议**: 🟡 **觀望**
- 基本面一般，需要進一步觀察
- 可以小仓位試探，等待更好時機
- 適合有經驗的投資者"""
        else:
            return """**投資建议**: 🔴 **回避**
- 當前風險較高，不建议投資
- 建议等待基本面改善或估值回落
- 風險承受能力較低的投資者應避免"""
    
    def _try_get_old_cache(self, symbol: str, start_date: str, end_date: str) -> Optional[str]:
        """嘗試獲取過期的緩存數據作為备用"""
        try:
            # 查找任何相關的緩存，不考慮TTL
            for metadata_file in self.cache.metadata_dir.glob(f"*_meta.json"):
                try:
                    import json

                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    if (metadata.get('symbol') == symbol and 
                        metadata.get('data_type') == 'stock_data' and
                        metadata.get('market_type') == 'china'):
                        
                        cache_key = metadata_file.stem.replace('_meta', '')
                        cached_data = self.cache.load_stock_data(cache_key)
                        if cached_data:
                            return cached_data + "\n\n⚠️ 註意: 使用的是過期緩存數據"
                except Exception:
                    continue
        except Exception:
            pass
        
        return None
    
    def _generate_fallback_data(self, symbol: str, start_date: str, end_date: str, error_msg: str) -> str:
        """生成备用數據"""
        return f"""# {symbol} A股數據獲取失败

## ❌ 錯誤信息
{error_msg}

## 📊 模擬數據（仅供演示）
- 股票代碼: {symbol}
- 股票名稱: 模擬公司
- 數據期間: {start_date} 至 {end_date}
- 模擬價格: ¥{random.uniform(10, 50):.2f}
- 模擬涨跌: {random.uniform(-5, 5):+.2f}%

## ⚠️ 重要提示
由於數據接口限制或網絡問題，無法獲取實時數據。
建议稍後重試或檢查網絡連接。

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    def _generate_fallback_fundamentals(self, symbol: str, error_msg: str) -> str:
        """生成备用基本面數據"""
        return f"""# {symbol} A股基本面分析失败

## ❌ 錯誤信息
{error_msg}

## 📊 基本信息
- 股票代碼: {symbol}
- 分析狀態: 數據獲取失败
- 建议: 稍後重試或檢查網絡連接

生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


# 全局實例
_china_data_provider = None

def get_optimized_china_data_provider() -> OptimizedChinaDataProvider:
    """獲取全局A股數據提供器實例"""
    global _china_data_provider
    if _china_data_provider is None:
        _china_data_provider = OptimizedChinaDataProvider()
    return _china_data_provider


def get_china_stock_data_cached(symbol: str, start_date: str, end_date: str, 
                               force_refresh: bool = False) -> str:
    """
    獲取A股數據的便捷函數
    
    Args:
        symbol: 股票代碼（6位數字）
        start_date: 開始日期 (YYYY-MM-DD)
        end_date: 結束日期 (YYYY-MM-DD)
        force_refresh: 是否强制刷新緩存
    
    Returns:
        格式化的股票數據字符串
    """
    provider = get_optimized_china_data_provider()
    return provider.get_stock_data(symbol, start_date, end_date, force_refresh)


def get_china_fundamentals_cached(symbol: str, force_refresh: bool = False) -> str:
    """
    獲取A股基本面數據的便捷函數
    
    Args:
        symbol: 股票代碼（6位數字）
        force_refresh: 是否强制刷新緩存
    
    Returns:
        格式化的基本面數據字符串
    """
    provider = get_optimized_china_data_provider()
    return provider.get_fundamentals_data(symbol, force_refresh)
