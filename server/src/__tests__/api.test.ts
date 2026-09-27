import request from 'supertest';
import { app } from '../index';

describe('NexDev Full-Stack API Integration Tests', () => {
  it('GET /api/health should return 200 OK and ONLINE status', async () => {
    const res = await request(app).get('/api/health');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ONLINE');
    expect(res.body.version).toBe('1.0.0');
  });

  it('GET /api/projects should return project list', async () => {
    const res = await request(app).get('/api/projects');
    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(Array.isArray(res.body.data)).toBe(true);
    expect(res.body.count).toBeGreaterThan(0);
  });

  it('GET /api/metrics should return valid KPI numbers', async () => {
    const res = await request(app).get('/api/metrics');
    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.data).toHaveProperty('totalRequests');
    expect(res.body.data).toHaveProperty('avgLatencyMs');
    expect(res.body.data).toHaveProperty('activeDeployments');
  });

  it('GET /api/ai/analytics should return models and logs', async () => {
    const res = await request(app).get('/api/ai/analytics');
    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);
    expect(res.body.data).toHaveProperty('models');
    expect(res.body.data).toHaveProperty('logs');
  });

  it('POST /api/projects should register a new service', async () => {
    const newProject = {
      name: 'Automated CI Service',
      category: 'Cloud Infra',
      status: 'Healthy',
      latencyMs: 15,
      uptime: '99.99%',
      tags: ['GitHub Actions', 'Docker'],
    };

    const res = await request(app)
      .post('/api/projects')
      .send(newProject);

    expect(res.status).toBe(201);
    expect(res.body.success).toBe(true);
    expect(res.body.data.name).toBe('Automated CI Service');
  });
});
