import prisma from "@utils/prisma";

export interface LogCreateDTO {
  level: "info" | "warning" | "error";
  message: string;
  metadata?: any;
}

export const LogModel = {
  async create(data: LogCreateDTO) {
    return prisma.log.create({
      data: {
        ...data,
        metadata: data.metadata ? JSON.stringify(data.metadata) : null,
      },
    });
  },

  async list() {
    return prisma.log.findMany({
      orderBy: { createdAt: "desc" },
    });
  },
};
