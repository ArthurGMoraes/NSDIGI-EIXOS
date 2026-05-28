from fastapi import APIRouter, HTTPException
from app.database import get_conn
from app.models import AtividadeOut, AtividadeCreate, AcaoOut

router = APIRouter()


@router.post("/{eixo_id}", response_model=AtividadeOut, status_code=201)
def create_atividade(eixo_id: str, body: AtividadeCreate):
    conn = get_conn()
    if not conn.execute("SELECT 1 FROM eixos WHERE id = ?", (eixo_id,)).fetchone():
        conn.close()
        raise HTTPException(404, "Eixo não encontrado")

    # Auto-generate codigo (AT1, AT2, ...)
    existing = conn.execute(
        "SELECT COUNT(*) FROM atividades WHERE eixo_id = ?", (eixo_id,)
    ).fetchone()[0]
    codigo = f"AT{existing + 1}"
    at_id  = f"{eixo_id}-{codigo}"

    conn.execute(
        "INSERT INTO atividades VALUES (?,?,?,?)",
        (at_id, eixo_id, codigo, body.nome),
    )
    conn.commit()
    at = conn.execute("SELECT * FROM atividades WHERE id = ?", (at_id,)).fetchone()
    conn.close()
    return AtividadeOut(id=at["id"], eixo_id=at["eixo_id"], codigo=at["codigo"], nome=at["nome"])


@router.get("/{at_id}", response_model=AtividadeOut)
def get_atividade(at_id: str):
    conn = get_conn()
    at = conn.execute("SELECT * FROM atividades WHERE id = ?", (at_id,)).fetchone()
    if not at:
        raise HTTPException(404, "Atividade não encontrada")
    acoes = conn.execute("SELECT * FROM acoes WHERE at_id = ? ORDER BY id", (at_id,)).fetchall()
    conn.close()
    return AtividadeOut(
        id=at["id"], eixo_id=at["eixo_id"], codigo=at["codigo"], nome=at["nome"],
        acoes=[AcaoOut(**dict(a)) for a in acoes],
    )


@router.delete("/{at_id}", status_code=204)
def delete_atividade(at_id: str):
    conn = get_conn()

    if not conn.execute(
        "SELECT 1 FROM atividades WHERE id = ?",
        (at_id,)
    ).fetchone():
        conn.close()
        raise HTTPException(404, "Atividade não encontrada")

    conn.execute(
        "DELETE FROM acoes WHERE at_id = ?",
        (at_id,)
    )

    conn.execute(
        "DELETE FROM atividades WHERE id = ?",
        (at_id,)
    )

    conn.commit()
    conn.close()
