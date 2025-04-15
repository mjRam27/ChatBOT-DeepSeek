FROM python:3.9

# 🧠 Install Tesseract OCR

RUN apt-get update && apt-get install -y tesseract-ocr

# 🛠️ Setup working directory and copy code
WORKDIR /app
COPY . .

# 📦 Install Python dependencies (add python-multipart)
RUN pip install fastapi uvicorn httpx pymongo python-dotenv pillow pytesseract python-multipart

# 🚀 Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
