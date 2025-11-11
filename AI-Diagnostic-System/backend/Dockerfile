# ml/Dockerfile - ambiente para treinamento e mlflow helpers
FROM python:3.10-slim


# Metadados
LABEL maintainer="devsasa <devsasa@example.com>"


WORKDIR /app


# Evitar buffers durante execução
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# Dependências do sistema (OpenCV e bibliotecas básicas)
RUN apt-get update && apt-get install -y --no-install-recommends \
build-essential \
libglib2.0-0 \
libsm6 \
libxrender1 \
libxext6 \
ffmpeg \
&& rm -rf /var/lib/apt/lists/*


# Copia requirements se houver (o projeto deve ter ml/requirements.txt)
COPY ./ml/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
pip install --no-cache-dir -r /app/requirements.txt


# Criar diretórios esperados
RUN mkdir -p /app/ml/models /app/ml/datasets /app/ml/artifacts


VOLUME ["/app/ml/models", "/app/ml/artifacts"]


WORKDIR /app/ml


CMD ["bash"]