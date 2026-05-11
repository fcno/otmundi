# 🌍 Otmundi - Backend

Sistema de monitoramento e ingestão de dados para mundos e monstros (Open Tibia), desenvolvido com foco em estabilidade técnica, padronização de código e arquitetura resiliente.

## 🎯 Objetivo do Projeto

O Otmundi fornece uma infraestrutura robusta para a gestão de estatísticas de jogo. O foco principal é a integridade dos dados, garantindo que o ciclo de vida da informação — desde a extração até a persistência — ocorra sem inconsistências.

O sistema utiliza um motor de aprendizado automático para prever janelas de spawn baseadas em dados históricos e oferece uma interface de curadoria dedicada, permitindo que administradores validem as sugestões do sistema e realizem o ajuste fino das configurações de cada criatura.

## 🏗️ Arquitetura e Estrutura do Sistema

O projeto segue uma arquitetura baseada em camadas para garantir a separação de responsabilidades e facilitar a manutenção:

* **Camada de Ingestão (Providers)**: Responsável pela comunicação externa e normalização primária dos dados brutos. Utiliza `TypedDict` para garantir contratos de dados rígidos desde a entrada.
* **Camada de Serviços (Services)**: Contém a lógica de negócio central. Realiza a sanitização de dados, orquestra a validação e gerencia o `ConfigLearningService` para recalibração de intervalos.
* **Camada de Eventos (Signals)**: Automação que utiliza Django Signals para disparar o aprendizado das configurações sempre que uma nova morte ou "puff" é registrado.
* **Camada de Persistência (Repositories)**: Abstrai a lógica do banco de dados (Django ORM), permitindo que o serviço foque na regra de negócio enquanto o repositório lida com a criação de registros.
* **Camada de Interface (UI/Templates)**: Interface responsiva construída com Tailwind CSS v4 e DaisyUI. Utiliza HTMX para interações dinâmicas e possui um sistema centralizado de Toasts (notificações) com lógica de auto-dismiss e pause-on-hover.
* **Estrutura de Módulos**: Todos os apps estão concentrados no diretório apps/. O projeto exige o uso de imports absolutos (ex: from apps.app_name...) para garantir a integridade do registro de modelos e evitar conflitos de namespace.

## 🧠 Motor de Aprendizado (Config Learning)

O sistema analisa automaticamente o histórico de eventos para gerar inteligência sobre o comportamento das criaturas:

* **Detecção de Janelas**: Identifica os intervalos mínimo e máximo observados entre aparições.
* **Tratamento de Outliers**: Filtra ruídos estatísticos ignorando intervalos inconsistentes.
* **Puff & Kill**: Trata desaparecimentos (puffs) e mortes confirmadas com o mesmo peso para o reset da janela de spawn.
* **Curadoria Humana**: As predições geradas pelo motor são apresentadas em uma interface dedicada para validação e ajuste fino por administradores.

## 📂 Fluxo de Gestão de Arquivos (Data Pipeline)

O sistema gerencia a ingestão de forma segmentada por tipo de dado. Cada módulo possui sua própria estrutura sob o diretório `data/`:

* `data/<modulo>/pending/`: Local para novos arquivos JSON para processamento. (ex: `data/killstats/pending/`).
* `data/<modulo>/imported/`: Arquivos processados com sucesso.
* `data/<modulo>/error/`: Arquivos que falharam na validação, preservados para análise técnica.


## 🛠️ Tecnologias e Estratégia de Qualidade

* **Backend**: Django com PostgreSQL, utilizando Window Functions (LAG) para análise temporal de alta performance.
* **Frontend**: Tailwind CSS v4, DaisyUI e HTMX para uma interface moderna e interações assíncronas.
* **Qualidade de Código**: Uso rigoroso de `Mypy` (tipagem), `Ruff` (linter) e `Black` (formatador).
* **I18n**: Suporte total a tradução via tags de localização do Django em templates e código.
* **Testes**: Suíte baseada em `Pytest`, garantindo a integridade dos modelos, cálculos de predição e regras de negócio como a exclusão mútua de preferências.

---

## 🚀 Guia de Configuração Passo a Passo

### 1. Clonar e Acessar o Projeto

`powershell
git clone <https://github.com/fcno/otmundi.git>
cd otmundi
`

### 2. Criar e Ativar o Ambiente Virtual (venv)

`powershell
python -m venv venv

# Ativar no Windows (PowerShell)
.\venv\Scripts\activate

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

### 6. Inicializar o Frontend (Tailwind CSS v4)

Como o projeto utiliza Tailwind v4 com DaisyUI, você precisa compilar os estilos para que a interface e os Toasts apareçam corretamente:

`powershell
# Instala as dependências do Node
npm install

# Compila e monitora mudanças no CSS
npx tailwindcss -i ./theme/static_src/src/styles.css -o ./theme/static/css/dist/styles.css --watch

ou

python manage.py tailwind start
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

* **Validação Completa**: `.\scripts\validate.ps1`
* **Rodar Testes**: `pytest` (Garante a integridade das métricas, o isolamento de locales, a exclusão mútua de preferências e o registro único de modelos).
* **Formatar Código**: `black .`
* **Verificar Linter**: `ruff check . --fix`
* **Análise de Tipos**: `mypy .` (Obrigatório passar sem erros de análise semântica para garantir contratos de dados).

---

## 📜 Padronização de Commits

Para manter o histórico do Git organizado, sempre utilize o padrão do projeto (Commitizen):

`powershell
cz commit
`

---

## 📂 Organização de Pastas Importantes

Para evitar conflitos de namespace e garantir a escalabilidade, todos os aplicativos residem no diretório `apps/` e devem ser referenciados via imports absolutos:

* **apps/engine**: Lógica de ingestão de dados, processamento de `killstats`, aprendizado das configurações e a interface de Curadoria.
* **apps/game_data**: Definições centrais do domínio, como Monstros e Mundos.
* **apps/identity**: Gestão de usuários, autenticação e preferências.
* **apps/core**: Helpers de sanitização, validadores base, utilitários de tradução e exceções customizadas.
* **apps/snapshots**: Registro histórico e estados temporais do jogo.
* **data/**: Estrutura de diretórios para o pipeline de arquivos (pending, imported, error).