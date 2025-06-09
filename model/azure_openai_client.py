"""
Azure OpenAI LLM handler for text generation.
"""
import openai
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../config/.env'))



class AzureOpenAIClient:
    def __init__(self):
        self.client = openai.AzureOpenAI(
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION')
        )

    def generate(self, prompt, max_tokens=1024, temperature=0.2):
        deployment = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
        try:
            response = self.client.chat.completions.create(
                model=deployment,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[AzureOpenAIClient] Error: {e}")
            return "[LLM Error: Unable to generate response]"
