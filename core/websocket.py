from fastapi import WebSocket, WebSocketDisconnect
from celery.result import AsyncResult
import asyncio
import json
from fastapi import Query
from utils.jwt_auth import get_user_from_ws
from starlette.websockets import WebSocket, WebSocketDisconnect


async def websocket_endpoint(websocket: WebSocket, task_id: str):
    await websocket.accept()
    try:
        user = await get_user_from_ws(websocket)
        username = user.get("sub")
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
                "progress": None,  # include progress
            }

            task_owner = (
                task.result.get("username")
                if task.result and isinstance(task.result, dict)
                else None
            )
            if username != "synchroni" and username != task_owner:
                response["error"] = "Access denied for this task."
                try:
                    await websocket.send_json(response)
                except RuntimeError:
                    # connection closed already
                    break
                try:
                    await websocket.close()
                except RuntimeError:
                    pass
                break

            if task.state == "SUCCESS":
                response["result"] = task.info
                await websocket.send_json(response)
                break
            elif task.state == "FAILURE":
                response["error"] = str(task.info)
                await websocket.send_json(response)
                break
            elif task.state == "PROGRESS":
                response["progress"] = task.info.get("progress")  # Get progress data
                await websocket.send_json(response)
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
#############