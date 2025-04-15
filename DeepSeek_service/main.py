from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
import httpx
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image
import pytesseract
import io
import os

load_dotenv()

app = FastAPI()

# Environment variables
OPENROUTER_API_KEY = os.getenv("DEEPSEEK_API_KEY")
mongo_uri = os.getenv("MONGODB_URI")

# MongoDB setup
client = MongoClient(mongo_uri)
db = client["chatbot_db"]
collection = db["deepseek_messages"]

# POST /chat – Send user message to DeepSeek and store response
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

            # Save chat to MongoDB
            collection.insert_one({
                "input": user_input,
                "response": message
            })

            return {"response": message}
        else:
            return {"error": result.get("error", {}).get("message", "No valid response.")}

    except Exception as e:
        print("❌ Chat Error:", e)
        return {"error": "Something went wrong. Check logs."}

# GET /history – Return chat history
@app.get("/history")
async def get_chat_history():
    try:
        chats = list(collection.find({}, {"_id": 0}))
        return JSONResponse(content=chats)
    except Exception as e:
        print("❌ History Error:", e)
        return JSONResponse(content={"error": "Could not fetch chat history"}, status_code=500)

# POST /ocr – Extract text from uploaded image
@app.post("/ocr")
async def extract_text_from_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        extracted_text = pytesseract.image_to_string(image)

        return {"extracted_text": extracted_text.strip()}
    except Exception as e:
        print("❌ OCR Error:", e)
        return {"error": "Could not extract text from image."}
