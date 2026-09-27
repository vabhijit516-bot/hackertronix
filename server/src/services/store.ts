import { Project, MetricSummary, AIModelTelemetry, AIQueryLog } from '../types';

class InMemStore {
  private projects: Project[] = [
    {
      id: 'proj-001',
      name: 'NexDev AI Platform',
      category: 'Full-Stack',
      status: 'Healthy',
      latencyMs: 18,
      uptime: '99.99%',
      tags: ['Next.js 14', 'Node.js', 'Express', 'PostgreSQL', 'Docker'],
      repoUrl: 'https://github.com/vabhijit516-bot/hackertronix',
      lastDeployedAt: new Date(Date.now() - 3600000 * 2).toISOString(),
      requestVolume24h: 142500,
    },
    {
      id: 'proj-002',
      name: 'Vision World Model AI',
      category: 'AI / Computer Vision',
      status: 'Healthy',
      latencyMs: 32,
      uptime: '99.95%',
      tags: ['Python', 'FastAPI', 'YOLOv8', 'OpenCV', 'WebSockets'],
      repoUrl: 'https://github.com/vabhijit516-bot/hackertronix',
      lastDeployedAt: new Date(Date.now() - 3600000 * 24).toISOString(),
      requestVolume24h: 89400,
    },
    {
      id: 'proj-003',
      name: 'Autonomous SQL LLM Agent',
      category: 'Autonomous Agent',
      status: 'Healthy',
      latencyMs: 45,
      uptime: '99.92%',
      tags: ['LangChain', 'OpenAI', 'Python', 'PostgreSQL'],
      repoUrl: 'https://github.com/vabhijit516-bot/hackertronix',
      lastDeployedAt: new Date(Date.now() - 3600000 * 48).toISOString(),
      requestVolume24h: 42100,
    },
    {
      id: 'proj-004',
      name: 'Interactive Dev Portfolio',
      category: 'Full-Stack',
      status: 'Healthy',
      latencyMs: 12,
      uptime: '100%',
      tags: ['React', 'TypeScript', 'Tailwind CSS', 'Vite'],
      repoUrl: 'https://github.com/vabhijit516-bot/hackertronix',
      lastDeployedAt: new Date(Date.now() - 3600000 * 12).toISOString(),
      requestVolume24h: 31200,
    }
  ];

  private aiModels: AIModelTelemetry[] = [
    {
      modelName: 'gpt-4o-developer-core',
      totalTokensProcessed: 2840500,
      avgInferenceLatencyMs: 320,
      estimatedCostUsd: 18.42,
      successRate: 99.8,
      queriesPerMinute: 48,
    },
    {
      modelName: 'claude-3-5-sonnet-code',
      totalTokensProcessed: 4120000,
      avgInferenceLatencyMs: 290,
      estimatedCostUsd: 24.15,
      successRate: 99.9,
      queriesPerMinute: 62,
    },
    {
      modelName: 'yolov8-edge-vision',
      totalTokensProcessed: 0,
      avgInferenceLatencyMs: 38,
      estimatedCostUsd: 2.10,
      successRate: 99.6,
      queriesPerMinute: 110,
    }
  ];

  private recentLogs: AIQueryLog[] = [
    {
      id: 'log-101',
      timestamp: new Date().toISOString(),
      promptSnippet: 'SELECT u.id, count(p.id) FROM users u JOIN projects...',
      model: 'gpt-4o-developer-core',
      tokens: 342,
      durationMs: 280,
      status: 'SUCCESS',
    },
    {
      id: 'log-102',
      timestamp: new Date(Date.now() - 45000).toISOString(),
      promptSnippet: 'Generate Kubernetes ingress manifests with cert-manager SSL...',
      model: 'claude-3-5-sonnet-code',
      tokens: 890,
      durationMs: 410,
      status: 'SUCCESS',
    },
    {
      id: 'log-103',
      timestamp: new Date(Date.now() - 95000).toISOString(),
      promptSnippet: 'Edge object detection bounding boxes on frame #4881...',
      model: 'yolov8-edge-vision',
      tokens: 0,
      durationMs: 35,
      status: 'SUCCESS',
    }
  ];

  public getProjects(): Project[] {
    return [...this.projects];
  }

  public getProjectById(id: string): Project | undefined {
    return this.projects.find(p => p.id === id);
  }

  public addProject(data: Omit<Project, 'id' | 'lastDeployedAt' | 'requestVolume24h'>): Project {
    const newProj: Project = {
      ...data,
      id: `proj-${Date.now()}`,
      lastDeployedAt: new Date().toISOString(),
      requestVolume24h: 100,
    };
    this.projects.unshift(newProj);
    return newProj;
  }

  public deleteProject(id: string): boolean {
    const index = this.projects.findIndex(p => p.id === id);
    if (index !== -1) {
      this.projects.splice(index, 1);
      return true;
    }
    return false;
  }

  public getMetrics(): MetricSummary {
    const totalRequests = this.projects.reduce((acc, curr) => acc + curr.requestVolume24h, 0);
    const avgLatency = Math.round(
      this.projects.reduce((acc, curr) => acc + curr.latencyMs, 0) / (this.projects.length || 1)
    );

    return {
      totalRequests,
      avgLatencyMs: avgLatency,
      errorRatePercent: 0.04,
      activeDeployments: this.projects.length,
      cpuUtilizationPercent: 24.8,
      memoryUsageMb: 412,
      healthyServicesCount: this.projects.filter(p => p.status === 'Healthy').length,
    };
  }

  public getAITelemetry(): { models: AIModelTelemetry[]; logs: AIQueryLog[] } {
    return {
      models: this.aiModels,
      logs: this.recentLogs,
    };
  }
}

export const dbStore = new InMemStore();
