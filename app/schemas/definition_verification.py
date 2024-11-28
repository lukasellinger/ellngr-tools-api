from pydantic import BaseModel


class VerificationRequest(BaseModel):
    word: str
    claim: str


class VerificationResponse(BaseModel):
    word: str
    claim: str
    predicted: str
    in_wiki: str
    selected_evidences: list[dict] | None = None
