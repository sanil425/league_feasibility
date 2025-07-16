// frontend/src/App.jsx

import React, { useState } from 'react';
import InputForm from './components/InputForm';
import ResultsDisplay from './components/ResultsDisplay';

function App() {
    const [result, setResult] = useState(null);

    return (
        <div style={{ padding: '20px' }}>
            <h1>League Feasibility Simulator</h1>
            <InputForm onResult={setResult} />
            {result ? (
                <ResultsDisplay result={result} />
            ) : (
                <p>Please enter a scenario and click Simulate.</p>
            )}
        </div>
    );
}

export default App;
