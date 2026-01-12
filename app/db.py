import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("app.db")


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict처럼 접근 가능
    return conn


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                action TEXT NOT NULL,
                model TEXT NOT NULL,
                input TEXT NOT NULL,
                output TEXT NOT NULL
            )
            """
        )
        conn.commit()


def insert_history(timestamp: str, action: str, model: str, input_text: str, output_text: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO history (timestamp, action, model, input, output)
            VALUES (?, ?, ?, ?, ?)
            """,
            (timestamp, action, model, input_text, output_text),
        )
        conn.commit()
        return int(cur.lastrowid)


def list_history(q: str = "", action: str = "all", limit: int = 50) -> List[Dict[str, Any]]:
    q = (q or "").strip()
    action = (action or "all").strip()

    where = []
    params: List[Any] = []

    if action != "all":
        where.append("action = ?")
        params.append(action)

    if q:
        where.append("(input LIKE ? OR output LIKE ?)")
        like = f"%{q}%"
        params.extend([like, like])

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    sql = f"""
        SELECT id, timestamp, action, model,
               substr(input, 1, 120) AS input_preview,
               substr(output, 1, 120) AS output_preview
        FROM history
        {where_sql}
        ORDER BY id DESC
        LIMIT ?
    """
    params.append(limit)

    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]


def get_history(history_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, timestamp, action, model, input, output FROM history WHERE id = ?",
            (history_id,),
        ).fetchone()
        return dict(row) if row else None
