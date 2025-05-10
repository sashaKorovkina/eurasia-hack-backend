from google import genai
from dotenv import load_dotenv
import os

class GeminiClient:
    def __init__(self):
        load_dotenv()

        self.api_key = os.getenv('GEMINI_API_KEY')

        if not self.api_key:
            raise ValueError("API Key not found in environment variables")

        self.client = genai.Client(api_key=self.api_key)

    def get_client(self):
        return self.client