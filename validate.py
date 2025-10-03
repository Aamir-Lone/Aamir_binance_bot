#!/usr/bin/env python3
"""
Validation script to check project setup and configuration
Run this before using the bot to ensure everything is configured correctly
"""
import sys
import os

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print("🐍 Python Version Check...")
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def check_dependencies():
    """Check required packages"""
    print("\n📦 Dependencies Check...")
    required = {
        'requests': 'HTTP client for API calls',
        'dotenv': 'Environment variable management'
    }
    
    all_ok = True
    for package, description in required.items():
        try:
            if package == 'dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"   ✅ {package} - {description}")
        except ImportError:
            print(f"   ❌ {package} - {description} (NOT INSTALLED)")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check .env file configuration"""
    print("\n⚙️  Configuration Check...")
    
    if not os.path.exists('.env'):
        print("   ❌ .env file not found")
        print("   💡 Copy .env.example to .env and configure your API keys")
        return False
    
    print("   ✅ .env file exists")
    
    # Try to load configuration
    try:
        from src.config import API_KEY, API_SECRET, TESTNET
        
        if not API_KEY or API_KEY == 'your_api_key_here':
            print("   ⚠️  API_KEY not configured")
            print("   💡 Add your Binance API key to .env file")
            return False
        else:
            print(f"   ✅ API_KEY configured (length: {len(API_KEY)})")
        
        if not API_SECRET or API_SECRET == 'your_api_secret_here':
            print("   ⚠️  API_SECRET not configured")
            print("   💡 Add your Binance API secret to .env file")
            return False
        else:
            print(f"   ✅ API_SECRET configured (length: {len(API_SECRET)})")
        
        if TESTNET:
            print("   🧪 Mode: TESTNET (Safe for testing)")
        else:
            print("   ⚠️  Mode: LIVE (Real money - be careful!)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error loading configuration: {str(e)}")
        return False

def check_file_structure():
    """Check project file structure"""
    print("\n📁 File Structure Check...")
    
    required_files = {
        'src/config.py': 'Configuration module',
        'src/constants.py': 'Constants and enums',
        'src/utils.py': 'Utility functions',
        'src/market_orders.py': 'Market orders',
        'src/limit_orders.py': 'Limit orders',
        'src/advanced/stop_limit.py': 'Stop-limit orders',
        'src/advanced/oco.py': 'OCO orders',
        'src/advanced/twap.py': 'TWAP strategy',
        'src/advanced/grid_orders.py': 'Grid trading',
        'bot.py': 'Interactive CLI',
        'requirements.txt': 'Dependencies',
        'README.md': 'Documentation'
    }
    
    all_ok = True
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"   ✅ {file} - {description}")
        else:
            print(f"   ❌ {file} - {description} (MISSING)")
            all_ok = False
    
    return all_ok

def check_api_connection():
    """Test API connection (optional, only if configured)"""
    print("\n🌐 API Connection Check...")
    
    try:
        from src.config import API_KEY, TESTNET
        
        if not API_KEY or API_KEY == 'your_api_key_here':
            print("   ⏭️  Skipping (API not configured)")
            return True
        
        from src.utils import get_symbol_price
        
        print("   🔍 Testing connection to Binance...")
        price = get_symbol_price('BTCUSDT')
        print(f"   ✅ Connection OK - BTC Price: ${price:,.2f}")
        
        if TESTNET:
            print("   ℹ️  Connected to TESTNET")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        print("   💡 Check your API keys and internet connection")
        return False

def check_logs():
    """Check logging setup"""
    print("\n📝 Logging Check...")
    
    try:
        from src.utils import logger
        
        # Test log write
        logger.info("Validation script test log entry")
        
        if os.path.exists('bot.log'):
            print("   ✅ Logging configured - bot.log exists")
            size = os.path.getsize('bot.log')
            print(f"   ℹ️  Log file size: {size} bytes")
        else:
            print("   ✅ Logging configured - bot.log will be created")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Logging error: {str(e)}")
        return False

def print_summary(results):
    """Print validation summary"""
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {check}")
    
    print("="*60)
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to use the bot.")
        print("\n📚 Next steps:")
        print("   1. Review README.md for usage instructions")
        print("   2. Try: python bot.py (interactive mode)")
        print("   3. Or use CLI: python src/market_orders.py BTCUSDT BUY 0.001")
        return True
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\n💡 Quick fixes:")
        if not results.get('Dependencies'):
            print("   • Install dependencies: pip install -r requirements.txt")
        if not results.get('Configuration'):
            print("   • Configure .env: cp .env.example .env (then edit)")
            print("   • Get testnet keys: https://testnet.binancefuture.com/")
        return False

def main():
    """Run all validation checks"""
    print("\n" + "="*60)
    print("BINANCE FUTURES BOT - VALIDATION SCRIPT")
    print("="*60)
    
    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'File Structure': check_file_structure(),
        'Configuration': check_env_file(),
        'Logging': check_logs(),
        'API Connection': check_api_connection()
    }
    
    success = print_summary(results)
    
    return 0 if success else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Validation cancelled by user\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}\n")
        sys.exit(1)
