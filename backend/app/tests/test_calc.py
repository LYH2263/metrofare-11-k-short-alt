from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import second_simple_path, shortest_hops, shortest_path
from app.engines.route_quote import quote_route

EDGES = [("A1", "A2"), ("A2", "A3"), ("A2", "B1"), ("B1", "B2")]
RULES = [{"max_hops": 2, "price": 3.0}, {"max_hops": 4, "price": 4.0}, {"max_hops": None, "price": 6.0}]
# 三角+尾巴：A→C 最短 1 站，次短 2 站
TRI = [("A", "B"), ("B", "C"), ("C", "A"), ("C", "D")]
# 双通道：S→T 最短 2 站，次短 3 站；删掉最短路上的一条边后旧次短变新最短
DIA = [("S", "X"), ("X", "T"), ("S", "Y"), ("Y", "Z"), ("Z", "T")]


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


def test_shortest_path_stations():
    assert shortest_path(EDGES, "A1", "B2") == ["A1", "A2", "B1", "B2"]
    assert shortest_path(EDGES, "A1", "A1") == ["A1"]
    assert shortest_path(EDGES, "A1", "ZZ") is None


def test_second_simple_path_strictly_longer():
    alt = second_simple_path(TRI, "A", "C")
    assert alt == ["A", "B", "C"]
    assert len(alt) > len(shortest_path(TRI, "A", "C"))


def test_second_simple_path_none_on_tree():
    # 树图上任意两站只有一条简单路，次短必须为空而不是复制最短
    assert second_simple_path(EDGES, "A1", "B2") is None
    assert second_simple_path(EDGES, "A1", "A1") is None


def test_quote_includes_alt():
    q = quote_route(TRI, "A", "C", RULES)
    assert q["reachable"] and q["hops"] == 1 and q["path"] == ["A", "C"]
    assert q["alt"] == {"hops": 2, "fare": 3.0, "path": ["A", "B", "C"]}


def test_quote_alt_none_when_no_longer_simple_path():
    q = quote_route(EDGES, "A1", "B2", RULES)
    assert q["reachable"] and q["alt"] is None


def test_quote_unreachable():
    q = quote_route(EDGES, "A1", "ZZ", RULES)
    assert q["reachable"] is False and q["alt"] is None


def test_alt_becomes_shortest_after_edge_removal():
    before = quote_route(DIA, "S", "T", RULES)
    assert before["path"] == ["S", "X", "T"]
    assert before["alt"]["path"] == ["S", "Y", "Z", "T"]
    after = quote_route([e for e in DIA if e != ("S", "X")], "S", "T", RULES)
    assert after["path"] == ["S", "Y", "Z", "T"] and after["hops"] == 3
    assert after["alt"] is None
