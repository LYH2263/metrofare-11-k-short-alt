import sqlite3


def list_pairs(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    return [(r["a"], r["b"]) for r in conn.execute("SELECT a,b FROM edges").fetchall()]


def delete_pair(conn: sqlite3.Connection, a: str, b: str) -> None:
    conn.execute("DELETE FROM edges WHERE (a=? AND b=?) OR (a=? AND b=?)", (a, b, b, a))
    conn.commit()
