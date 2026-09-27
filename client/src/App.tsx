import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { MetricsCards } from './components/MetricsCards';
import { ProjectList } from './components/ProjectList';
import { AITelemetry } from './components/AITelemetry';
import { ArchitectureView } from './components/ArchitectureView';
import { Project, MetricSummary, AIModelTelemetry, AIQueryLog } from './types';
import {
  fetchProjects,
  fetchMetrics,
  fetchAIAnalytics,
  createProjectApi,
  fallbackProjects,
  fallbackMetrics,
  fallbackTelemetry,
} from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'projects' | 'ai' | 'architecture'>('dashboard');
  const [projects, setProjects] = useState<Project[]>(fallbackProjects);
  const [metrics, setMetrics] = useState<MetricSummary>(fallbackMetrics);
  const [telemetry, setTelemetry] = useState<{ models: AIModelTelemetry[]; logs: AIQueryLog[] }>(fallbackTelemetry);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form State
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectCategory, setNewProjectCategory] = useState<'Full-Stack' | 'AI / Computer Vision' | 'Cloud Infra' | 'Autonomous Agent'>('Full-Stack');
  const [newProjectTags, setNewProjectTags] = useState('React, Node.js, TypeScript');

  useEffect(() => {
    const loadData = async () => {
      const [projData, metData, telData] = await Promise.all([
        fetchProjects(),
        fetchMetrics(),
        fetchAIAnalytics(),
      ]);
      setProjects(projData);
      setMetrics(metData);
      setTelemetry(telData);
    };

    loadData();
  }, []);

  const handleRegisterProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    const tagsArray = newProjectTags.split(',').map(t => t.trim()).filter(Boolean);
    const created = await createProjectApi({
      name: newProjectName,
      category: newProjectCategory,
      status: 'Healthy',
      latencyMs: Math.floor(Math.random() * 20) + 15,
      uptime: '100%',
      tags: tagsArray,
      repoUrl: 'https://github.com/vabhijit516-bot/hackertronix',
    });

    setProjects(prev => [created, ...prev]);
    setIsModalOpen(false);
    setNewProjectName('');
  };

  const handleDeleteProject = (id: string) => {
    setProjects(prev => prev.filter(p => p.id !== id));
  };

  return (
    <div>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onNewProjectClick={() => setIsModalOpen(true)}
      />

      <main className="container">
        {/* Hero Section */}
        <section className="hero">
          <div className="hero-pill">
            <span>✨</span> Full-Stack Developer Operations Environment
          </div>
          <h1 className="hero-title">
            Enterprise Cloud & <span className="hero-gradient">AI Systems Architecture</span>
          </h1>
          <p className="hero-desc">
            Engineered by <strong>Abhijit</strong> (<code>vabhijit516-bot</code>). Centralizing real-time microservices observability,
            automated deployment telemetry, and distributed AI inference pipelines.
          </p>
        </section>

        {/* Global KPIs */}
        <MetricsCards metrics={metrics} />

        {/* Dynamic View Sections */}
        {activeTab === 'dashboard' && (
          <div className="main-grid">
            <ProjectList projects={projects} onDeleteProject={handleDeleteProject} />
            <AITelemetry telemetry={telemetry} />
          </div>
        )}

        {activeTab === 'projects' && (
          <div style={{ marginBottom: '48px' }}>
            <ProjectList projects={projects} onDeleteProject={handleDeleteProject} />
          </div>
        )}

        {activeTab === 'ai' && (
          <div style={{ marginBottom: '48px' }}>
            <AITelemetry telemetry={telemetry} />
          </div>
        )}

        {activeTab === 'architecture' && (
          <div style={{ marginBottom: '48px' }}>
            <ArchitectureView />
          </div>
        )}
      </main>

      {/* Registration Modal */}
      {isModalOpen && (
        <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '16px', color: 'var(--text-main)' }}>
              ⚡ Register Full-Stack Microservice
            </h3>
            <form onSubmit={handleRegisterProject}>
              <div className="form-group">
                <label className="form-label">Service / Project Name</label>
                <input
                  type="text"
                  required
                  className="form-input"
                  placeholder="e.g. Distributed Ingestion Worker"
                  value={newProjectName}
                  onChange={e => setNewProjectName(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Architecture Category</label>
                <select
                  className="form-input"
                  value={newProjectCategory}
                  onChange={e => setNewProjectCategory(e.target.value as any)}
                >
                  <option value="Full-Stack">Full-Stack Application</option>
                  <option value="AI / Computer Vision">AI / Computer Vision</option>
                  <option value="Cloud Infra">Cloud & DevOps Infra</option>
                  <option value="Autonomous Agent">Autonomous Agent</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Technology Tags (Comma Separated)</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="React, TypeScript, Docker, Redis"
                  value={newProjectTags}
                  onChange={e => setNewProjectTags(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '20px' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Deploy & Register
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <p>
            Designed & Engineered by <strong>Abhijit</strong> • GitHub: <a href="https://github.com/vabhijit516-bot" style={{ color: 'var(--accent-cyan)' }}>@vabhijit516-bot</a>
          </p>
          <p style={{ marginTop: '4px', fontSize: '0.78rem' }}>
            Next.js 14 • React 18 • Node.js • Express • PostgreSQL • Docker • TypeScript
          </p>
        </div>
      </footer>
    </div>
  );
};
