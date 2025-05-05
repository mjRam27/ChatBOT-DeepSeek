# Use official Python base image
FROM python:3.9

# Install tesseract + ffmpeg (needed by pydub for audio processing)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ffmpeg

# Set working directory
WORKDIR /app

# Copy all project files including .env
COPY . .

# Debug: Check if .env copied
RUN ls -la .env

# Install Python dependencies
RUN pip install --no-cache-dir fastapi uvicorn httpx pymongo python-dotenv pillow pytesseract python-multipart speechrecognition pydub

# Set Python path for proper module resolution
ENV PYTHONPATH=/app

# Start FastAPI app on port 8001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
