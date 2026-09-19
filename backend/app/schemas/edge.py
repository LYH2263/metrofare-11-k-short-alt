from pydantic import BaseModel


class EdgeBody(BaseModel):
    a: str
    b: str
