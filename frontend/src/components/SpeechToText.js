import React, { useRef, useState } from 'react';
import axios from 'axios';

const SpeechInput = ({ onTextReady }) => {
  const mediaRecorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [chunks, setChunks] = useState([]);

  const handleRecord = async () => {
    if (!recording) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      setChunks([]);

      mediaRecorder.ondataavailable = (e) => {
        setChunks((prev) => [...prev, e.data]);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });

        const formData = new FormData();
        formData.append('file', blob, 'mic.webm');

        try {
          const response = await axios.post('http://localhost:8001/speech2text', formData);
          const { transcription, response: deepseekResponse } = response.data;

          if (onTextReady) {
            onTextReady({ transcription, deepseekResponse });
          }
        } catch (err) {
          console.error('Mic speech-to-text failed:', err);
        }
      };

      mediaRecorder.start();
      setRecording(true);
    } else {
      mediaRecorderRef.current.stop();
      setRecording(false);
    }
  };

  return (
    <button onClick={handleRecord} title="Record mic audio">
      {recording ? '🛑 Stop' : '🎤 Speak'}
    </button>
  );
};

export default SpeechInput;
