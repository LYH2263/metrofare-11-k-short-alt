from app.db import connect
from app.engines.route_quote import quote_route
from app.repositories import edges as edges_repo
from app.repositories import fare_rules as rules_repo
from app.repositories import runs as runs_repo
from app.repositories import settings as settings_repo
from app.repositories import stations as stations_repo


class MetroService:
    def __init__(self):
        self._conn = connect()

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()

    def stations(self):
        return stations_repo.list_all(self._conn)

    def station(self, code: str):
        return stations_repo.get_by_code(self._conn, code)

    def edges(self):
        return [{"a": a, "b": b} for a, b in edges_repo.list_pairs(self._conn)]

    def add_edge(self, a: str, b: str):
        if a == b:
            raise ValueError("起讫站不能相同")
        edges_repo.add_pair(self._conn, a, b)
        return self.edges()

    def delete_edge(self, a: str, b: str):
        edges_repo.delete_pair(self._conn, a, b)
        return self.edges()

    def fare_rules(self):
        return rules_repo.list_ordered(self._conn)

    def settings(self):
        return settings_repo.get_map(self._conn)

    def quote(self, start: str, end: str, persist: bool):
        edges = edges_repo.list_pairs(self._conn)
        rules = rules_repo.as_calc_rules(self._conn)
        result = quote_route(edges, start, end, rules)
        run_id = None
        if persist and result.get("reachable"):
            # 只读对照：次短仅当次返回，落库只保留最短路那一条记录
            stored = {k: v for k, v in result.items() if k != "second"}
            run_id = runs_repo.insert(self._conn, "quote", {"start": start, "end": end}, stored)
        return {"run_id": run_id, **result}

    def history(self, limit=50):
        return runs_repo.list_recent(self._conn, limit)

    def dashboard(self):
        st = stations_repo.list_all(self._conn)
        clean = [s for s in st if "种子" not in s["name"]]
        dirty = [s for s in st if "种子" in s["name"]]
        return {
            "station_count": len(st),
            "edge_count": len(edges_repo.list_pairs(self._conn)),
            "clean_stations": len(clean),
            "dirty_stations": len(dirty),
        }
