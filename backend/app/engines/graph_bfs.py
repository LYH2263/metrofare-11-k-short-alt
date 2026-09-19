from collections import defaultdict, deque


def _adjacency(edges: list[tuple[str, str]]) -> dict[str, list[str]]:
    """Undirected adjacency with sorted neighbors so results are deterministic."""
    g: dict[str, set[str]] = defaultdict(set)
    for a, b in edges:
        g[a].add(b)
        g[b].add(a)
    return {node: sorted(nbrs) for node, nbrs in g.items()}


def shortest_hops(edges: list[tuple[str, str]], start: str, end: str) -> int | None:
    """Undirected graph BFS hop count; None if unreachable."""
    path = shortest_path(edges, start, end)
    return None if path is None else len(path) - 1


def shortest_path(edges: list[tuple[str, str]], start: str, end: str) -> list[str] | None:
    """BFS shortest path as an ordered station list; None if unreachable."""
    if start == end:
        return [start]
    g = _adjacency(edges)
    if start not in g or end not in g:
        return None
    parent: dict[str, str | None] = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        for nxt in g[cur]:
            if nxt in parent:
                continue
            parent[nxt] = cur
            if nxt == end:
                path = [end]
                while path[-1] != start:
                    path.append(parent[path[-1]])
                return path[::-1]
            q.append(nxt)
    return None


def second_simple_path(edges: list[tuple[str, str]], start: str, end: str) -> list[str] | None:
    """Shortest simple path with strictly more stations than the shortest path.

    None when unreachable, when start == end, or when no strictly longer
    simple path exists (never a copy of the shortest path).
    """
    shortest = shortest_path(edges, start, end)
    if shortest is None or start == end:
        return None
    g = _adjacency(edges)
    min_hops = len(shortest)  # strictly more stations == strictly more hops
    for limit in range(min_hops, len(g)):  # a simple path has at most len(g)-1 hops
        found = _simple_path_between(g, start, end, min_hops, limit)
        if found is not None:
            return found
    return None


def _simple_path_between(
    g: dict[str, list[str]], start: str, end: str, min_hops: int, max_hops: int
) -> list[str] | None:
    """DFS for a simple start->end path with hop count in [min_hops, max_hops]."""
    visited = {start}
    trail = [start]

    def dfs(cur: str, hops_left: int) -> list[str] | None:
        if cur == end:
            return list(trail) if len(trail) - 1 >= min_hops else None
        if hops_left == 0:
            return None
        for nxt in g[cur]:
            if nxt in visited:
                continue
            visited.add(nxt)
            trail.append(nxt)
            found = dfs(nxt, hops_left - 1)
            if found is not None:
                return found
            trail.pop()
            visited.discard(nxt)
        return None

    return dfs(start, max_hops)
