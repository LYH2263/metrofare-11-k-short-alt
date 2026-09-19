from app.engines.fare_rules import fare_for_hops
from app.engines.graph_bfs import two_simple_paths


def quote_route(edges: list[tuple[str, str]], start: str, end: str, rules: list[dict]) -> dict:
    shortest, second = two_simple_paths(edges, start, end)
    if shortest is None:
        return {
            "start": start,
            "end": end,
            "reachable": False,
            "hops": None,
            "fare": None,
            "path": None,
            "second": None,
        }
    hops = len(shortest) - 1
    result = {
        "start": start,
        "end": end,
        "reachable": True,
        "hops": hops,
        "fare": fare_for_hops(hops, rules),
        "path": shortest,
        "second": None,
    }
    if second is not None:
        second_hops = len(second) - 1
        result["second"] = {
            "hops": second_hops,
            "fare": fare_for_hops(second_hops, rules),
            "path": second,
        }
    return result
