import React from 'react';
import { MetricSummary } from '../types';

interface MetricsCardsProps {
  metrics: MetricSummary;
}

export const MetricsCards: React.FC<MetricsCardsProps> = ({ metrics }) => {
  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">24h Ingress Requests</span>
          <span className="metric-icon">🌐</span>
        </div>
        <div className="metric-value">{metrics.totalRequests.toLocaleString()}</div>
        <div className="metric-sub" style={{ color: 'var(--accent-emerald)' }}>
          ↑ 14.8% from prior window
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">Avg API Latency</span>
          <span className="metric-icon">⚡</span>
        </div>
        <div className="metric-value">{metrics.avgLatencyMs} ms</div>
        <div className="metric-sub" style={{ color: 'var(--accent-cyan)' }}>
          P99: 42ms • Edge Accelerated
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">Global Error Rate</span>
          <span className="metric-icon">🛡️</span>
        </div>
        <div className="metric-value">{metrics.errorRatePercent}%</div>
        <div className="metric-sub" style={{ color: 'var(--accent-emerald)' }}>
          Zero fatal crashes reported
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">Containerized Nodes</span>
          <span className="metric-icon">🐳</span>
        </div>
        <div className="metric-value">{metrics.activeDeployments} Active</div>
        <div className="metric-sub">
          {metrics.healthyServicesCount}/{metrics.activeDeployments} Services 100% Healthy
        </div>
      </div>
    </div>
  );
};
