from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routers import eixos, atividades, acoes

app = FastAPI(
    title="OKR Saúde Digital — Microrregião BH",
    description="API de acompanhamento dos OKRs do Plano Local de Saúde Digital",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

app.include_router(eixos.router, prefix="/eixos", tags=["Eixos"])
app.include_router(atividades.router, prefix="/atividades", tags=["Atividades"])
app.include_router(acoes.router, prefix="/acoes", tags=["Ações"])

@app.get("/health")
def health():
    return {"status": "ok"}
