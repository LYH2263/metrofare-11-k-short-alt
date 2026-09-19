from fastapi import APIRouter, HTTPException
from app.schemas.edge import EdgeBody
from app.services.metro_service import MetroService

router = APIRouter(tags=["edges"])

@router.get("/edges")
def list_edges():
    with MetroService() as s:
        return {"items": s.edges()}

@router.post("/edges")
def add_edge(body: EdgeBody):
    with MetroService() as s:
        try:
            items = s.add_edge(body.a, body.b)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"items": items}

@router.delete("/edges/{a}/{b}")
def delete_edge(a: str, b: str):
    with MetroService() as s:
        return {"items": s.delete_edge(a, b)}
