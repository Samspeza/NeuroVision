import { PrismaClient } from "@prisma/client";

const prisma = new PrismaClient();

/**
 * Salva uma nova análise iridológica no banco de dados
 */
export async function salvarAnaliseIris(
  nomeArquivo: string,
  caminhoImagem: string,
  resultado: string,
  probabilidade: number,
  distribuicao: Record<string, number>,
  usuarioId?: number
) {
  try {
    const analise = await prisma.analiseIris.create({
      data: {
        nomeArquivo,
        caminhoImagem,
        resultado,
        probabilidade,
        distribuicao,
        usuarioId,
      },
    });
    return analise;
  } catch (error) {
    console.error("Erro ao salvar análise de íris:", error);
    throw new Error("Falha ao salvar análise no banco de dados.");
  }
}

/**
 * Lista todas as análises de íris registradas
 */
export async function listarAnalises() {
  try {
    return await prisma.analiseIris.findMany({
      orderBy: { criadoEm: "desc" },
      include: { usuario: true },
    });
  } catch (error) {
    console.error("Erro ao listar análises:", error);
    throw new Error("Falha ao buscar registros de análises.");
  }
}

/**
 * Busca uma análise específica por ID
 */
export async function buscarAnalisePorId(id: number) {
  try {
    return await prisma.analiseIris.findUnique({
      where: { id },
      include: { usuario: true },
    });
  } catch (error) {
    console.error("Erro ao buscar análise:", error);
    throw new Error("Falha ao buscar a análise especificada.");
  }
}
