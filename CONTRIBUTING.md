# Contributing to Linux Code Agent

Obrigado por considerar contribuir com o **Linux Code Agent** 🚀  
Este projeto está em estágio inicial (MVP funcional) e contribuições são bem-vindas.

---

## 📌 Objetivo do Projeto

Linux Code Agent é um agente de desenvolvimento local que:
- Planeja ações usando LLMs
- Executa ações reais no sistema
- Expõe uma API REST para controle e automação
- Prioriza controle local, auditabilidade e extensibilidade

---

## 🗂 Estrutura do Projeto

Resumo da estrutura principal:

backend/
├── app/
│ ├── api/ # Endpoints HTTP (FastAPI)
│ ├── core/ # Agent, planner, executor e registry
│ ├── services/ # Gerenciamento de tasks e estado
│ ├── schemas/ # Schemas Pydantic
│ ├── tools/ # Tools locais (shell, fs, git)
│ └── config.py # Configuração central

A documentação completa está nos arquivos do projeto.

---

## 🧑‍💻 Como Contribuir

### 1. Fork e Clone

```bash
git clone https://github.com/joaz0/agent_autonomo.git
cd agent_autonomo

2. Crie uma Branch
git checkout -b feature/nome-da-feature

3. Ambiente de Desenvolvimento
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Configure o .env a partir do exemplo:

cp .env.example .env

🧪 Testes

No momento, o projeto está em MVP e possui testes limitados.

Contribuições que adicionem testes são altamente encorajadas.

📝 Padrão de Commits

Utilizamos Conventional Commits:

feat: nova funcionalidade
fix: correção de bug
docs: mudanças em documentação
refactor: refatoração sem mudança de comportamento
test: adição ou ajuste de testes
chore: tarefas auxiliares

Exemplo:

git commit -m "feat: adiciona nova tool de análise de código"

📦 Boas Práticas

Não commitar .env ou secrets

Manter funções de tools pequenas e auditáveis

Separar claramente responsabilidade entre camadas

Evitar lógica de negócio dentro da API layer

Preferir código explícito a “mágico”

🐛 Reportando Problemas

Abra uma Issue contendo:

Descrição clara do problema

Passos para reproduzir

Logs relevantes

Ambiente (OS, Python, versão do projeto)

📄 Licença

Ao contribuir, você concorda que sua contribuição será licenciada sob a MIT License.

Obrigado por contribuir ❤️

---