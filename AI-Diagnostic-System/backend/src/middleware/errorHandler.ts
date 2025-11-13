import { Request, Response, NextFunction } from "express";
import { logger } from "../utils/logger";

/**
 * Middleware global de tratamento de erros
 * Captura exceções e envia respostas padronizadas
 */
export function errorHandler(
  err: any,
  req: Request,
  res: Response,
  _next: NextFunction
) {
  const status = err.status || 500;
  const message = err.message || "Erro interno no servidor.";

  logger.error(
    `Erro [${req.method} ${req.originalUrl}] → ${message} | Detalhes: ${
      err.stack || "sem stack trace"
    }`
  );

  res.status(status).json({
    error: true,
    message,
    status,
  });
}
