import prisma from "../utils/prisma";

export interface DiagnosisCreateDTO {
  imageId: string;
  prediction: string;
  confidence: number;
  modelVersion: string;
}

export const DiagnosisModel = {
  async create(data: DiagnosisCreateDTO) {
    return prisma.diagnosis.create({ data });
  },

  async findById(id: string) {
    return prisma.diagnosis.findUnique({
      where: { id },
    });
  },

  async list() {
    return prisma.diagnosis.findMany({
      orderBy: { createdAt: "desc" },
    });
  },

  async findByImage(imageId: string) {
    return prisma.diagnosis.findMany({
      where: { imageId },
    });
  },
};
