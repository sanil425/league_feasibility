// frontend/src/components/ResultsDisplay.jsx

import React from 'react';

function ResultsDisplay({ result }) {
    return (
        <div style={{ marginTop: '20px' }}>
            <h2>Simulation Result</h2>
            <p><strong>Explanation:</strong> {result.explanation}</p>
            <p><strong>Feasibility:</strong> {result.feasible ? "✅ Possible" : "❌ Not Possible"}</p>
            <p><strong>Probability:</strong> {Math.round(result.probability * 100)}%</p>

            <h3>Required Outcomes:</h3>
            <ul>
                {result.solution_outcomes.map((outcome, idx) => (
                    <li key={idx}>{outcome.match}: {outcome.result}</li>
                ))}
            </ul>
        </div>
    );
}

export default ResultsDisplay;
