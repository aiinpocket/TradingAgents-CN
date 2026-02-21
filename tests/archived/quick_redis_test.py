#!/usr/bin/env python3
"""
Redis快速連接測試指令碼
"""

import redis
import time
import sys

def quick_redis_test(host=None, port=None, password=None):
    """快速Redis連接和性能測試"""
    
    # 從環境變數取得配置
    host = host or os.getenv('REDIS_HOST', 'localhost')
    port = port or int(os.getenv('REDIS_PORT', 6379))
    password = password or os.getenv('REDIS_PASSWORD')
    
    print(f" 測試Redis連接: {host}:{port}")
    
    try:
        # 建立Redis連接
        start_time = time.time()
        r = redis.Redis(
            host=host, 
            port=port, 
            password=password,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # 測試連接
        r.ping()
        connect_time = (time.time() - start_time) * 1000
        print(f" 連接成功! 連接時間: {connect_time:.2f} ms")
        
        # 測試基本操作延遲
        print("\n 基本操作延遲測試:")
        
        # SET操作測試
        start_time = time.time()
        r.set("test_key", "test_value")
        set_time = (time.time() - start_time) * 1000
        print(f"  SET操作: {set_time:.2f} ms")
        
        # GET操作測試
        start_time = time.time()
        value = r.get("test_key")
        get_time = (time.time() - start_time) * 1000
        print(f"  GET操作: {get_time:.2f} ms")
        
        # PING操作測試
        ping_times = []
        for i in range(10):
            start_time = time.time()
            r.ping()
            ping_time = (time.time() - start_time) * 1000
            ping_times.append(ping_time)
        
        avg_ping = sum(ping_times) / len(ping_times)
        min_ping = min(ping_times)
        max_ping = max(ping_times)
        
        print(f"  PING操作 (10次平均): {avg_ping:.2f} ms")
        print(f"  PING最小/最大: {min_ping:.2f} / {max_ping:.2f} ms")
        
        # 簡單吞吐量測試
        print("\n 簡單吞吐量測試 (100次操作):")
        
        start_time = time.time()
        for i in range(100):
            r.set(f"throughput_test_{i}", f"value_{i}")
        set_duration = time.time() - start_time
        set_throughput = 100 / set_duration
        
        start_time = time.time()
        for i in range(100):
            r.get(f"throughput_test_{i}")
        get_duration = time.time() - start_time
        get_throughput = 100 / get_duration
        
        print(f"  SET吞吐量: {set_throughput:.2f} 操作/秒")
        print(f"  GET吞吐量: {get_throughput:.2f} 操作/秒")
        
        # 清理測試資料
        r.delete("test_key")
        for i in range(100):
            r.delete(f"throughput_test_{i}")
        
        # 連接資訊
        print(f"\n Redis 伺服器資訊:")
        info = r.info()
        print(f"  Redis版本: {info.get('redis_version', 'N/A')}")
        print(f"  執行模式: {info.get('redis_mode', 'N/A')}")
        print(f"  已連接客戶端: {info.get('connected_clients', 'N/A')}")
        print(f"  記憶體使用: {info.get('used_memory_human', 'N/A')}")
        
        return True
        
    except redis.ConnectionError as e:
        print(f" Redis連接失敗: {e}")
        return False
    except redis.TimeoutError as e:
        print(f" Redis連接超時: {e}")
        return False
    except Exception as e:
        print(f" 測試過程中出錯: {e}")
        return False

def main():
    """主函式"""
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = 'localhost'
    
    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = 6379
    
    if len(sys.argv) > 3:
        password = sys.argv[3]
    else:
        password = None
    
    success = quick_redis_test(host, port, password)
    
    if success:
        print("\n Redis連接測試完成!")
    else:
        print("\n Redis連接測試失敗!")
        sys.exit(1)

if __name__ == "__main__":
    main()
