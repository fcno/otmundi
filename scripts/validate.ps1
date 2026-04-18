Write-Host "Ruff (qualidade e erros obvios)..."
ruff check . --fix
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Black (padronizacao)..."
black .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Mypy (analise semantica)..."
mypy .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Testes..."
python manage.py test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Projeto validado com sucesso!"