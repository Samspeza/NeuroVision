Arquivo: docs/api_referencia.md

#  Referência da API – IrisAI Diagnostic System

##  Base URL
http://localhost:5000/api


## Endpoints Principais

### 1. **Upload de Imagem**
Realiza o upload de uma imagem da íris e envia para o modelo de IA.

**POST** `/api/upload`

#### Corpo da Requisição (Form Data)
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|--------------|------------|
| `file` | `image/jpeg` ou `image/png` | ✅ | Imagem da íris para análise |

#### Exemplo de Requisição (curl)
```bash
curl -X POST http://localhost:5000/api/upload \
  -F "file=@iris_sample.jpg"

 Exemplo de Resposta (200)
{
  "message": "Upload concluído com sucesso.",
  "filePath": "uploads/iris_sample.jpg",
  "analysisId": "3f8a2b10-742c-4f2b-b4de-3827f9b2c7f3"
}

2. Execução de Predição (Diagnóstico)

Envia uma imagem previamente carregada para o modelo de IA e retorna o diagnóstico.

POST /api/predict

Corpo da Requisição (JSON)
Campo	Tipo	Obrigatório	Descrição
filePath	string	✅	Caminho da imagem no servidor
Exemplo de Requisição
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"filePath": "uploads/iris_sample.jpg"}'

Exemplo de Resposta (200)
{
  "status": "success",
  "prediction": {
    "class": "Iris Saudável",
    "confidence": 0.94
  },
  "timestamp": "2025-11-13T15:22:08Z",
  "analysisId": "3f8a2b10-742c-4f2b-b4de-3827f9b2c7f3"
}

Possíveis Erros
Código	Mensagem
400	"Arquivo não encontrado ou inválido."
500	"Erro interno durante a predição."
3. Histórico de Diagnósticos

Retorna todos os diagnósticos armazenados no banco de dados.

GET /api/history

Exemplo de Requisição
curl http://localhost:5000/api/history

Exemplo de Resposta (200)
[
  {
    "id": "b18a9f02-01dc-44e7-b51a-c55c71b1b89d",
    "filePath": "uploads/iris1.png",
    "prediction": "Iris Saudável",
    "confidence": 0.97,
    "createdAt": "2025-11-10T14:25:00Z"
  },
  {
    "id": "c92a7f31-dfb0-4f9e-b837-327f121fa34a",
    "filePath": "uploads/iris2.png",
    "prediction": "Sinais de Inflamação",
    "confidence": 0.88,
    "createdAt": "2025-11-12T09:50:00Z"
  }
]

4. Consulta de Diagnóstico Específico

Busca um diagnóstico pelo ID.

GET /api/history/:id

Exemplo de Requisição
curl http://localhost:5000/api/history/3f8a2b10-742c-4f2b-b4de-3827f9b2c7f3

Exemplo de Resposta
{
  "id": "3f8a2b10-742c-4f2b-b4de-3827f9b2c7f3",
  "filePath": "uploads/iris_sample.jpg",
  "prediction": "Iris Saudável",
  "confidence": 0.94,
  "createdAt": "2025-11-13T15:22:08Z"
}

Estrutura Padrão de Erros
{
  "status": "error",
  "message": "Descrição do erro."
}

Autenticação (opcional futura)

A API atual não exige autenticação, mas pode ser estendida com:

JWT Tokens para autenticação de usuários.

Roles (admin, técnico, visitante) para controle de acesso.

Registro de auditoria no banco via middleware Express.

Integração com o Módulo de IA

O backend realiza as chamadas ao modelo TensorFlow salvo em /ml/models/ via script Python.
A comunicação é feita por subprocesso ou microserviço containerizado.