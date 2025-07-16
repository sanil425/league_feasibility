import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ResultsDisplay from './components/ResultsDisplay';
import { simulateLeague } from './services/api';

const App = () => {
    const [results, setResults] = useState(null);

    console.log("App loaded"); // Check if React is rendering

    const handleSimulate = async (promptHeader) => {
        console.log("Calling API with:", promptHeader);
        try {
            const res = await simulateLeague(promptHeader);
            console.log("Received response:", res);
            setResults(res);
        } catch (err) {
            console.error("API call failed", err);
        }
    };

    return (
        <div style={{ padding: '20px' }}>
            <h1>League Feasibility Simulator</h1>
            <InputForm onSubmit={handleSimulate} />
            {!results && <p>Please enter a scenario and click Simulate.</p>}
            <ResultsDisplay results={results} />
        </div>
    );
};

export default App;
