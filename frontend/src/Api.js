import axios from 'axios';



// DeepSeek Endpoints
const DEEPSEEK_BASE = 'http://localhost:8001'; // Example port for DeepSeek

// Use model = 'gemini' or 'deepseek'
const GEMINI_BASE = 'http://localhost:8002'; // ✅ Gemini backend

export const fetchChatResponse = async (text) => {
    try {
        const res = await axios.post(`${DEEPSEEK_BASE}/chat`, { message: text });
        return res.data.response;
    } catch (err) {
        console.error("Deepseek fetch error:", err);
        return "Error getting response from Gemini.";
    }
};


export const sendSpeechToText = async (audioBlob, model) => {
    const BASE = model === 'deepseek' ? DEEPSEEK_BASE : GEMINI_BASE;
    const formData = new FormData();
    formData.append('audio', audioBlob);

    const res = await axios.post(`${BASE}/speech2text`, formData);
    return res.data.text;
};

export const sendImageToOCR = async (imageFile, model) => {
    const BASE = model === 'deepseek' ? DEEPSEEK_BASE : GEMINI_BASE;
    const formData = new FormData();
    formData.append('image', imageFile);

    const res = await axios.post(`${BASE}/ocr`, formData);
    return res.data.text;
};
