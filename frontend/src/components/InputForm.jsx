// frontend/src/components/InputForm.jsx

import React, { useState } from 'react';
import { simulateLeague } from '../services/api';

function InputForm({ onResult }) {
    const [input, setInput] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await simulateLeague(input);
            onResult(result);
        } catch (error) {
            console.error(error);
            alert("Simulation failed. Check the backend or try again.");
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ marginBottom: '20px' }}>
            <input 
                type="text" 
                value={input} 
                onChange={(e) => setInput(e.target.value)} 
                placeholder="Enter scenario e.g. Can Liverpool make top 4?"
                style={{ width: "300px", marginRight: "10px" }}
            />
            <button type="submit">Simulate</button>
        </form>
    );
}

export default InputForm;
