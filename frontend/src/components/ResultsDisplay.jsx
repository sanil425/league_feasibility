// frontend/src/components/ResultsDisplay.jsx

import React from 'react';

const ResultsDisplay = ({ results }) => {
    if (!results) return null;

    return (
        <div>
            <h2>Results:</h2>
            <p><strong>Feasible:</strong> {results.feasible ? "Yes" : "No"}</p>
            <p><strong>Probability:</strong> {results.probability}</p>
            <p><strong>Explanation:</strong> {results.explanation}</p>

            <h3>Match Outcomes:</h3>
            <ul>
                {results.solution_outcomes.map((outcome, idx) => (
                    <li key={idx}>{outcome.match}: {outcome.result}</li>
                ))}
            </ul>
        </div>
    );
};

export default ResultsDisplay;
