from typing import Awaitable, Callable
from fastapi import WebSocket, WebSocketDisconnect
import json


def create_progress_callback(websocket: WebSocket, is_connected: Callable[[], bool]):
    async def progress_callback(message: str):
        if is_connected():
            try:
                await websocket.send_text(json.dumps({"type": "progress", "message": message}))
            except RuntimeError:
                print("WebSocket unexpectedly closed. Stopping progress updates.")
    return progress_callback


async def handle_websocket(
    websocket: WebSocket,
    process_request: Callable[[dict, Callable[[str], Awaitable[None]]], Awaitable[dict]],
):
    """
    Handles a WebSocket connection for a generic request-processing workflow.

    Args:
        websocket: The WebSocket connection.
        process_request: A callback function that takes the request data and a progress callback.
                         It should return the result of processing.
    """
    await websocket.accept()
    is_connected = True

    try:
        while True:
            try:
                data = await websocket.receive_text()
                request = json.loads(data)

                progress_callback = create_progress_callback(websocket, lambda: is_connected)

                # Process the request and get the result
                result = await process_request(request, progress_callback)

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
            except RuntimeError:
                print("Attempted to close an already closed WebSocket.")
            except Exception as e:
                print(f"Error while closing WebSocket: {str(e)}")
