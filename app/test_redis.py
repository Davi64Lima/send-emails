import os
import redis
import json
from datetime import datetime

def test_redis_connection():
    print("=== Redis Connection Test ===")
    
    # Get Redis configuration
    redis_host = os.getenv('REDIS_HOST', 'queue')
    redis_port = 6379
    redis_db = 0
    
    print(f"Redis Host: {redis_host}")
    print(f"Redis Port: {redis_port}")
    print(f"Redis DB: {redis_db}")
    print()
    
    try:
        # Create Redis connection
        print("Creating Redis connection...")
        r = redis.StrictRedis(
            host=redis_host, 
            port=redis_port, 
            db=redis_db,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connection
        print("Testing connection with PING...")
        result = r.ping()
        print(f"PING result: {result}")
        
        if result:
            print("✅ Redis connection successful!")
            
            # Test basic operations
            print("\nTesting basic operations...")
            
            # Test SET/GET
            r.set('test_key', 'test_value')
            value = r.get('test_key')
            print(f"SET/GET test: {value}")
            
            # Test RPUSH
            test_msg = {
                'data': datetime.utcnow().isoformat(),
                'assunto': 'Test Subject',
                'mensagem': 'Test Message',
                'email': 'test@example.com'
            }
            
            msg_json = json.dumps(test_msg)
            print(f"Message to push: {msg_json}")
            
            result = r.rpush('sender', msg_json)
            print(f"RPUSH result: {result}")
            
            # Test LLEN
            queue_length = r.llen('sender')
            print(f"Queue length: {queue_length}")
            
            # Test LPOP (get one message)
            if queue_length > 0:
                popped_msg = r.lpop('sender')
                print(f"Popped message: {popped_msg}")
            
            print("✅ All Redis operations successful!")
            
        else:
            print("❌ Redis PING failed!")
            
    except redis.ConnectionError as e:
        print(f"❌ Redis Connection Error: {e}")
        print("Possible causes:")
        print("- Redis server is not running")
        print("- Wrong host/port configuration")
        print("- Network connectivity issues")
        
    except redis.TimeoutError as e:
        print(f"❌ Redis Timeout Error: {e}")
        print("Possible causes:")
        print("- Redis server is overloaded")
        print("- Network latency issues")
        
    except Exception as e:
        print(f"❌ Redis Error: {e}")
        print(f"Error type: {type(e)}")

def test_redis_with_connection_pool():
    print("\n=== Redis Connection Pool Test ===")
    
    redis_host = os.getenv('REDIS_HOST', 'queue')
    
    try:
        # Test with connection pool
        pool = redis.ConnectionPool(
            host=redis_host,
            port=6379,
            db=0,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        r = redis.Redis(connection_pool=pool)
        
        # Test connection
        result = r.ping()
        print(f"Connection pool PING result: {result}")
        
        if result:
            print("✅ Redis connection pool successful!")
            
            # Test queue operations
            test_msg = {'test': 'data', 'timestamp': datetime.utcnow().isoformat()}
            r.rpush('test_queue', json.dumps(test_msg))
            
            queue_len = r.llen('test_queue')
            print(f"Test queue length: {queue_len}")
            
            # Clean up
            r.delete('test_queue')
            print("✅ Connection pool test completed!")
            
    except Exception as e:
        print(f"❌ Connection pool error: {e}")

if __name__ == '__main__':
    test_redis_connection()
    test_redis_with_connection_pool() 