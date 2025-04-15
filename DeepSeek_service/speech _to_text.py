import speech_recognition as sr

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
