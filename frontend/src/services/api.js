// frontend/src/services/api.js

import axios from 'axios';

export const simulateLeague = async (userPrompt) => {
    try {
        const response = await axios.post('http://localhost:8000/simulate/', { user_prompt: userPrompt });
        return response.data;
    } catch (error) {
        console.error('Error simulating league:', error);
        throw error;
    }
};
