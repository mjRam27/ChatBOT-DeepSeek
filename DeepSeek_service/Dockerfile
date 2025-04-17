# Dockerfile
FROM python:3.9

RUN apt-get update && apt-get install -y tesseract-ocr

WORKDIR /app

# ✅ Copy everything including .env
COPY . .

# ✅ Ensure .env is present in container
RUN ls -la .env

# 🔧 Install dependencies
RUN pip install fastapi uvicorn httpx pymongo python-dotenv pillow pytesseract python-multipart speechrecognition

# 📍 Set Python path
ENV PYTHONPATH=/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
