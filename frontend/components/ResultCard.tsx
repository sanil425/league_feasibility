'use client';

interface ResultCardProps {
  result: unknown;
}

export default function ResultCard({ result }: ResultCardProps) {
  return (
    <div className="result-card">
      <h3>Simulation Result</h3>
      <div className="json-viewer">
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </div>
    </div>
  );
}
