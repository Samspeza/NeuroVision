# frontend/Dockerfile - ambiente React + TypeScript + Tailwind
FROM node:20-alpine


LABEL maintainer="devsasa <devsasa@example.com>"


WORKDIR /app/frontend


# Copiar dependências
COPY ./frontend/package*.json ./


# Instalar dependências do projeto
RUN npm install --silent


# Copiar código-fonte
COPY ./frontend /app/frontend


# Construir a aplicação para produção
RUN npm run build


EXPOSE 3000


# Comando padrão
CMD ["npm", "run", "dev"]