#  Guia de Instalação e Configuração – IrisAI Diagnostic System

Este guia orienta a instalação do ambiente completo do **IrisAI**, composto por:
-  **Módulo de Inteligência Artificial** (Python + TensorFlow)
-  **API Backend** (Node.js + Express)
-  **Frontend Web** (React + Tailwind)
-  **Containerização via Docker Compose**

---

## 1. Pré-requisitos

Antes de iniciar, garanta que o ambiente possua:

| Dependência | Versão Recomendada | Observações |
|--------------|--------------------|--------------|
| **Python** | 3.10+ | Necessário para IA |
| **Node.js** | 20.x | Backend e Frontend |
| **npm** ou **yarn** | Última | Gerenciamento de pacotes |
| **Docker + Docker Compose** | 24.x | Execução containerizada |
| **Git** | Qualquer | Clonagem do repositório |

---

## 2. Clonando o Repositório

```bash
git clone https://github.com/seuusuario/irisai-diagnostic.git
cd irisai-diagnostic
3. Configuração do Ambiente Python
Entre na pasta de IA:

bash
Copiar código
cd ml
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Instale as dependências:

bash
Copiar código
pip install -r requirements.txt
O arquivo requirements.txt inclui:

nginx
Copiar código
tensorflow
numpy
opencv-python
flask
mlflow
pillow
4. Configuração da API Node.js
bash
Copiar código
cd backend
npm install
Crie o arquivo .env com as variáveis:

env
Copiar código
PORT=5000
MONGO_URI=mongodb://localhost:27017/irisai
ML_MODEL_PATH=../ml/models/model.h5
Execute localmente:

bash
Copiar código
npm run dev
A API será iniciada em:

arduino
Copiar código
http://localhost:5000
5. Configuração do Frontend React
bash
Copiar código
cd AI-Diagnostic-System\frontend
npm install
npm start
O frontend será iniciado em:

arduino
Copiar código
http://localhost:3000
6. Execução via Docker Compose
Para rodar toda a aplicação com um único comando:

bash
Copiar código
docker compose up --build
Estrutura de pastas esperada:
Copiar código
irisai-diagnostic/
│
├── backend/
├── frontend/
├── ml/
├── docker-compose.yml
└── docs/
Exemplo de docker-compose.yml
yaml
Copiar código
version: "3.9"
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    env_file: ./backend/.env
    depends_on:
      - mongo
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  mongo:
    image: mongo
    container_name: irisai_db
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
volumes:
  mongo_data:
🧩 7. Teste do Sistema Completo
Após tudo estar em execução:

Acesse o frontend em http://localhost:3000

Faça upload de uma imagem da íris

A API enviará a imagem para o modelo TensorFlow

O resultado será exibido na tela com:

Classe predita (ex: “Iris Saudável”)

Grau de confiança (ex: 94%)

8. Solução de Problemas
Erro	Causa	Solução
ModuleNotFoundError: tensorflow	Ambiente virtual não ativo	Ative o venv antes de executar
ECONNREFUSED 5000	API não iniciada	Execute npm run dev no backend
Docker build failed	Docker antigo	Atualize Docker Engine e Compose

9. Implantação (Produção)
Para deploy em servidor Linux:

bash
Copiar código
docker compose -f docker-compose.prod.yml up -d
Inclua NGINX reverso com SSL via Let’s Encrypt.

Configure variáveis de ambiente seguras.

Utilize MLflow tracking remoto se desejar auditoria de modelos.

10. Estrutura Final do Projeto
bash
Copiar código
irisai-diagnostic/
├── backend/          # API Express
├── frontend/         # React Web App
├── ml/               # Modelos e scripts de IA
├── docs/             # Documentação técnica
├── docker-compose.yml
└── README.md
Sistema pronto!
Você pode iniciar o IrisAI localmente ou via Docker, realizar diagnósticos e expandir o modelo conforme novas coletas de dados.

Copiar código
 Desenvolvido com Python, Node.js, React e TensorFlow.