from typing import Awaitable, Callable

from fastapi import APIRouter, HTTPException
from langdetect import detect
from starlette.websockets import WebSocket

from app.api.endpoints.common import handle_websocket
from app.api.singeltons import def_pipeline
from app.schemas.definition_verification import VerificationRequest, VerificationResponse

router = APIRouter()


async def process_verify_definition(request: dict, progress_callback: Callable[[str], Awaitable[None]]):
    def_pipeline.set_progress_callback(progress_callback)
    def_pipeline.lang = 'de' if detect(request["claim"]) == 'de' else 'en'
    return await def_pipeline.verify(request["word"], request["claim"])


@router.websocket("/verify-definition/ws")
async def websocket_verify_definition(websocket: WebSocket):
    await handle_websocket(websocket, process_verify_definition)


@router.post("/verify-definition", response_model=VerificationResponse)
async def verify_definition(request: VerificationRequest):
    def_pipeline.lang = 'de' if detect(request.claim) == 'de' else 'en'
    try:
        result = await def_pipeline.verify(request.word, request.claim)
        return VerificationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
