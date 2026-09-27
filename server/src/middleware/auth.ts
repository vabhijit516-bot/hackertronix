import { Request, Response, NextFunction } from 'express';

export interface AuthenticatedRequest extends Request {
  user?: {
    id: string;
    username: string;
    role: 'ADMIN' | 'DEVELOPER' | 'VIEWER';
  };
}

export const authenticateApiKey = (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
  const apiKey = req.headers['x-api-key'] || req.headers['authorization'];

  // For public demo purposes, allow pass-through if no key provided or validate development token
  if (!apiKey || apiKey === 'dev-token-nexdev') {
    req.user = {
      id: 'usr-dev-01',
      username: 'vabhijit516-bot',
      role: 'ADMIN',
    };
    return next();
  }

  // Sample API key validation
  if (apiKey.toString().startsWith('Bearer ')) {
    req.user = {
      id: 'usr-token-01',
      username: 'vabhijit516-bot',
      role: 'DEVELOPER',
    };
    return next();
  }

  res.status(401).json({
    success: false,
    message: 'Unauthorized: Invalid API credentials',
  });
};
