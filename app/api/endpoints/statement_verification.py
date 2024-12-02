from typing import Awaitable, Callable

from fastapi import APIRouter, HTTPException
from langdetect import detect
from starlette.websockets import WebSocket

from app.api.endpoints.common import handle_websocket
from app.api.singeltons import claim_pipeline
from app.schemas.statement_verification import VerificationRequest, VerificationResponse

router = APIRouter()


async def process_verify_statement(request: dict, progress_callback: Callable[[str], Awaitable[None]]):
    claim_pipeline.set_progress_callback(progress_callback)
    claim_pipeline.lang = 'de' if detect(request["claim"]) == 'de' else 'en'
    return await claim_pipeline.verify(request["claim"])


@router.websocket("/verify-statement/ws")
async def websocket_endpoint(websocket: WebSocket):
    await handle_websocket(websocket, process_verify_statement)


@router.post("/verify-statement", response_model=VerificationResponse)
async def verify_definition(request: VerificationRequest):
    claim_pipeline.lang = 'de' if detect(request.claim) == 'de' else 'en'
    try:
        result = await claim_pipeline.verify(request.claim)
        return VerificationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
