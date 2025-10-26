# 數據處理流程

## 概述

TradingAgents 框架的數據處理系統负责将來自多個數據源的原始數據轉換為智能體可以使用的標準化、高质量信息。本文档詳細介紹了數據獲取、清洗、轉換、驗證和分發的完整流程。

## 數據處理架構

### 數據處理管道

```mermaid
graph TB
    subgraph "數據獲取層"
        API1[FinnHub API]
        API2[Yahoo Finance]
        API3[Reddit API]
        API4[Google News]
    end
    
    subgraph "數據預處理層"
        COLLECT[數據收集器]
        VALIDATE[數據驗證器]
        CLEAN[數據清洗器]
        NORMALIZE[數據標準化器]
    end
    
    subgraph "數據轉換層"
        TRANSFORM[數據轉換器]
        ENRICH[數據增强器]
        AGGREGATE[數據聚合器]
        FEATURE[特征工程器]
    end
    
    subgraph "數據存储層"
        CACHE[緩存系統]
        DATABASE[數據庫]
        MEMORY[內存存储]
    end
    
    subgraph "數據分發層"
        ROUTER[數據路由器]
        FORMATTER[格式化器]
        DISPATCHER[分發器]
    end
    
    API1 --> COLLECT
    API2 --> COLLECT
    API3 --> COLLECT
    API4 --> COLLECT
    
    COLLECT --> VALIDATE
    VALIDATE --> CLEAN
    CLEAN --> NORMALIZE
    
    NORMALIZE --> TRANSFORM
    TRANSFORM --> ENRICH
    ENRICH --> AGGREGATE
    AGGREGATE --> FEATURE
    
    FEATURE --> CACHE
    FEATURE --> DATABASE
    FEATURE --> MEMORY
    
    CACHE --> ROUTER
    DATABASE --> ROUTER
    MEMORY --> ROUTER
    
    ROUTER --> FORMATTER
    FORMATTER --> DISPATCHER
```

## 1. 數據收集器

### 核心功能
```python
class DataCollector:
    """數據收集器 - 統一收集各數據源的數據"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.data_sources = self._initialize_data_sources()
        self.collection_scheduler = CollectionScheduler()
        self.error_handler = DataErrorHandler()
        
    def collect_comprehensive_data(self, symbol: str, date: str = None) -> Dict:
        """收集综合數據"""
        
        collection_tasks = {
            "price_data": self._collect_price_data,
            "fundamental_data": self._collect_fundamental_data,
            "technical_data": self._collect_technical_data,
            "news_data": self._collect_news_data,
            "social_data": self._collect_social_data,
            "market_data": self._collect_market_data
        }
        
        collected_data = {}
        collection_metadata = {}
        
        # 並行收集數據
        with ThreadPoolExecutor(max_workers=6) as executor:
            future_to_task = {
                executor.submit(task_func, symbol, date): task_name
                for task_name, task_func in collection_tasks.items()
            }
            
            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    result = future.result(timeout=30)  # 30秒超時
                    collected_data[task_name] = result["data"]
                    collection_metadata[task_name] = result["metadata"]
                except Exception as e:
                    self.error_handler.handle_collection_error(task_name, e)
                    collected_data[task_name] = {}
                    collection_metadata[task_name] = {"error": str(e)}
        
        return {
            "data": collected_data,
            "metadata": collection_metadata,
            "collection_timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "date": date
        }
    
    def _collect_price_data(self, symbol: str, date: str = None) -> Dict:
        """收集價格數據"""
        
        price_sources = ["finnhub", "yahoo_finance"]
        price_data = {}
        
        for source in price_sources:
            try:
                if source == "finnhub" and "finnhub" in self.data_sources:
                    data = self.data_sources["finnhub"].get_stock_price(symbol)
                    price_data["finnhub"] = data
                    break  # 優先使用 FinnHub
                elif source == "yahoo_finance":
                    data = self.data_sources["yahoo"].get_current_price(symbol)
                    price_data["yahoo"] = data
            except Exception as e:
                print(f"Error collecting price data from {source}: {e}")
        
        # 選擇最佳數據源
        best_price_data = self._select_best_price_data(price_data)
        
        return {
            "data": best_price_data,
            "metadata": {
                "sources_attempted": price_sources,
                "sources_successful": list(price_data.keys()),
                "primary_source": self._identify_primary_source(price_data)
            }
        }
    
    def _collect_fundamental_data(self, symbol: str, date: str = None) -> Dict:
        """收集基本面數據"""
        
        fundamental_data = {}
        
        # 財務報表數據
        try:
            if "finnhub" in self.data_sources:
                financials = self.data_sources["finnhub"].get_financial_statements(symbol)
                fundamental_data["financials"] = financials
        except Exception as e:
            print(f"Error collecting financial statements: {e}")
        
        # 公司概况
        try:
            if "finnhub" in self.data_sources:
                profile = self.data_sources["finnhub"].get_company_profile(symbol)
                fundamental_data["profile"] = profile
        except Exception as e:
            print(f"Error collecting company profile: {e}")
        
        # 估值指標
        try:
            if "yahoo" in self.data_sources:
                valuation = self.data_sources["yahoo"].get_valuation_metrics(symbol)
                fundamental_data["valuation"] = valuation
        except Exception as e:
            print(f"Error collecting valuation metrics: {e}")
        
        return {
            "data": fundamental_data,
            "metadata": {
                "data_completeness": self._assess_fundamental_completeness(fundamental_data),
                "data_freshness": self._assess_data_freshness(fundamental_data)
            }
        }
```

## 2. 數據驗證器

### 數據质量檢查
```python
class DataValidator:
    """數據驗證器 - 確保數據质量和完整性"""
    
    def __init__(self):
        self.validation_rules = self._load_validation_rules()
        self.quality_metrics = QualityMetrics()
        
    def validate_collected_data(self, collected_data: Dict) -> Dict:
        """驗證收集的數據"""
        
        validation_results = {}
        
        for data_type, data in collected_data["data"].items():
            validation_result = self._validate_data_type(data_type, data)
            validation_results[data_type] = validation_result
        
        # 計算整體數據质量評分
        overall_quality = self._calculate_overall_quality(validation_results)
        
        return {
            "validation_results": validation_results,
            "overall_quality": overall_quality,
            "quality_grade": self._assign_quality_grade(overall_quality),
            "issues_found": self._extract_issues(validation_results),
            "recommendations": self._generate_quality_recommendations(validation_results)
        }
    
    def _validate_data_type(self, data_type: str, data: Dict) -> Dict:
        """驗證特定類型的數據"""
        
        validation_checks = {
            "completeness": self._check_completeness(data_type, data),
            "accuracy": self._check_accuracy(data_type, data),
            "consistency": self._check_consistency(data_type, data),
            "timeliness": self._check_timeliness(data_type, data),
            "format": self._check_format(data_type, data)
        }
        
        # 計算驗證評分
        validation_score = sum(check["score"] for check in validation_checks.values()) / len(validation_checks)
        
        return {
            "checks": validation_checks,
            "validation_score": validation_score,
            "status": "passed" if validation_score > 0.8 else "warning" if validation_score > 0.6 else "failed",
            "critical_issues": [check["issue"] for check in validation_checks.values() if check.get("critical")]
        }
    
    def _check_completeness(self, data_type: str, data: Dict) -> Dict:
        """檢查數據完整性"""
        
        required_fields = self.validation_rules[data_type]["required_fields"]
        missing_fields = [field for field in required_fields if field not in data]
        
        completeness_score = 1.0 - (len(missing_fields) / len(required_fields))
        
        return {
            "score": completeness_score,
            "missing_fields": missing_fields,
            "critical": len(missing_fields) > len(required_fields) * 0.5,
            "issue": f"Missing {len(missing_fields)} required fields" if missing_fields else None
        }
    
    def _check_accuracy(self, data_type: str, data: Dict) -> Dict:
        """檢查數據準確性"""
        
        accuracy_issues = []
        
        if data_type == "price_data":
            # 價格合理性檢查
            if "current_price" in data:
                price = data["current_price"]
                if not isinstance(price, (int, float)) or price <= 0:
                    accuracy_issues.append("Invalid price value")
                elif price > 10000:  # 異常高價格
                    accuracy_issues.append("Unusually high price")
        
        elif data_type == "fundamental_data":
            # 財務數據合理性檢查
            if "market_cap" in data:
                market_cap = data["market_cap"]
                if market_cap and market_cap < 0:
                    accuracy_issues.append("Negative market cap")
        
        accuracy_score = 1.0 if not accuracy_issues else 0.5
        
        return {
            "score": accuracy_score,
            "issues": accuracy_issues,
            "critical": len(accuracy_issues) > 0,
            "issue": "; ".join(accuracy_issues) if accuracy_issues else None
        }
```

## 3. 數據清洗器

### 數據清洗流程
```python
class DataCleaner:
    """數據清洗器 - 清理和修複數據問題"""
    
    def __init__(self):
        self.cleaning_strategies = self._initialize_cleaning_strategies()
        self.outlier_detector = OutlierDetector()
        
    def clean_data(self, validated_data: Dict) -> Dict:
        """清洗數據"""
        
        cleaned_data = {}
        cleaning_log = {}
        
        for data_type, data in validated_data["data"].items():
            cleaning_result = self._clean_data_type(data_type, data)
            cleaned_data[data_type] = cleaning_result["cleaned_data"]
            cleaning_log[data_type] = cleaning_result["cleaning_log"]
        
        return {
            "cleaned_data": cleaned_data,
            "cleaning_log": cleaning_log,
            "cleaning_summary": self._generate_cleaning_summary(cleaning_log)
        }
    
    def _clean_data_type(self, data_type: str, data: Dict) -> Dict:
        """清洗特定類型的數據"""
        
        cleaned_data = data.copy()
        cleaning_operations = []
        
        # 處理缺失值
        missing_value_result = self._handle_missing_values(data_type, cleaned_data)
        cleaned_data.update(missing_value_result["data"])
        cleaning_operations.extend(missing_value_result["operations"])
        
        # 處理異常值
        outlier_result = self._handle_outliers(data_type, cleaned_data)
        cleaned_data.update(outlier_result["data"])
        cleaning_operations.extend(outlier_result["operations"])
        
        # 數據類型轉換
        type_conversion_result = self._convert_data_types(data_type, cleaned_data)
        cleaned_data.update(type_conversion_result["data"])
        cleaning_operations.extend(type_conversion_result["operations"])
        
        # 數據格式標準化
        standardization_result = self._standardize_formats(data_type, cleaned_data)
        cleaned_data.update(standardization_result["data"])
        cleaning_operations.extend(standardization_result["operations"])
        
        return {
            "cleaned_data": cleaned_data,
            "cleaning_log": {
                "operations": cleaning_operations,
                "data_quality_improvement": self._measure_quality_improvement(data, cleaned_data)
            }
        }
    
    def _handle_missing_values(self, data_type: str, data: Dict) -> Dict:
        """處理缺失值"""
        
        operations = []
        updated_data = {}
        
        if data_type == "price_data":
            # 價格數據的缺失值處理
            if "current_price" not in data or data["current_price"] is None:
                # 嘗試從歷史數據推斷
                if "previous_close" in data and data["previous_close"]:
                    updated_data["current_price"] = data["previous_close"]
                    operations.append("Imputed current_price from previous_close")
        
        elif data_type == "fundamental_data":
            # 基本面數據的缺失值處理
            if "market_cap" not in data or data["market_cap"] is None:
                # 嘗試計算市值
                if "shares_outstanding" in data and "current_price" in data:
                    if data["shares_outstanding"] and data["current_price"]:
                        updated_data["market_cap"] = data["shares_outstanding"] * data["current_price"]
                        operations.append("Calculated market_cap from shares and price")
        
        return {
            "data": updated_data,
            "operations": operations
        }
    
    def _handle_outliers(self, data_type: str, data: Dict) -> Dict:
        """處理異常值"""
        
        operations = []
        updated_data = {}
        
        if data_type == "price_data":
            # 檢查價格異常值
            if "current_price" in data:
                price = data["current_price"]
                if isinstance(price, (int, float)):
                    # 使用歷史價格範围檢查異常值
                    if self._is_price_outlier(price, data):
                        # 使用前一交易日收盘價替代
                        if "previous_close" in data:
                            updated_data["current_price"] = data["previous_close"]
                            operations.append(f"Replaced outlier price {price} with previous_close")
        
        return {
            "data": updated_data,
            "operations": operations
        }
```

## 4. 數據轉換器

### 數據標準化和轉換
```python
class DataTransformer:
    """數據轉換器 - 標準化和轉換數據格式"""
    
    def __init__(self):
        self.transformation_rules = self._load_transformation_rules()
        self.unit_converter = UnitConverter()
        
    def transform_data(self, cleaned_data: Dict) -> Dict:
        """轉換數據"""
        
        transformed_data = {}
        transformation_log = {}
        
        for data_type, data in cleaned_data["cleaned_data"].items():
            transformation_result = self._transform_data_type(data_type, data)
            transformed_data[data_type] = transformation_result["transformed_data"]
            transformation_log[data_type] = transformation_result["transformation_log"]
        
        return {
            "transformed_data": transformed_data,
            "transformation_log": transformation_log,
            "transformation_summary": self._generate_transformation_summary(transformation_log)
        }
    
    def _transform_data_type(self, data_type: str, data: Dict) -> Dict:
        """轉換特定類型的數據"""
        
        transformed_data = {}
        transformations = []
        
        if data_type == "price_data":
            transformed_data = self._transform_price_data(data)
            transformations.append("Price data standardization")
            
        elif data_type == "fundamental_data":
            transformed_data = self._transform_fundamental_data(data)
            transformations.append("Fundamental data normalization")
            
        elif data_type == "news_data":
            transformed_data = self._transform_news_data(data)
            transformations.append("News data processing")
            
        elif data_type == "social_data":
            transformed_data = self._transform_social_data(data)
            transformations.append("Social data analysis")
        
        return {
            "transformed_data": transformed_data,
            "transformation_log": {
                "transformations": transformations,
                "data_schema": self._generate_data_schema(transformed_data)
            }
        }
    
    def _transform_price_data(self, data: Dict) -> Dict:
        """轉換價格數據"""
        
        transformed = {
            "symbol": data.get("symbol"),
            "price": {
                "current": float(data.get("current_price", 0)),
                "open": float(data.get("open", 0)),
                "high": float(data.get("high", 0)),
                "low": float(data.get("low", 0)),
                "previous_close": float(data.get("previous_close", 0))
            },
            "change": {
                "absolute": float(data.get("change", 0)),
                "percentage": float(data.get("change_percent", 0))
            },
            "volume": int(data.get("volume", 0)),
            "timestamp": self._standardize_timestamp(data.get("timestamp"))
        }
        
        # 計算額外指標
        if transformed["price"]["current"] and transformed["price"]["previous_close"]:
            transformed["metrics"] = {
                "daily_return": (transformed["price"]["current"] - transformed["price"]["previous_close"]) / transformed["price"]["previous_close"],
                "volatility_indicator": abs(transformed["price"]["high"] - transformed["price"]["low"]) / transformed["price"]["current"] if transformed["price"]["current"] else 0
            }
        
        return transformed
    
    def _transform_fundamental_data(self, data: Dict) -> Dict:
        """轉換基本面數據"""
        
        transformed = {
            "company_info": {
                "symbol": data.get("symbol"),
                "name": data.get("name"),
                "sector": data.get("sector"),
                "industry": data.get("industry"),
                "market_cap": self._normalize_market_cap(data.get("market_cap"))
            },
            "valuation_metrics": {
                "pe_ratio": float(data.get("pe_ratio", 0)) if data.get("pe_ratio") else None,
                "pb_ratio": float(data.get("pb_ratio", 0)) if data.get("pb_ratio") else None,
                "ps_ratio": float(data.get("ps_ratio", 0)) if data.get("ps_ratio") else None,
                "ev_ebitda": float(data.get("ev_ebitda", 0)) if data.get("ev_ebitda") else None
            },
            "financial_health": {
                "debt_to_equity": float(data.get("debt_to_equity", 0)) if data.get("debt_to_equity") else None,
                "current_ratio": float(data.get("current_ratio", 0)) if data.get("current_ratio") else None,
                "roe": float(data.get("roe", 0)) if data.get("roe") else None,
                "roa": float(data.get("roa", 0)) if data.get("roa") else None
            },
            "growth_metrics": {
                "revenue_growth": float(data.get("revenue_growth", 0)) if data.get("revenue_growth") else None,
                "earnings_growth": float(data.get("earnings_growth", 0)) if data.get("earnings_growth") else None,
                "book_value_growth": float(data.get("book_value_growth", 0)) if data.get("book_value_growth") else None
            }
        }
        
        return transformed
```

## 5. 特征工程器

### 特征提取和生成
```python
class FeatureEngineer:
    """特征工程器 - 生成分析特征"""
    
    def __init__(self):
        self.feature_generators = self._initialize_feature_generators()
        
    def engineer_features(self, transformed_data: Dict) -> Dict:
        """工程化特征"""
        
        features = {}
        
        # 價格特征
        if "price_data" in transformed_data:
            features["price_features"] = self._generate_price_features(transformed_data["price_data"])
        
        # 基本面特征
        if "fundamental_data" in transformed_data:
            features["fundamental_features"] = self._generate_fundamental_features(transformed_data["fundamental_data"])
        
        # 技術特征
        if "technical_data" in transformed_data:
            features["technical_features"] = self._generate_technical_features(transformed_data["technical_data"])
        
        # 情感特征
        sentiment_data = {}
        if "news_data" in transformed_data:
            sentiment_data["news"] = transformed_data["news_data"]
        if "social_data" in transformed_data:
            sentiment_data["social"] = transformed_data["social_data"]
        
        if sentiment_data:
            features["sentiment_features"] = self._generate_sentiment_features(sentiment_data)
        
        # 综合特征
        features["composite_features"] = self._generate_composite_features(features)
        
        return {
            "features": features,
            "feature_metadata": self._generate_feature_metadata(features)
        }
    
    def _generate_price_features(self, price_data: Dict) -> Dict:
        """生成價格特征"""
        
        price_info = price_data.get("price", {})
        
        features = {
            "price_momentum": self._calculate_price_momentum(price_info),
            "price_volatility": self._calculate_price_volatility(price_info),
            "price_trend": self._identify_price_trend(price_info),
            "support_resistance": self._identify_support_resistance(price_info),
            "volume_profile": self._analyze_volume_profile(price_data.get("volume", 0))
        }
        
        return features
    
    def _generate_fundamental_features(self, fundamental_data: Dict) -> Dict:
        """生成基本面特征"""
        
        valuation = fundamental_data.get("valuation_metrics", {})
        health = fundamental_data.get("financial_health", {})
        growth = fundamental_data.get("growth_metrics", {})
        
        features = {
            "valuation_score": self._calculate_valuation_score(valuation),
            "financial_strength": self._calculate_financial_strength(health),
            "growth_quality": self._assess_growth_quality(growth),
            "profitability_trend": self._analyze_profitability_trend(fundamental_data),
            "competitive_position": self._assess_competitive_position(fundamental_data)
        }
        
        return features
```

## 6. 數據分發器

### 智能數據路由
```python
class DataDispatcher:
    """數據分發器 - 将處理後的數據分發給智能體"""
    
    def __init__(self):
        self.routing_rules = self._load_routing_rules()
        self.agent_requirements = self._load_agent_requirements()
        
    def dispatch_data(self, engineered_data: Dict, target_agents: List[str]) -> Dict:
        """分發數據給目標智能體"""
        
        dispatched_data = {}
        
        for agent in target_agents:
            agent_data = self._prepare_agent_data(agent, engineered_data)
            dispatched_data[agent] = agent_data
        
        return {
            "agent_data": dispatched_data,
            "dispatch_metadata": {
                "target_agents": target_agents,
                "dispatch_timestamp": datetime.now().isoformat(),
                "data_completeness": self._assess_dispatch_completeness(dispatched_data)
            }
        }
    
    def _prepare_agent_data(self, agent: str, data: Dict) -> Dict:
        """為特定智能體準备數據"""
        
        agent_requirements = self.agent_requirements.get(agent, {})
        required_features = agent_requirements.get("required_features", [])
        
        agent_data = {}
        
        # 根據智能體需求筛選數據
        for feature_category in required_features:
            if feature_category in data["features"]:
                agent_data[feature_category] = data["features"][feature_category]
        
        # 添加智能體特定的數據格式化
        formatted_data = self._format_for_agent(agent, agent_data)
        
        return {
            "data": formatted_data,
            "metadata": {
                "agent": agent,
                "data_version": data.get("feature_metadata", {}).get("version"),
                "completeness_score": self._calculate_completeness_score(agent_data, required_features)
            }
        }
```

通過這個完整的數據處理流程，TradingAgents 確保智能體獲得高质量、標準化、相關的數據，為準確的分析和決策提供坚實基础。
