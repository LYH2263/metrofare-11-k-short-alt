import sqlite3


def list_pairs(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    return [(r["a"], r["b"]) for r in conn.execute("SELECT a,b FROM edges").fetchall()]


def add_pair(conn: sqlite3.Connection, a: str, b: str) -> bool:
    """Insert an undirected edge; no-op if the pair already exists."""
    exists = conn.execute(
        "SELECT 1 FROM edges WHERE (a=? AND b=?) OR (a=? AND b=?)", (a, b, b, a)
    ).fetchone()
    if exists:
        return False
    conn.execute("INSERT INTO edges(a,b) VALUES (?,?)", (a, b))
    conn.commit()
    return True


def delete_pair(conn: sqlite3.Connection, a: str, b: str) -> int:
    """Delete an undirected edge either orientation; returns rows removed."""
    cur = conn.execute(
        "DELETE FROM edges WHERE (a=? AND b=?) OR (a=? AND b=?)", (a, b, b, a)
    )
    conn.commit()
    return cur.rowcount
