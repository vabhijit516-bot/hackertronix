import React, { useState } from 'react';
import { AIModelTelemetry, AIQueryLog } from '../types';

interface AITelemetryProps {
  telemetry: {
    models: AIModelTelemetry[];
    logs: AIQueryLog[];
  };
}

export const AITelemetry: React.FC<AITelemetryProps> = ({ telemetry }) => {
  const [testPrompt, setTestPrompt] = useState('');
  const [isSimulating, setIsSimulating] = useState(false);
  const [simulationResult, setSimulationResult] = useState<{
    text: string;
    tokens: number;
    latency: number;
  } | null>(null);

  const handleSimulate = async () => {
    if (!testPrompt.trim()) return;
    setIsSimulating(true);

    try {
      const res = await fetch('/api/ai/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: testPrompt }),
      });
      const data = await res.json();
      setSimulationResult({
        text: data.data.generatedOutput,
        tokens: data.data.telemetry.tokensUsed,
        latency: data.data.telemetry.latencyMs,
      });
    } catch {
      // Offline fallback simulation
      setTimeout(() => {
        setSimulationResult({
          text: `[Offline Local Simulation]: Query "${testPrompt.slice(0, 30)}..." synthesized successfully across distributed workers.`,
          tokens: 280,
          latency: 210,
        });
      }, 300);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <h2 className="panel-title">
          <span>🤖</span> AI Inference & Telemetry
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px', marginBottom: '20px' }}>
        {telemetry.models.map(m => (
          <div
            key={m.modelName}
            style={{
              background: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              padding: '12px',
            }}
          >
            <div style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', marginBottom: '4px' }}>
              {m.modelName}
            </div>
            <div style={{ fontSize: '1.1rem', fontWeight: 700 }}>{m.queriesPerMinute} QPM</div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>
              Avg Latency: {m.avgInferenceLatencyMs}ms • Success: {m.successRate}%
            </div>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: '20px' }}>
        <h3 style={{ fontSize: '0.9rem', marginBottom: '8px', color: 'var(--text-muted)' }}>
          ⚡ Interactive Prompt Simulation Engine
        </h3>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            className="form-input"
            placeholder="E.g., Synthesize PostgreSQL index strategy for 10M rows..."
            value={testPrompt}
            onChange={e => setTestPrompt(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSimulate()}
          />
          <button
            className="btn btn-primary"
            style={{ whiteSpace: 'nowrap' }}
            onClick={handleSimulate}
            disabled={isSimulating}
          >
            {isSimulating ? 'Processing...' : 'Run Query'}
          </button>
        </div>

        {simulationResult && (
          <div
            style={{
              marginTop: '12px',
              padding: '12px',
              background: 'rgba(56, 189, 248, 0.08)',
              border: '1px solid rgba(56, 189, 248, 0.25)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.85rem',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', fontSize: '0.75rem' }}>
              <span>RESPONSE RECEIVED</span>
              <span>{simulationResult.latency}ms • {simulationResult.tokens} Tokens</span>
            </div>
            <p style={{ color: '#E2E8F0' }}>{simulationResult.text}</p>
          </div>
        )}
      </div>

      <h3 style={{ fontSize: '0.9rem', marginBottom: '10px', color: 'var(--text-muted)' }}>
        Live Telemetry Ingress Log Stream
      </h3>
      <div className="log-stream">
        {telemetry.logs.map(log => (
          <div key={log.id} className="log-item">
            <div className="log-header">
              <span className="log-model">{log.model}</span>
              <span>{log.durationMs}ms • {log.tokens} tokens</span>
            </div>
            <div className="log-snippet">&gt; {log.promptSnippet}</div>
          </div>
        ))}
      </div>
    </div>
  );
};
