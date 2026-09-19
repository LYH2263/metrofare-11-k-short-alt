from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import second_simple_path, shortest_path


def quote_route(edges: list[tuple[str, str]], start: str, end: str, rules: list[dict]) -> dict:
    path = shortest_path(edges, start, end)
    if path is None:
        return {"start": start, "end": end, "hops": None, "fare": None,
                "path": None, "alt": None, "reachable": False}
    hops = len(path) - 1
    alt_path = second_simple_path(edges, start, end)
    alt = None
    if alt_path is not None:
        alt_hops = len(alt_path) - 1
        alt = {"hops": alt_hops, "fare": fare_for_hops(alt_hops, rules), "path": alt_path}
    return {"start": start, "end": end, "hops": hops, "fare": fare_for_hops(hops, rules),
            "path": path, "alt": alt, "reachable": True}
