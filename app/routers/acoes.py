from fastapi import APIRouter, HTTPException
from app.database import get_conn
from app.models import AcaoOut, AcaoCreate, AcaoStatusUpdate

router = APIRouter()

STATUS_VALIDOS = {"Não iniciado", "Em andamento", "Concluído", "Atrasado", "Bloqueado"}


@router.post("/{at_id}", response_model=AcaoOut, status_code=201)
def create_acao(at_id: str, body: AcaoCreate):
    conn = get_conn()
    if not conn.execute("SELECT 1 FROM atividades WHERE id = ?", (at_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Atividade não encontrada")
    cur = conn.execute(
        "INSERT INTO acoes (at_id, descricao, areas, inicio, termino) VALUES (?,?,?,?,?)",
        (at_id, body.descricao, body.areas, body.inicio, body.termino),
    )
    conn.commit()
    a = conn.execute("SELECT * FROM acoes WHERE id = ?", (cur.lastrowid,)).fetchone()
    conn.close()
    return AcaoOut(**dict(a))


@router.get("/atrasadas", response_model=list[AcaoOut])
def get_atrasadas():
    from datetime import date
    conn = get_conn()
    acoes = conn.execute("SELECT * FROM acoes WHERE status != 'Concluído' AND termino IS NOT NULL").fetchall()
    result = [AcaoOut(**dict(a)) for a in acoes if _parse_date(a["termino"]) and _parse_date(a["termino"]) < date.today()]
    conn.close()
    return result


@router.patch("/{acao_id}/status", response_model=AcaoOut)
def update_status(acao_id: int, body: AcaoStatusUpdate):
    if body.status not in STATUS_VALIDOS:
        raise HTTPException(400, f"Status inválido. Use: {STATUS_VALIDOS}")
    conn = get_conn()
    if not conn.execute("SELECT 1 FROM acoes WHERE id = ?", (acao_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Ação não encontrada")
    conn.execute(
        "UPDATE acoes SET status = ?, tendencia = ?, updated_at = datetime('now') WHERE id = ?",
        (body.status, body.tendencia, acao_id),
    )
    conn.commit()
    a = conn.execute("SELECT * FROM acoes WHERE id = ?", (acao_id,)).fetchone()
    conn.close()
    return AcaoOut(**dict(a))


@router.delete("/{acao_id}", status_code=204)
def delete_acao(acao_id: int):
    conn = get_conn()
    if not conn.execute("SELECT 1 FROM acoes WHERE id = ?", (acao_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Ação não encontrada")
    conn.execute("DELETE FROM acoes WHERE id = ?", (acao_id,))
    conn.commit()
    conn.close()


@router.get("/{acao_id}", response_model=AcaoOut)
def get_acao(acao_id: int):
    conn = get_conn()
    a = conn.execute("SELECT * FROM acoes WHERE id = ?", (acao_id,)).fetchone()
    conn.close()
    if not a:
        raise HTTPException(404, "Ação não encontrada")
    return AcaoOut(**dict(a))


def _parse_date(s: str):
    from datetime import date
    try:
        d, m, y = s.split("/")
        return date(int(y), int(m), int(d))
    except Exception:
        return None
