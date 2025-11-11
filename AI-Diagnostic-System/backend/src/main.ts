import "reflect-metadata";
import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import dotenv from "dotenv";
import multer from "multer";
import path from "path";
import fs from "fs";
import { PrismaClient } from "@prisma/client";
import { loadModel, predictImage } from "./utils/tensorflow";
import { errorHandler } from "./utils/errorHandler";

dotenv.config();

const app = express();
const prisma = new PrismaClient();
const PORT = process.env.PORT || 4000;

// Middleware base
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Configuração de uploads
const uploadDir = path.join(__dirname, "../../uploads");
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
  destination: (_req, _file, cb) => cb(null, uploadDir),
  filename: (_req, file, cb) =>
    cb(null, `${Date.now()}-${file.originalname.replace(/\s+/g, "_")}`)
});
const upload = multer({ storage });

// Verificação de saúde da API
app.get("/api/health", (_req, res) => {
  res.status(200).json({ status: "ok", message: "API ativa e funcional" });
});

// Upload de imagem biomédica
app.post("/api/upload", upload.single("image"), async (req, res, next) => {
  try {
    if (!req.file) throw new Error("Nenhuma imagem enviada");
    const filePath = req.file.path;

    // Armazenar metadados do upload no banco
    const record = await prisma.imageUpload.create({
      data: {
        filename: req.file.filename,
        filepath: filePath,
        uploadedAt: new Date()
      }
    });

    res.status(200).json({
      message: "Upload realizado com sucesso",
      file: record
    });
  } catch (err) {
    next(err);
  }
});

// Predição via modelo TensorFlow
app.post("/api/predict", upload.single("image"), async (req, res, next) => {
  try {
    if (!req.file) throw new Error("Imagem não enviada");
    const filePath = req.file.path;

    const modelPath = path.join(__dirname, "../../ml/models/model.h5");
    const model = await loadModel(modelPath);
    const prediction = await predictImage(model, filePath);

    // Registrar diagnóstico
    const result = await prisma.diagnostic.create({
      data: {
        filename: req.file.filename,
        result: JSON.stringify(prediction),
        createdAt: new Date()
      }
    });

    res.status(200).json({
      message: "Predição concluída",
      prediction,
      record: result
    });
  } catch (err) {
    next(err);
  }
});

// Middleware global de erros
app.use(errorHandler);

// Inicialização do servidor
app.listen(PORT, () => {
  console.log(`🚀 Servidor rodando na porta ${PORT}`);
});
