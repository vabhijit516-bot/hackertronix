import { Request, Response, NextFunction } from 'express';
import { dbStore } from '../services/store';

export const getAIAnalytics = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const data = dbStore.getAITelemetry();
    res.status(200).json({
      success: true,
      data,
    });
  } catch (error) {
    next(error);
  }
};

export const simulateAIQuery = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
  try {
    const { prompt, model } = req.body;

    const chosenModel = model || 'gpt-4o-developer-core';
    const simulatedDuration = Math.floor(Math.random() * 200) + 150;
    const simulatedTokens = Math.floor(Math.random() * 500) + 120;

    res.status(200).json({
      success: true,
      data: {
        id: `gen-${Date.now()}`,
        model: chosenModel,
        prompt: prompt || 'Analyze microservice health metrics',
        generatedOutput: `[NexDev AI Engine]: Optimized full-stack analysis completed in ${simulatedDuration}ms. All 4 distributed nodes operating within normal SLA thresholds.`,
        telemetry: {
          tokensUsed: simulatedTokens,
          latencyMs: simulatedDuration,
          costEstimateUsd: Number((simulatedTokens * 0.00002).toFixed(5)),
        }
      }
    });
  } catch (error) {
    next(error);
  }
};
