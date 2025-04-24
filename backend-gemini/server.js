const express = require('express');
const cors = require('cors');
const multer = require('multer');
const tesseract = require('tesseract.js');
const fs = require('fs');
const path = require('path');
const bodyParser = require('body-parser');

const app = express();
const PORT = 8002;

app.use(cors());
app.use(bodyParser.json());

// OCR: Image to text
const imageUpload = multer({ storage: multer.memoryStorage() });
app.post('/ocr', imageUpload.single('image'), async (req, res) => {
    try {
        const {
            data: { text }
        } = await tesseract.recognize(req.file.buffer, 'eng');
        res.json({ text });
    } catch {
        res.status(500).json({ error: 'OCR failed' });
    }
});

// Speech: Dummy speech-to-text
const audioUpload = multer({ dest: 'uploads/' });
app.post('/speech2text', audioUpload.single('audio'), async (req, res) => {
    const dummyText = "Transcribed speech (Gemini simulated).";
    res.json({ text: dummyText });
    fs.unlinkSync(path.join(__dirname, req.file.path)); // cleanup
});

// Chat: Echo-style Gemini response
app.post('/chat', async (req, res) => {
    const { prompt } = req.body;
    res.json({ response: `Gemini: You said "${prompt}"` });
});

app.listen(PORT, () => {
    console.log(` Gemini backend running at http://localhost:${PORT}`);
});
