from pydantic import BaseModel


class VerificationRequest(BaseModel):
    claim: str


class EvidResponse(BaseModel):
    title: str
    line_idx: int
    text: str
    sim: float


class AtomResponse(BaseModel):
    atom: str
    predicted: str
    selected_evids: list[EvidResponse]


class VerificationResponse(BaseModel):
    claim: str
    predicted: str
    factuality: float
    in_wiki: str
    atoms: list[AtomResponse] | None = None
