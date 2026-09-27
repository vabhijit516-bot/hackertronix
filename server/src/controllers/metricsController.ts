import { Request, Response, NextFunction } from 'express';
import { dbStore } from '../services/store';

export const getMetrics = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const metrics = dbStore.getMetrics();
    res.status(200).json({
      success: true,
      data: metrics,
    });
  } catch (error) {
    next(error);
  }
};

export const getHealth = async (req: Request, res: Response): Promise<void> => {
  res.status(200).json({
    status: 'ONLINE',
    uptimeSeconds: Math.floor(process.uptime()),
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    environment: process.env.NODE_ENV || 'development',
  });
};
