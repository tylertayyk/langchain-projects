import sys
import os
from dotenv import load_dotenv

def check_python_version():
    "Verify Python version is compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f" ☑ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"X Python {version.major}.{version.minor}.{version.micro} - Need 3.9+")
        return False

def check_dependencies():
    """Verify core dependencies are installed"""
    dependencies = [
    'langchain',
    'langchain_community',
    'langgraph',
    'langchain_openai',
    'streamlit',
    'chromadb']
    all_good = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f" {dep}")
        except ImportError:
            print(f" X {dep} - Run: pip install {dep}")
            all_good = False
    return all_good

def check_environment():
    """Verify environment variables are set"""
    load_dotenv()
    required_vars = ['OPENAI_API_KEY']
    optional_vars = ['ANTHROPIC_API_KEY', 'GOOGLE_API_KEY', 'LANGCHAIN_API_KEY']
    all_required = True
    for var in required_vars:
        if os.getenv(var):
            print(f" {var}")
        else:
            print(f" X {var} - Add to .env file")
            all_required = False
    for var in optional_vars:
        if os.getenv(var):
            print(f" {var} (optional)")
        else:
            print(f"A {var} (optional) - Add to .env file for full functionality")
    return all_required

def test_basic_functionality():
    """Test basic LangChain functionality"""
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage
        # Only test if API key is available
        if not os.getenv('OPENAI_API_KEY'):
            print("ASkipping API test - no OpenAI API key")
            return True
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        response = llm.invoke([HumanMessage(content="Hello! Respond with just 'Setup verified.'")])
        if "Setup verified" in response.content:
            print(" LangChain API integration working")
            return True
        else:
            print("A LangChain API test gave unexpected response")
            return False
    except Exception as e:
        print(f" X LangChain API test failed: {e}")
        return False

if __name__ == '__main__':
    print('Verifying LangChain Book Environment Setup\n')
    checks = [
        ('Python Version', check_python_version),
        ('Dependencies', check_dependencies),
        ('Environment Variables', check_environment),
        ('Basic Functionality', test_basic_functionality)
    ]
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_passed = False
    print(f"\n{' Setup Complete!' if all_passed else' Setup Issues Found'}")
    print("\nYou're ready to start building with LangChain!" if all_passed else
          "\nPlease resolve the issues above before continuing.")
