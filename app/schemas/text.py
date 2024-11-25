from pydantic import BaseModel, Field


class SummaryOpenAiResponse(BaseModel):
    """Response format for OpenAi request for summarizing texts"""

    summary: str


class SummaryRequest(BaseModel):
    """Request schema for summarizing text."""
    text: str = Field(..., max_length=1024, description="Text, which should be summarized.")
    language: str | None = 'English'

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy "
                        "eirmod tempor invidunt ut labore et dolore magna aliquyam",
                "language": "German"
            }
        }


class SummaryResponse(BaseModel):
    """Response format for summary request."""

    summary: str


class FactsplitOpenAiResponse(BaseModel):
    """Response format for OpenAi request for splitting sentences into facts."""

    facts: list[str]


class FactsplitRequest(BaseModel):
    """Request schema for summarizing text."""
    sentence: str = Field(..., max_length=256, description="Sentence, which should be split into facts.")
    language: str | None = 'English'

    class Config:
        json_schema_extra = {
            "example": {
                "sentence": "A bicycle is a vehicle with two wheels that people padle to move, and"
                            "it can fly through the air.",
                "language": "German"
            }
        }


class FactsplitResponse(BaseModel):
    """Response format for splitting a sentence into facts."""

    original_sentence: str
    facts: list[str]
