import os
import pytest
from dotenv import load_dotenv

# Load environment variables from the root .env file
# This ensures that OPENAI_API_KEY is available for DeepEval
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(root_dir, ".env")

if os.path.exists(env_path):
    load_dotenv(env_path)

def pytest_configure(config):
    """
    Setup any DeepEval or global pytest configuration here.
    """
    pass
