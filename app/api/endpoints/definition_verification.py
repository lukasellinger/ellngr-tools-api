import json

from fastapi import APIRouter, HTTPException
from langdetect import detect
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.singeltons import pipeline
from app.schemas.definition_verification import VerificationRequest, VerificationResponse

router = APIRouter()


@router.websocket("/verify-definition/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    is_connected = True

    try:
        while True:
            try:
                data = await websocket.receive_text()
                request = json.loads(data)
                async def progress_callback(message: str):
                    if is_connected:
                        try:
                            await websocket.send_text(json.dumps({"type": "progress",
                                                                  "message": message}))
                        except RuntimeError:
                            print("WebSocket unexpectedly closed. Stopping progress updates.")
                            return

                pipeline.set_progress_callback(progress_callback)

                pipeline.lang = 'de' if detect(request["claim"]) == 'de' else 'en'
                result = await pipeline.verify(
                    request["word"],
                    request["claim"],
                )

                if is_connected:
                    try:
                        await websocket.send_text(json.dumps({"type": "result", "data": result}))
                    except RuntimeError:
                        print("WebSocket closed during result sending. Exiting.")
                        break

            except WebSocketDisconnect:
                print("Client disconnected")
                is_connected = False
                break
            except Exception as e:
                if is_connected:
                    await websocket.send_text(json.dumps({"type": "error", "message": str(e)}))
                break

    finally:
        if is_connected:
            try:
                await websocket.close()
                is_connected = False
            except RuntimeError:
                print("Attempted to close an already closed WebSocket.")
            except Exception as e:
                print(f"Error while closing WebSocket: {str(e)}")


@router.post("/verify-definition", response_model=VerificationResponse)
async def verify_definition(request: VerificationRequest):
    pipeline.lang = 'de' if detect(request.claim) == 'de' else 'en'
    try:
        result = await pipeline.verify(request.word, request.claim)
        return VerificationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
