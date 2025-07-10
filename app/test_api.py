import requests
import json

def test_api():
    url = "http://localhost:8080/api"
    
    # Test data
    data = {
        'assunto': 'Test Subject',
        'mensagem': 'This is a test message',
        'email': 'test@example.com'
    }
    
    print("=== Testing API Endpoint ===")
    print(f"URL: {url}")
    print(f"Data: {data}")
    print()
    
    try:
        # Test POST request
        response = requests.post(url, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("✅ API test successful!")
        else:
            print("❌ API test failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def test_index():
    url = "http://localhost:8080/"
    
    print("\n=== Testing Index Endpoint ===")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Index test successful!")
        else:
            print("❌ Index test failed!")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

if __name__ == '__main__':
    test_index()
    test_api() 