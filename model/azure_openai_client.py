"""
Azure OpenAI LLM handler for text generation.
"""
import openai
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))

class AzureOpenAIClient:
    def __init__(self):
        openai.api_key = os.getenv('AZURE_OPENAI_API_KEY')
        openai.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
    def generate(self, prompt):
        # Dummy: returns prompt for now
        return prompt
