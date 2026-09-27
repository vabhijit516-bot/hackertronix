import { Router } from 'express';
import { getProjects, getProjectById, createProject, deleteProject } from '../controllers/projectController';
import { getAIAnalytics, simulateAIQuery } from '../controllers/aiController';
import { getMetrics, getHealth } from '../controllers/metricsController';
import { authenticateApiKey } from '../middleware/auth';

const router = Router();

// Health Check
router.get('/health', getHealth);

// Metrics & KPIs
router.get('/metrics', getMetrics);

// Projects & Services
router.get('/projects', getProjects);
router.get('/projects/:id', getProjectById);
router.post('/projects', authenticateApiKey, createProject);
router.delete('/projects/:id', authenticateApiKey, deleteProject);

// AI Model Telemetry & Simulation
router.get('/ai/analytics', getAIAnalytics);
router.post('/ai/simulate', authenticateApiKey, simulateAIQuery);

export default router;
