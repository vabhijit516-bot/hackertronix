import React, { useState } from 'react';
import { Project } from '../types';

interface ProjectListProps {
  projects: Project[];
  onDeleteProject?: (id: string) => void;
}

export const ProjectList: React.FC<ProjectListProps> = ({ projects, onDeleteProject }) => {
  const [filter, setFilter] = useState<string>('ALL');

  const filteredProjects = projects.filter(p => {
    if (filter === 'ALL') return true;
    return p.category === filter;
  });

  return (
    <div className="panel">
      <div className="panel-header">
        <div>
          <h2 className="panel-title">
            <span>📦</span> Full-Stack Microservices & Projects
          </h2>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Showing {filteredProjects.length} registered production workloads
          </span>
        </div>

        <div style={{ display: 'flex', gap: '6px' }}>
          {['ALL', 'Full-Stack', 'AI / Computer Vision', 'Autonomous Agent'].map(cat => (
            <button
              key={cat}
              className={`btn btn-secondary ${filter === cat ? 'active' : ''}`}
              style={{
                fontSize: '0.75rem',
                padding: '4px 10px',
                borderColor: filter === cat ? 'var(--accent-cyan)' : 'var(--border-subtle)',
                color: filter === cat ? 'var(--accent-cyan)' : 'var(--text-muted)'
              }}
              onClick={() => setFilter(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      <div className="project-list">
        {filteredProjects.map(proj => (
          <div key={proj.id} className="project-item">
            <div className="project-meta">
              <div className="project-title-row">
                <span className="project-name">{proj.name}</span>
                <span className="badge-status healthy">
                  ● {proj.status}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                  ({proj.category})
                </span>
              </div>

              <div className="project-tags">
                {proj.tags.map(tag => (
                  <span key={tag} className="tag-pill">
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div className="project-metrics">
              <div>
                <div className="metric-col-val">{proj.latencyMs} ms</div>
                <div className="metric-col-label">Response SLA</div>
              </div>

              <div>
                <div className="metric-col-val" style={{ color: 'var(--accent-emerald)' }}>
                  {proj.uptime}
                </div>
                <div className="metric-col-label">Uptime</div>
              </div>

              <div>
                <div className="metric-col-val" style={{ color: '#F1F5F9' }}>
                  {proj.requestVolume24h.toLocaleString()}
                </div>
                <div className="metric-col-label">24h Requests</div>
              </div>

              <a
                href={proj.repoUrl}
                target="_blank"
                rel="noreferrer"
                className="btn btn-secondary"
                style={{ padding: '6px 12px', fontSize: '0.75rem' }}
              >
                GitHub ↗
              </a>

              {onDeleteProject && (
                <button
                  className="btn btn-secondary"
                  style={{ padding: '6px 10px', color: 'var(--accent-rose)' }}
                  onClick={() => onDeleteProject(proj.id)}
                  title="Remove Service"
                >
                  ✕
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
