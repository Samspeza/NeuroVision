import { prisma } from "../utils/prisma";

export interface ImageCreateDTO {
  filename: string;
  filepath: string;
  mimetype: string;
  size: number;
}

export const ImageModel = {
  async create(data: ImageCreateDTO) {
    return prisma.image.create({
      data,
    });
  },

  async findById(id: string) {
    return prisma.image.findUnique({
      where: { id },
    });
  },

  async list() {
    return prisma.image.findMany({
      orderBy: { createdAt: "desc" },
    });
  }
};
