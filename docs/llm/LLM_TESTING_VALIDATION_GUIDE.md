# LLM 適配器測試指南與驗證清單

## 📋 概述

本指南提供了完整的 LLM 適配器測試流程，確保新集成的大模型能夠穩定運行並正確集成到 TradingAgents 系統中。

## 🧪 測試類型

### 1. 基礎連接測試
驗證適配器能夠成功連接到 LLM 提供商的 API。

### 2. 工具調用測試
驗證適配器能夠正確執行 function calling，這是 TradingAgents 分析功能的核心。

### 3. Web 界面集成測試
驗證新的 LLM 選項在前端界面中正確顯示和工作。

### 4. 端到端分析測試
驗證完整的股票分析流程能夠使用新的 LLM 正常運行。

## 🔧 測試環境準備

### 第一步：設置 API 密鑰

1. **複制環境變量模板**
   ```bash
   cp .env.example .env
   ```

2. **添加您的 API 密鑰**
   ```bash
   # 在 .env 文件中添加
   YOUR_PROVIDER_API_KEY=your_actual_api_key_here
   ```

3. **驗證環境變量加載**
   ```python
   import os
   from dotenv import load_dotenv
   
   load_dotenv()
   api_key = os.getenv("YOUR_PROVIDER_API_KEY")
   print(f"API Key 是否配置: {'是' if api_key else '否'}")
   ```

### 第二步：安裝測試依賴

```bash
# 確保項目已安裝
pip install -e .

# 安裝測試相關依賴
pip install pytest pytest-asyncio
```

## 📝 測試腳本模板

### 基礎連接測試

創建 `tests/test_your_provider_adapter.py`：

### 模型專項測試（OpenAI 兼容模式）

創建 `tests/test__adapter.py`：

```python
import os
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

def test__api_key_config():
    """測試 API Key 配置"""
    api_key = os.environ.get("_API_KEY")
    
    if not api_key:
        print("❌ 缺少API密鑰配置: _API_KEY")
        return False
    
    if not api_key.startswith("bce-v3/"):
        print("⚠️ API密鑰格式可能不正確，建議使用 bce-v3/ 開頭的格式")
        return False
    
    print(f"✅ API密鑰配置正確 (格式: {api_key[:10]}...)")
    return True

def test__basic_chat():
    """測試基礎對話（OpenAI 兼容模式）"""
    try:
        llm = create_openai_compatible_llm(
            provider="",
            model="ernie-3.5-8k",
            temperature=0.1,
            max_tokens=500
        )
        
        response = llm.invoke([
            HumanMessage(content="你好，請簡單介紹一下你自己")
        ])
        
        print(f"✅ 對話成功: {response.content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ 對話失敗: {e}")
        return False

def test__function_calling():
    """測試工具調用功能"""
    try:
        @tool
        def get_stock_price(symbol: str) -> str:
            """獲取股票價格
            
            Args:
                symbol: 股票代碼，如 AAPL
            
            Returns:
                股票價格信息
            """
            return f"股票 {symbol} 的當前價格是 $150.00"
        
        llm = create_openai_compatible_llm(
            provider="",
            model="ernie-4.0-turbo-8k",
            temperature=0.1
        )
        
        llm_with_tools = llm.bind_tools([get_stock_price])
        
        response = llm_with_tools.invoke([
            HumanMessage(content="請幫我查詢 AAPL 股票的價格")
        ])
        
        print(f"✅ 工具調用成功: {response.content[:200]}...")
        
        # 檢查是否包含工具調用結果
        if "150.00" in response.content or "AAPL" in response.content:
            print("✅ 工具調用結果正確返回")
            return True
        else:
            print("⚠️ 工具調用可能未正確執行")
            return False
            
    except Exception as e:
        print(f"❌ 工具調用失敗: {e}")
        return False

def test__chinese_analysis():
    """測試中文金融分析能力"""
    try:
        llm = create_openai_compatible_llm(
            provider="",
            model="ernie-3.5-8k",
            temperature=0.1
        )
        
        test_prompt = """請簡要分析苹果公司（AAPL）的投資價值，包括：
        1. 公司基本面
        2. 技術面趨勢
        3. 投資建議
        
        請用中文回答，字數控制在200字以內。"""
        
        response = llm.invoke([HumanMessage(content=test_prompt)])
        
        # 檢查響應是否包含中文和關鍵分析要素
        content = response.content
        if (any('\u4e00' <= char <= '\u9fff' for char in content) and 
            ("苹果" in content or "AAPL" in content) and
            len(content) > 50):
            print("✅ 中文金融分析能力正常")
            print(f"📄 分析內容預覽: {content[:150]}...")
            return True
        else:
            print("⚠️ 中文分析響應可能有問題")
            print(f"📄 實際響應: {content}")
            return False
            
    except Exception as e:
        print(f"❌ 中文分析測試失敗: {e}")
        return False

def test__model_variants():
    """測試不同模型變體"""
    models_to_test = ["ernie-3.5-8k", "ernie-4.0-turbo-8k", "
    
    for model in models_to_test:
        try:
            llm = create_openai_compatible_llm(
                provider="",
                model=model,
                temperature=0.1,
                max_tokens=100
            )
            
            response = llm.invoke([
                HumanMessage(content="簡單說明一下你的能力特點")
            ])
            
            print(f"✅ 模型 {model} 連接成功: {response.content[:50]}...")
        except Exception as e:
            print(f"❌ 模型 {model} 測試失敗: {e}")

if __name__ == "__main__":
    print("=== 模型專項測試（OpenAI 兼容模式）===")
    print()
    
    # 基礎配置測試
    test__api_key_config()
    print()
    
    # 基礎對話測試
    test__basic_chat()
    print()
    
    # 工具調用測試
    test__function_calling()
    print()
    
    # 中文分析測試
    test__chinese_analysis()
    print()
    
    # 模型變體測試
    print("--- 測試不同模型變體 ---")
    test__model_variants()
```

```python
#!/usr/bin/env python3
"""
{Provider} 適配器測試腳本
測試基礎連接、工具調用和集成功能
"""

import os
import sys
import pytest
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# 加載環境變量
load_dotenv()

def test_api_key_configuration():
    """測試 API 密鑰配置"""
    print("\n🔑 測試 API 密鑰配置")
    print("=" * 50)
    
    api_key = os.getenv("YOUR_PROVIDER_API_KEY")
    assert api_key is not None, "YOUR_PROVIDER_API_KEY 環境變量未設置"
    assert len(api_key) > 10, "API 密鑰長度不足，請檢查是否正確"
    
    print(f"✅ API 密鑰已配置 (長度: {len(api_key)})")
    return True

def test_adapter_import():
    """測試適配器導入"""
    print("\n📦 測試適配器導入")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.your_provider_adapter import ChatYourProvider
        print("✅ 適配器導入成功")
        return True
    except ImportError as e:
        print(f"❌ 適配器導入失敗: {e}")
        pytest.fail(f"適配器導入失敗: {e}")

def test_basic_connection():
    """測試基礎連接"""
    print("\n🔗 測試基礎連接")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.your_provider_adapter import ChatYourProvider
        
        # 創建適配器實例
        llm = ChatYourProvider(
            model="your-default-model",
            temperature=0.1,
            max_tokens=100
        )
        
        # 發送簡單測試消息
        response = llm.invoke([
            HumanMessage(content="請回複'連接測試成功'")
        ])
        
        print(f"✅ 連接成功")
        print(f"📄 回複內容: {response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ 連接失敗: {e}")
        pytest.fail(f"基礎連接測試失敗: {e}")

def test_function_calling():
    """測試工具調用功能"""
    print("\n🛠️ 測試工具調用功能")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.your_provider_adapter import ChatYourProvider
        
        # 定義測試工具
        @tool
        def get_stock_price(symbol: str) -> str:
            """獲取股票價格
            
            Args:
                symbol: 股票代碼，如 AAPL
            
            Returns:
                股票價格信息
            """
            return f"股票 {symbol} 的當前價格是 $150.00"
        
        # 創建帶工具的適配器
        llm = ChatYourProvider(
            model="your-default-model",
            temperature=0.1,
            max_tokens=500
        )
        llm_with_tools = llm.bind_tools([get_stock_price])
        
        # 測試工具調用
        response = llm_with_tools.invoke([
            HumanMessage(content="請幫我查詢 AAPL 股票的價格")
        ])
        
        print(f"✅ 工具調用成功")
        print(f"📄 回複內容: {response.content[:200]}...")
        
        # 檢查是否包含工具調用
        if "150.00" in response.content or "AAPL" in response.content:
            print("✅ 工具調用結果正確返回")
            return True
        else:
            print("⚠️ 工具調用可能未正確執行")
            return False
            
    except Exception as e:
        print(f"❌ 工具調用失敗: {e}")
        pytest.fail(f"工具調用測試失敗: {e}")

def test_factory_function():
    """測試工廠函數"""
    print("\n🏭 測試工廠函數")
    print("=" * 50)
    
    try:
        from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
        
        # 使用工廠函數創建實例
        llm = create_openai_compatible_llm(
            provider="your_provider",
            model="your-default-model",
            temperature=0.1,
            max_tokens=100
        )
        
        # 測試簡單調用
        response = llm.invoke([
            HumanMessage(content="測試工廠函數")
        ])
        
        print(f"✅ 工廠函數測試成功")
        print(f"📄 回複內容: {response.content[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ 工廠函數測試失敗: {e}")
        pytest.fail(f"工廠函數測試失敗: {e}")

def test_trading_graph_integration():
    """測試與 TradingGraph 的集成"""
    print("\n🔧 測試與 TradingGraph 的集成")
    print("=" * 50)
    
    try:
        from tradingagents.graph.trading_graph import TradingAgentsGraph
        
        # 創建配置
        config = {
            "llm_provider": "your_provider",
            "deep_think_llm": "your-default-model",
            "quick_think_llm": "your-default-model",
            "max_debate_rounds": 1,
            "online_tools": False,  # 關闭在線工具以加快測試
            "selected_analysts": ["fundamentals_analyst"]
        }
        
        print("🔄 創建 TradingGraph...")
        graph = TradingAgentsGraph(config)
        
        print("✅ TradingGraph 創建成功")
        print(f"   Deep thinking LLM: {type(graph.deep_thinking_llm).__name__}")
        print(f"   Quick thinking LLM: {type(graph.quick_thinking_llm).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ TradingGraph 集成測試失敗: {e}")
        pytest.fail(f"TradingGraph 集成測試失敗: {e}")

def run_all_tests():
    """運行所有測試"""
    print("🚀 開始 {Provider} 適配器全套測試")
    print("=" * 60)
    
    tests = [
        test_api_key_configuration,
        test_adapter_import,
        test_basic_connection,
        test_function_calling,
        test_factory_function,
        test_trading_graph_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except (AssertionError, Exception) as e:
            print(f"❌ 測試失敗: {test.__name__}")
            print(f"   錯誤信息: {e}")
            failed += 1
        print()
    
    print("📊 測試結果摘要")
    print("=" * 60)
    print(f"✅ 通過: {passed}")
    print(f"❌ 失敗: {failed}")
    print(f"📈 成功率: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 所有測試通過！適配器可以正常使用")
    else:
        print(f"\n⚠️ 有 {failed} 個測試失敗，請檢查配置")

if __name__ == "__main__":
    run_all_tests()
```

## 🌐 Web 界面測試

### 手動測試步驟

1. **啟動 Web 應用**
   ```bash
   python start_web.py
   ```

2. **檢查模型選擇器**
   - 在左側邊欄找到"LLM提供商"下拉菜單
   - 確認您的提供商出現在選項中
   - 選擇您的提供商

3. **檢查模型選項**
   - 選擇提供商後，確認模型選擇器顯示正確的模型列表
   - 嘗試選擇不同的模型

4. **進行簡單分析**
   - 輸入股票代碼（如 AAPL）
   - 選擇一個分析師（建議選擇"基本面分析師"）
   - 點擊"開始分析"
   - 觀察分析是否正常進行

### 自動化 Web 測試

創建 `tests/test_web_integration.py`：

```python
import streamlit as st
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_sidebar_integration():
    """測試側邊欄集成"""
    print("\n🔧 測試 Web 界面集成")
    print("=" * 50)
    
    try:
        # 模擬 Streamlit session state
        with patch('streamlit.session_state') as mock_state:
            mock_state.llm_provider = "your_provider"
            mock_state.llm_model = "your-default-model"
            
            # 導入側邊欄組件
            from web.components.sidebar import create_sidebar
            
            # 模擬 Streamlit 組件
            with patch('streamlit.selectbox') as mock_selectbox:
                mock_selectbox.return_value = "your_provider"
                
                # 測試側邊欄創建
                config = create_sidebar()
                
                print("✅ 側邊欄集成測試通過")
                return True
                
    except Exception as e:
        print(f"❌ Web 界面集成測試失敗: {e}")
        return False

if __name__ == "__main__":
    test_sidebar_integration()
```

## 📊 完整驗證清單

### ✅ 開發階段驗證

- [ ] **代碼品質**
  - [ ] 適配器類繼承自 `OpenAICompatibleBase`
  - [ ] 正確設置 `provider_name`、`api_key_env_var`、`base_url`
  - [ ] 模型配置添加到 `OPENAI_COMPATIBLE_PROVIDERS`
  - [ ] 適配器導出添加到 `__init__.py`

- [ ] **基礎功能**
  - [ ] API 密鑰環境變量正確配置
  - [ ] 基礎連接測試通過
  - [ ] 簡單文本生成正常工作
  - [ ] 錯誤處理機制有效

- [ ] **工具調用功能**
  - [ ] Function calling 正常工作
  - [ ] 工具參數正確解析
  - [ ] 工具結果正確返回
  - [ ] 複雜工具調用場景穩定

### ✅ 集成階段驗證

- [ ] **前端集成**
  - [ ] 提供商出現在下拉菜單中
  - [ ] 模型選擇器正常工作
  - [ ] UI 格式化顯示正確
  - [ ] 會話狀態正確保存

- [ ] **後端集成**
  - [ ] 工廠函數正確創建實例
  - [ ] TradingGraph 正確使用適配器
  - [ ] 配置參數正確傳遞
  - [ ] 錯誤處理正確集成

- [ ] **系統集成**
  - [ ] 環境變量檢查腳本支持新提供商
  - [ ] 日誌記錄正常工作
  - [ ] Token 使用統計正確
  - [ ] 內存管理正常

### ✅ 端到端驗證

- [ ] **基本分析流程**
  - [ ] 能夠進行簡單股票分析
  - [ ] 分析師選擇正常工作
  - [ ] 工具調用在分析中正常執行
  - [ ] 分析結果格式正確

- [ ] **高級功能**
  - [ ] 多輪對話正常工作
  - [ ] 記忆功能正常（如果啟用）
  - [ ] 並發請求處理穩定
  - [ ] 長時間運行穩定

- [ ] **錯誤處理**
  - [ ] API 錯誤正確處理
  - [ ] 網絡錯誤優雅降級
  - [ ] 配置錯誤清晰提示
  - [ ] 重試機制正常工作

### ✅ 性能與穩定性驗證

- [ ] **性能指標**
  - [ ] 響應時間合理（< 30秒）
  - [ ] 內存使用穩定
  - [ ] CPU 使用率正常
  - [ ] 無內存泄漏

- [ ] **穩定性測試**
  - [ ] 連續運行 30 分鐘無錯誤
  - [ ] 處理 50+ 請求無問題
  - [ ] 網絡中斷後能恢復
  - [ ] 並發請求處理正確

## 🐛 常見測試問題與解決方案

### 問題 1: API 密鑰錯誤

**症狀**: `AuthenticationError` 或 `InvalidAPIKey`

**解決方案**:
```bash
# 檢查環境變量
echo $YOUR_PROVIDER_API_KEY

# 重新加載環境變量
source .env

# 驗證 API 密鑰格式
python -c "import os; print(f'API Key: {os.getenv(\"YOUR_PROVIDER_API_KEY\")[:10]}...')"
```

### 問題 2: 工具調用失敗

**症狀**: `ToolCallError` 或工具未被調用

**解決方案**:
```python
# 檢查模型是否支持 function calling
from tradingagents.llm_adapters.openai_compatible_base import OPENAI_COMPATIBLE_PROVIDERS

provider_config = OPENAI_COMPATIBLE_PROVIDERS["your_provider"]
models = provider_config["models"]
print(f"模型支持 function calling: {models}")
```

### 問題 3: 前端集成失敗

**症狀**: 提供商不出現在下拉菜單中

**解決方案**:
```python
# 檢查 sidebar.py 配置
# 確保在 options 列表中包含您的提供商
# 確保在 format_func 字典中包含格式化映射
```

### 問題 4: 導入錯誤

**症狀**: `ModuleNotFoundError` 或 `ImportError`

**解決方案**:
```bash
# 確保項目已安裝
pip install -e .

# 檢查 __init__.py 導出
python -c "from tradingagents.llm_adapters import ChatYourProvider; print('導入成功')"
```

### 問題 5: 模型認證失敗

**症狀**: `AuthenticationError` 或 `invalid_client`

**解決方案**:
```bash
# 檢查API密鑰配置（僅需一個密鑰）
echo $_API_KEY

# 驗證密鑰格式（應該以 bce-v3/ 開頭）
python -c "import os; print(f'API Key格式: {os.getenv("_API_KEY", "未設置")[:10]}...')"

# 建議：使用 OpenAI 兼容路徑進行連通性驗證（無需 AK/SK 獲取 Token）
python - << 'PY'
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
llm = create_openai_compatible_llm(provider="", model="ernie-3.5-8k")
print(llm.invoke("ping").content)
PY
```

### 問題 6: 模型中文亂碼

**症狀**: 返回內容包含亂碼或編碼錯誤

**解決方案**:
```python
# 檢查系統編碼設置
import locale
import sys
print(f"系統編碼: {locale.getpreferredencoding()}")
print(f"Python編碼: {sys.getdefaultencoding()}")

# 強制設置UTF-8編碼
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 測試中文處理
test_text = "測試中文編碼"
print(f"原文: {test_text}")
print(f"編碼: {test_text.encode('utf-8')}")
print(f"解碼: {test_text.encode('utf-8').decode('utf-8')}")
```

### 問題 7: 調用失敗（OpenAI 兼容路徑）

**症狀**: `AuthenticationError`、`RateLimitError` 或 `ModelNotFound`

**解決方案**:
```python
# 1) 檢查 API Key 是否正確設置
action = "已設置" if os.getenv("_API_KEY") else "未設置"
print(f"_API_KEY: {action}")

# 2) 確認模型名稱是否在映射列表
from tradingagents.llm_adapters.openai_compatible_base import OPENAI_COMPATIBLE_PROVIDERS
print(OPENAI_COMPATIBLE_PROVIDERS[""]["models"].keys())

# 3) 低並發/延時重試
from tradingagents.llm_adapters.openai_compatible_base import create_openai_compatible_llm
llm = create_openai_compatible_llm(provider="", model="ernie-3.5-8k", request_timeout=60)
print(llm.invoke("hello").content)
```

## 📝 測試報告模板

完成測試後，創建測試報告：

```markdown
# {Provider} 適配器測試報告

## 基本信息
- **提供商**: {Provider}
- **適配器類**: Chat{Provider}
- **測試日期**: {Date}
- **測試者**: {Name}

## 測試結果摘要
- ✅ 基礎連接: 通過
- ✅ 工具調用: 通過  
- ✅ Web 集成: 通過
- ✅ 端到端: 通過

## 性能指標
- 平均響應時間: {X}秒
- 工具調用成功率: {X}%
- 內存使用: {X}MB
- 穩定性測試: 通過

## 已知問題
- 無重大問題

## 建議
- 適配器可以正常使用
- 建議合並到主分支
```

## 🎯 最佳實踐

1. **測試驅動開發**: 先寫測試，再實現功能
2. **小步快跑**: 每完成一個功能就進行測試
3. **自動化測試**: 使用腳本自動運行所有測試
4. **文檔同步**: 測試通過後及時更新文檔
5. **版本控制**: 每次測試創建 git 提交記錄

## 🔄 持續驗證

集成完成後，建議定期進行以下驗證：

- **每周**: 運行基礎連接測試
- **每月**: 運行完整測試套件
- **版本更新**: 重新運行所有測試
- **API 變更**: 重新驗證工具調用功能

---

通過遵循這個完整的測試指南，您可以確保新集成的 LLM 適配器品質可靠，功能完整，能夠穩定地為 TradingAgents 用戶提供服務。