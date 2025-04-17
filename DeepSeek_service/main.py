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
async def extract_text_from_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        extracted_text = pytesseract.image_to_string(image)

        return {"extracted_text": extracted_text.strip()}
    except Exception as e:
        print("❌ OCR Error:", e)
        return {"error": "Could not extract text from image."}


# Function to convert uploaded audio file to text
def convert_speech_to_text(audio_path: str) -> str:
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except sr.RequestError as e:
        return f"Request error: {e}"


# Function to convert mic input to text
def convert_microphone_to_text() -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Speak now...")
        audio = recognizer.listen(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except sr.RequestError as e:
        return f"Request error: {e}"



# POST /speech-to-text – Convert uploaded audio file to text
@app.post("/speech-to-text")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        file_path = f"temp_{file.filename}"

        with open(file_path, "wb") as f:
            f.write(contents)

        transcript = convert_speech_to_text(file_path)
        os.remove(file_path)

        return {"transcription": transcript}

    except Exception as e:
        print("❌ Speech-to-Text Error:", e)
        return {"error": "Could not process audio"}


# POST /speech-to-text-mic – Convert live mic input to text (local use only)
@app.post("/speech-to-text-mic")
async def mic_to_text():
    try:
        transcript = convert_microphone_to_text()
        return {"transcription": transcript}
    except Exception as e:
        print("❌ Mic Speech-to-Text Error:", e)
        return {"error": "Could not capture or process microphone audio"}


