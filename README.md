# IrisAI Diagnostic System

Sistema inteligente de **análise iridológica** baseado em **Inteligência Artificial e Processamento de Imagens**.  
Desenvolvido para auxiliar diagnósticos preditivos através de imagens da íris, combinando **Deep Learning** com um **pipeline automatizado de rastreamento e gestão de modelos (MLflow)**.

---

## Visão Geral

O **IrisAI** realiza a detecção e classificação de padrões iridológicos a partir de imagens oculares.  
Seu objetivo é fornecer suporte ao diagnóstico preventivo, analisando características sutis da íris humana com técnicas avançadas de visão computacional.

O projeto é modular e integra três principais camadas:

| Camada            |           Descrição                               | Stack Principal                       |
|  **IA/ML**        | Treinamento e inferência do modelo de diagnóstico | Python, TensorFlow, OpenCV, MLflow    |
|  **Backend API**  | Comunicação entre modelo, banco e frontend        | Node.js, Express, MongoDB             |
|  **Frontend Web** | Interface visual para upload e análise de imagens | React, TypeScript, TailwindCSS        |

---

##  Arquitetura

+--------------------+ +---------------------+ +----------------------+
| Frontend | <---> | API Backend | <---> | Módulo de IA (ML) |
| React + Tailwind | | Node.js + Express | | Python + TensorFlow |
+--------------------+ +---------------------+ +----------------------+

A aplicação segue uma arquitetura escalável com comunicação RESTful e rastreamento de experimentos via **MLflow**.

---

## Funcionalidades Principais

 Upload e pré-processamento de imagens da íris  
 Classificação automática com TensorFlow  
 Registro de métricas e parâmetros no MLflow  
 Painel visual com histórico de diagnósticos  
 Deploy simplificado via Docker Compose  
 Logs e versionamento completo dos modelos

---

## Estrutura do Projeto

irisai-diagnostic/
│
├── backend/ # API Node.js + Express
│ ├── src/
│ └── .env
│
├── frontend/ # Interface React
│ ├── src/
│ └── public/
│
├── ml/ # Inteligência Artificial
│ ├── data/
│ ├── models/
│ ├── mlflow_tracking.py
│ └── train_model.py
│
├── docs/ # Documentação técnica
│ ├── guia_instalacao.md
│ └── arquitetura_sistema.md
│
├── docker-compose.yml
└── README.md

## Instalação Rápida

Clone o repositório e siga os passos:

```bash
git clone https://github.com/seuusuario/irisai-diagnostic.git
cd irisai-diagnostic
docker compose up --build
O sistema será iniciado em:

Frontend → http://localhost:3000

API Backend → http://localhost:5000

MongoDB → localhost:27017

Exemplo de Uso
Acesse a interface web

Faça o upload de uma imagem da íris

Aguarde o processamento

Veja o resultado com a classe predita e o grau de confiança

Exemplo de saída:

makefile
Copiar código
Classe: Iris Saudável
Confiança: 94.6%

Rastreamento de Modelos (MLflow)
O MLflow é utilizado para registrar:

Parâmetros de treino

Acurácia, perda e métricas

Versões de modelo e datasets

Acesse o painel MLflow via:

bash
Copiar código
mlflow ui
Endereço: http://localhost:5001

Tecnologias Utilizadas | Categoria	Tecnologias
IA e Processamento	TensorFlow, Keras, OpenCV, NumPy, Pillow
Backend	Node.js, Express, MongoDB
Frontend	React, TypeScript, TailwindCSS
Controle e Deploy	Docker, MLflow, Git
Monitoramento	Logs estruturados e métricas via MLflow

Pipeline de Diagnóstico
Upload da Imagem

Pré-processamento (Resize, Normalização, Equalização)

Predição com TensorFlow

Registro no MLflow

Resposta via API

Exibição do Resultado no Frontend

Licença
Este projeto é distribuído sob a Licença MIT.

Autor(a)
Samantha Vico Spezamiglio
Desenvolvedora Full Stack | Especialista em Processamento de Imagens e Inteligência Artificial

Mello Consultoria Empresarial & Inovando Sistemas
Projetos com React, Node.js, .NET, Python e MLflow




