from fastapi import APIRouter

from app.schemas.example import ExampleSchema, ExampleResponseSchema

router = APIRouter()

@router.post("/", response_model=ExampleResponseSchema)
async def create_example(data: ExampleSchema):
    return ExampleResponseSchema(name=data.name, description=data.description)
