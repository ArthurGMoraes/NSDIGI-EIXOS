from fastapi import APIRouter, HTTPException
from app.database import get_conn
from app.models import EixoOut, EixoSummary, EixoCreate, AtividadeOut, AcaoOut
import re

router = APIRouter()


@router.get("/", response_model=list[EixoSummary])
def list_eixos():
    conn = get_conn()
    eixos = conn.execute("SELECT * FROM eixos ORDER BY numero").fetchall()
    result = []
    for e in eixos:
        acoes = conn.execute(
            "SELECT a.status, a.termino FROM acoes a JOIN atividades at ON at.id = a.at_id WHERE at.eixo_id = ?",
            (e["id"],),
        ).fetchall()
        total      = len(acoes)
        concluidas = sum(1 for a in acoes if a["status"] == "Concluído")
        em_andamento = sum(1 for a in acoes if a["status"] == "Em andamento")
        atrasadas  = sum(1 for a in acoes if a["status"] not in ("Concluído",) and a["termino"] and _is_overdue(a["termino"]))
        prog       = round(((concluidas + em_andamento * 0.5) / total * 100) if total else 0, 1)
        result.append(EixoSummary(
            id=e["id"], numero=e["numero"], nome=e["nome"],
            total_acoes=total, concluidas=concluidas,
            em_andamento=em_andamento, atrasadas=atrasadas,
            progresso_pct=prog,
        ))
    conn.close()
    return result


@router.post("/", response_model=EixoOut, status_code=201)
def create_eixo(body: EixoCreate):
    conn = get_conn()
    
    eixo_id = f"E{body.numero}"
    if conn.execute("SELECT 1 FROM eixos WHERE id = ?", (eixo_id,)).fetchone():
        conn.close()
        raise HTTPException(409, f"Eixo {eixo_id} já existe")
    conn.execute(
        "INSERT INTO eixos VALUES (?,?,?,?,?)",
        (eixo_id, body.numero, body.nome, body.objetivo, body.descricao),
    )
    conn.commit()
    e = conn.execute("SELECT * FROM eixos WHERE id = ?", (eixo_id,)).fetchone()
    conn.close()
    return EixoOut(**dict(e))


@router.get("/{eixo_id}", response_model=EixoOut)
def get_eixo(eixo_id: str):
    conn = get_conn()
    e = conn.execute("SELECT * FROM eixos WHERE id = ?", (eixo_id,)).fetchone()
    if not e:
        raise HTTPException(404, "Eixo não encontrado")
    atividades = conn.execute(
        "SELECT * FROM atividades WHERE eixo_id = ? ORDER BY codigo", (eixo_id,)
    ).fetchall()
    ats_out = []
    for at in atividades:
        acoes = conn.execute("SELECT * FROM acoes WHERE at_id = ? ORDER BY id", (at["id"],)).fetchall()
        ats_out.append(AtividadeOut(
            id=at["id"], eixo_id=at["eixo_id"], codigo=at["codigo"], nome=at["nome"],
            acoes=[AcaoOut(**dict(a)) for a in acoes],
        ))
    conn.close()
    return EixoOut(id=e["id"], numero=e["numero"], nome=e["nome"],
                   objetivo=e["objetivo"], descricao=e["descricao"],
                   atividades=ats_out)


@router.delete("/{eixo_id}", status_code=204)
def delete_eixo(eixo_id: str):
    conn = get_conn()

    if not conn.execute(
        "SELECT 1 FROM eixos WHERE id = ?",
        (eixo_id,)
    ).fetchone():
        conn.close()
        raise HTTPException(404, "Eixo não encontrado")

    # deleta ações do eixo
    conn.execute("""
        DELETE FROM acoes
        WHERE at_id IN (
            SELECT id FROM atividades WHERE eixo_id = ?
        )
    """, (eixo_id,))

    # deleta atividades do eixo
    conn.execute(
        "DELETE FROM atividades WHERE eixo_id = ?",
        (eixo_id,)
    )

    # deleta eixo
    conn.execute(
        "DELETE FROM eixos WHERE id = ?",
        (eixo_id,)
    )

    conn.commit()
    conn.close()


def _is_overdue(termino: str) -> bool:
    from datetime import date
    try:
        d, m, y = termino.split("/")
        return date(int(y), int(m), int(d)) < date.today()
    except Exception:
        return False
