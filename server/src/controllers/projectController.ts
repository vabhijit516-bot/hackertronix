import { Request, Response, NextFunction } from 'express';
import { dbStore } from '../services/store';

export const getProjects = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const projects = dbStore.getProjects();
    res.status(200).json({
      success: true,
      count: projects.length,
      data: projects,
    });
  } catch (error) {
    next(error);
  }
};

export const getProjectById = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const project = dbStore.getProjectById(req.params.id);
    if (!project) {
      res.status(404).json({
        success: false,
        message: `Project with ID ${req.params.id} not found`,
      });
      return;
    }
    res.status(200).json({
      success: true,
      data: project,
    });
  } catch (error) {
    next(error);
  }
};

export const createProject = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const { name, category, status, latencyMs, uptime, tags, repoUrl } = req.body;

    if (!name || !category) {
      res.status(400).json({
        success: false,
        message: 'Project name and category are required fields',
      });
      return;
    }

    const created = dbStore.addProject({
      name,
      category,
      status: status || 'Healthy',
      latencyMs: Number(latencyMs) || 20,
      uptime: uptime || '99.9%',
      tags: Array.isArray(tags) ? tags : ['Full-Stack', 'TypeScript'],
      repoUrl: repoUrl || 'https://github.com/vabhijit516-bot/hackertronix',
    });

    res.status(201).json({
      success: true,
      message: 'Project service registered successfully',
      data: created,
    });
  } catch (error) {
    next(error);
  }
};

export const deleteProject = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const deleted = dbStore.deleteProject(req.params.id);
    if (!deleted) {
      res.status(404).json({
        success: false,
        message: `Project with ID ${req.params.id} not found`,
      });
      return;
    }
    res.status(200).json({
      success: true,
      message: 'Project removed successfully',
    });
  } catch (error) {
    next(error);
  }
};
