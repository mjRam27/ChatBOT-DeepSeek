import os
import speech_recognition as sr
from dotenv import load_dotenv
from pydub import AudioSegment
from chat import ask_deepseek

# Load environment variables
load_dotenv()

# Convert .webm audio to .wav for compatibility with speech recognition
def convert_webm_to_wav(file_path: str) -> str:
    wav_path = file_path.replace(".webm", ".wav")
    audio = AudioSegment.from_file(file_path, format="webm")
    audio.export(wav_path, format="wav")
    return wav_path

# Transcribe uploaded audio file to text only (no model call)
async def convert_audio_to_text(file) -> str:
    try:
        contents = await file.read()
        path = f"temp_{file.filename}"
        with open(path, "wb") as f:
            f.write(contents)

        if path.endswith(".webm"):
            path = convert_webm_to_wav(path)

        recognizer = sr.Recognizer()
        with sr.AudioFile(path) as source:
            audio = recognizer.record(source)

        transcript = recognizer.recognize_google(audio)
        os.remove(path)

        return transcript

    except sr.UnknownValueError:
        return "Sorry, could not understand the audio."
    except sr.RequestError as e:
        return f"Speech recognition request error: {e}"
    except Exception as e:
        return f"Transcription error: {e}"

# Transcribe audio and send to DeepSeek
async def process_audio_file(file):
    try:
        transcript = await convert_audio_to_text(file)

        if "error" in transcript or transcript.startswith("Sorry"):
            return {"transcription": transcript, "response": None}

        response = await ask_deepseek(transcript)

        return {"transcription": transcript, "response": response}
    except Exception as e:
        return {"error": str(e)}
