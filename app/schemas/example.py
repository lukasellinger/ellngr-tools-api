from pydantic import BaseModel, Field


class ExampleSchema(BaseModel):
    """Request schema for creating an example."""
    name: str = Field(..., max_length=10, description="Name of the example")
    description: str

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Example",
                "description": "This is an example schema for FastAPI."
            }
        }

class ExampleResponseSchema(BaseModel):
    """Response schema for returning an example."""
    name: str
    description: str
