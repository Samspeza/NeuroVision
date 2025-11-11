import { Router } from "express";
import { listarAnalises, buscarAnalisePorId } from "../services/irisService";

const router = Router();

/**
 * GET /api/analises
 * Retorna a lista de todas as análises de íris realizadas
 */
router.get("/", async (_, res) => {
  try {
    const analises = await listarAnalises();
    res.json(analises);
  } catch (error) {
    console.error("Erro ao listar análises:", error);
    res.status(500).json({ error: "Falha ao buscar análises." });
  }
});

/**
 * GET /api/analises/:id
 * Retorna uma análise específica pelo ID
 */
router.get("/:id", async (req, res) => {
  try {
    const id = parseInt(req.params.id);
    const analise = await buscarAnalisePorId(id);
    if (!analise) {
      return res.status(404).json({ error: "Análise não encontrada." });
    }
    res.json(analise);
  } catch (error) {
    console.error("Erro ao buscar análise:", error);
    res.status(500).json({ error: "Falha ao buscar a análise." });
  }
});

export default router;
