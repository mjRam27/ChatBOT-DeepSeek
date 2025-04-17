from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse
import httpx
from pymongo import MongoClient
from dotenv import load_dotenv
from PIL import Image
import speech_recognition as sr
import pytesseract
import io
import os

load_dotenv()

app = FastAPI()

# Environment variables
OPENROUTER_API_KEY = os.getenv("DEEPSEEK_API_KEY")

print("🔐 Loaded API Key:", "Found ✅" if OPENROUTER_API_KEY else "Not Found ❌")

mongo_uri = os.getenv("MONGODB_URI")

# MongoDB setup
client = MongoClient(mongo_uri)
db = client["chatbot_db"]
collection = db["deepseek_messages"]

# Middleware to handle CORS
@app.post("/chat")
async def chat_with_deepseek(request: Request):
    try:
        data = await request.json()
        user_input = data["message"]

        # 🔐 Debug print
        print("🔐 Loaded API Key:", "✅ Found" if OPENROUTER_API_KEY else "❌ Not Found")

        if not OPENROUTER_API_KEY:
            return {"error": "API key is missing. Please check your .env setup."}

        async with httpx.AsyncClient() as client_http:
            response = await client_http.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    # "Authorization": "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",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8001",  # Or your frontend URL
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

            # 💾 Save to MongoDB
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
async def extract_text_and_chat(file: UploadFile = File(...)):
    try:
        # 1. Read and convert image to text
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        extracted_text = pytesseract.image_to_string(image).strip()

        # 2. Check for API key
        if not OPENROUTER_API_KEY:
            return {"error": "API key is missing. Please check your .env setup."}

        # 3. Send extracted text to OpenRouter model
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
                    "messages": [{"role": "user", "content": extracted_text}]
                }
            )

        result = response.json()
        print("📩 OCR Chat Response:", result)

        if "choices" in result and result["choices"]:
            return {
                "extracted_text": extracted_text,
                "response": result["choices"][0]["message"]["content"]
            }
        else:
            return {"error": result.get("error", {}).get("message", "No valid response.")}

    except Exception as e:
        print("❌ OCR Chat Error:", e)
        return {"error": "Could not process image or response"}


@app.post("/speech-to-text")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_path = f"temp_{file.filename}"

        with open(file_path, "wb") as f:
            f.write(contents)

        # Transcribe audio
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)

        transcript = recognizer.recognize_google(audio)

        os.remove(file_path)

        # Check for API key
        if not OPENROUTER_API_KEY:
            return {"error": "API key is missing. Please check your .env setup."}

        # Send transcription to model
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8001",
                    "X-Title": "Chatbot DeepSeek",
                },
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [{"role": "user", "content": transcript}],
                },
            )

        result = response.json()
        print("🧠 Speech Response:", result)

        if "choices" in result and result["choices"]:
            return {
                "transcription": transcript,
                "response": result["choices"][0]["message"]["content"]
            }
        else:
            return {"transcription": transcript, "error": "No valid response from model"}

    except Exception as e:
        print("❌ Speech-to-Text Error:", e)
        return {"error": "Could not process audio"}




@app.post("/speech-to-text-mic")
async def mic_to_text():
    try:
        transcript = convert_microphone_to_text()

        if not OPENROUTER_API_KEY:
            return {"error": "API key is missing. Please check your .env setup."}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "http://localhost:8001",
                    "X-Title": "Chatbot DeepSeek"
                },
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [{"role": "user", "content": transcript}]
                }
            )

        result = response.json()
        print("🧠 Mic Response:", result)

        if "choices" in result and result["choices"]:
            return {
                "transcription": transcript,
                "response": result["choices"][0]["message"]["content"]
            }

        return {"transcription": transcript, "error": "No valid response from model"}

    except Exception as e:
        print("❌ Mic Speech-to-Text Error:", e)
        return {"error": "Could not capture or process microphone audio"}
