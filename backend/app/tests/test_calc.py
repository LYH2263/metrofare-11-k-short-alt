import importlib
import json

from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import shortest_hops, two_simple_paths
from app.engines.route_quote import quote_route

EDGES = [("A1", "A2"), ("A2", "A3"), ("A2", "B1"), ("B1", "B2")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]

# 环线：A1-A2-A3 两站，A1-X-Y-A3 三站
RING = [("A1", "A2"), ("A2", "A3"), ("A1", "X"), ("X", "Y"), ("Y", "A3")]
# 菱形：A1 到 A3 两条等长（2 站）路径，不存在严格更长的简单路
DIAMOND = [("A1", "A2"), ("A2", "A3"), ("A1", "X"), ("X", "A3")]
# 三角形：直达 1 站，绕行 2 站
TRIANGLE = [("A1", "A2"), ("A2", "A3"), ("A1", "A3")]


def test_hops_a1_a3():
    assert shortest_hops(EDGES, "A1", "A3") == 2


def test_hops_a1_b2():
    assert shortest_hops(EDGES, "A1", "B2") == 3


def test_fare_by_hops():
    assert fare_for_hops(2, RULES) == 3.0
    assert fare_for_hops(3, RULES) == 4.0
    assert fare_for_hops(10, RULES) == 6.0


def test_quote():
    q = quote_route(EDGES, "A1", "B2", RULES)
    assert q["hops"] == 3 and q["fare"] == 4.0


def test_tree_has_no_second():
    """树中两点间只有一条简单路，次短必须为空，不得复制最短路。"""
    shortest, second = two_simple_paths(EDGES, "A1", "B2")
    assert shortest == ["A1", "A2", "B1", "B2"]
    assert second is None
    q = quote_route(EDGES, "A1", "B2", RULES)
    assert q["path"] == shortest
    assert q["second"] is None


def test_ring_second_is_strictly_longer_simple_path():
    shortest, second = two_simple_paths(RING, "A1", "A3")
    assert shortest == ["A1", "A2", "A3"]
    assert second == ["A1", "X", "Y", "A3"]
    assert len(second) - 1 > len(shortest) - 1
    assert len(second) == len(set(second))  # 简单路：无重复站
    q = quote_route(RING, "A1", "A3", RULES)
    assert q["hops"] == 2 and q["fare"] == 3.0
    assert q["second"] == {"hops": 3, "fare": 4.0, "path": ["A1", "X", "Y", "A3"]}


def test_triangle_second_detour():
    shortest, second = two_simple_paths(TRIANGLE, "A1", "A3")
    assert shortest == ["A1", "A3"]
    assert second == ["A1", "A2", "A3"]


def test_equal_length_alternative_is_not_second():
    """等长的另一条路不算次短，严格更长的简单路不存在时为空。"""
    shortest, second = two_simple_paths(DIAMOND, "A1", "A3")
    assert len(shortest) - 1 == 2
    assert second is None


def test_unreachable():
    q = quote_route([("A1", "A2")], "A1", "B2", RULES)
    assert q["reachable"] is False and q["hops"] is None and q["second"] is None


def test_persist_stores_shortest_only_and_edge_delete_promotes_second(monkeypatch, tmp_path):
    """删边后旧次短成为新最短；已写入的最短路记录不被改成次短。"""
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from app import config, db
    from app.services import metro_service
    importlib.reload(config)
    importlib.reload(db)
    importlib.reload(metro_service)

    svc = metro_service.MetroService()
    conn = svc._conn
    conn.executescript(
        """
        CREATE TABLE stations(id INTEGER PRIMARY KEY, code TEXT, name TEXT);
        CREATE TABLE edges(a TEXT, b TEXT);
        CREATE TABLE fare_rules(id INTEGER PRIMARY KEY, max_hops INTEGER, price REAL);
        CREATE TABLE settings(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE calc_runs(
            id INTEGER PRIMARY KEY, kind TEXT, input_json TEXT, result_json TEXT, created_at TEXT);
        """
    )
    for a, b in RING:
        conn.execute("INSERT INTO edges(a,b) VALUES (?,?)", (a, b))
    conn.executemany(
        "INSERT INTO fare_rules(max_hops, price) VALUES (?,?)",
        [(2, 3.0), (4, 4.0), (None, 6.0)],
    )
    conn.commit()

    first = svc.quote("A1", "A3", persist=True)
    assert first["path"] == ["A1", "A2", "A3"]
    assert first["second"]["path"] == ["A1", "X", "Y", "A3"]
    assert first["run_id"] is not None

    # 落库记录只含最短路，不含次短对照
    stored = json.loads(conn.execute("SELECT result_json FROM calc_runs WHERE id=?",
                                     (first["run_id"],)).fetchone()["result_json"])
    assert stored["hops"] == 2 and stored["path"] == ["A1", "A2", "A3"]
    assert "second" not in stored

    # 删掉最短路上的一条边：旧次短变成新最短，且不再有严格更长的简单路
    svc.delete_edge("A1", "A2")
    after = svc.quote("A1", "A3", persist=False)
    assert after["path"] == ["A1", "X", "Y", "A3"]
    assert after["hops"] == 3 and after["fare"] == 4.0
    assert after["second"] is None

    # 早先写入的最短路记录保持原样
    stored_again = json.loads(conn.execute("SELECT result_json FROM calc_runs WHERE id=?",
                                           (first["run_id"],)).fetchone()["result_json"])
    assert stored_again == stored
    svc.close()
