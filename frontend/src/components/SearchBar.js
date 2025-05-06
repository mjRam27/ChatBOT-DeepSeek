import React, { useRef, useState } from 'react';
import axios from 'axios';

const ChatInterface = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [pendingFile, setPendingFile] = useState(null);
  const [previewURL, setPreviewURL] = useState(null);
  const mediaRecorderRef = useRef(null);
  const [recording, setRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);

  const handleSend = async () => {
    let userBlock = null;
    let botResponse = '';

    const fileToSend = recordedBlob || pendingFile;

    if (fileToSend) {
      const formData = new FormData();
      formData.append('file', fileToSend, recordedBlob ? 'mic.webm' : fileToSend.name);

      const isAudio = fileToSend.type.startsWith('audio/');
      const endpoint = isAudio ? 'speech2text' : 'ocr';

      try {
        const response = await axios.post(`http://localhost:8001/${endpoint}`, formData);
        const transcript = response.data.transcription;
        const geminiResponse = response.data.response;

        botResponse = geminiResponse || ' No Deepseek response';

        userBlock = (
          <div>
            {/* Show preview only for uploaded files */}
            {!recordedBlob && <div>[Uploaded {isAudio ? 'Audio' : 'Image'}]</div>}

            {/* Show preview image if it is an image */}
            {!isAudio && previewURL && (
              <img src={previewURL} alt="preview" style={{ maxWidth: '200px', marginTop: '5px' }} />
            )}

            {/* Show transcript if available */}
            {transcript && (
              <div style={{ marginTop: '5px', fontStyle: 'italic' }}>
                 {transcript}
              </div>
            )}

            {/* Show audio preview only for uploaded audio, not mic */}
            {isAudio && !recordedBlob && previewURL && (
              <audio controls src={previewURL} style={{ marginTop: '5px' }} />
            )}
          </div>
        );
      } catch (err) {
        botResponse = ' Failed to process file.';
        userBlock = `[Upload Error]`;
      }

      setPendingFile(null);
      setPreviewURL(null);
      setRecordedBlob(null);
      setInput('');
    } else if (input.trim()) {
      const response = await axios.post('http://localhost:8001/chat', { message: input });
      botResponse = response.data.response;
      userBlock = input;
      setInput('');
    } else {
      return;
    }

    setMessages([...messages, { user: userBlock, bot: botResponse }]);
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setPendingFile(file);

    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => setPreviewURL(reader.result);
      reader.readAsDataURL(file);
    } else if (file.type.startsWith('audio/')) {
      const audioURL = URL.createObjectURL(file);
      setPreviewURL(audioURL);
    }
  };

  const triggerFileInput = () => {
    document.getElementById('hidden-file-input').click();
  };

  const handleRecord = async () => {
    if (!recording) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const chunks = [];

      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunks, { type: 'audio/webm' });
        setRecordedBlob(audioBlob);

        const formData = new FormData();
        formData.append('file', audioBlob, 'mic.webm');

        try {
          const response = await axios.post("http://localhost:8001/speech2text", formData);
          const transcription = response.data.transcription;
          if (transcription) {
            setInput(transcription); // Show transcript only
          } else {
            console.warn("No transcription returned.");
          }
        } catch (err) {
          console.error("Speech-to-text failed:", err);
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
    <div style={{ marginTop: '20px', width: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', minHeight: '100vh' }}>
      <div style={{
        flex: 1,
        maxHeight: 'calc(100vh - 120px)',
        overflowY: 'auto',
        padding: '10px',
        border: '1px solid #ccc',
        borderRadius: '5px',
        marginBottom: '10px'
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: '10px' }}>
            <div><strong>You:</strong> {msg.user}</div>
            <div><strong>DeepSeek:</strong> {msg.bot}</div>
            <hr />
          </div>
        ))}
      </div>
      {pendingFile && (
  <div style={{ paddingBottom: '10px' }}>
    {pendingFile.type.startsWith('image/') && previewURL && (
      <img src={previewURL} alt="preview" style={{ maxWidth: '200px', marginTop: '5px' }} />
    )}

    {pendingFile.type.startsWith('audio/') && previewURL && (
      <audio controls src={previewURL} style={{ marginTop: '5px' }} />
    )}
  </div>
)}


      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', paddingBottom: '10px' }}>
        <input
          id="hidden-file-input"
          type="file"
          accept="image/*,audio/*"
          style={{ display: 'none' }}
          onChange={handleFileUpload}
        />
        <button onClick={triggerFileInput} title="Upload file" style={{ padding: '10px', fontSize: '20px', cursor: 'pointer' }}>➕</button>

        <button
          onClick={handleRecord}
          title={recording ? "Stop recording" : "Start recording"}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            border: '1px solid #ccc',
            backgroundColor: recording ? '#f8d7da' : '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            cursor: 'pointer',
            boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
          }}
        >
          🎤
        </button>

        <input
          style={{ flex: 1, padding: '10px', borderRadius: '4px', border: '1px solid #ccc' }}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          handleSend();
       }
      }}
       placeholder="Type a message or use the mic..."
      />


        <button
          onClick={handleSend}
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px'
          }}
        >
          Send
        </button>
      </div>

      {/* Show mic input text only (no audio preview) */}
      {/* {recordedBlob && input && (
        <div style={{ margin: '10px 0', fontStyle: 'italic' }}>
          <strong>Mic input:</strong> {input}
        </div>
      )} */}
    </div>
  );
};

export default ChatInterface;
