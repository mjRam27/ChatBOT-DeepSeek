from fastapi import FastAPI, Request
import httpx
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI()

# Load environment variables
OPENROUTER_API_KEY = os.getenv("DEEPSEEK_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

# Setup MongoDB
client = MongoClient(mongo_uri)
db = client["chatbot_db"]
collection = db["deepseek_messages"]

# POST /chat – send message to DeepSeek via OpenRouter and store in Mongo
@app.post("/chat")
async def chat_with_deepseek(request: Request):
    try:
        data = await request.json()
        user_input = data["message"]

        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
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
        print("📩 OpenRouter Response:", result)

        if "choices" in result and result["choices"]:
            message = result["choices"][0]["message"]["content"]

            # Save to MongoDB
            collection.insert_one({
                "input": user_input,
                "response": message
            })

            return {"response": message}
        else:
            return {"error": result.get("error", {}).get("message", "No valid response.")}

    except Exception as e:
        print("Error:", e)
        return {"error": "Something went wrong. Check logs."}

# GET /history – fetch all chat logs
@app.get("/history")
async def get_chat_history():
    try:
        chats = list(collection.find({}, {"_id": 0}))
        return JSONResponse(content=chats)
    except Exception as e:
        print(" Error fetching history:", e)
        return JSONResponse(content={"error": "Could not fetch chat history"}, status_code=500)
