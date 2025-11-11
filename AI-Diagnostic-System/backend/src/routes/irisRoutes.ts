import { Router } from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import { predictIris } from "../controllers/irisController";

const router = Router();

// Configuração do multer para upload de imagens
const uploadDir = path.join(__dirname, "../../uploads");
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
  destination: (_, __, cb) => cb(null, uploadDir),
  filename: (_, file, cb) => {
    const uniqueSuffix = Date.now() + "-" + Math.round(Math.random() * 1e9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  },
});

const upload = multer({ storage });

// Rotas
router.post("/upload", upload.single("image"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "Nenhuma imagem enviada." });
    }

    const result = await predictIris(req.file.path);
    res.json({
      message: "Imagem processada com sucesso.",
      prediction: result,
    });
  } catch (error) {
    console.error("Erro na predição:", error);
    res.status(500).json({ error: "Falha ao processar imagem." });
  }
});

export default router;
