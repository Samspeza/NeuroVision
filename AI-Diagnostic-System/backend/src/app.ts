import express from "express";
import cors from "cors";
import morgan from "morgan";
import dotenv from "dotenv";
import path from "path";
import { PrismaClient } from "@prisma/client";
import irisRoutes from "./routes/irisRoutes";

dotenv.config();
const app = express();
const prisma = new PrismaClient();

// Middlewares globais
app.use(cors());
app.use(express.json());
app.use(morgan("dev"));
app.use("/uploads", express.static(path.join(__dirname, "../uploads")));

// Rotas principais
app.use("/api/iris", irisRoutes);

// Teste de conexão com banco
(async () => {
  try {
    await prisma.$connect();
    console.log("✅ Conectado ao banco de dados com sucesso!");
  } catch (error) {
    console.error("❌ Erro ao conectar ao banco de dados:", error);
  }
})();

// Endpoint base
app.get("/", (_, res) => {
  res.json({
    status: "ok",
    message: "Servidor de diagnóstico iridológico em execução 🚀",
  });
});

// Inicialização do servidor
const PORT = process.env.PORT || 4000;
app.listen(PORT, () => {
  console.log(`🌐 Servidor rodando na porta ${PORT}`);
});

export default app;
