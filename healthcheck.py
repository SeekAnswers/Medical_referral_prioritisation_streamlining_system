import requests
import sys

def health_check():
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("Health check passed")
            sys.exit(0)
        else:
            print(f"Health check failed: {response.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"Health check error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    health_check()