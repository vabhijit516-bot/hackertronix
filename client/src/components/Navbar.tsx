import React from 'react';

interface NavbarProps {
  activeTab: 'dashboard' | 'projects' | 'ai' | 'architecture';
  setActiveTab: (tab: 'dashboard' | 'projects' | 'ai' | 'architecture') => void;
  onNewProjectClick: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab, onNewProjectClick }) => {
  return (
    <header className="navbar">
      <div className="container nav-content">
        <a href="#" className="brand">
          <div className="brand-icon">⚡</div>
          <div>
            <span className="brand-title">NexDev</span>
          </div>
          <span className="brand-badge">Full-Stack Cloud OS</span>
        </a>

        <nav className="nav-links">
          <button
            className={`nav-tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Telemetry
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'projects' ? 'active' : ''}`}
            onClick={() => setActiveTab('projects')}
          >
            📦 Microservices
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'ai' ? 'active' : ''}`}
            onClick={() => setActiveTab('ai')}
          >
            🤖 AI Operations
          </button>
          <button
            className={`nav-tab-btn ${activeTab === 'architecture' ? 'active' : ''}`}
            onClick={() => setActiveTab('architecture')}
          >
            🏗️ Architecture
          </button>
        </nav>

        <div className="nav-profile">
          <div className="live-pill">
            <span className="live-dot" />
            <span>SYSTEM HEALTHY</span>
          </div>
          <button className="btn btn-primary" onClick={onNewProjectClick}>
            + Register Service
          </button>
        </div>
      </div>
    </header>
  );
};
