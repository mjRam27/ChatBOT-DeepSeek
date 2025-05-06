import pytesseract
from PIL import Image
import io
from chat import ask_deepseek

async def handle_ocr_with_deepseek(file):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        extracted_text = pytesseract.image_to_string(image).strip()

        response = await ask_deepseek(extracted_text)

        return {
            "extracted_text": extracted_text,
            "response": response
        }
    except Exception as e:
        return {"error": str(e)}
