# OKR Saúde Digital — Microrregião BH

Painel de acompanhamento dos OKRs do Plano Local de Saúde Digital da microrregião de Belo Horizonte (BH, Nova Lima, Santa Luzia).

Permite que equipes acompanhem e atualizem o status de ações distribuídas em 3 eixos estratégicos: Formação e Desenvolvimento, Telessaúde, e Monitoramento e Informações.

---

## Como rodar

**Requisitos:** Python 3.10+

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 3. Subir a API
uvicorn app.main:app --reload
```

Abrir `frontend/index.html` no navegador.  
A documentação da API fica em `http://localhost:8000/docs`.

---

## Arquitetura

```
okr_bh/
├── app/
│   ├── main.py          # Entrypoint FastAPI
│   ├── database.py      # Conexão SQLite e criação das tabelas
│   ├── models.py        # Schemas de entrada e saída (Pydantic)
│   ├── seed_data.py     # Dados iniciais dos eixos
│   └── routers/
│       ├── eixos.py     # CRUD de eixos
│       ├── atividades.py# CRUD de atividades
│       └── acoes.py     # CRUD de ações + atualização de status
├── frontend/
│   ├── index.html       # Interface web
│   ├── style.css        # Estilos JS puro
│   └── script.js
└── eixos.db            # Banco SQLite (gerado automaticamente)
```

**Stack:** FastAPI + SQLite no backend, HTML/CSS/JS puro no frontend.