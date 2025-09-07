import subprocess
import sys
from pathlib import Path

def install_dependencies():
    """Install evaluation dependencies"""
    
    packages = ["aiohttp>=3.8.0", "psutil>=5.9.0"]
    
    print(" Installing evaluation dependencies...")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f" Installed {package}")
        except subprocess.CalledProcessError:
            print(f" Failed to install {package}")

def create_directories():
    """Create evaluation directories"""
    
    directories = ["evaluation", "evaluation_results"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f" Created {directory}/")

def main():
    print(" Setting up Quantitative Evaluation Framework")
    print("=" * 50)
    
    install_dependencies()
    create_directories()
    
    print("\n Setup complete!")
    print("\nNext steps:")
    print("1. Start your FastAPI server: python app.py")
    print("2. Run evaluation: python -m evaluation.run_evaluation")

if __name__ == "__main__":
    main()