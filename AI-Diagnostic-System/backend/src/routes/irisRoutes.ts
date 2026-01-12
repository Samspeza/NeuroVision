import { Router, Request, Response } from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import { predictIris } from "../controllers/irisController";

const router = Router();

/**
 * Diretório de upload
 */
const uploadDir = path.resolve(__dirname, "../../uploads");

if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

/**
 * Configuração do storage do multer
 */
const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    cb(null, uploadDir);
  },
  filename: (_req, file, cb) => {
    const uniqueName = `${Date.now()}-${Math.round(
      Math.random() * 1e9
    )}${path.extname(file.originalname)}`;

    cb(null, uniqueName);
  },
});

/**
 * Filtro para aceitar apenas imagens
 */
const fileFilter: multer.Options["fileFilter"] = (
  _req,
  file,
  cb
) => {
  const allowedTypes = ["image/jpeg", "image/png", "image/jpg"];

  if (!allowedTypes.includes(file.mimetype)) {
    return cb(new Error("Tipo de arquivo não suportado."));
  }

  cb(null, true);
};

const upload = multer({
  storage,
  fileFilter,
});

/**
 * POST /upload
 * Upload de imagem e predição da íris
 */
router.post(
  "/upload",
  upload.single("image"),
  async (req: Request, res: Response) => {
    try {
      if (!req.file) {
        return res.status(400).json({
          error: "Nenhuma imagem enviada.",
        });
      }

      const prediction = await predictIris(req.file.path);

      return res.status(200).json({
        message: "Imagem processada com sucesso.",
        prediction,
      });
    } catch (error) {
      console.error("Erro na predição:", error);

      return res.status(500).json({
        error: "Falha ao processar a imagem.",
      });
    }
  }
);

export default router;
