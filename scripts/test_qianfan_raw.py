#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
千帆API原生測試腳本
直接使用千帆官方SDK測試連通性，不依賴項目集成代碼
"""

import os
import sys
from dotenv import load_dotenv

# 加載環境變量
load_dotenv()

def test_qianfan_with_sdk():
    """使用千帆官方SDK測試"""
    try:
        import qianfan
        
        # 優先使用新的API Key
        api_key = os.getenv('QIANFAN_API_KEY')
        access_key = os.getenv('QIANFAN_ACCESS_KEY')
        secret_key = os.getenv('QIANFAN_SECRET_KEY')
        
        print("==== 千帆SDK測試 ====")
        print(f"API_KEY: {'已設置' if api_key else '未設置'}")
        print(f"ACCESS_KEY: {'已設置' if access_key else '未設置'}")
        print(f"SECRET_KEY: {'已設置' if secret_key else '未設置'}")
        
        if api_key:
            # 使用新的API Key方式
            print("使用新的API Key認證方式")
            os.environ["QIANFAN_API_KEY"] = api_key
        elif access_key and secret_key:
            # 使用旧的AK/SK方式
            print("使用傳統的AK/SK認證方式")
            os.environ["QIANFAN_ACCESS_KEY"] = access_key
            os.environ["QIANFAN_SECRET_KEY"] = secret_key
        else:
            print("❌ 請在.env文件中設置QIANFAN_API_KEY或QIANFAN_ACCESS_KEY+QIANFAN_SECRET_KEY")
            return False
        
        # 創建聊天完成客戶端
        chat_comp = qianfan.ChatCompletion(model="ERNIE-Speed-8K")
        
        # 發送測試消息
        print("\n發送測試消息...")
        resp = chat_comp.do(
            messages=[
                {
                    "role": "user",
                    "content": "你好，請簡單介紹一下你自己"
                }
            ],
            temperature=0.1
        )
        
        print("✅ 千帆API調用成功！")
        print(f"響應: {resp.get('result', '無響應內容')}")
        return True
        
    except ImportError:
        print("❌ 千帆SDK未安裝，請運行: pip install qianfan")
        return False
    except Exception as e:
        print(f"❌ 千帆SDK調用失败: {e}")
        return False

def test_qianfan_with_requests():
    """使用requests直接調用千帆API"""
    try:
        import requests
        import json
        
        api_key = os.getenv('QIANFAN_API_KEY')
        access_key = os.getenv('QIANFAN_ACCESS_KEY')
        secret_key = os.getenv('QIANFAN_SECRET_KEY')
        
        print("\n==== 千帆HTTP API測試 ====")
        
        # 方法1: 嘗試v2 API (OpenAI兼容)
        print("\n測試千帆v2 API (OpenAI兼容)...")
        
        # 構造Bearer token
        if api_key:
            print("使用新的API Key認證")
            bearer_token = api_key
        elif access_key and secret_key:
            print("使用傳統的AK/SK認證")
            bearer_token = f"bce-v3/{access_key}/{secret_key}"
        else:
            print("❌ 請在.env文件中設置QIANFAN_API_KEY或QIANFAN_ACCESS_KEY+QIANFAN_SECRET_KEY")
            return False
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bearer_token}"
        }
        
        data = {
            "model": "ernie-3.5-8k",
            "messages": [
                {
                    "role": "user",
                    "content": "你好，請簡單介紹一下你自己"
                }
            ],
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                "https://qianfan.baidubce.com/v2/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 千帆v2 API調用成功！")
                print(f"響應: {result.get('choices', [{}])[0].get('message', {}).get('content', '無響應內容')}")
                return True
            else:
                print(f"❌ 千帆v2 API調用失败: {response.status_code}")
                print(f"錯誤信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 千帆v2 API請求異常: {e}")
            
        # 方法2: 嘗試傳統API (需要獲取access_token)
        if not api_key and access_key and secret_key:
            print("\n測試千帆傳統API...")
            
            # 獲取access_token
            token_url = "https://aip.baidubce.com/oauth/2.0/token"
            token_params = {
                "grant_type": "client_credentials",
                "client_id": access_key,
                "client_secret": secret_key
            }
            
            try:
                token_response = requests.post(token_url, params=token_params, timeout=30)
                
                if token_response.status_code == 200:
                    token_data = token_response.json()
                    access_token = token_data.get("access_token")
                    
                    if access_token:
                        print("✅ 獲取access_token成功")
                        
                        # 調用聊天API
                        chat_url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-speed-8k?access_token={access_token}"
                        
                        chat_data = {
                            "messages": [
                                {
                                    "role": "user",
                                    "content": "你好，請簡單介紹一下你自己"
                                }
                            ],
                            "temperature": 0.1
                        }
                        
                        chat_response = requests.post(
                            chat_url,
                            headers={"Content-Type": "application/json"},
                            json=chat_data,
                            timeout=30
                        )
                        
                        if chat_response.status_code == 200:
                            chat_result = chat_response.json()
                            print("✅ 千帆傳統API調用成功！")
                            print(f"響應: {chat_result.get('result', '無響應內容')}")
                            return True
                        else:
                            print(f"❌ 千帆傳統API調用失败: {chat_response.status_code}")
                            print(f"錯誤信息: {chat_response.text}")
                    else:
                        print("❌ 未能獲取access_token")
                        print(f"響應: {token_data}")
                else:
                    print(f"❌ 獲取access_token失败: {token_response.status_code}")
                    print(f"錯誤信息: {token_response.text}")
                    
            except Exception as e:
                print(f"❌ 千帆傳統API請求異常: {e}")
        else:
            print("\n跳過傳統API測試（使用新API Key或缺少AK/SK）")
            
        return False
        
    except ImportError:
        print("❌ requests庫未安裝")
        return False
    except Exception as e:
        print(f"❌ HTTP請求測試失败: {e}")
        return False

def main():
    """主函數"""
    print("千帆API原生連通性測試")
    print("=" * 50)
    
    # 檢查環境變量
    api_key = os.getenv('QIANFAN_API_KEY')
    access_key = os.getenv('QIANFAN_ACCESS_KEY')
    secret_key = os.getenv('QIANFAN_SECRET_KEY')
    
    if not api_key and (not access_key or not secret_key):
        print("❌ 請確保在.env文件中設置了以下環境變量之一:")
        print("   方式1 (推薦): QIANFAN_API_KEY=your_api_key")
        print("   方式2 (傳統): QIANFAN_ACCESS_KEY=your_access_key + QIANFAN_SECRET_KEY=your_secret_key")
        return
    
    # 測試方法1: 使用千帆官方SDK
    sdk_success = test_qianfan_with_sdk()
    
    # 測試方法2: 使用HTTP請求
    http_success = test_qianfan_with_requests()
    
    print("\n=== 測試結果汇总 ===")
    print(f"千帆SDK測試: {'✅ 成功' if sdk_success else '❌ 失败'}")
    print(f"HTTP API測試: {'✅ 成功' if http_success else '❌ 失败'}")
    
    if sdk_success or http_success:
        print("\n🎉 千帆API連通性正常！")
    else:
        print("\n❌ 千帆API連通性測試失败，請檢查密鑰配置")

if __name__ == "__main__":
    main()