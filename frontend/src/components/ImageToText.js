import React, { useState } from 'react';
import { sendImageToOCR } from '../Api';

const ImageUploader = ({ onExtractedText, model }) => {
    const [image, setImage] = useState(null);

    const handleUpload = async () => {
        if (!image) return;
        const extractedText = await sendImageToOCR(image, model);
        onExtractedText(extractedText);
    };

    return (
        <div>
            <input type="file" onChange={(e) => setImage(e.target.files[0])} />
            <button onClick={handleUpload}> Upload Image</button>
        </div>
    );
};

export default ImageUploader;
