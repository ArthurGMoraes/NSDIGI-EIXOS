import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "eixos.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS eixos (
            id       TEXT PRIMARY KEY,
            numero   TEXT NOT NULL,
            nome     TEXT NOT NULL,
            icone    TEXT,
            cor      TEXT,
            objetivo TEXT,
            descricao TEXT
        );

        CREATE TABLE IF NOT EXISTS atividades (
            id       TEXT PRIMARY KEY,
            eixo_id  TEXT NOT NULL REFERENCES eixos(id),
            codigo   TEXT NOT NULL,
            nome     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS acoes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            at_id     TEXT NOT NULL REFERENCES atividades(id),
            descricao TEXT NOT NULL,
            areas     TEXT,
            inicio    TEXT,
            termino   TEXT,
            status    TEXT DEFAULT 'Não iniciado',
            tendencia TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        );
    """)

    # Seed only if empty
    if cur.execute("SELECT COUNT(*) FROM eixos").fetchone()[0] == 0:
        _seed(cur)

    conn.commit()
    conn.close()


def _seed(cur):
    from app.seed_data import EIXOS
    for e in EIXOS:
        cur.execute(
            "INSERT INTO eixos VALUES (?,?,?,?,?,?,?)",
            (e["id"], e["numero"], e["nome"], e["icone"], e["cor"], e["objetivo"], e["descricao"]),
        )
        for at in e["atividades"]:
            cur.execute(
                "INSERT INTO atividades VALUES (?,?,?,?)",
                (at["id"], e["id"], at["codigo"], at["nome"]),
            )
            for a in at["acoes"]:
                cur.execute(
                    "INSERT INTO acoes (at_id, descricao, areas, inicio, termino) VALUES (?,?,?,?,?)",
                    (at["id"], a["descricao"], a["areas"], a["inicio"], a["termino"]),
                )
