// frontend/src/components/ResultsDisplay.jsx

import React from 'react';

const ResultsDisplay = ({ result }) => {
    if (!result) return null;

    return (
        <div>
            <h2>Results:</h2>
            <p><strong>Feasible:</strong> {result.feasible ? "Yes" : "No"}</p>
            <p><strong>Probability:</strong> {result.probability}</p>
            <p><strong>Explanation:</strong> {result.explanation}</p>

            <h3>Match Outcomes:</h3>
            <ul>
                {result.match_outcomes.map((outcome, idx) => (
                    <li key={idx}>{outcome.match}: {outcome.result}</li>
                ))}
            </ul>
        </div>
    );
};

export default ResultsDisplay;
