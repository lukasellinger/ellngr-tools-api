from pydantic import BaseModel, Field


class FixedJsonOpenAiResponse(BaseModel):
    """Response format for OpenAi request for fixing json"""

    fixed_json: str
    explanation: str


class FixedJsonRequest(BaseModel):
    """Request schema for fixing json."""
    malformed_json: str = Field(..., description="Malformed json that need to be fixed.")

    class Config:
        json_schema_extra = {
            "example": {
                "malformed_json": "{\"asdf\": '1'}",
            }
        }


class FixedJsonResponse(BaseModel):
    """Response format for fixed-json request."""

    json: dict
    explanation: str | None = ''
