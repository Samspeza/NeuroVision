import prisma from "../utils/prisma";
import { Prisma } from "@prisma/client";

/* =========================
 * DTOs
 * ========================= */

export interface DiagnosisCreateDTO {
  imageId: string;
  prediction: string;
  confidence: number;
  modelVersion: string;
}

export interface DiagnosisUpdateDTO {
  prediction?: string;
  confidence?: number;
  modelVersion?: string;
}

export interface DiagnosisListParams {
  page?: number;
  pageSize?: number;
  imageId?: string;
  modelVersion?: string;
  minConfidence?: number;
  maxConfidence?: number;
}

/* =========================
 * Helpers
 * ========================= */

function validateCreateDTO(data: DiagnosisCreateDTO) {
  if (!data.imageId) throw new Error("imageId é obrigatório");
  if (!data.prediction) throw new Error("prediction é obrigatória");
  if (data.confidence < 0 || data.confidence > 1) {
    throw new Error("confidence deve estar entre 0 e 1");
  }
}

/* =========================
 * Model
 * ========================= */

export const DiagnosisModel = {
  /* ---------- Create ---------- */
  async create(data: DiagnosisCreateDTO) {
    validateCreateDTO(data);

    return prisma.diagnosis.create({
      data,
    });
  },

  /* ---------- Read ---------- */
  async findById(id: string) {
    return prisma.diagnosis.findUnique({
      where: { id },
    });
  },

  async findByImage(imageId: string) {
    return prisma.diagnosis.findMany({
      where: {
        imageId,
        deletedAt: null,
      },
      orderBy: { createdAt: "desc" },
    });
  },

  /* ---------- List com paginação e filtros ---------- */
  async list(params: DiagnosisListParams = {}) {
    const {
      page = 1,
      pageSize = 10,
      imageId,
      modelVersion,
      minConfidence,
      maxConfidence,
    } = params;

    const where: Prisma.DiagnosisWhereInput = {
      deletedAt: null,
      imageId,
      modelVersion,
      confidence: {
        gte: minConfidence,
        lte: maxConfidence,
      },
    };

    const [items, total] = await prisma.$transaction([
      prisma.diagnosis.findMany({
        where,
        skip: (page - 1) * pageSize,
        take: pageSize,
        orderBy: { createdAt: "desc" },
      }),
      prisma.diagnosis.count({ where }),
    ]);

    return {
      data: items,
      meta: {
        total,
        page,
        pageSize,
        totalPages: Math.ceil(total / pageSize),
      },
    };
  },

  /* ---------- Update ---------- */
  async update(id: string, data: DiagnosisUpdateDTO) {
    return prisma.diagnosis.update({
      where: { id },
      data,
    });
  },

  /* ---------- Soft delete ---------- */
  async softDelete(id: string) {
    return prisma.diagnosis.update({
      where: { id },
      data: {
        deletedAt: new Date(),
      },
    });
  },

  /* ---------- Hard delete ---------- */
  async delete(id: string) {
    return prisma.diagnosis.delete({
      where: { id },
    });
  },

  /* ---------- Estatísticas ---------- */
  async getStats() {
    const [total, avgConfidence, byPrediction] = await prisma.$transaction([
      prisma.diagnosis.count({
        where: { deletedAt: null },
      }),
      prisma.diagnosis.aggregate({
        _avg: {
          confidence: true,
        },
        where: { deletedAt: null },
      }),
      prisma.diagnosis.groupBy({
        by: ["prediction"],
        _count: { prediction: true },
        where: { deletedAt: null },
      }),
    ]);

    return {
      total,
      averageConfidence: avgConfidence._avg.confidence,
      byPrediction,
    };
  },
};
