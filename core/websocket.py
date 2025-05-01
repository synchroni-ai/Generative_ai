from fastapi import WebSocket, WebSocketDisconnect
from celery.result import AsyncResult
import asyncio
import json


async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        # Validate task_id
        if not task_id:
            await websocket.send_json({"error": "Task ID is required"})
            await websocket.close()
            return

        # Poll Celery task status
        while True:
            task = AsyncResult(task_id)
            response = {
                "task_id": task_id,
                "status": task.state,
                "result": None,
                "error": None,
            }

            if task.state == "SUCCESS":
                response["result"] = task.result
                await websocket.send_json(response)
                break
            elif task.state == "FAILURE":
                response["error"] = str(task.info)
                await websocket.send_json(response)
                break
            else:
                # PENDING or other states
                await websocket.send_json(response)

            # Wait before polling again to avoid overwhelming the server
            await asyncio.sleep(1)

        # Close the connection after task completion
        await websocket.close()

    except WebSocketDisconnect:
        # Handle client disconnect
        print(f"WebSocket disconnected for task_id: {task_id}")
    except Exception as e:
        # Handle unexpected errors
        await websocket.send_json({"error": str(e)})
        await websocket.close()
