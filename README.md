# 🌍 Otmundi - Backend

Sistema de monitoramento de mundos e monstros desenvolvido com Django e Django REST Framework.

## 🚀 Guia de Configuração Passo a Passo

Siga estes comandos no seu terminal para preparar o ambiente do zero:

### 1. Clonar e Acessar o Projeto

```powershell
git clone <https://github.com/seu-usuario/otmundi.git>
cd otmundi
```

### 2. Criar e Ativar o Ambiente Virtual (venv)

1. Criar o ambiente

```powershell
python -m venv venv

# Ativar no Windows (PowerShell)
.\venv\Scripts\activate

# Ativar no Linux ou Mac
source venv/bin/activate
```

### 3. Instalar Todas as Dependências

```powershell
# Instala o projeto e as ferramentas de dev (Ruff, Black, Mypy, Pytest)
pip install -e ".[dev]"
```

### 4. Configurar Variáveis de Ambiente (.env)

Crie um arquivo chamado `.env` na raiz do projeto, copiando o conteúdo do `.env.example` e ajustando suas credenciais:

### 5. Inicializar o Django

```powershell
# Criar as tabelas e rodar o servidor
python manage.py migrate
python manage.py runserver
```

---

## 🧪 Qualidade de Código e Testes

* Validação Completa: `.\scripts\validate.ps1`
* Rodar Testes: `pytest`
* Formatar Código: `black .`
* Verificar Linter: `ruff check . --fix`
* Análise de Tipos: `mypy .`

---

## 📜 Padronização de Commits

Sempre utilize o padrão do projeto para novos commits:

```powershell
cz commit
```
