import React, { useState } from 'react';
import axios from 'axios';

const Tagger = () => {
    const [text, setText] = useState('');
    const [taggedResults, setTaggedResults] = useState([]);

    const handleTagging = async () => {
        try {
            const response = await axios.post('http://localhost:5000/tag', { text });
            setTaggedResults(response.data);
        } catch (error) {
            console.error('Error tagging text:', error);
        }
    };

    return (
        <div>
            <h1>Potential AI Agent</h1>
            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter your text here"
                rows="10"
                cols="50"
            />
            <button onClick={handleTagging}>Tag Text</button>
            <h2>Tagged Results</h2>
            {taggedResults.length > 0 && (
                <ul>
                    {taggedResults.map((sentence, index) => (
                        <li key={index}>
                            {sentence.map((wordObj) => (
                                <span key={wordObj.word}>
                                    {wordObj.word} ({wordObj.tag}){' '}
                                </span>
                            ))}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default Tagger;
