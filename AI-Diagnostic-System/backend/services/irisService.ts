import { PrismaClient, Prisma } from "@prisma/client";

const prisma = new PrismaClient();

/* =======================
 * TIPOS E INTERFACES
 * ======================= */

export interface CriarAnaliseIrisDTO {
  nomeArquivo: string;
  caminhoImagem: string;
  resultado: string;
  probabilidade: number;
  distribuicao: Record<string, number>;
  usuarioId?: number;
}

export interface FiltroAnaliseIris {
  usuarioId?: number;
  resultado?: string;
  ativo?: boolean;
  dataInicio?: Date;
  dataFim?: Date;
}

export interface Paginacao {
  pagina?: number;
  limite?: number;
}

/* =======================
 * ERROS CUSTOMIZADOS
 * ======================= */

class AnaliseIrisError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AnaliseIrisError";
  }
}

/* =======================
 * UTILITÁRIOS
 * ======================= */

function validarProbabilidade(valor: number) {
  if (valor < 0 || valor > 1) {
    throw new AnaliseIrisError(
      "Probabilidade inválida. O valor deve estar entre 0 e 1."
    );
  }
}

function normalizarDistribuicao(
  distribuicao: Record<string, number>
): Record<string, number> {
  const soma = Object.values(distribuicao).reduce((a, b) => a + b, 0);

  if (soma === 0) {
    throw new AnaliseIrisError("Distribuição inválida. Soma igual a zero.");
  }

  return Object.fromEntries(
    Object.entries(distribuicao).map(([chave, valor]) => [
      chave,
      Number((valor / soma).toFixed(4)),
    ])
  );
}

function logErro(contexto: string, erro: unknown) {
  console.error(`[AnaliseIris][${contexto}]`, {
    erro,
    timestamp: new Date().toISOString(),
  });
}

/* =======================
 * CRIAÇÃO
 * ======================= */

export async function salvarAnaliseIris(
  dados: CriarAnaliseIrisDTO
) {
  try {
    validarProbabilidade(dados.probabilidade);

    const distribuicaoNormalizada = normalizarDistribuicao(
      dados.distribuicao
    );

    return await prisma.$transaction(async (tx) => {
      const analise = await tx.analiseIris.create({
        data: {
          nomeArquivo: dados.nomeArquivo,
          caminhoImagem: dados.caminhoImagem,
          resultado: dados.resultado,
          probabilidade: dados.probabilidade,
          distribuicao: distribuicaoNormalizada,
          usuarioId: dados.usuarioId,
          ativo: true,
        },
        include: {
          usuario: true,
        },
      });

      return analise;
    });
  } catch (error) {
    logErro("salvarAnaliseIris", error);
    throw error instanceof AnaliseIrisError
      ? error
      : new AnaliseIrisError("Falha ao salvar análise de íris.");
  }
}

/* =======================
 * LISTAGEM COM FILTROS
 * ======================= */

export async function listarAnalises(
  filtros: FiltroAnaliseIris = {},
  paginacao: Paginacao = {}
) {
  try {
    const pagina = paginacao.pagina ?? 1;
    const limite = paginacao.limite ?? 10;
    const skip = (pagina - 1) * limite;

    const where: Prisma.AnaliseIrisWhereInput = {
      ativo: filtros.ativo ?? true,
      usuarioId: filtros.usuarioId,
      resultado: filtros.resultado,
      criadoEm:
        filtros.dataInicio || filtros.dataFim
          ? {
              gte: filtros.dataInicio,
              lte: filtros.dataFim,
            }
          : undefined,
    };

    const [total, dados] = await prisma.$transaction([
      prisma.analiseIris.count({ where }),
      prisma.analiseIris.findMany({
        where,
        skip,
        take: limite,
        orderBy: { criadoEm: "desc" },
        include: { usuario: true },
      }),
    ]);

    return {
      pagina,
      limite,
      total,
      totalPaginas: Math.ceil(total / limite),
      dados,
    };
  } catch (error) {
    logErro("listarAnalises", error);
    throw new AnaliseIrisError("Erro ao listar análises.");
  }
}

/* =======================
 * BUSCA POR ID
 * ======================= */

export async function buscarAnalisePorId(id: number) {
  try {
    const analise = await prisma.analiseIris.findFirst({
      where: { id, ativo: true },
      include: { usuario: true },
    });

    if (!analise) {
      throw new AnaliseIrisError("Análise não encontrada.");
    }

    return analise;
  } catch (error) {
    logErro("buscarAnalisePorId", error);
    throw error instanceof AnaliseIrisError
      ? error
      : new AnaliseIrisError("Erro ao buscar análise.");
  }
}

/* =======================
 * SOFT DELETE
 * ======================= */

export async function removerAnalise(id: number) {
  try {
    return await prisma.analiseIris.update({
      where: { id },
      data: { ativo: false },
    });
  } catch (error) {
    logErro("removerAnalise", error);
    throw new AnaliseIrisError("Erro ao remover análise.");
  }
}

/* =======================
 * ESTATÍSTICAS
 * ======================= */

export async function obterEstatisticasGerais() {
  try {
    const [total, mediaProbabilidade] = await prisma.$transaction([
      prisma.analiseIris.count({ where: { ativo: true } }),
      prisma.analiseIris.aggregate({
        _avg: { probabilidade: true },
        where: { ativo: true },
      }),
    ]);

    return {
      totalAnalises: total,
      probabilidadeMedia: mediaProbabilidade._avg.probabilidade ?? 0,
    };
  } catch (error) {
    logErro("obterEstatisticasGerais", error);
    throw new AnaliseIrisError("Erro ao gerar estatísticas.");
  }
}
