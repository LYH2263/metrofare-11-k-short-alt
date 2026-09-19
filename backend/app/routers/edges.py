from fastapi import APIRouter
from app.services.metro_service import MetroService

router = APIRouter(tags=["edges"])

@router.get("/edges")
def list_edges():
    with MetroService() as s:
        return {"items": s.edges()}


@router.delete("/edges")
def delete_edge(a: str, b: str):
    with MetroService() as s:
        s.delete_edge(a, b)
        return {"ok": True}
