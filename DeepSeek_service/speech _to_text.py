# import speech_recognition as sr

# def convert_speech_to_text(audio_path: str) -> str:
#     recognizer = sr.Recognizer()
#     with sr.AudioFile(audio_path) as source:
#         audio = recognizer.record(source)
#     try:
#         return recognizer.recognize_google(audio)
#     except sr.UnknownValueError:
#         return "Sorry, could not understand the audio."
#     except sr.RequestError as e:
#         return f"Request error: {e}"

# def convert_microphone_to_text() -> str:
#     recognizer = sr.Recognizer()
#     mic = sr.Microphone()
#     with mic as source:
#         print("🎙️ Listening... Speak now.")
#         recognizer.adjust_for_ambient_noise(source)
#         audio = recognizer.listen(source)
#     try:
#         return recognizer.recognize_google(audio)
#     except sr.UnknownValueError:
#         return "Sorry, could not understand what you said."
#     except sr.RequestError as e:
#         return f"Request error: {e}"
