import React, { useState } from 'react';

interface ArchitectureNode {
  id: string;
  name: string;
  type: 'Frontend' | 'Gateway' | 'Backend' | 'Database' | 'AI Layer';
  tech: string;
  status: string;
  description: string;
  details: string[];
}

const architectureNodes: ArchitectureNode[] = [
  {
    id: 'node-client',
    name: 'Client Presentation Tier',
    type: 'Frontend',
    tech: 'React 18 + Vite + TypeScript',
    status: 'Healthy (200 OK)',
    description: 'Reactive single-page application optimized for sub-100ms first paint and modular state hydration.',
    details: ['TypeScript interfaces', 'Tailwind custom properties', 'Automatic API fallback handling', 'Responsive mobile grid']
  },
  {
    id: 'node-gateway',
    name: 'Reverse Proxy & Security Gateway',
    type: 'Gateway',
    tech: 'Nginx / Helmet / Rate-Limiter',
    status: 'Active (DDoS Protected)',
    description: 'Enforces SSL termination, CORS origin checks, request rate-limiting, and JWT authentication filters.',
    details: ['Helmet HTTP security headers', 'IP-based sliding window rate limiter', 'CORS whitelisting', 'JWT token introspection']
  },
  {
    id: 'node-api',
    name: 'Backend Microservices Core',
    type: 'Backend',
    tech: 'Node.js 20 + Express + TypeScript',
    status: 'Operational (P99 35ms)',
    description: 'High-throughput asynchronous REST API managing business logic, project registration, and telemetry ingestion.',
    details: ['Controller/Service separation', 'Global error boundary middleware', 'Async JSON handlers', 'Docker multi-stage packaging']
  },
  {
    id: 'node-storage',
    name: 'Persistence & In-Memory Caching',
    type: 'Database',
    tech: 'PostgreSQL 16 + Redis 7',
    status: 'Connected (ACID Compliant)',
    description: 'Dual-tier data architecture pairing persistent relational schema with sub-millisecond Redis cache.',
    details: ['Indexed relational tables', 'Redis session & telemetry caching', 'Automated docker volumes', 'Healthcheck probe scripts']
  },
  {
    id: 'node-ai',
    name: 'AI & Inference Engine Pipeline',
    type: 'AI Layer',
    tech: 'FastAPI + YOLOv8 + LangChain + OpenAI',
    status: 'Streaming (Active)',
    description: 'Hybrid machine intelligence layer orchestrating real-time vision inference and autonomous LLM agents.',
    details: ['YOLOv8 real-time object detection', 'LangChain self-correcting SQL agent', 'Token cost estimation telemetry', 'WebSocket HUD broadcast']
  }
];

export const ArchitectureView: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<ArchitectureNode>(architectureNodes[0]);

  return (
    <div className="panel">
      <div className="panel-header">
        <h2 className="panel-title">
          <span>🏗️</span> Full-Stack System Architecture Blueprint
        </h2>
        <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
          Distributed Multi-Tier Topology
        </span>
      </div>

      <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '24px' }}>
        Click on any layer below to inspect component responsibilities, engineering patterns, and data flow.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px', marginBottom: '24px' }}>
        {architectureNodes.map(node => (
          <div
            key={node.id}
            onClick={() => setSelectedNode(node)}
            style={{
              padding: '16px',
              borderRadius: 'var(--radius-md)',
              background: selectedNode.id === node.id ? 'rgba(56, 189, 248, 0.15)' : 'rgba(15, 23, 42, 0.6)',
              border: selectedNode.id === node.id ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
              {node.type}
            </div>
            <div style={{ fontWeight: 700, fontSize: '0.95rem', color: 'var(--text-main)', marginBottom: '4px' }}>
              {node.name}
            </div>
            <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)' }}>
              {node.tech}
            </div>
          </div>
        ))}
      </div>

      <div
        style={{
          background: 'rgba(15, 23, 42, 0.8)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '24px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <div>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>
              Layer Inspector
            </span>
            <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--text-main)' }}>
              {selectedNode.name}
            </h3>
          </div>
          <span className="badge-status healthy">
            ● {selectedNode.status}
          </span>
        </div>

        <p style={{ color: '#CBD5E1', fontSize: '0.95rem', marginBottom: '16px' }}>
          {selectedNode.description}
        </p>

        <h4 style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase' }}>
          Core Engineering Specifications:
        </h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '8px' }}>
          {selectedNode.details.map((detail, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '8px 12px',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                fontSize: '0.8rem',
                fontFamily: 'var(--font-mono)',
                color: '#94A3B8',
              }}
            >
              ✓ {detail}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
