from pydantic import BaseModel
from typing import Optional, List

# outputs
class AcaoOut(BaseModel):
    id: int
    at_id: str
    descricao: str
    areas: Optional[str]
    inicio: Optional[str]
    termino: Optional[str]
    status: str
    tendencia: Optional[str]
    updated_at: Optional[str]


class AtividadeOut(BaseModel):
    id: str
    eixo_id: str
    codigo: str
    nome: str
    acoes: List[AcaoOut] = []


class EixoOut(BaseModel):
    id: str
    numero: str
    nome: str
    icone: Optional[str]
    cor: Optional[str]
    objetivo: Optional[str]
    descricao: Optional[str]
    atividades: List[AtividadeOut] = []


class EixoSummary(BaseModel):
    id: str
    numero: str
    nome: str
    icone: Optional[str]
    cor: Optional[str]
    total_acoes: int
    concluidas: int
    em_andamento: int
    atrasadas: int
    progresso_pct: float


# inputs

class AcaoStatusUpdate(BaseModel):
    status: str
    tendencia: Optional[str] = None


class EixoCreate(BaseModel):
    numero: str
    nome: str
    icone: Optional[str] = "📋"
    cor: Optional[str] = "#64748b"
    objetivo: Optional[str] = ""
    descricao: Optional[str] = ""


class AtividadeCreate(BaseModel):
    nome: str


class AcaoCreate(BaseModel):
    descricao: str
    areas: Optional[str] = ""
    inicio: Optional[str] = ""
    termino: Optional[str] = ""
