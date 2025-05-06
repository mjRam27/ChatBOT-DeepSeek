import os
import httpx
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("DEEPSEEK_API_KEY")
MONGO_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGO_URI)
collection = client["chatbot_db"]["deepseek_messages"]

async def ask_deepseek(user_input: str) -> str:
    async with httpx.AsyncClient() as client_http:
        response = await client_http.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8001",
                "X-Title": "Chatbot DeepSeek"
            },
            json={
                "model": "deepseek/deepseek-r1:free",
                "messages": [{"role": "user", "content": user_input}]
            }
        )
    result = response.json()
    return result["choices"][0]["message"]["content"] if "choices" in result else "No response"

def save_message_to_db(user_input, response):
    collection.insert_one({"input": user_input, "response": response})
