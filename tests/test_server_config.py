#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試數據服務器配置功能
"""

from enhanced_stock_list_fetcher import load_tdx_servers_config, get_mainmarket_ip
import json

def test_server_config():
    """測試服務器配置加載功能"""
    print("=== 測試數據服務器配置功能 ===")
    
    # 測試加載服務器配置
    print("\n1. 測試加載服務器配置:")
    servers = load_tdx_servers_config()
    print(f"✅ 成功加載 {len(servers)} 個服務器配置")
    
    # 顯示前5個服務器
    print("\n前5個服務器配置:")
    for i, server in enumerate(servers[:5]):
        print(f"  {i+1}. {server.get('name', '未命名')} - {server['ip']}:{server['port']}")
    
    # 測試獲取主市場IP
    print("\n2. 測試獲取主市場IP:")
    for i in range(3):
        ip, port = get_mainmarket_ip()
        print(f"  第{i+1}次隨機選擇: {ip}:{port}")
    
    # 測試指定IP和端口
    print("\n3. 測試指定IP和端口:")
    ip, port = get_mainmarket_ip('192.168.1.1', 8888)
    print(f"  指定IP和端口: {ip}:{port}")
    
    # 顯示完整的服務器配置信息
    print("\n4. 完整服務器配置信息:")
    print(json.dumps(servers, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_server_config()