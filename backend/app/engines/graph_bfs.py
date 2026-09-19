from collections import defaultdict, deque


def _build_graph(edges: list[tuple[str, str]]) -> dict[str, set[str]]:
    g: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        if a == b:
            continue
        g[a].add(b)
        g[b].add(a)
    return g


def _bfs_path(
    g: dict[str, set[str]], start: str, end: str, drop: tuple[str, str] | None = None
) -> list[str] | None:
    """BFS returning the node list of a shortest path; None if unreachable."""
    if start == end:
        return [start]
    if start not in g or end not in g:
        return None
    parent: dict[str, str | None] = {start: None}
    q: deque[str] = deque([start])
    while q:
        cur = q.popleft()
        for nxt in g[cur]:
            if drop and ((cur == drop[0] and nxt == drop[1]) or
                         (cur == drop[1] and nxt == drop[0])):
                continue
            if nxt in parent:
                continue
            parent[nxt] = cur
            if nxt == end:
                path = [nxt]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])  # type: ignore[arg-type]
                path.reverse()
                return path
            q.append(nxt)
    return None


def shortest_path(edges: list[tuple[str, str]], start: str, end: str) -> list[str] | None:
    return _bfs_path(_build_graph(edges), start, end)


def shortest_hops(edges: list[tuple[str, str]], start: str, end: str) -> int | None:
    """Undirected graph BFS hop count; None if unreachable."""
    path = shortest_path(edges, start, end)
    return None if path is None else len(path) - 1


def two_simple_paths(
    edges: list[tuple[str, str]], start: str, end: str
) -> tuple[list[str] | None, list[str] | None]:
    """Return (shortest, second) simple paths as node lists.

    The second path has strictly more hops than the shortest; equal-length
    alternatives do not qualify. It is found by forbidding one shortest-path
    edge at a time and taking the shortest surviving route, which yields the
    shortest of all simple paths longer than the shortest. Returns
    (None, None) when unreachable and (shortest, None) when no strictly
    longer simple path exists.
    """
    g = _build_graph(edges)
    shortest = _bfs_path(g, start, end)
    if shortest is None:
        return None, None
    min_hops = len(shortest) - 1
    second: list[str] | None = None
    for i in range(min_hops):
        cand = _bfs_path(g, start, end, drop=(shortest[i], shortest[i + 1]))
        if cand is None or len(cand) - 1 <= min_hops:
            continue
        if second is None or len(cand) < len(second):
            second = cand
    return shortest, second
