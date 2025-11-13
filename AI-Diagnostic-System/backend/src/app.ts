import express from "express";
import cors from "cors";
import morgan from "morgan";
import path from "path";
import irisRoutes from "./routes/irisRoutes";
import analiseRoutes from "./routes/analiseRoutes";
import { errorHandler } from "./middleware/errorHandler";
import { logger } from "./utils/logger";

const app = express();

// Configurações básicas
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Logs HTTP
app.use(morgan("dev"));

// Diretório público para uploads
app.use("/uploads", express.static(path.join(__dirname, "../uploads")));

// Rotas principais
app.use("/api/iris", irisRoutes);
app.use("/api/analises", analiseRoutes);

// Middleware de erro global
app.use(errorHandler);

// Inicialização
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  logger.info(`🚀 Servidor backend iniciado na porta ${PORT}`);
});

export default app;
