// frontend/src/components/InputForm.jsx

import React, { useState } from 'react';

const InputForm = ({ onSubmit }) => {
    const [promptHeader, setPromptHeader] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(promptHeader);
    };

    return (
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
            <label>Enter Query:</label>
            <input
                type="text"
                value={promptHeader}
                onChange={(e) => setPromptHeader(e.target.value)}
                placeholder="e.g. Can Manchester City make it into the top 4 even if they lose to Arsenal?"
                style={{ margin: '10px', padding: '8px' }}
            />
            <button type="submit">Simulate</button>
        </form>
    );
};

export default InputForm;
