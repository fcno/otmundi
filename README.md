# 🌍 Otmundi - Backend

Sistema de monitoramento e ingestão de dados para mundos e monstros (Open Tibia), desenvolvido com foco em estabilidade técnica, padronização de código e arquitetura resiliente.

## 🎯 Objetivo do Projeto

O Otmundi visa fornecer uma infraestrutura robusta para a gestão de estatísticas de jogo (Kill Stats). O foco principal é a integridade dos dados, garantindo que o ciclo de vida da informação — desde a raspagem (scraping) até a persistência no banco de dados — ocorra sem erros silenciosos ou inconsistências.

## 🏗️ Arquitetura e Estrutura do Sistema

O projeto segue uma arquitetura baseada em camadas para garantir a separação de responsabilidades e facilitar a manutenção:

* **Camada de Ingestão (Providers)**: Responsável pela comunicação externa e normalização primária dos dados brutos. Utiliza `TypedDict` para garantir contratos de dados rígidos desde a entrada.
* **Camada de Serviços (Services)**: Contém a lógica de negócio central. Realiza a sanitização de dados (trimming e conversão de vazios para nulos) e orquestra a validação antes da persistência.
* **Camada de Persistência (Repositories)**: Abstrai a lógica do banco de dados (Django ORM), permitindo que o serviço foque na regra de negócio enquanto o repositório lida com a criação de registros e relacionamentos complexos.
* **Helpers e Validadores**: Utilitários globais para sanitização recursiva e um pipeline de validação/normalização que assegura que apenas dados válidos cheguem ao banco.

## 📂 Fluxo de Gestão de Arquivos (Data Pipeline)

O sistema gerencia o estado da ingestão através de uma estrutura de diretórios na raiz do projeto:

* `data/pending/`: Local para colocar novos arquivos JSON para processamento.
* `data/imported/`: Arquivos processados com sucesso são movidos para cá automaticamente.
* `data/error/`: Arquivos que falharam na validação ou processamento são movidos para cá para análise.

## 🛠️ Tecnologias e Estratégia de Qualidade

* **Framework**: Django e Django REST Framework.
* **Banco de Dados**: PostgreSQL (escolhido pela robustez e suporte a tipos complexos).
* **I18n**: Suporte total a localização e tradução via arquivos `.po/.mo` (Locales).
* **Análise Estática**: Uso rigoroso de `Mypy` para verificação de tipos e `Ruff/Black` para padronização de estilo.
* **Testes**: Suite baseada em `Pytest` com foco em testes de integração reais, garantindo que o fluxo Payload -> Service -> Repository -> DB funcione integralmente.

---

## 🚀 Guia de Configuração Passo a Passo

### 1. Clonar e Acessar o Projeto

`powershell
git clone <https://github.com/seu-usuario/otmundi.git>
cd otmundi
`

### 2. Criar e Ativar o Ambiente Virtual (venv)

`powershell
python -m venv venv

# Ativar no Windows (PowerShell)
.\\\\venv\\\\Scripts\\\\activate

# Ativar no Linux ou Mac
source venv/bin/activate
`

### 3. Instalar Todas as Dependências

`powershell
# Instala o projeto e as ferramentas de dev (Ruff, Black, Mypy, Pytest)
pip install -e ".[dev]"
`

### 4. Configurar Variáveis de Ambiente (.env)

Crie um arquivo chamado `.env` na raiz do projeto, copiando o conteúdo do `.env.example` e ajustando suas credenciais de banco de dados e chaves de segurança.

### 5. Inicializar o Django

`powershell
# Criar as tabelas, carregar traduções e rodar o servidor
python manage.py migrate
python manage.py compilemessages
python manage.py runserver
`

---

## ⚙️ Operações: Ingestão de Dados

Para processar arquivos de estatísticas que estão na pasta `data/pending/`, utilize o Management Command dedicado:

`powershell
# O comando processa o arquivo e o move conforme o resultado (Success ou Error)
python manage.py ingest_killstats nome_do_arquivo.json
`

---

## 🧪 Qualidade de Código e Testes

O projeto utiliza um pipeline de validação para impedir a entrada de código que não siga os padrões estabelecidos:

* **Validação Completa**: `.\\\\scripts\\\\validate.ps1`
* **Rodar Testes**: `pytest` (Os testes garantem a integridade de todos os campos de métricas e o isolamento de locales).
* **Formatar Código**: `black .`
* **Verificar Linter**: `ruff check . --fix`
* **Análise de Tipos**: `mypy .` (Obrigatório passar sem erros de análise semântica).

---

## 📜 Padronização de Commits

Para manter o histórico do Git organizado, sempre utilize o padrão do projeto (Commitizen):

`powershell
cz commit
`

---

## 📂 Organização de Pastas Importantes

* `apps/ingestion`: Lógica de entrada de dados, Providers, Services e Commands.
* `apps/core`: Helpers de sanitização, validadores base e exceções customizadas.
* `apps/snapshots`: Modelos de dados para registros históricos.
* `apps/killstats`: Modelos específicos de estatísticas de morte por criatura.
* `data/`: Estrutura de diretórios para o pipeline de arquivos (pending, imported, error).