#!/usr/bin/env python3
"""
Easy launcher script for the RAG Chatbot application.
This script performs system checks and starts the application.
"""

import os
import sys
import subprocess
import requests
import time
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_colored(message: str, color: str = Colors.END):
    """Print colored message to terminal."""
    print(f"{color}{message}{Colors.END}")


def print_header():
    """Print application header."""
    print_colored("="*60, Colors.CYAN)
    print_colored("🤖 RAG CHATBOT - PRODUCTION LAUNCHER", Colors.BOLD + Colors.BLUE)
    print_colored("भाषा-स्मार्ट RAG चैटबॉट | Language-Smart RAG Chatbot", Colors.CYAN)
    print_colored("="*60, Colors.CYAN)
    print()


def check_python_version():
    """Check if Python version is compatible."""
    print_colored("🐍 Checking Python version...", Colors.BLUE)
    
    if sys.version_info < (3, 8):
        print_colored("❌ Python 3.8+ required. Current version: " + sys.version, Colors.RED)
        return False
    
    print_colored(f"✅ Python {sys.version.split()[0]} - OK", Colors.GREEN)
    return True


def check_dependencies():
    """Check if required dependencies are installed."""
    print_colored("📦 Checking dependencies...", Colors.BLUE)
    
    required_packages = [
        'streamlit',
        'langchain',
        'langchain_community',
        'chromadb',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_colored(f"✅ {package}", Colors.GREEN)
        except ImportError:
            print_colored(f"❌ {package} - Missing", Colors.RED)
            missing_packages.append(package)
    
    if missing_packages:
        print_colored("\n📥 Install missing packages:", Colors.YELLOW)
        print_colored(f"pip install {' '.join(missing_packages)}", Colors.CYAN)
        return False
    
    return True


def check_environment():
    """Check environment configuration."""
    print_colored("🔧 Checking environment configuration...", Colors.BLUE)
    
    # Check for .env file
    env_file = Path('.env')
    if env_file.exists():
        print_colored("✅ .env file found", Colors.GREEN)
        # Load .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print_colored("⚠️  python-dotenv not installed, using system environment", Colors.YELLOW)
    else:
        print_colored("⚠️  .env file not found, using system environment", Colors.YELLOW)
    
    # Check Groq API key
    groq_key = os.getenv('GROQ_API_KEY')
    if not groq_key or groq_key == 'your_groq_api_key_here':
        print_colored("❌ GROQ_API_KEY not configured", Colors.RED)
        print_colored("   Get your key from: https://console.groq.com", Colors.CYAN)
        print_colored("   Set: export GROQ_API_KEY=your_key_here", Colors.CYAN)
        return False
    else:
        print_colored("✅ GROQ_API_KEY configured", Colors.GREEN)
    
    return True


def check_ollama():
    """Check if Ollama is running and model is available."""
    print_colored("🦙 Checking Ollama...", Colors.BLUE)
    
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    try:
        # Check if Ollama server is running
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            print_colored("✅ Ollama server is running", Colors.GREEN)
            
            # Check if required model is available
            models = response.json().get('models', [])
            model_name = os.getenv('OLLAMA_MODEL', 'nomic-embed-text')
            
            model_found = any(model['name'].startswith(model_name) for model in models)
            
            if model_found:
                print_colored(f"✅ Model '{model_name}' is available", Colors.GREEN)
                return True
            else:
                print_colored(f"❌ Model '{model_name}' not found", Colors.RED)
                print_colored(f"   Install with: ollama pull {model_name}", Colors.CYAN)
                return False
        else:
            print_colored("❌ Ollama server responded with error", Colors.RED)
            return False
            
    except requests.exceptions.ConnectionError:
        print_colored("❌ Cannot connect to Ollama server", Colors.RED)
        print_colored("   Start with: ollama serve", Colors.CYAN)
        return False
    except Exception as e:
        print_colored(f"❌ Ollama check failed: {str(e)}", Colors.RED)
        return False


def create_directories():
    """Create necessary directories."""
    print_colored("📁 Creating directories...", Colors.BLUE)
    
    directories = [
        './chroma_db',
        './logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_colored(f"✅ {directory}", Colors.GREEN)


def run_health_check():
    """Run comprehensive health check."""
    print_colored("🏥 Running health check...", Colors.BLUE)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Ollama", check_ollama)
    ]
    
    failed_checks = []
    
    for check_name, check_func in checks:
        print_colored(f"\n--- {check_name} ---", Colors.YELLOW)
        if not check_func():
            failed_checks.append(check_name)
    
    print_colored("\n" + "="*40, Colors.CYAN)
    
    if failed_checks:
        print_colored("❌ HEALTH CHECK FAILED", Colors.RED + Colors.BOLD)
        print_colored(f"Failed checks: {', '.join(failed_checks)}", Colors.RED)
        print_colored("\nPlease fix the issues above before running the application.", Colors.YELLOW)
        return False
    else:
        print_colored("✅ ALL CHECKS PASSED", Colors.GREEN + Colors.BOLD)
        return True


def start_application():
    """Start the Streamlit application."""
    print_colored("\n🚀 Starting RAG Chatbot...", Colors.BLUE + Colors.BOLD)
    
    # Create directories
    create_directories()
    
    # Set environment variables for Streamlit
    env = os.environ.copy()
    env.update({
        'STREAMLIT_SERVER_HEADLESS': 'true',
        'STREAMLIT_SERVER_PORT': os.getenv('STREAMLIT_SERVER_PORT', '8501'),
        'STREAMLIT_SERVER_ADDRESS': os.getenv('STREAMLIT_SERVER_ADDRESS', 'localhost'),
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false'
    })
    
    try:
        # Start Streamlit
        cmd = [sys.executable, '-m', 'streamlit', 'run', 'main.py']
        
        print_colored(f"Command: {' '.join(cmd)}", Colors.CYAN)
        print_colored("Press Ctrl+C to stop the application", Colors.YELLOW)
        print_colored("-" * 40, Colors.CYAN)
        
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print_colored("\n\n👋 Application stopped by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\n❌ Failed to start application: {str(e)}", Colors.RED)


def show_quick_setup():
    """Show quick setup instructions."""
    print_colored("\n🔧 QUICK SETUP GUIDE", Colors.YELLOW + Colors.BOLD)
    print_colored("-" * 30, Colors.CYAN)
    
    print_colored("1. Install dependencies:", Colors.BLUE)
    print_colored("   pip install -r requirements.txt", Colors.CYAN)
    
    print_colored("\n2. Set up Groq API:", Colors.BLUE)
    print_colored("   - Get key from: https://console.groq.com", Colors.CYAN)
    print_colored("   - Set: export GROQ_API_KEY=your_key_here", Colors.CYAN)
    
    print_colored("\n3. Install and start Ollama:", Colors.BLUE)
    print_colored("   - Install from: https://ollama.ai", Colors.CYAN)
    print_colored("   - ollama pull nomic-embed-text", Colors.CYAN)
    print_colored("   - ollama serve", Colors.CYAN)
    
    print_colored("\n4. Run application:", Colors.BLUE)
    print_colored("   python run.py", Colors.CYAN)


def main():
    """Main function."""
    print_header()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--setup':
            show_quick_setup()
            return
        elif sys.argv[1] == '--health':
            run_health_check()
            return
        elif sys.argv[1] == '--help':
            print_colored("Usage:", Colors.BLUE)
            print_colored("  python run.py          # Run health check and start app", Colors.CYAN)
            print_colored("  python run.py --health # Run health check only", Colors.CYAN)
            print_colored("  python run.py --setup  # Show setup instructions", Colors.CYAN)
            print_colored("  python run.py --help   # Show this help", Colors.CYAN)
            return
    
    # Run health check
    if run_health_check():
        # Ask user to continue
        print_colored("\n" + "="*40, Colors.CYAN)
        response = input("🚀 Start the application? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            start_application()
        else:
            print_colored("👋 Goodbye!", Colors.YELLOW)
    else:
        print_colored("\n💡 Run 'python run.py --setup' for setup instructions", Colors.BLUE)


if __name__ == "__main__":
    main()