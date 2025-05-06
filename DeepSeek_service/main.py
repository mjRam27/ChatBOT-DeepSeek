from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from chat import ask_deepseek, save_message_to_db
from ocr import handle_ocr_with_deepseek
from speech import process_audio_file, convert_audio_to_text

import os

load_dotenv()

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chat endpoint
@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("message")
    response = await ask_deepseek(user_input)
    save_message_to_db(user_input, response)
    return {"response": response}

# OCR endpoint
@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    return await handle_ocr_with_deepseek(file)

# Full speech-to-text + chat
@app.post("/speech2text")
async def speech_to_text_endpoint(file: UploadFile = File(...)):
    return await process_audio_file(file)  # handles transcription + deepseek

# Only transcription (for mic input preview)
@app.post("/transcribe")
async def transcribe_only(file: UploadFile = File(...)):
    transcript = await convert_audio_to_text(file)
    return {"transcription": transcript}
