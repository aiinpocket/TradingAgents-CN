#!/usr/bin/env python3
"""
Redis連接和性能測試腳本
"""

import redis
import time
import statistics
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json

class RedisPerformanceTester:
    """Redis性能測試器"""
    
    def __init__(self, host=None, port=None, password=None, db=None):
        # 從環境變量獲取配置，如果没有則使用默認值
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', 6379))
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.db = db or int(os.getenv('REDIS_DATABASE', 0))
        self.redis_client = None
        
    def connect(self):
        """連接到Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 測試連接
            self.redis_client.ping()
            print(f"✅ 成功連接到Redis: {self.host}:{self.port}")
            return True
        except redis.ConnectionError as e:
            print(f"❌ Redis連接失败: {e}")
            return False
        except Exception as e:
            print(f"❌ 連接錯誤: {e}")
            return False
    
    def test_connection_latency(self, iterations=100):
        """測試連接延迟"""
        print(f"\n🔍 測試連接延迟 ({iterations} 次ping測試)...")
        
        latencies = []
        failed_count = 0
        
        for i in range(iterations):
            try:
                start_time = time.time()
                self.redis_client.ping()
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # 轉換為毫秒
                latencies.append(latency)
                
                if (i + 1) % 20 == 0:
                    print(f"  進度: {i + 1}/{iterations}")
                    
            except Exception as e:
                failed_count += 1
                print(f"  第{i+1}次ping失败: {e}")
        
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            median_latency = statistics.median(latencies)
            
            print(f"\n📊 連接延迟統計:")
            print(f"  平均延迟: {avg_latency:.2f} ms")
            print(f"  最小延迟: {min_latency:.2f} ms")
            print(f"  最大延迟: {max_latency:.2f} ms")
            print(f"  中位延迟: {median_latency:.2f} ms")
            print(f"  失败次數: {failed_count}/{iterations}")
            
            return {
                'avg_latency': avg_latency,
                'min_latency': min_latency,
                'max_latency': max_latency,
                'median_latency': median_latency,
                'failed_count': failed_count,
                'success_rate': (iterations - failed_count) / iterations * 100
            }
        else:
            print("❌ 所有ping測試都失败了")
            return None
    
    def test_throughput(self, operations=1000, operation_type='set'):
        """測試吞吐量"""
        print(f"\n🚀 測試{operation_type.upper()}操作吞吐量 ({operations} 次操作)...")
        
        start_time = time.time()
        failed_count = 0
        
        try:
            if operation_type == 'set':
                for i in range(operations):
                    try:
                        self.redis_client.set(f"test_key_{i}", f"test_value_{i}")
                    except Exception:
                        failed_count += 1
                        
            elif operation_type == 'get':
                # 先設置一些測試數據
                for i in range(min(100, operations)):
                    self.redis_client.set(f"test_key_{i}", f"test_value_{i}")
                
                for i in range(operations):
                    try:
                        self.redis_client.get(f"test_key_{i % 100}")
                    except Exception:
                        failed_count += 1
                        
            elif operation_type == 'ping':
                for i in range(operations):
                    try:
                        self.redis_client.ping()
                    except Exception:
                        failed_count += 1
            
            end_time = time.time()
            duration = end_time - start_time
            successful_ops = operations - failed_count
            throughput = successful_ops / duration if duration > 0 else 0
            
            print(f"\n📈 {operation_type.upper()}操作吞吐量統計:")
            print(f"  总操作數: {operations}")
            print(f"  成功操作: {successful_ops}")
            print(f"  失败操作: {failed_count}")
            print(f"  总耗時: {duration:.2f} 秒")
            print(f"  吞吐量: {throughput:.2f} 操作/秒")
            print(f"  平均每操作: {(duration/successful_ops)*1000:.2f} ms")
            
            return {
                'operation_type': operation_type,
                'total_operations': operations,
                'successful_operations': successful_ops,
                'failed_operations': failed_count,
                'duration': duration,
                'throughput': throughput,
                'avg_operation_time': (duration/successful_ops)*1000 if successful_ops > 0 else 0
            }
            
        except Exception as e:
            print(f"❌ 吞吐量測試失败: {e}")
            return None
    
    def test_concurrent_connections(self, num_threads=10, operations_per_thread=100):
        """測試並發連接性能"""
        print(f"\n🔀 測試並發連接性能 ({num_threads} 線程, 每線程 {operations_per_thread} 操作)...")
        
        def worker_task(thread_id):
            """工作線程任務"""
            try:
                # 每個線程創建自己的Redis連接
                client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    decode_responses=True
                )
                
                start_time = time.time()
                failed_count = 0
                
                for i in range(operations_per_thread):
                    try:
                        client.set(f"thread_{thread_id}_key_{i}", f"value_{i}")
                        client.get(f"thread_{thread_id}_key_{i}")
                    except Exception:
                        failed_count += 1
                
                end_time = time.time()
                duration = end_time - start_time
                successful_ops = (operations_per_thread * 2) - failed_count  # set + get
                
                return {
                    'thread_id': thread_id,
                    'duration': duration,
                    'successful_operations': successful_ops,
                    'failed_operations': failed_count,
                    'throughput': successful_ops / duration if duration > 0 else 0
                }
                
            except Exception as e:
                return {
                    'thread_id': thread_id,
                    'error': str(e),
                    'successful_operations': 0,
                    'failed_operations': operations_per_thread * 2
                }
        
        # 執行並發測試
        start_time = time.time()
        results = []
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_task, i) for i in range(num_threads)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                print(f"  線程 {result['thread_id']} 完成")
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 統計結果
        total_successful = sum(r['successful_operations'] for r in results)
        total_failed = sum(r['failed_operations'] for r in results)
        total_operations = total_successful + total_failed
        overall_throughput = total_successful / total_duration if total_duration > 0 else 0
        
        print(f"\n📊 並發測試統計:")
        print(f"  总線程數: {num_threads}")
        print(f"  总操作數: {total_operations}")
        print(f"  成功操作: {total_successful}")
        print(f"  失败操作: {total_failed}")
        print(f"  总耗時: {total_duration:.2f} 秒")
        print(f"  整體吞吐量: {overall_throughput:.2f} 操作/秒")
        print(f"  成功率: {(total_successful/total_operations)*100:.1f}%")
        
        return {
            'num_threads': num_threads,
            'total_operations': total_operations,
            'successful_operations': total_successful,
            'failed_operations': total_failed,
            'total_duration': total_duration,
            'overall_throughput': overall_throughput,
            'success_rate': (total_successful/total_operations)*100,
            'thread_results': results
        }
    
    def test_memory_usage(self):
        """測試Redis內存使用情况"""
        print(f"\n💾 Redis內存使用情况:")
        
        try:
            info = self.redis_client.info('memory')
            
            used_memory = info.get('used_memory', 0)
            used_memory_human = info.get('used_memory_human', 'N/A')
            used_memory_peak = info.get('used_memory_peak', 0)
            used_memory_peak_human = info.get('used_memory_peak_human', 'N/A')
            
            print(f"  當前內存使用: {used_memory_human} ({used_memory} bytes)")
            print(f"  峰值內存使用: {used_memory_peak_human} ({used_memory_peak} bytes)")
            
            return {
                'used_memory': used_memory,
                'used_memory_human': used_memory_human,
                'used_memory_peak': used_memory_peak,
                'used_memory_peak_human': used_memory_peak_human
            }
            
        except Exception as e:
            print(f"❌ 獲取內存信息失败: {e}")
            return None
    
    def run_full_test(self):
        """運行完整的性能測試"""
        print("🧪 開始Redis性能測試...")
        
        if not self.connect():
            return None
        
        results = {}
        
        # 1. 連接延迟測試
        results['latency'] = self.test_connection_latency(100)
        
        # 2. 吞吐量測試
        results['set_throughput'] = self.test_throughput(1000, 'set')
        results['get_throughput'] = self.test_throughput(1000, 'get')
        results['ping_throughput'] = self.test_throughput(1000, 'ping')
        
        # 3. 並發測試
        results['concurrent'] = self.test_concurrent_connections(10, 50)
        
        # 4. 內存使用
        results['memory'] = self.test_memory_usage()
        
        # 清理測試數據
        try:
            self.redis_client.flushdb()
            print("\n🧹 清理測試數據完成")
        except Exception as e:
            print(f"⚠️  清理測試數據失败: {e}")
        
        return results

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="Redis性能測試工具")
    parser.add_argument("--host", default="localhost", help="Redis主機地址")
    parser.add_argument("--port", type=int, default=6379, help="Redis端口")
    parser.add_argument("--password", help="Redis密碼")
    parser.add_argument("--db", type=int, default=0, help="Redis數據庫編號")
    parser.add_argument("--test", choices=['latency', 'throughput', 'concurrent', 'memory', 'all'], 
                       default='all', help="測試類型")
    parser.add_argument("--output", help="結果輸出文件(JSON格式)")
    
    args = parser.parse_args()
    
    tester = RedisPerformanceTester(args.host, args.port, args.password, args.db)
    
    if args.test == 'all':
        results = tester.run_full_test()
    else:
        if not tester.connect():
            return
            
        if args.test == 'latency':
            results = {'latency': tester.test_connection_latency()}
        elif args.test == 'throughput':
            results = {
                'set_throughput': tester.test_throughput(1000, 'set'),
                'get_throughput': tester.test_throughput(1000, 'get')
            }
        elif args.test == 'concurrent':
            results = {'concurrent': tester.test_concurrent_connections()}
        elif args.test == 'memory':
            results = {'memory': tester.test_memory_usage()}
    
    # 保存結果
    if args.output and results:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n💾 測試結果已保存到: {args.output}")
        except Exception as e:
            print(f"❌ 保存結果失败: {e}")
    
    print("\n✅ Redis性能測試完成!")

if __name__ == "__main__":
    main()
