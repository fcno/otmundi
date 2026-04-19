django-admin makemessages -l en `
  --ignore venv/* `
  --ignore .venv/* `
  --ignore */site-packages/* `
  --ignore */migrations/* `
  --ignore __pycache__/*

django-admin makemessages -l pt_BR `
  --ignore venv/* `
  --ignore .venv/* `
  --ignore */site-packages/* `
  --ignore */migrations/* `
  --ignore __pycache__/*

django-admin compilemessages