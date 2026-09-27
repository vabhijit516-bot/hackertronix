export interface Project {
  id: string;
  name: string;
  category: 'Full-Stack' | 'AI / Computer Vision' | 'Cloud Infra' | 'Autonomous Agent';
  status: 'Healthy' | 'Degraded' | 'Deploying' | 'Standby';
  latencyMs: number;
  uptime: string;
  tags: string[];
  repoUrl: string;
  lastDeployedAt: string;
  requestVolume24h: number;
}

export interface MetricSummary {
  totalRequests: number;
  avgLatencyMs: number;
  errorRatePercent: number;
  activeDeployments: number;
  cpuUtilizationPercent: number;
  memoryUsageMb: number;
  healthyServicesCount: number;
}

export interface AIModelTelemetry {
  modelName: string;
  totalTokensProcessed: number;
  avgInferenceLatencyMs: number;
  estimatedCostUsd: number;
  successRate: number;
  queriesPerMinute: number;
}

export interface AIQueryLog {
  id: string;
  timestamp: string;
  promptSnippet: string;
  model: string;
  tokens: number;
  durationMs: number;
  status: 'SUCCESS' | 'ERROR';
}
