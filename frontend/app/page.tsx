'use client';

import { useState } from 'react';
import { simulate } from '../lib/api';
import ResultCard from '../components/ResultCard';

export default function Home() {
  const [userPrompt, setUserPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<unknown | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userPrompt.trim()) return;

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const simulationResult = await simulate(userPrompt.trim());
      setResult(simulationResult);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setIsLoading(false);
    }
  };

  const isSubmitDisabled = !userPrompt.trim() || isLoading;

  return (
    <div className="container">
      <h1>League Feasibility Simulator</h1>
      <p>Check if your football team can still reach their target position</p>
      
      <form onSubmit={handleSubmit} className="input-form">
        <input
          type="text"
          value={userPrompt}
          onChange={(e) => setUserPrompt(e.target.value)}
          placeholder="e.g., Can Man United still make top 4?"
          aria-label="Enter your scenario"
          disabled={isLoading}
        />
        <button 
          type="submit" 
          disabled={isSubmitDisabled}
          aria-label="Run simulation"
        >
          {isLoading ? 'Simulating...' : 'Simulate'}
        </button>
      </form>

      {isLoading && (
        <div className="loading" aria-live="polite">
          Running simulation... This may take a few moments.
        </div>
      )}

      {error && (
        <div className="error" role="alert" aria-live="polite">
          <strong>Error:</strong> {error}
        </div>
      )}

      {result !== null && <ResultCard result={result} />}
    </div>
  );
}
