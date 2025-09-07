import asyncio
import socket
import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from evaluation.run_evaluation import main

def check_server_detailed():
    """Detailed server connectivity check"""
    
    print(" Checking FastAPI server status...")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 8000))
        sock.close()
        
        if result == 0:
            print(" FastAPI server detected on localhost:8000")
            return True
        else:
            print(" No server detected on localhost:8000")
            return False
            
    except Exception as e:
        print(f" Connection check failed: {e}")
        return False

def wait_for_server_startup():
    """Wait for server to start up"""
    
    print(" Waiting for FastAPI server to start...")
    
    for i in range(10):  # Wait up to 10 seconds
        if check_server_detailed():
            print(" Server is ready!")
            return True
        
        print(f"   Attempt {i+1}/10 - waiting 1 second...")
        time.sleep(1)
    
    return False

if __name__ == "__main__":
    print(" FastAPI Medical Referral System - Quantitative Evaluation")
    print("=" * 60)
    
    # Check if server is running
    if not check_server_detailed():
        print("\n SOLUTION STEPS:")
        print("1. Open a NEW terminal window")
        print("2. Navigate to your project directory:")
        print("   cd \"c:\\Users\\kccha\\OneDrive\\Desktop\\Programming\\Language_Agents_raws_projects\\Best_treatment_recommendation_system_in_cases_transi_to_hospi\"")
        print("3. Start FastAPI server:")
        print("   python app.py")
        print("4. Wait for 'Uvicorn running on http://127.0.0.1:8000' message")
        print("5. Come back to this terminal and run evaluation again")
        
        response = input("\nServer not running. Try to wait for startup? (y/N): ")
        
        if response.lower() == 'y':
            if not wait_for_server_startup():
                print(" Server didn't start. Please start it manually and try again.")
                sys.exit(1)
        else:
            sys.exit(0)
    
    print("\n Starting evaluation...")
    asyncio.run(main())