import os
import psycopg2
import redis
from datetime import datetime

def test_environment():
    print("=== Environment Variables ===")
    print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
    print(f"DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
    print(f"DB_PASS: {os.getenv('DB_PASS', 'NOT SET')}")
    print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
    print(f"REDIS_HOST: {os.getenv('REDIS_HOST', 'NOT SET')}")
    print()

def test_database():
    print("=== Database Connection Test ===")
    try:
        dsn = f"dbname={os.getenv('DB_NAME', 'email_sender')} " \
              f"user={os.getenv('DB_USER', 'postgres')} " \
              f"password={os.getenv('DB_PASS', 'postgres')} " \
              f"host={os.getenv('DB_HOST', 'db')}"
        
        print(f"DSN: {dsn}")
        
        with psycopg2.connect(dsn) as conn:
            print("✅ Database connection successful!")
            
            # Test if emails table exists
            with conn.cursor() as cur:
                cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'emails')")
                table_exists = cur.fetchone()[0]
                print(f"Emails table exists: {table_exists}")
                
                if table_exists:
                    # Test insert
                    SQL = 'INSERT INTO emails (data, assunto, mensagem, email) VALUES (%s, %s, %s, %s)'
                    now = datetime.utcnow()
                    cur.execute(SQL, (now, 'test', 'test message', 'test@test.com'))
                    conn.commit()
                    print("✅ Database insert test successful!")
                else:
                    print("❌ Emails table does not exist!")
                    
    except Exception as e:
        print(f"❌ Database error: {e}")
    print()

def test_redis():
    print("=== Redis Connection Test ===")
    try:
        redis_host = os.getenv('REDIS_HOST', 'queue')
        print(f"Redis host: {redis_host}")
        
        fila = redis.StrictRedis(host=redis_host, port=6379, db=0)
        
        # Test connection
        fila.ping()
        print("✅ Redis connection successful!")
        
        # Test push
        test_msg = {'data': datetime.utcnow().isoformat(), 'assunto': 'test', 'mensagem': 'test', 'email': 'test@test.com'}
        import json
        fila.rpush('sender', json.dumps(test_msg))
        print("✅ Redis push test successful!")
        
    except Exception as e:
        print(f"❌ Redis error: {e}")
    print()

if __name__ == '__main__':
    test_environment()
    test_database()
    test_redis() 