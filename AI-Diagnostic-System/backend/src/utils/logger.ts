import fs from "fs";
import path from "path";

const logDir = path.join(__dirname, "../../logs");
if (!fs.existsSync(logDir)) fs.mkdirSync(logDir, { recursive: true });

const logFile = path.join(logDir, "app.log");

/**
 * Função genérica para formatar e registrar logs
 */
function writeLog(level: string, message: string) {
  const timestamp = new Date().toISOString();
  const formatted = `[${timestamp}] [${level.toUpperCase()}]: ${message}\n`;

  console.log(formatted.trim());
  fs.appendFileSync(logFile, formatted);
}

export const logger = {
  info: (msg: string) => writeLog("info", msg),
  warn: (msg: string) => writeLog("warn", msg),
  error: (msg: string) => writeLog("error", msg),
};
