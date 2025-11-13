# Arquitetura do Sistema – IrisAI Diagnostic System

## Visão Geral

O **IrisAI** é um sistema full stack baseado em Inteligência Artificial para **análise e diagnóstico automatizado de imagens iridológicas**.  
Seu objetivo é identificar padrões visuais na íris humana e auxiliar em diagnósticos preliminares com base em modelos de **Deep Learning**.

O projeto segue uma **arquitetura modular e integrada**, composta por quatro grandes blocos:

/ml → Inteligência Artificial e Processamento de Imagens
/backend → API RESTful (Node.js + TypeScript + Express)
/frontend → Interface Web (React + TypeScript + TailwindCSS)
/infra → Infraestrutura e Docker (Ambiente padronizado)

##  Camadas da Arquitetura

### 1. Inteligência Artificial (`/ml`)
- Responsável por todo o pipeline de **processamento e classificação de imagens**.
- Utiliza **TensorFlow/Keras** para treinar e servir modelos.
- Registra métricas e experimentos via **MLflow**.
- Estrutura principal:
  - `preprocess.py` → Normalização e segmentação da íris.
  - `train.py` → Treinamento do modelo CNN.
  - `evaluate.py` → Avaliação de métricas.
  - `mlflow_tracking.py` → Registro de experimentos e versões.


### 2. Backend (`/backend`)
- Desenvolvido em **Node.js + TypeScript** usando **Express**.
- Expõe uma **API RESTful** para:
  - Upload de imagens.
  - Inferência do modelo (carregado de `/ml/models`).
  - Consulta de diagnósticos armazenados no banco.
- Integra com o banco via **Prisma ORM** e com o módulo de IA via chamadas internas a Python.
- Arquitetura limpa e escalável:
  - `/controllers` → Lógica de controle.
  - `/routes` → Definição de endpoints.
  - `/models` → Definição de entidades do Prisma.
  - `/utils` → Funções auxiliares e integração com IA.


### 3. Frontend (`/frontend`)
- Desenvolvido em **React + TypeScript + TailwindCSS**.
- Permite:
  - Upload de imagens da íris.
  - Visualização de diagnósticos e histórico.
  - Interface moderna, responsiva e intuitiva.
- Comunicação direta com a API via **Axios**.

Componentes principais:
- `Home.tsx` → Página inicial com upload e resultado.
- `History.tsx` → Histórico de diagnósticos.
- `Navbar.tsx` → Navegação entre páginas.

### 4. Banco de Dados
- Banco **PostgreSQL** (ou MongoDB, conforme `.env`).
- Armazena:
  - Logs e auditorias.
  - Histórico de diagnósticos.
  - Resultados e métricas inferidas.
- Acesso e versionamento controlados via **Prisma**.


### 5. Infraestrutura (`/infra`)
- Containerização completa com **Docker**.
- Arquivo `docker-compose.yml` define os serviços:
  - `backend`, `frontend`, `mlflow`, `db`.
- Uso de `.env` padronizado para segredos e variáveis.


## Fluxo de Comunicação

```mermaid
graph LR
A[Frontend React] -->|Upload /api/upload| B[Backend Express]
B -->|Executa script Python| C[Modelo IA - TensorFlow]
C -->|Retorna diagnóstico| B
B -->|Grava resultado| D[(Banco de Dados)]
B -->|Responde JSON| A
A -->|Exibe diagnóstico e histórico| User[Usuário]

 Tecnologias Principais
Camada	Tecnologias
IA	Python, TensorFlow, OpenCV, MLflow
Backend	Node.js, TypeScript, Express, Prisma
Frontend	React, TypeScript, TailwindCSS, Axios
Banco	PostgreSQL / MongoDB
Infraestrutura	Docker, Docker Compose

 Padrões Arquiteturais
Clean Architecture e Camadas Modulares.

Separação entre processamento de IA, serviço de API e apresentação visual.

Comunicação via HTTP REST e persistência padronizada.

Alta coesão entre módulos e baixo acoplamento.

 Estrutura Completa de Diretórios
css
Copiar código
AI-Diagnostic-System/
│
├── ml/
│   ├── datasets/
│   ├── models/
│   ├── scripts/
│   ├── preprocess.py
│   ├── train.py
│   ├── evaluate.py
│   └── mlflow_tracking.py
│
├── backend/
│   ├── src/
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── routes/
│   │   └── utils/
│   ├── main.ts
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── assets/
│   ├── package.json
│   └── tsconfig.json
│
├── infra/
│   ├── docker-compose.yml
│   └── .env.example
│
└── docs/
    ├── arquitetura.md
    ├── api_referencia.md
    └── guia_instalacao.md
