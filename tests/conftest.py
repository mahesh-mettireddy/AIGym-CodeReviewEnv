import os
import sys

# Ensure the project root is in sys.path so that 'server' and 'models' can be imported.
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set dummy API key for offline testing without OpenAI errors
os.environ["OPENAI_API_KEY"] = "sk-dummy-test-key-12345"
